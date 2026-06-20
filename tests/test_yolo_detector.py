import numpy as np

from app.vision.yolo_detector import YoloDetector


class FakeValue:
    def __init__(self, value):
        self.value = value

    def item(self):
        return self.value


class FakeBox:
    def __init__(self, cls, conf, xyxy):
        self.cls = [FakeValue(cls)]
        self.conf = [FakeValue(conf)]
        self.xyxy = [np.array(xyxy, dtype=float)]


class FakeResult:
    names = {0: "person", 56: "chair"}

    def __init__(self):
        self.boxes = [
            FakeBox(0, 0.91, [10.2, 20.7, 100.4, 220.9]),
            FakeBox(56, 0.20, [1, 2, 3, 4]),
        ]


class FakeModel:
    def __init__(self):
        self.received_source = None
        self.received_conf = None

    def predict(self, source, conf, verbose):
        self.received_source = source
        self.received_conf = conf
        return [FakeResult()]


def test_yolo_detector_accepts_opencv_image_and_standardizes_output() -> None:
    fake_model = FakeModel()
    detector = YoloDetector(
        model_path="fake.pt",
        confidence_threshold=0.25,
        model_factory=lambda _: fake_model,
    )
    opencv_image = np.zeros((240, 320, 3), dtype=np.uint8)

    detections = detector.detect(opencv_image)

    assert fake_model.received_source is opencv_image
    assert fake_model.received_conf == 0.25
    assert len(detections) == 1
    assert detections[0].class_name == "person"
    assert detections[0].confidence == 0.91
    assert detections[0].bbox == [10, 21, 100, 221]


def test_yolo_detector_uses_custom_model_path_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("ARGUS_YOLO_MODEL_PATH", "models/best.pt")

    detector = YoloDetector()

    assert detector.model_path == "models/best.pt"
