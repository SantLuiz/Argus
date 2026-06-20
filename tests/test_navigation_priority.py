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


def test_navigation_priority_favors_centered_point_of_interest_over_person() -> None:
    priority = NavigationPriority()

    prioritized = priority.prioritize(
        [
            detection("person", zone="centro", proximity="very_near", confidence=0.95),
            detection("door", zone="centro", proximity="medium", confidence=0.70),
        ]
    )

    assert prioritized[0].class_name == "porta"
    assert prioritized[0].semantic_role == "ponto_interesse"
    assert prioritized[0].priority == "alta"


def test_navigation_priority_favors_accessibility_element() -> None:
    priority = NavigationPriority()

    prioritized = priority.prioritize(
        [
            detection("chair", zone="centro", proximity="near", confidence=0.95),
            detection("wheelchair ramp", zone="esquerda", proximity="medium", confidence=0.65),
        ]
    )

    assert prioritized[0].class_name == "rampa acessivel"
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

    assert generator.generate(detections, hint) == "Escada a direita, proximo."


def test_message_generator_reports_clear_path_to_centered_door() -> None:
    priority = NavigationPriority()
    generator = MessageGenerator()
    detections = priority.prioritize([detection("door", zone="centro", proximity="medium")])
    hint = priority.build_hint(detections)

    assert generator.generate(detections, hint) == "Caminho livre em direcao a porta."
