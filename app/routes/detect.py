from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.detection import DetectionResponse
from app.services.detection_pipeline import DetectionPipeline
from app.vision.preprocessing import load_image_cv2

router = APIRouter()
detection_pipeline = DetectionPipeline()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/detect", response_model=DetectionResponse)
async def detect_image(image: UploadFile = File(...)) -> DetectionResponse:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Formato invalido. Envie uma imagem JPEG, PNG ou WebP.",
        )

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Arquivo de imagem vazio.")

    cv2_image = load_image_cv2(image_bytes)
    return detection_pipeline.analyze(cv2_image, image_name=image.filename)
