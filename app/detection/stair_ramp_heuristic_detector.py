import cv2
import numpy as np

from app.schemas.detection import ObjectDetection


class StairRampHeuristicDetector:
    """Heuristicas simples e conservadoras para escadas/rampas usando bordas."""

    def detect(self, image: np.ndarray) -> list[ObjectDetection]:
        if image.size == 0:
            return []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 160)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=60, maxLineGap=12)
        if lines is None:
            return []

        horizontal_lines = []
        diagonal_lines = []
        for line in lines[:, 0]:
            x1, y1, x2, y2 = [int(value) for value in line]
            dx = x2 - x1
            dy = y2 - y1
            if abs(dy) <= max(abs(dx) * 0.18, 4):
                horizontal_lines.append((x1, y1, x2, y2))
            elif 0.25 <= abs(dy / max(dx, 1)) <= 1.2:
                diagonal_lines.append((x1, y1, x2, y2))

        height, width = image.shape[:2]
        if len(horizontal_lines) >= 5:
            return [
                ObjectDetection(
                    class_name="stairs",
                    confidence=0.32,
                    bbox=[0, height // 3, width, height],
                    source_model="stair_ramp_heuristic",
                    detection_type="heuristic",
                )
            ]
        if len(diagonal_lines) >= 4:
            return [
                ObjectDetection(
                    class_name="ramp",
                    confidence=0.28,
                    bbox=[0, height // 2, width, height],
                    source_model="stair_ramp_heuristic",
                    detection_type="heuristic",
                )
            ]
        return []

