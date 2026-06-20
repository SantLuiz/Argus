from collections.abc import Callable
import os
from typing import Any

import numpy as np
from PIL import Image

from app.schemas.detection import ObjectDetection


class YoloDetector:
    """Detector de objetos baseado em Ultralytics YOLO.

    Aceita imagens OpenCV em formato numpy array, normalmente BGR, e tambem
    imagens PIL. O retorno e padronizado para o fluxo do ARGUS IC.
    """

    def __init__(
        self,
        model_path: str | None = None,
        confidence_threshold: float = 0.25,
        model_factory: Callable[[str], Any] | None = None,
    ) -> None:
        # Classes de acessibilidade podem exigir um YOLO customizado treinado
        # com dataset proprio/Roboflow. Ex.: ARGUS_YOLO_MODEL_PATH=models/best.pt
        self.model_path = model_path or os.getenv("ARGUS_YOLO_MODEL_PATH", "yolov8n.pt")
        self.confidence_threshold = confidence_threshold
        self._model_factory = model_factory
        self._model: Any | None = None

    def detect(self, image: np.ndarray | Image.Image) -> list[ObjectDetection]:
        model = self._load_model()
        results = model.predict(
            source=self._normalize_image(image),
            conf=self.confidence_threshold,
            verbose=False,
        )

        if not results:
            return []

        return self._parse_result(results[0])

    def _load_model(self) -> Any:
        if self._model is None:
            factory = self._model_factory or _default_model_factory
            self._model = factory(self.model_path)
        return self._model

    def _normalize_image(self, image: np.ndarray | Image.Image) -> np.ndarray:
        if isinstance(image, Image.Image):
            return np.array(image.convert("RGB"))

        if not isinstance(image, np.ndarray):
            raise TypeError("YoloDetector espera uma imagem OpenCV numpy.ndarray ou PIL.Image.")

        if image.ndim not in {2, 3}:
            raise ValueError("Imagem OpenCV deve ter 2 ou 3 dimensoes.")

        return image

    def _parse_result(self, result: Any) -> list[ObjectDetection]:
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
                    source_model="default_yolo",
                    detection_type="object_detection",
                )
            )

        return detections


def _default_model_factory(model_path: str) -> Any:
    from ultralytics import YOLO

    return YOLO(model_path)


def _to_float(value: Any) -> float:
    if hasattr(value, "item"):
        return float(value.item())
    return float(value)


def _to_list(value: Any) -> list[float]:
    if hasattr(value, "tolist"):
        return [float(item) for item in value.tolist()]
    return [float(item) for item in value]
