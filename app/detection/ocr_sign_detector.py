import numpy as np

from app.schemas.detection import ObjectDetection


class OCRSignDetector:
    """OCR opcional para placas de elevador, recepcao, entrada/saida e acessibilidade."""

    KEYWORDS = {
        "elevador": "elevator",
        "elevator": "elevator",
        "recepcao": "reception",
        "recepção": "reception",
        "reception": "reception",
        "atendimento": "reception",
        "saida": "exit",
        "saída": "exit",
        "exit": "exit",
        "entrada": "entrance",
        "acessivel": "accessibility sign",
        "acessível": "accessibility sign",
    }

    def __init__(self) -> None:
        self.last_error: str | None = None

    def detect(self, image: np.ndarray) -> list[ObjectDetection]:
        try:
            import easyocr  # type: ignore
        except Exception as exc:
            self.last_error = f"easyocr indisponivel: {exc.__class__.__name__}"
            return []

        try:
            reader = easyocr.Reader(["pt", "en"], gpu=False)
            results = reader.readtext(image)
        except Exception as exc:
            self.last_error = f"OCR falhou: {exc.__class__.__name__}"
            return []

        detections: list[ObjectDetection] = []
        for bbox_points, text, confidence in results:
            class_name = self._class_from_text(text)
            if class_name is None:
                continue
            xs = [int(point[0]) for point in bbox_points]
            ys = [int(point[1]) for point in bbox_points]
            detections.append(
                ObjectDetection(
                    class_name=class_name,
                    confidence=max(min(float(confidence), 0.80), 0.20),
                    bbox=[min(xs), min(ys), max(xs), max(ys)],
                    source_model="ocr",
                    detection_type="ocr",
                )
            )
        return detections

    def _class_from_text(self, text: str) -> str | None:
        normalized = text.strip().lower()
        for keyword, class_name in self.KEYWORDS.items():
            if keyword in normalized:
                return class_name
        return None

