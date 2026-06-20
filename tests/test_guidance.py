from app.guidance.message_builder import build_guidance_message
from app.schemas.detection import DepthInfo, DetectionItem


def test_build_guidance_message_prioritizes_near_center_obstacle() -> None:
    detections = [
        DetectionItem(
            class_name="cadeira",
            confidence=0.70,
            bbox=[0, 0, 100, 100],
            zone="esquerda",
            depth=DepthInfo(relative_value=0.2, proximity="far", label_pt="distante"),
            priority="baixa",
        ),
        DetectionItem(
            class_name="obstaculo",
            confidence=0.80,
            bbox=[100, 100, 300, 400],
            zone="centro",
            depth=DepthInfo(relative_value=0.8, proximity="near", label_pt="proximo"),
            priority="alta",
        ),
    ]

    message = build_guidance_message(detections)

    assert message.startswith("Obstaculo ao centro, proximo")
    assert "Cadeira a esquerda, distante" in message


def test_build_guidance_message_handles_empty_list() -> None:
    assert build_guidance_message([]) == "Nenhum ponto de interesse ou obstaculo relevante detectado."


def test_build_guidance_message_orders_by_proximity_before_priority() -> None:
    detections = [
        DetectionItem(
            class_name="porta",
            confidence=0.95,
            bbox=[0, 0, 100, 100],
            zone="centro",
            depth=DepthInfo(relative_value=0.4, proximity="medium", label_pt="medio"),
            priority="alta",
        ),
        DetectionItem(
            class_name="person",
            confidence=0.70,
            bbox=[0, 0, 100, 100],
            zone="direita",
            depth=DepthInfo(relative_value=0.9, proximity="very_near", label_pt="muito proximo"),
            priority="media",
        ),
    ]

    message = build_guidance_message(detections)

    assert message.startswith("Pessoa a direita, muito proxima")
    assert "Porta ao centro, a media distancia" in message


def test_build_guidance_message_limits_number_of_items() -> None:
    detections = [
        DetectionItem(
            class_name=f"objeto{i}",
            confidence=0.90,
            bbox=[0, 0, 100, 100],
            zone="centro",
            depth=DepthInfo(relative_value=0.8, proximity="near", label_pt="proximo"),
            priority="media",
        )
        for i in range(4)
    ]

    message = build_guidance_message(detections)

    assert message.count(".") == 4
    assert "Ha outros objetos detectados na cena." in message
