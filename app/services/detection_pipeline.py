from time import perf_counter
from typing import Protocol

import numpy as np

from app.audio.speech_payload import build_audio_payload
from app.detection.post_processor import DetectionPostProcessor
from app.guidance.message_generator import MessageGenerator
from app.guidance.navigation_policy import build_navigation_hint, prepare_navigation_detections
from app.schemas.detection import DetectionResponse, ObjectDetection, ProcessingTime
from app.vision.depth import combine_detections_with_depth
from app.vision.midas_estimator import MidasEstimator
from app.vision.yolo_detector import YoloDetector


class ObjectDetector(Protocol):
    def detect(self, image: np.ndarray) -> list[ObjectDetection]:
        ...


class DepthEstimator(Protocol):
    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        ...


class DetectionPipeline:
    """Pipeline completo do ARGUS IC para imagem OpenCV.

    Fluxo:
    imagem -> YOLO -> MiDaS -> bbox + profundidade + posicao -> mensagem PT-BR.
    """

    def __init__(
        self,
        detector: ObjectDetector | None = None,
        depth_estimator: DepthEstimator | None = None,
        post_processor: DetectionPostProcessor | None = None,
        message_generator: MessageGenerator | None = None,
    ) -> None:
        self.detector = detector or YoloDetector()
        self.depth_estimator = depth_estimator or MidasEstimator()
        self.post_processor = post_processor or DetectionPostProcessor()
        self.message_generator = message_generator or MessageGenerator()

    def analyze(self, image: np.ndarray, image_name: str | None = None) -> DetectionResponse:
        if not isinstance(image, np.ndarray):
            raise TypeError("DetectionPipeline espera uma imagem OpenCV numpy.ndarray.")

        total_start = perf_counter()

        detection_start = perf_counter()
        raw_detections = self.detector.detect(image)
        filtered_detections = self.post_processor.process(raw_detections)
        detection_ms = _elapsed_ms(detection_start)

        depth_start = perf_counter()
        notes = [
            "Pipeline experimental com YOLO e profundidade monocular MiDaS.",
            "A profundidade e relativa e nao representa distancia exata em metros.",
        ]
        if filtered_detections:
            try:
                depth_map = self.depth_estimator.estimate_depth(image)
            except Exception as exc:
                depth_map = _fallback_depth_map(image)
                notes.append(
                    "MiDaS nao ficou disponivel nesta execucao; foi usado fallback relativo "
                    f"para evitar falha do endpoint. Motivo: {exc.__class__.__name__}."
                )
            detections = prepare_navigation_detections(combine_detections_with_depth(filtered_detections, depth_map))
            depth_ms = _elapsed_ms(depth_start)
        else:
            detections = []
            depth_ms = 0

        navigation = build_navigation_hint(detections)
        message = self.message_generator.generate(detections, navigation)
        audio = build_audio_payload(message)

        return DetectionResponse(
            detections=detections,
            raw_detections=raw_detections,
            message=message,
            audio=audio,
            processing_time_ms=ProcessingTime(
                detection_ms=detection_ms,
                depth_ms=depth_ms,
                total_ms=_elapsed_ms(total_start),
            ),
            navigation=navigation,
            image_name=image_name,
            notes=notes,
        )


def _elapsed_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


def _fallback_depth_map(image: np.ndarray) -> np.ndarray:
    """Mapa relativo simples usado apenas quando o modelo MiDaS nao carrega.

    Valores mais altos na parte inferior da imagem sao tratados como mais
    proximos. Isso evita erro 500 em ambiente sem cache/rede, mas deve ser
    substituido por MiDaS assim que os pesos estiverem disponiveis.
    """

    height, width = image.shape[:2]
    if height <= 0 or width <= 0:
        raise ValueError("Imagem invalida para gerar mapa de profundidade.")

    vertical_gradient = np.linspace(0.0, 1.0, height, dtype=np.float32)
    return np.repeat(vertical_gradient[:, None], width, axis=1)
