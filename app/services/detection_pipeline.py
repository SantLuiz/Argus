from time import perf_counter
from typing import Protocol

import numpy as np

from app.audio.speech_payload import build_audio_payload
from app.detection.classic_tactile_detector import ClassicTactileDetector
from app.detection.detection_merger import DetectionMerger
from app.detection.ocr_sign_detector import OCRSignDetector
from app.detection.post_processor import DetectionPostProcessor
from app.detection.semantic_segmentation_detector import SemanticSegmentationDetector
from app.detection.stair_ramp_heuristic_detector import StairRampHeuristicDetector
from app.detection.tactile_paving_detector import TactilePavingDetector
from app.guidance.message_generator import MessageGenerator
from app.guidance.navigation_policy import build_navigation_hint, prepare_navigation_detections
from app.navigation.local_navigator import LocalNavigator
from app.navigation.navigation_state import AUTO_MODE, EXPLORATION_MODE, NAVIGATION_MODE
from app.routing.generalist_scene_analyzer import GeneralistSceneAnalyzer
from app.routing.scene_router import SceneRouter
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
        scene_router: SceneRouter | None = None,
        generalist_analyzer: GeneralistSceneAnalyzer | None = None,
        detection_merger: DetectionMerger | None = None,
        tactile_detector: ObjectDetector | None = None,
        classic_tactile_detector: ObjectDetector | None = None,
        ocr_detector: ObjectDetector | None = None,
        stair_ramp_detector: ObjectDetector | None = None,
        semantic_detector: ObjectDetector | None = None,
    ) -> None:
        self.detector = detector or YoloDetector()
        self.depth_estimator = depth_estimator or MidasEstimator()
        self.post_processor = post_processor or DetectionPostProcessor()
        self.message_generator = message_generator or MessageGenerator()
        self.open_vocab_detector = open_vocab_detector or OpenVocabularyDetector()
        self.local_navigator = local_navigator or LocalNavigator()
        self.scene_router = scene_router or SceneRouter()
        self.semantic_detector = semantic_detector or SemanticSegmentationDetector()
        self.generalist_analyzer = generalist_analyzer or GeneralistSceneAnalyzer(
            open_vocab_detector=self.open_vocab_detector,
            semantic_detector=self.semantic_detector,
        )
        self.detection_merger = detection_merger or DetectionMerger()
        self.tactile_detector = tactile_detector or TactilePavingDetector()
        self.classic_tactile_detector = classic_tactile_detector or ClassicTactileDetector()
        self.ocr_detector = ocr_detector or OCRSignDetector()
        self.stair_ramp_detector = stair_ramp_detector or StairRampHeuristicDetector()

    def analyze(
        self,
        image: np.ndarray,
        image_name: str | None = None,
        mode: str = EXPLORATION_MODE,
        target_class: str | None = None,
        use_open_vocab: bool = False,
        use_semantic_segmentation: bool = False,
        use_tactile_specialist: bool = False,
        use_classic_tactile: bool = False,
        use_ocr: bool = False,
    ) -> DetectionResponse:
        if not isinstance(image, np.ndarray):
            raise TypeError("DetectionPipeline espera uma imagem OpenCV numpy.ndarray.")

        total_start = perf_counter()
        notes = [
            "Pipeline experimental com YOLO e profundidade monocular MiDaS.",
            "A profundidade e relativa e nao representa distancia exata em metros.",
        ]

        detection_start = perf_counter()
        initial_plan = self.scene_router.build_plan(
            mode=mode,
            target_class=target_class,
            use_open_vocab=use_open_vocab,
            use_semantic_segmentation=use_semantic_segmentation,
            use_tactile_specialist=use_tactile_specialist,
            use_classic_tactile=use_classic_tactile,
            use_ocr=use_ocr,
        )
        generalist_findings = self.generalist_analyzer.analyze(
            image,
            use_open_vocab=initial_plan.use_open_vocab,
            use_semantic_segmentation=initial_plan.use_semantic_segmentation,
        )
        notes.extend(self.generalist_analyzer.last_notes)
        detection_plan = self.scene_router.build_plan(
            mode=mode,
            target_class=target_class,
            findings=generalist_findings,
            use_open_vocab=initial_plan.use_open_vocab,
            use_semantic_segmentation=initial_plan.use_semantic_segmentation,
            use_tactile_specialist=initial_plan.use_tactile_specialist,
            use_classic_tactile=initial_plan.use_classic_tactile,
            use_ocr=initial_plan.use_ocr,
        )

        detection_groups: list[list[ObjectDetection]] = []
        models_called: list[str] = []
        if detection_plan.use_default_yolo:
            raw_yolo_detections = self.detector.detect(image)
            detection_groups.append(raw_yolo_detections)
            models_called.append("default_yolo")
        if detection_plan.use_open_vocab:
            open_vocab_detections = self.generalist_analyzer.last_open_vocab_detections
            if not open_vocab_detections and not initial_plan.use_open_vocab:
                open_vocab_detections = self.open_vocab_detector.detect(image)
            detection_groups.append(open_vocab_detections)
            notes.append(f"Open-vocabulary experimental ativado; adicionou {len(open_vocab_detections)} deteccoes.")
            provider = getattr(self.open_vocab_detector, "last_provider", None)
            models_called.append(provider or "open_vocab")
            last_error = getattr(self.open_vocab_detector, "last_error", None)
            if not open_vocab_detections and last_error:
                notes.append(f"Detector open-vocabulary indisponivel: {last_error}.")
        if detection_plan.use_semantic_segmentation:
            detection_groups.append(_safe_detect(self.semantic_detector, image, notes, "semantic_segmentation"))
            models_called.append("semantic_segmentation")
        if detection_plan.use_tactile_specialist:
            detection_groups.append(_safe_detect(self.tactile_detector, image, notes, "tactile_specialist"))
            models_called.append("tactile_specialist")
        if detection_plan.use_classic_tactile:
            detection_groups.append(_safe_detect(self.classic_tactile_detector, image, notes, "classic_tactile"))
            models_called.append("classic_tactile")
        if detection_plan.use_ocr:
            detection_groups.append(_safe_detect(self.ocr_detector, image, notes, "ocr"))
            models_called.append("ocr")
        if detection_plan.use_stair_ramp_heuristics:
            detection_groups.append(_safe_detect(self.stair_ramp_detector, image, notes, "stair_ramp_heuristic"))
            models_called.append("stair_ramp_heuristic")

        raw_detections = self.detection_merger.merge(detection_groups)
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

        if mode == NAVIGATION_MODE or detection_plan.use_local_navigation:
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
            use_open_vocab=detection_plan.use_open_vocab,
            detection_plan=detection_plan.model_dump(),
            generalist_findings=[finding.model_dump() for finding in generalist_findings],
            models_called=models_called,
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


def _safe_detect(detector: ObjectDetector, image: np.ndarray, notes: list[str], label: str) -> list[ObjectDetection]:
    try:
        return detector.detect(image)
    except Exception as exc:
        notes.append(f"{label} indisponivel: {exc.__class__.__name__}.")
        return []


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
