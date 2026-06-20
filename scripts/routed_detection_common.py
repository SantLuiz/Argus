from __future__ import annotations

import json
from pathlib import Path
import sys

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.detection_pipeline import DetectionPipeline


DEFAULT_IMAGE = Path("tests/img_exemplo/[IA]corredor_elevador.jpg")


def read_image(image_path: Path) -> np.ndarray:
    data = np.fromfile(image_path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f"Nao foi possivel abrir a imagem: {image_path}")
    return image


def run_pipeline(
    image_path: Path,
    mode: str,
    target_class: str | None = None,
    use_open_vocab: bool = False,
    use_semantic_segmentation: bool = False,
    use_tactile_specialist: bool = False,
    use_classic_tactile: bool = False,
    use_ocr: bool = False,
):
    pipeline = DetectionPipeline()
    return pipeline.analyze(
        read_image(image_path),
        image_name=image_path.name,
        mode=mode,
        target_class=target_class,
        use_open_vocab=use_open_vocab,
        use_semantic_segmentation=use_semantic_segmentation,
        use_tactile_specialist=use_tactile_specialist,
        use_classic_tactile=use_classic_tactile,
        use_ocr=use_ocr,
    )


def print_json(payload) -> None:
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump()
    print(json.dumps(payload, ensure_ascii=False, indent=2))

