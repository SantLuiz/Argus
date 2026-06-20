from app.detection.post_processor import DetectionPostProcessor, bbox_iou, intersection_ratio
from app.schemas.detection import ObjectDetection


def detection(class_name: str, bbox: list[int], confidence: float = 0.90) -> ObjectDetection:
    return ObjectDetection(class_name=class_name, confidence=confidence, bbox=bbox)


def test_person_plus_overlapping_backpack_returns_only_person() -> None:
    processor = DetectionPostProcessor()
    detections = [
        detection("person", [100, 50, 250, 400]),
        detection("backpack", [130, 140, 230, 300]),
    ]

    filtered = processor.process(detections)

    assert [item.class_name for item in filtered] == ["person"]


def test_person_plus_near_handbag_returns_only_person() -> None:
    processor = DetectionPostProcessor()
    detections = [
        detection("person", [100, 50, 250, 400]),
        detection("handbag", [220, 210, 290, 310]),
    ]

    filtered = processor.process(detections)

    assert [item.class_name for item in filtered] == ["person"]


def test_isolated_suitcase_far_from_person_can_remain() -> None:
    processor = DetectionPostProcessor()
    detections = [
        detection("person", [20, 40, 120, 360]),
        detection("suitcase", [400, 260, 500, 430]),
    ]

    filtered = processor.process(detections)

    assert [item.class_name for item in filtered] == ["person", "suitcase"]


def test_door_person_backpack_prioritizes_door_and_person_after_filtering() -> None:
    processor = DetectionPostProcessor()
    detections = [
        detection("door", [300, 20, 480, 420]),
        detection("person", [80, 50, 220, 390]),
        detection("backpack", [120, 150, 205, 280]),
    ]

    filtered = processor.process(detections)

    assert [item.class_name for item in filtered] == ["door", "person"]


def test_overlap_helpers_measure_iou_and_accessory_intersection() -> None:
    person_bbox = [100, 50, 250, 400]
    backpack_bbox = [130, 140, 230, 300]

    assert bbox_iou(backpack_bbox, person_bbox) > 0
    assert intersection_ratio(backpack_bbox, person_bbox) == 1.0
