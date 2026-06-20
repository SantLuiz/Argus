from pydantic import BaseModel, Field


class GeneralistFinding(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_model: str
    bbox: list[int] | None = None
    reason: str | None = None


class DetectionPlan(BaseModel):
    mode: str = "auto"
    target_class: str | None = None
    use_default_yolo: bool = True
    use_open_vocab: bool = False
    use_semantic_segmentation: bool = False
    use_tactile_specialist: bool = False
    use_classic_tactile: bool = False
    use_ocr: bool = False
    use_stair_ramp_heuristics: bool = False
    use_local_navigation: bool = False
    target_classes: list[str] = []
    poi_candidates: list[str] = []
    reason: list[str] = []

