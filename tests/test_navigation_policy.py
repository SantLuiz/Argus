from app.guidance.navigation_policy import build_navigation_hint, prepare_navigation_detections
from app.schemas.detection import DepthInfo, DetectionItem


def detection(class_name, bbox, zone="centro", proximity="medium", confidence=0.80):
    return DetectionItem(
        class_name=class_name,
        confidence=confidence,
        bbox=bbox,
        zone=zone,
        depth=DepthInfo(relative_value=0.5, proximity=proximity, label_pt="medio"),
        priority="baixa",
    )


def test_prepare_navigation_detections_marks_accessories_as_low_priority() -> None:
    detections = [
        detection("person", [100, 40, 220, 360], confidence=0.90),
        detection("backpack", [130, 150, 190, 260], confidence=0.85),
        detection("bottle", [10, 10, 30, 80], zone="esquerda", confidence=0.70),
    ]

    prepared = prepare_navigation_detections(detections)

    assert [item.class_name for item in prepared] == ["pessoa", "mochila", "garrafa"]
    assert prepared[0].semantic_role == "pessoa"
    assert prepared[1].semantic_role == "baixa_prioridade"
    assert prepared[2].semantic_role == "baixa_prioridade"


def test_prepare_navigation_detections_prioritizes_points_of_interest() -> None:
    detections = [
        detection("person", [10, 10, 80, 200], zone="centro", proximity="very_near", confidence=0.95),
        detection("door", [200, 10, 280, 220], zone="direita", proximity="medium", confidence=0.70),
    ]

    prepared = prepare_navigation_detections(detections)

    assert prepared[0].class_name == "porta"
    assert prepared[0].semantic_role == "ponto_interesse"
    assert prepared[0].priority == "alta"


def test_build_navigation_hint_uses_direction_and_relative_distance() -> None:
    prepared = prepare_navigation_detections(
        [
            detection("elevator", [120, 20, 220, 260], zone="esquerda", proximity="near", confidence=0.88),
        ]
    )

    hint = build_navigation_hint(prepared)

    assert hint.target_label_pt == "elevador"
    assert hint.direction == "esquerda"
    assert hint.proximity == "near"
    assert "à esquerda" in hint.instruction


def test_isolated_low_priority_item_can_appear_with_low_priority() -> None:
    prepared = prepare_navigation_detections(
        [
            detection("suitcase", [100, 120, 180, 260], zone="centro", proximity="very_near", confidence=0.92),
        ]
    )

    assert prepared[0].class_name == "mala"
    assert prepared[0].semantic_role == "baixa_prioridade"
    assert prepared[0].priority == "baixa"
