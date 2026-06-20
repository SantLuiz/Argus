from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.navigation.navigation_state import EXPLORATION_MODE, NAVIGATION_MODE, VALID_MODES
from app.schemas.detection import DetectionResponse
from app.services.detection_pipeline import DetectionPipeline
from app.vision.preprocessing import load_image_cv2

router = APIRouter()
detection_pipeline = DetectionPipeline()

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
        raise HTTPException(status_code=400, detail="Modo invalido. Use fast, poi, tactile, auto, exploration ou navigation.")
    if mode == NAVIGATION_MODE and not target_class:
        raise HTTPException(status_code=400, detail="Informe target_class no modo navigation.")

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Formato invalido. Envie uma imagem JPEG, PNG ou WebP.",
        )

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Arquivo de imagem vazio.")

    cv2_image = load_image_cv2(image_bytes)
    return detection_pipeline.analyze(
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
