import numpy as np

from app.schemas.detection import ObjectDetection
from app.services.detection_pipeline import DetectionPipeline


class FakeDetector:
    def detect(self, image):
        assert image.shape == (4, 4, 3)
        return [
            ObjectDetection(class_name="chair", confidence=0.70, bbox=[0, 0, 2, 2]),
            ObjectDetection(class_name="person", confidence=0.90, bbox=[2, 0, 4, 2]),
        ]


class AccessoryDetector:
    def detect(self, image):
        return [
            ObjectDetection(class_name="person", confidence=0.90, bbox=[0, 0, 3, 4]),
            ObjectDetection(class_name="backpack", confidence=0.85, bbox=[1, 1, 3, 3]),
        ]


class FakeDepthEstimator:
    def estimate_depth(self, image):
        return np.array(
            [
                [0.20, 0.20, 0.90, 0.90],
                [0.20, 0.20, 0.90, 0.90],
                [0.40, 0.40, 0.50, 0.50],
                [0.40, 0.40, 0.50, 0.50],
            ],
            dtype=np.float32,
        )


class EmptyDetector:
    def detect(self, image):
        return []


class DepthEstimatorThatShouldNotRun:
    def estimate_depth(self, image):
        raise AssertionError("Profundidade nao deve rodar sem deteccoes.")


class BrokenDepthEstimator:
    def estimate_depth(self, image):
        raise RuntimeError("modelo indisponivel")


class FakeOpenVocabularyDetector:
    last_provider = "fake_open_vocab"
    last_error = None

    def detect(self, image):
        return [ObjectDetection(class_name="door", confidence=0.88, bbox=[1, 1, 3, 3])]


def test_detection_pipeline_integrates_detection_depth_position_and_message() -> None:
    image = np.zeros((4, 4, 3), dtype=np.uint8)
    pipeline = DetectionPipeline(
        detector=FakeDetector(),
        depth_estimator=FakeDepthEstimator(),
    )

    result = pipeline.analyze(image, image_name="teste.jpg")

    assert result.image_name == "teste.jpg"
    assert result.mode == "exploration"
    assert result.use_open_vocab is False
    assert result.raw_detections is not None
    assert [item.class_name for item in result.raw_detections] == ["chair", "person"]
    assert len(result.detections) == 2
    assert result.detections[0].class_name == "pessoa"
    assert result.detections[0].zone == "direita"
    assert result.detections[0].depth.proximity == "very_near"
    assert result.detections[0].semantic_role == "pessoa"
    assert result.detections[1].class_name == "cadeira"
    assert result.detections[1].zone == "esquerda"
    assert result.detections[1].depth.proximity == "far"
    assert result.detections[1].semantic_role == "obstaculo"
    assert result.navigation is not None
    assert result.navigation.target_class_name == "pessoa"
    assert result.message.startswith("Pessoa à direita")
    assert result.audio.text == result.message
    assert result.processing_time_ms.depth_ms >= 0


def test_detection_pipeline_navigation_mode_guides_to_target() -> None:
    image = np.zeros((4, 4, 3), dtype=np.uint8)
    pipeline = DetectionPipeline(
        detector=FakeOpenVocabularyDetector(),
        depth_estimator=FakeDepthEstimator(),
    )

    result = pipeline.analyze(image, mode="navigation", target_class="door")

    assert result.mode == "navigation"
    assert result.navigation is not None
    assert result.navigation.target_found is True
    assert result.navigation.action == "forward"
    assert result.message == "Porta a frente, siga em frente."


def test_detection_pipeline_can_add_open_vocabulary_detections() -> None:
    image = np.zeros((4, 4, 3), dtype=np.uint8)
    pipeline = DetectionPipeline(
        detector=EmptyDetector(),
        depth_estimator=FakeDepthEstimator(),
        open_vocab_detector=FakeOpenVocabularyDetector(),
    )

    result = pipeline.analyze(image, use_open_vocab=True)

    assert result.use_open_vocab is True
    assert result.raw_detections is not None
    assert [item.class_name for item in result.raw_detections] == ["door"]
    assert result.detections[0].class_name == "porta"
    assert any("Open-vocabulary experimental ativado" in note for note in result.notes)


def test_detection_pipeline_preserves_raw_detections_but_uses_filtered_output() -> None:
    image = np.zeros((4, 4, 3), dtype=np.uint8)
    pipeline = DetectionPipeline(
        detector=AccessoryDetector(),
        depth_estimator=FakeDepthEstimator(),
    )

    result = pipeline.analyze(image)

    assert result.raw_detections is not None
    assert [item.class_name for item in result.raw_detections] == ["person", "backpack"]
    assert [item.class_name for item in result.detections] == ["pessoa"]


def test_detection_pipeline_skips_depth_when_no_objects_are_detected() -> None:
    image = np.zeros((4, 4, 3), dtype=np.uint8)
    pipeline = DetectionPipeline(
        detector=EmptyDetector(),
        depth_estimator=DepthEstimatorThatShouldNotRun(),
    )

    result = pipeline.analyze(image)

    assert result.detections == []
    assert result.processing_time_ms.depth_ms == 0
    assert result.navigation is not None
    assert result.message == "Nenhum ponto de interesse ou obstaculo relevante detectado."


def test_detection_pipeline_uses_fallback_depth_when_midas_fails() -> None:
    image = np.zeros((4, 4, 3), dtype=np.uint8)
    pipeline = DetectionPipeline(
        detector=FakeDetector(),
        depth_estimator=BrokenDepthEstimator(),
    )

    result = pipeline.analyze(image)

    assert result.detections
    assert any("fallback relativo" in note for note in result.notes)
