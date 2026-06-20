import numpy as np

from app.config import OPEN_VOCAB_PROMPTS
from app.routing.detection_plan import GeneralistFinding
from app.schemas.detection import ObjectDetection
from app.vision.open_vocabulary_detector import OpenVocabularyDetector


class GeneralistSceneAnalyzer:
    """Busca indicios de POIs para orientar o plano de detectores.

    O analisador nao gera a mensagem final. Ele apenas retorna evidencias leves
    para o `SceneRouter` decidir se vale chamar open-vocabulary, segmentacao ou
    especialistas. Qualquer modelo indisponivel deve virar nota, nao erro.
    """

    def __init__(
        self,
        open_vocab_detector: OpenVocabularyDetector | None = None,
        semantic_detector: object | None = None,
    ) -> None:
        self.open_vocab_detector = open_vocab_detector or OpenVocabularyDetector(classes=OPEN_VOCAB_PROMPTS)
        self.semantic_detector = semantic_detector
        self.last_notes: list[str] = []
        self.last_open_vocab_detections: list[ObjectDetection] = []

    def analyze(
        self,
        image: np.ndarray,
        use_open_vocab: bool = False,
        use_semantic_segmentation: bool = False,
    ) -> list[GeneralistFinding]:
        findings: list[GeneralistFinding] = []
        self.last_notes = []
        self.last_open_vocab_detections = []

        if use_open_vocab:
            try:
                detections = self.open_vocab_detector.detect(image)
                self.last_open_vocab_detections = detections
                findings.extend(_findings_from_detections(detections))
                provider = getattr(self.open_vocab_detector, "last_provider", None)
                if provider:
                    self.last_notes.append(f"GeneralistSceneAnalyzer usou {provider}.")
            except Exception as exc:
                self.last_notes.append(f"Open-vocabulary indisponivel no analisador: {exc.__class__.__name__}.")

        if use_semantic_segmentation and self.semantic_detector is not None:
            try:
                semantic_detections = self.semantic_detector.detect(image)
                findings.extend(_findings_from_detections(semantic_detections))
            except Exception as exc:
                self.last_notes.append(f"Segmentacao semantica indisponivel: {exc.__class__.__name__}.")

        return findings


def _findings_from_detections(detections: list[ObjectDetection]) -> list[GeneralistFinding]:
    return [
        GeneralistFinding(
            class_name=detection.class_name,
            confidence=detection.confidence,
            source_model=detection.source_model,
            bbox=detection.bbox,
            reason="indicio generalista",
        )
        for detection in detections
    ]
