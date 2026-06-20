import os

import numpy as np

from app.schemas.detection import ObjectDetection


class SemanticSegmentationDetector:
    """Interface opcional para SegFormer/ADE20K como evidencia estrutural.

    A implementacao completa depende de `transformers` e pesos locais/cacheados.
    Por padrao retorna vazio para nao impor dependencia pesada ao MVP.
    """

    def __init__(self, enabled: bool | None = None) -> None:
        self.enabled = enabled if enabled is not None else os.getenv("ARGUS_ENABLE_SEGFORMER", "0") == "1"
        self.last_error: str | None = None

    def detect(self, image: np.ndarray) -> list[ObjectDetection]:
        if not self.enabled:
            return []
        try:
            import torch  # type: ignore  # noqa: F401
            from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor  # type: ignore  # noqa: F401
        except Exception as exc:
            self.last_error = f"SegFormer indisponivel: {exc.__class__.__name__}"
            return []

        self.last_error = "SegFormer habilitado, mas inferencia completa fica para etapa experimental posterior."
        return []

