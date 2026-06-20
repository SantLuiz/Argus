import cv2
import numpy as np

from app.schemas.detection import ObjectDetection


class ClassicTactileDetector:
    """Fallback experimental em OpenCV para possivel piso tatil amarelo/alto contraste."""

    def detect(self, image: np.ndarray) -> list[ObjectDetection]:
        if image.size == 0:
            return []

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        yellow_mask = cv2.inRange(hsv, (18, 60, 80), (42, 255, 255))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        height, width = image.shape[:2]
        min_area = max((height * width) * 0.006, 80)
        detections: list[ObjectDetection] = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / max(h, 1)
            confidence = 0.35 if 0.25 <= aspect_ratio <= 6.0 else 0.25
            detections.append(
                ObjectDetection(
                    class_name="tactile paving",
                    confidence=confidence,
                    bbox=[x, y, x + w, y + h],
                    source_model="classic_tactile",
                    detection_type="heuristic",
                )
            )

        return detections

