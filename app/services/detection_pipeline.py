from time import perf_counter
from typing import Protocol

import numpy as np

from app.audio.speech_payload import build_audio_payload
from app.detection.post_processor import DetectionPostProcessor
from app.guidance.message_generator import MessageGenerator
from app.guidance.navigation_policy import build_navigation_hint, prepare_navigation_detections
from app.navigation.local_navigator import LocalNavigator
from app.navigation.navigation_state import EXPLORATION_MODE, NAVIGATION_MODE
from app.schemas.detection import DetectionResponse, ObjectDetection, ProcessingTime
from app.vision.depth import combine_detections_with_depth
from app.vision.midas_estimator import MidasEstimator
from app.vision.open_vocabulary_detector import OpenVocabularyDetector
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
        open_vocab_detector: ObjectDetector | None = None,
        local_navigator: LocalNavigator | None = None,
    ) -> None:
        self.detector = detector or YoloDetector()
        self.depth_estimator = depth_estimator or MidasEstimator()
        self.post_processor = post_processor or DetectionPostProcessor()
        self.message_generator = message_generator or MessageGenerator()
        self.open_vocab_detector = open_vocab_detector or OpenVocabularyDetector()
        self.local_navigator = local_navigator or LocalNavigator()

    def analyze(
        self,
        image: np.ndarray,
        image_name: str | None = None,
        mode: str = EXPLORATION_MODE,
        target_class: str | None = None,
        use_open_vocab: bool = False,
    ) -> DetectionResponse:
        if not isinstance(image, np.ndarray):
            raise TypeError("DetectionPipeline espera uma imagem OpenCV numpy.ndarray.")

        total_start = perf_counter()
        notes = [
            "Pipeline experimental com YOLO e profundidade monocular MiDaS.",
            "A profundidade e relativa e nao representa distancia exata em metros.",
        ]

        detection_start = perf_counter()
        raw_yolo_detections = self.detector.detect(image)
        raw_detections = raw_yolo_detections
        if use_open_vocab:
            open_vocab_detections = self.open_vocab_detector.detect(image)
            raw_detections = _merge_detections(raw_yolo_detections, open_vocab_detections)
            notes.append(f"Open-vocabulary experimental ativado; adicionou {len(open_vocab_detections)} deteccoes.")
            last_provider = getattr(self.open_vocab_detector, "last_provider", None)
            last_error = getattr(self.open_vocab_detector, "last_error", None)
            if last_provider:
                notes.append(f"Detector open-vocabulary usado: {last_provider}.")
            elif last_error:
                notes.append(f"Detector open-vocabulary indisponivel: {last_error}.")
        filtered_detections = self.post_processor.process(raw_detections)
        detection_ms = _elapsed_ms(detection_start)

        depth_start = perf_counter()
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

        if mode == NAVIGATION_MODE:
            navigation = self.local_navigator.navigate(detections, target_class)
        else:
            navigation = build_navigation_hint(detections)
        message = self.message_generator.generate(detections, navigation, mode=mode)
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
            mode=mode,
            use_open_vocab=use_open_vocab,
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


def _merge_detections(base: list[ObjectDetection], extra: list[ObjectDetection]) -> list[ObjectDetection]:
    merged = list(base)
    for detection in extra:
        duplicate_index = _find_duplicate(merged, detection)
        if duplicate_index is None:
            merged.append(detection)
        elif detection.confidence > merged[duplicate_index].confidence:
            merged[duplicate_index] = detection
    return merged


def _find_duplicate(detections: list[ObjectDetection], candidate: ObjectDetection) -> int | None:
    for index, detection in enumerate(detections):
        if detection.class_name == candidate.class_name and _iou(detection.bbox, candidate.bbox) >= 0.75:
            return index
    return None


def _iou(first: list[int], second: list[int]) -> float:
    ax1, ay1, ax2, ay2 = first
    bx1, by1, bx2, by2 = second
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = max(inter_x2 - inter_x1, 0) * max(inter_y2 - inter_y1, 0)
    if inter_area == 0:
        return 0.0
    first_area = max(ax2 - ax1, 0) * max(ay2 - ay1, 0)
    second_area = max(bx2 - bx1, 0) * max(by2 - by1, 0)
    return inter_area / max(first_area + second_area - inter_area, 1)
