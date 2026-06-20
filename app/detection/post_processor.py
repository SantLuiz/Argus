from app.detection.priority import LOW_PRIORITY_CLASSES, PERSON_CLASSES, normalize_class_name
from app.schemas.detection import ObjectDetection


class DetectionPostProcessor:
    """Remove ruido de deteccoes YOLO antes de profundidade e guidance.

    A regra principal e tratar pessoa + acessorios carregados como uma unica
    entidade visual: pessoa. Acessorios isolados continuam podendo aparecer,
    mas serao pontuados como baixa prioridade nas etapas seguintes.
    """

    def __init__(
        self,
        iou_threshold: float = 0.03,
        accessory_intersection_threshold: float = 0.25,
        center_margin_ratio: float = 0.20,
        near_distance_ratio: float = 0.35,
    ) -> None:
        self.iou_threshold = iou_threshold
        self.accessory_intersection_threshold = accessory_intersection_threshold
        self.center_margin_ratio = center_margin_ratio
        self.near_distance_ratio = near_distance_ratio

    def process(self, detections: list[ObjectDetection]) -> list[ObjectDetection]:
        people = [item for item in detections if _is_person(item)]
        filtered: list[ObjectDetection] = []

        for detection in detections:
            if _is_low_priority(detection) and self._belongs_to_person(detection, people):
                continue
            filtered.append(detection)

        return filtered

    def _belongs_to_person(self, detection: ObjectDetection, people: list[ObjectDetection]) -> bool:
        return any(
            bbox_iou(detection.bbox, person.bbox) >= self.iou_threshold
            or intersection_ratio(detection.bbox, person.bbox) >= self.accessory_intersection_threshold
            or center_inside(detection.bbox, person.bbox, self.center_margin_ratio)
            or boxes_are_near(detection.bbox, person.bbox, self.near_distance_ratio)
            for person in people
        )


def bbox_iou(a: list[int], b: list[int]) -> float:
    inter_area = _intersection_area(a, b)
    area_a = _bbox_area(a)
    area_b = _bbox_area(b)
    union = area_a + area_b - inter_area
    return inter_area / union if union else 0.0


def intersection_ratio(inner: list[int], outer: list[int]) -> float:
    area = _bbox_area(inner)
    return _intersection_area(inner, outer) / area if area else 0.0


def center_inside(inner: list[int], outer: list[int], margin_ratio: float = 0.0) -> bool:
    x1, y1, x2, y2 = inner
    ox1, oy1, ox2, oy2 = outer
    margin_x = int((ox2 - ox1) * margin_ratio)
    margin_y = int((oy2 - oy1) * margin_ratio)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (ox1 - margin_x) <= center_x <= (ox2 + margin_x) and (oy1 - margin_y) <= center_y <= (oy2 + margin_y)


def boxes_are_near(a: list[int], b: list[int], distance_ratio: float) -> bool:
    ax, ay = _bbox_center(a)
    bx, by = _bbox_center(b)
    person_width = max(abs(b[2] - b[0]), 1)
    person_height = max(abs(b[3] - b[1]), 1)
    max_distance = ((person_width**2 + person_height**2) ** 0.5) * distance_ratio
    distance = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
    return distance <= max_distance


def _is_low_priority(detection: ObjectDetection) -> bool:
    return normalize_class_name(detection.class_name) in LOW_PRIORITY_CLASSES


def _is_person(detection: ObjectDetection) -> bool:
    return normalize_class_name(detection.class_name) in PERSON_CLASSES


def _bbox_area(bbox: list[int]) -> int:
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)


def _intersection_area(a: list[int], b: list[int]) -> int:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    return max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)


def _bbox_center(bbox: list[int]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2
