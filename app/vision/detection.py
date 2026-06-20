from PIL import Image

from app.schemas.detection import DetectionItem, DepthInfo


class PlaceholderObjectDetector:
    """Detector temporario para validar o contrato da API antes do modelo real."""

    def detect(self, image: Image.Image) -> list[DetectionItem]:
        width, height = image.size
        bbox_width = max(int(width * 0.34), 1)
        bbox_height = max(int(height * 0.45), 1)
        x1 = max((width - bbox_width) // 2, 0)
        y1 = max(int(height * 0.42), 0)
        x2 = min(x1 + bbox_width, width)
        y2 = min(y1 + bbox_height, height)

        return [
            DetectionItem(
                class_name="obstaculo",
                confidence=0.60,
                bbox=[x1, y1, x2, y2],
                zone=_horizontal_zone(x1, x2, width),
                depth=DepthInfo(relative_value=0.0, proximity="unknown", label_pt="nao estimado"),
                priority="media",
            )
        ]


def _horizontal_zone(x1: int, x2: int, image_width: int) -> str:
    center_x = (x1 + x2) / 2
    left_limit = image_width / 3
    right_limit = (image_width * 2) / 3

    if center_x < left_limit:
        return "esquerda"
    if center_x > right_limit:
        return "direita"
    return "centro"
