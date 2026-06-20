from app.schemas.detection import ObjectDetection


class DetectionMerger:
    """Combina deteccoes de fontes diferentes preservando origem e corroboracao."""

    def __init__(self, iou_threshold: float = 0.70) -> None:
        self.iou_threshold = iou_threshold

    def merge(self, detection_groups: list[list[ObjectDetection]]) -> list[ObjectDetection]:
        merged: list[ObjectDetection] = []
        for group in detection_groups:
            for detection in group:
                duplicate_index = self._find_duplicate(merged, detection)
                if duplicate_index is None:
                    merged.append(detection)
                else:
                    merged[duplicate_index] = _merge_pair(merged[duplicate_index], detection)
        return merged

    def _find_duplicate(self, detections: list[ObjectDetection], candidate: ObjectDetection) -> int | None:
        for index, detection in enumerate(detections):
            if _compatible_class(detection.class_name, candidate.class_name) and _iou(detection.bbox, candidate.bbox) >= self.iou_threshold:
                return index
        return None


def _merge_pair(first: ObjectDetection, second: ObjectDetection) -> ObjectDetection:
    chosen = first if first.confidence >= second.confidence else second
    confidence = min(max(first.confidence, second.confidence) + 0.08, 0.99)
    source_model = "+".join(dict.fromkeys([first.source_model, second.source_model]))
    detection_type = first.detection_type if first.detection_type == second.detection_type else "corroborated"
    return chosen.model_copy(
        update={
            "confidence": round(confidence, 4),
            "source_model": source_model,
            "detection_type": detection_type,
            "corroborated": True,
        }
    )


def _compatible_class(first: str, second: str) -> bool:
    if first == second:
        return True
    groups = [
        {"door", "elevator door", "entrance", "exit"},
        {"stairs", "stair", "staircase", "step"},
        {"tactile paving", "tactile floor", "guiding block", "warning block"},
        {"ramp", "accessibility ramp", "wheelchair ramp"},
        {"reception", "reception desk", "reception area", "front desk"},
    ]
    return any(first in group and second in group for group in groups)


def _iou(first: list[int], second: list[int]) -> float:
    ax1, ay1, ax2, ay2 = first
    bx1, by1, bx2, by2 = second
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = max(inter_x2 - inter_x1, 0) * max(inter_y2 - inter_y1, 0)
    if inter_area == 0:
        return 0.0
    first_area = max(ax2 - ax1, 0) * max(ay2 - ay1, 0)
    second_area = max(bx2 - bx1, 0) * max(by2 - by1, 0)
    return inter_area / max(first_area + second_area - inter_area, 1)

