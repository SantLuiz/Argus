from io import BytesIO

import numpy as np
from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException


def load_image_rgb(image_bytes: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(image_bytes))
        return image.convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Nao foi possivel ler a imagem enviada.") from exc


def load_image_cv2(image_bytes: bytes) -> np.ndarray:
    try:
        import cv2
    except ModuleNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="OpenCV nao esta instalado no ambiente do backend.",
        ) from exc

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Nao foi possivel ler a imagem enviada.")

    return image
