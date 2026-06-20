import os

import numpy as np

from app.schemas.detection import ObjectDetection
from app.vision.yolo_detector import YoloDetector


class TactilePavingDetector:
    """Especialista configuravel para piso tatil.

    Espera um peso futuro treinado com dataset proprio/Roboflow. Se o caminho
    nao existir, retorna lista vazia para manter o MVP funcionando.
    """

    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path or os.getenv("ARGUS_TACTILE_MODEL_PATH", "models/tactile_best.pt")
        self._detector: YoloDetector | None = None

    def detect(self, image: np.ndarray) -> list[ObjectDetection]:
        if not os.path.exists(self.model_path):
            return []
        if self._detector is None:
            self._detector = YoloDetector(model_path=self.model_path, confidence_threshold=0.20)
        detections = self._detector.detect(image)
        return [
            detection.model_copy(
                update={
                    "class_name": "tactile paving",
                    "source_model": "tactile_specialist",
                    "detection_type": "tactile_specialist",
                }
            )
            for detection in detections
        ]

