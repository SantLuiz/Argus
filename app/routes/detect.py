from threading import Lock

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from starlette.concurrency import run_in_threadpool

from app.config import (
    ARGUS_DETECT_RETRY_AFTER_SECONDS,
    ARGUS_MAX_DECODED_PIXELS,
    ARGUS_MAX_UPLOAD_BYTES,
    ARGUS_MVP_PROFILE,
    ARGUS_MVP_TARGET_CLASSES,
)
from app.errors import ArgusRuntimeError, BackendBusyError
from app.navigation.navigation_state import EXPLORATION_MODE, NAVIGATION_MODE, VALID_MODES
from app.schemas.detection import DetectionResponse, ReadyResponse
from app.services.detection_pipeline import DetectionPipeline
from app.vision.preprocessing import load_image_cv2

router = APIRouter()
detection_pipeline = DetectionPipeline()
inference_lock = Lock()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/detect", response_model=DetectionResponse)
async def detect_image(
    image: UploadFile = File(...),
    mode: str = Query(EXPLORATION_MODE),
    target_class: str | None = Query(None),
    use_open_vocab: bool = Query(False),
    use_semantic_segmentation: bool = Query(False),
    use_tactile_specialist: bool = Query(False),
    use_classic_tactile: bool = Query(False),
    use_ocr: bool = Query(False),
) -> DetectionResponse:
    if mode not in VALID_MODES:
        raise _structured_error(400, "INVALID_MODE", "Modo invalido. Use fast, poi, tactile, auto, exploration ou navigation.")
    if mode == NAVIGATION_MODE and not target_class:
        raise _structured_error(400, "TARGET_REQUIRED", "Informe target_class no modo navigation.")
    if ARGUS_MVP_PROFILE and mode == NAVIGATION_MODE and target_class.strip().lower() not in ARGUS_MVP_TARGET_CLASSES:
        raise _structured_error(400, "UNSUPPORTED_TARGET", "No perfil MVP, o modo navigation aceita apenas target_class=door.")

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise _structured_error(400, "INVALID_IMAGE_TYPE", "Formato invalido. Envie uma imagem JPEG, PNG ou WebP.")

    acquired = inference_lock.acquire(blocking=False)
    if not acquired:
        raise _http_error(
            BackendBusyError("Backend ocupado processando outra imagem. Tente novamente em instantes."),
            headers={"Retry-After": str(ARGUS_DETECT_RETRY_AFTER_SECONDS)},
        )

    try:
        image_bytes = await image.read(ARGUS_MAX_UPLOAD_BYTES + 1)
        if not image_bytes:
            raise _structured_error(400, "EMPTY_IMAGE", "Arquivo de imagem vazio.")
        if len(image_bytes) > ARGUS_MAX_UPLOAD_BYTES:
            raise _structured_error(413, "IMAGE_TOO_LARGE", "Imagem excede o limite de 5 MiB.")

        cv2_image = load_image_cv2(image_bytes)
        _validate_decoded_image_size(cv2_image)
        try:
            return await run_in_threadpool(
                detection_pipeline.analyze,
                cv2_image,
                image_name=image.filename,
                mode=mode,
                target_class=target_class,
                use_open_vocab=use_open_vocab,
                use_semantic_segmentation=use_semantic_segmentation,
                use_tactile_specialist=use_tactile_specialist,
                use_classic_tactile=use_classic_tactile,
                use_ocr=use_ocr,
            )
        except ArgusRuntimeError as exc:
            raise _http_error(exc) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        inference_lock.release()
        await image.close()


@router.get("/ready", response_model=ReadyResponse)
def ready_check() -> ReadyResponse:
    return detection_pipeline.readiness(busy=inference_lock.locked())


def _validate_decoded_image_size(cv2_image) -> None:
    height, width = cv2_image.shape[:2]
    if height * width > ARGUS_MAX_DECODED_PIXELS:
        raise _structured_error(413, "IMAGE_TOO_LARGE", "Imagem decodificada excede o limite de 12 MP.")


def _http_error(exc: ArgusRuntimeError, headers: dict[str, str] | None = None) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail={"code": exc.code, "message": exc.message},
        headers=headers,
    )


def _structured_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})
