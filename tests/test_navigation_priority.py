from app.guidance.message_generator import MessageGenerator
from app.guidance.navigation_priority import NavigationPriority
from app.schemas.detection import DepthInfo, DetectionItem


def detection(class_name, zone="centro", proximity="medium", confidence=0.80):
    return DetectionItem(
        class_name=class_name,
        confidence=confidence,
        bbox=[0, 0, 100, 100],
        zone=zone,
        depth=DepthInfo(relative_value=0.5, proximity=proximity, label_pt="medio"),
        priority="baixa",
    )


def test_navigation_priority_prioritizes_very_near_center_person_over_poi() -> None:
    priority = NavigationPriority()

    prioritized = priority.prioritize(
        [
            detection("person", zone="centro", proximity="very_near", confidence=0.95),
            detection("door", zone="centro", proximity="medium", confidence=0.70),
        ]
    )

    assert prioritized[0].class_name == "pessoa"
    assert prioritized[0].semantic_role == "pessoa"
    assert prioritized[0].priority == "alta"
    assert prioritized[1].raw_class_name == "door"
    assert prioritized[1].normalized_class == "porta"
    assert prioritized[1].label_pt == "porta"
    assert prioritized[1].category == "ponto_interesse"
    assert prioritized[0].priority_score > 0


def test_navigation_priority_favors_accessibility_element() -> None:
    priority = NavigationPriority()

    prioritized = priority.prioritize(
        [
            detection("chair", zone="centro", proximity="near", confidence=0.95),
            detection("wheelchair ramp", zone="esquerda", proximity="medium", confidence=0.65),
        ]
    )

    assert prioritized[0].class_name == "rampa acessível"
    assert prioritized[0].semantic_role == "acessibilidade"


def test_navigation_priority_keeps_generic_objects_low() -> None:
    priority = NavigationPriority()

    prioritized = priority.prioritize(
        [
            detection("bottle", zone="centro", proximity="very_near", confidence=0.99),
            detection("person", zone="direita", proximity="medium", confidence=0.70),
        ]
    )

    assert prioritized[0].class_name == "pessoa"
    assert prioritized[-1].semantic_role == "baixa_prioridade"
    assert prioritized[-1].priority == "baixa"


def test_message_generator_outputs_short_navigation_message() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([detection("stairs", zone="direita", proximity="near")])
    hint = priority.build_hint(detections)

    assert generator.generate(detections, hint) == "Escada à direita."


def test_message_generator_reports_clear_path_to_centered_door() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([detection("door", zone="centro", proximity="medium")])
    hint = priority.build_hint(detections)

    assert generator.generate(detections, hint) == "Caminho livre em direcao a porta."


def test_accessibility_mapping_generates_tactile_paving_message() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([detection("tactile_paving", zone="centro", proximity="medium")])
    hint = priority.build_hint(detections)

    assert detections[0].class_name == "piso tátil"
    assert detections[0].semantic_role == "acessibilidade"
    assert generator.generate(detections, hint) == "Piso tátil identificado à frente."


def test_accessibility_mapping_generates_handrail_message() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([detection("handrail", zone="direita", proximity="far")])
    hint = priority.build_hint(detections)

    assert generator.generate(detections, hint) == "Corrimão à direita."


def test_accessibility_mapping_generates_wheelchair_ramp_message() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([detection("wheelchair_ramp", zone="esquerda", proximity="medium")])
    hint = priority.build_hint(detections)

    assert generator.generate(detections, hint) == "Rampa acessível à esquerda."


def test_accessibility_mapping_generates_elevator_message() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([detection("elevator", zone="centro", proximity="medium")])
    hint = priority.build_hint(detections)

    assert generator.generate(detections, hint) == "Elevador à frente."


def test_no_accessibility_message_without_detection() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([])
    hint = priority.build_hint(detections)

    assert generator.generate(detections, hint) == "Nenhum ponto de interesse ou obstaculo relevante detectado."
