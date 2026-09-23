import numpy as np

from app.schemas.detection import DepthInfo, DetectionItem, ObjectDetection


def combine_detections_with_depth(
    detections: list[ObjectDetection],
    depth_map: np.ndarray,
    depth_source: str = "midas",
) -> list[DetectionItem]:
    """Associa cada bbox YOLO a uma profundidade relativa.

    O mapa de profundidade deve estar normalizado entre 0 e 1. Neste prototipo,
    valores maiores sao tratados como objetos mais proximos, coerente com o uso
    comum de mapas de profundidade/inversa de modelos monoculares como MiDaS.
    """

    if depth_map.ndim != 2:
        raise ValueError("depth_map deve ser uma matriz 2D.")

    height, width = depth_map.shape
    combined: list[DetectionItem] = []

    for detection in detections:
        x1, y1, x2, y2 = _clip_bbox(detection.bbox, width, height)
        if x2 <= x1 or y2 <= y1:
            depth = DepthInfo(relative_value=0.0, proximity="unknown", label_pt="nao estimado", source=depth_source)
        else:
            bbox_depth = depth_map[y1:y2, x1:x2]
            relative_value = float(np.median(bbox_depth))
            depth = _depth_info_from_relative(relative_value, source=depth_source)

        zone = _horizontal_zone(x1, x2, width)
        combined.append(
            DetectionItem(
                class_name=detection.class_name,
                confidence=detection.confidence,
                bbox=[x1, y1, x2, y2],
                zone=zone,
                depth=depth,
                priority=_priority_for(detection.class_name, zone, depth.proximity),
                source_model=detection.source_model,
                detection_type=detection.detection_type,
                corroborated=detection.corroborated,
            )
        )

    return combined


def _depth_info_from_relative(value: float, source: str = "unknown") -> DepthInfo:
    value = min(max(value, 0.0), 1.0)
    if value >= 0.85:
        return DepthInfo(relative_value=round(value, 3), proximity="very_near", label_pt="muito proximo", source=source)
    if value >= 0.60:
        return DepthInfo(relative_value=round(value, 3), proximity="near", label_pt="proximo", source=source)
    if value >= 0.35:
        return DepthInfo(relative_value=round(value, 3), proximity="medium", label_pt="medio", source=source)
    return DepthInfo(relative_value=round(value, 3), proximity="far", label_pt="distante", source=source)


def _priority_for(class_name: str, zone: str, proximity: str) -> str:
    critical_classes = {"obstaculo", "pessoa", "escada", "degrau"}
    close_labels = {"very_near", "near"}
    if class_name in critical_classes and zone == "centro" and proximity in close_labels:
        return "alta"
    if class_name in critical_classes or proximity in close_labels:
        return "media"
    return "baixa"


def _clip_bbox(bbox: list[int], image_width: int, image_height: int) -> tuple[int, int, int, int]:
    if len(bbox) != 4:
        raise ValueError("bbox deve conter quatro valores: [x1, y1, x2, y2].")

    x1, y1, x2, y2 = bbox
    clipped_x1 = min(max(int(round(x1)), 0), image_width)
    clipped_y1 = min(max(int(round(y1)), 0), image_height)
    clipped_x2 = min(max(int(round(x2)), 0), image_width)
    clipped_y2 = min(max(int(round(y2)), 0), image_height)
    return clipped_x1, clipped_y1, clipped_x2, clipped_y2


def _horizontal_zone(x1: int, x2: int, image_width: int) -> str:
    center_x = (x1 + x2) / 2
    left_limit = image_width / 3
    right_limit = (image_width * 2) / 3

    if center_x < left_limit:
        return "esquerda"
    if center_x > right_limit:
        return "direita"
    return "centro"
