from pydantic import BaseModel, Field


class DepthInfo(BaseModel):
    relative_value: float = Field(ge=0.0, le=1.0)
    proximity: str
    label_pt: str


class ObjectDetection(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[int]
    source_model: str = "unknown"
    detection_type: str = "object_detection"
    corroborated: bool = False


class DetectionItem(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[int]
    zone: str
    depth: DepthInfo
    priority: str
    raw_class_name: str | None = None
    normalized_class: str | None = None
    label_pt: str | None = None
    category: str | None = None
    priority_score: float = 0.0
    semantic_role: str = "contexto"
    navigation_score: float = 0.0
    source_model: str = "unknown"
    detection_type: str = "object_detection"
    corroborated: bool = False


class NavigationHint(BaseModel):
    target_class_name: str | None = None
    target_label_pt: str | None = None
    target_class: str | None = None
    target_found: bool = False
    direction: str | None = None
    action: str | None = None
    proximity: str | None = None
    distance_label: str | None = None
    instruction: str


class ProcessingTime(BaseModel):
    detection_ms: int
    depth_ms: int
    total_ms: int


class AudioPayload(BaseModel):
    text: str
    language: str = "pt-BR"
    mode: str = "tts_client"


class DetectionResponse(BaseModel):
    detections: list[DetectionItem]
    raw_detections: list[ObjectDetection] | None = None
    message: str
    audio: AudioPayload
    processing_time_ms: ProcessingTime
    mode: str = "exploration"
    use_open_vocab: bool = False
    detection_plan: dict | None = None
    generalist_findings: list[dict] = []
    models_called: list[str] = []
    navigation: NavigationHint | None = None
    image_name: str | None = None
    notes: list[str] = []
