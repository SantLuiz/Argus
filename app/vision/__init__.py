"""Modulos de visao computacional do ARGUS IC."""

from app.vision.yolo_detector import YoloDetector
from app.vision.midas_estimator import MidasEstimator

__all__ = ["MidasEstimator", "YoloDetector"]
