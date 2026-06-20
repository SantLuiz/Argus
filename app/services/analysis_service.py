from time import perf_counter

from app.audio.speech_payload import build_audio_payload
from app.guidance.message_builder import build_guidance_message
from app.schemas.detection import DetectionResponse, ProcessingTime
from app.vision.depth import PlaceholderDepthEstimator
from app.vision.detection import PlaceholderObjectDetector
from app.vision.preprocessing import load_image_rgb


class AnalysisService:
    """Orquestra o fluxo simples da IC: imagem, deteccao, profundidade e mensagem."""

    def __init__(self) -> None:
        self.detector = PlaceholderObjectDetector()
        self.depth_estimator = PlaceholderDepthEstimator()

    def analyze(self, image_bytes: bytes, image_name: str | None = None) -> DetectionResponse:
        total_start = perf_counter()
        image = load_image_rgb(image_bytes)

        detection_start = perf_counter()
        detections = self.detector.detect(image)
        detection_ms = _elapsed_ms(detection_start)

        depth_start = perf_counter()
        detections_with_depth = self.depth_estimator.attach_depth(image, detections)
        depth_ms = _elapsed_ms(depth_start)

        message = build_guidance_message(detections_with_depth)
        audio = build_audio_payload(message)

        return DetectionResponse(
            detections=detections_with_depth,
            message=message,
            audio=audio,
            processing_time_ms=ProcessingTime(
                detection_ms=detection_ms,
                depth_ms=depth_ms,
                total_ms=_elapsed_ms(total_start),
            ),
            image_name=image_name,
            notes=[
                "Deteccao e profundidade usam implementacao inicial simulada.",
                "A profundidade e relativa e nao representa distancia exata em metros.",
            ],
        )


def _elapsed_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)
