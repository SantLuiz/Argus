import numpy as np

from app.schemas.detection import ObjectDetection
from app.vision.depth import combine_detections_with_depth


def test_combine_detections_with_depth_uses_bbox_median_and_labels_proximity() -> None:
    depth_map = np.array(
        [
            [0.10, 0.20, 0.65, 0.75],
            [0.10, 0.30, 0.70, 0.80],
            [0.40, 0.45, 0.50, 0.55],
            [0.86, 0.90, 0.20, 0.10],
        ],
        dtype=np.float32,
    )
    detections = [
        ObjectDetection(class_name="person", confidence=0.91, bbox=[2, 0, 4, 2]),
        ObjectDetection(class_name="chair", confidence=0.70, bbox=[0, 0, 2, 2]),
        ObjectDetection(class_name="obstaculo", confidence=0.82, bbox=[0, 3, 2, 4]),
    ]

    combined = combine_detections_with_depth(detections, depth_map)

    assert combined[0].depth.proximity == "near"
    assert combined[0].depth.label_pt == "proximo"
    assert combined[0].zone == "direita"
    assert combined[1].depth.proximity == "far"
    assert combined[1].depth.label_pt == "distante"
    assert combined[2].depth.proximity == "very_near"
    assert combined[2].depth.label_pt == "muito proximo"


def test_combine_detections_with_depth_clips_bbox_to_depth_map() -> None:
    depth_map = np.full((10, 10), 0.5, dtype=np.float32)
    detections = [
        ObjectDetection(class_name="table", confidence=0.80, bbox=[-5, -4, 30, 20]),
    ]

    combined = combine_detections_with_depth(detections, depth_map)

    assert combined[0].bbox == [0, 0, 10, 10]
    assert combined[0].depth.proximity == "medium"
