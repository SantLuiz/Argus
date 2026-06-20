from app.detection.detection_merger import DetectionMerger
from app.routing.detection_plan import GeneralistFinding
from app.routing.scene_router import SceneRouter
from app.schemas.detection import ObjectDetection


def test_scene_router_activates_specialists_from_findings() -> None:
    router = SceneRouter()

    plan = router.build_plan(
        mode="auto",
        findings=[
            GeneralistFinding(class_name="tactile paving", confidence=0.60, source_model="yoloe"),
            GeneralistFinding(class_name="elevator", confidence=0.70, source_model="yoloe"),
        ],
    )

    assert plan.use_tactile_specialist is True
    assert plan.use_classic_tactile is True
    assert plan.use_ocr is True
    assert "tactile paving" in plan.poi_candidates
    assert "elevator" in plan.target_classes


def test_scene_router_fast_keeps_heavy_models_off_by_default() -> None:
    router = SceneRouter()

    plan = router.build_plan(mode="fast")

    assert plan.use_default_yolo is True
    assert plan.use_open_vocab is False
    assert plan.use_semantic_segmentation is False


def test_detection_merger_marks_overlapping_sources_as_corroborated() -> None:
    merger = DetectionMerger()
    default_detection = ObjectDetection(
        class_name="door",
        confidence=0.70,
        bbox=[10, 10, 100, 200],
        source_model="default_yolo",
    )
    open_vocab_detection = ObjectDetection(
        class_name="elevator door",
        confidence=0.76,
        bbox=[12, 12, 102, 202],
        source_model="yoloe",
    )

    merged = merger.merge([[default_detection], [open_vocab_detection]])

    assert len(merged) == 1
    assert merged[0].corroborated is True
    assert merged[0].confidence > 0.76
    assert merged[0].source_model == "default_yolo+yoloe"

