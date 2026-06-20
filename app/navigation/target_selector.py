from app.detection.class_mapper import map_class
from app.schemas.detection import DetectionItem


class TargetSelector:
    """Seleciona o melhor alvo visivel para orientacao local no frame atual."""

    def select(self, detections: list[DetectionItem], target_class: str | None) -> DetectionItem | None:
        if not target_class:
            return None

        target_normalized = map_class(target_class).canonical_name
        candidates = [
            detection
            for detection in detections
            if (detection.normalized_class or map_class(detection.class_name).canonical_name) == target_normalized
        ]
        if not candidates:
            return None

        return sorted(candidates, key=_target_sort_key)[0]


def _target_sort_key(detection: DetectionItem) -> tuple[float, int, int, float, float]:
    x1, y1, x2, y2 = detection.bbox
    bbox_area = max(x2 - x1, 0) * max(y2 - y1, 0)
    center_penalty = 0 if detection.zone == "centro" else 1
    return (
        -detection.navigation_score,
        center_penalty,
        -bbox_area,
        -detection.confidence,
        -detection.depth.relative_value,
    )

