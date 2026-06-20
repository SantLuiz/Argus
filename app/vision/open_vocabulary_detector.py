from collections.abc import Callable
import os
from typing import Any

import numpy as np

from app.schemas.detection import ObjectDetection
from app.vision.yolo_detector import _to_float, _to_list


OPEN_VOCAB_CLASSES = [
    "door",
    "elevator",
    "stairs",
    "stair",
    "handrail",
    "tactile paving",
    "ramp",
    "wheelchair ramp",
    "accessible entrance",
    "reception",
    "corridor",
    "passage",
    "person",
    "chair",
    "table",
    "obstacle",
]


class OpenVocabularyDetector:
    """Detector experimental de pontos de interesse por vocabulário aberto.

    Prioriza YOLOE quando disponível e tenta YOLO-World como fallback. Este
    detector complementa o YOLO atual e nao deve virar padrao antes de benchmark
    de latencia e qualidade no conjunto de imagens do ARGUS IC.
    """

    def __init__(
        self,
        classes: list[str] | None = None,
        confidence_threshold: float = 0.20,
        model_factory: Callable[[str], Any] | None = None,
        primary_model_path: str | None = None,
        fallback_model_path: str | None = None,
    ) -> None:
        self.classes = classes or OPEN_VOCAB_CLASSES
        self.confidence_threshold = confidence_threshold
        self.primary_model_path = primary_model_path or os.getenv("ARGUS_YOLOE_MODEL_PATH", "yoloe-11s-seg.pt")
        self.fallback_model_path = fallback_model_path or os.getenv("ARGUS_YOLO_WORLD_MODEL_PATH", "yolov8s-world.pt")
        self._model_factory = model_factory
        self._models: dict[str, Any] = {}
        self.last_provider: str | None = None
        self.last_error: str | None = None

    def detect(self, image: np.ndarray) -> list[ObjectDetection]:
        for provider, model_path in (("yoloe", self.primary_model_path), ("yolo_world", self.fallback_model_path)):
            try:
                detections = self._detect_with_model(image, model_path, provider)
                self.last_provider = provider
                self.last_error = None
                return detections
            except Exception as exc:
                self.last_error = f"{provider}: {exc.__class__.__name__}: {exc}"

        return []

    def _detect_with_model(self, image: np.ndarray, model_path: str, provider: str) -> list[ObjectDetection]:
        model = self._load_model(model_path)
        if hasattr(model, "set_classes"):
            model.set_classes(self.classes)

        results = model.predict(source=image, conf=self.confidence_threshold, verbose=False)
        if not results:
            return []
        return self._parse_result(results[0], provider)

    def _load_model(self, model_path: str) -> Any:
        if model_path not in self._models:
            factory = self._model_factory or _default_model_factory
            self._models[model_path] = factory(model_path)
        return self._models[model_path]

    def _parse_result(self, result: Any, provider: str) -> list[ObjectDetection]:
        names = getattr(result, "names", {}) or {}
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return []

        detections: list[ObjectDetection] = []
        for box in boxes:
            confidence = _to_float(box.conf[0])
            if confidence < self.confidence_threshold:
                continue
            class_id = int(_to_float(box.cls[0]))
            detections.append(
                ObjectDetection(
                    class_name=str(names.get(class_id, class_id)),
                    confidence=round(confidence, 4),
                    bbox=[int(round(value)) for value in _to_list(box.xyxy[0])],
                    source_model=provider,
                    detection_type="object_detection",
                )
            )
        return detections


def _default_model_factory(model_path: str) -> Any:
    from ultralytics import YOLO

    return YOLO(model_path)
