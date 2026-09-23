"""Interface de compatibilidade para a politica atual de prioridade."""

from app.schemas.detection import DetectionItem, NavigationHint
from app.guidance.navigation_priority import NavigationPriority

_navigation_priority = NavigationPriority()


def prepare_navigation_detections(detections: list[DetectionItem]) -> list[DetectionItem]:
    return _navigation_priority.prioritize(detections)


def build_navigation_hint(detections: list[DetectionItem]) -> NavigationHint:
    return _navigation_priority.build_hint(detections)
