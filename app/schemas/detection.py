from pydantic import BaseModel, Field


class DepthInfo(BaseModel):
    relative_value: float = Field(ge=0.0, le=1.0)
    proximity: str
    label_pt: str


class ObjectDetection(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[int]


class DetectionItem(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[int]
    zone: str
    depth: DepthInfo
    priority: str
    semantic_role: str = "contexto"
    navigation_score: float = 0.0


class NavigationHint(BaseModel):
    target_class_name: str | None = None
    target_label_pt: str | None = None
    direction: str | None = None
    proximity: str | None = None
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
    navigation: NavigationHint | None = None
    image_name: str | None = None
    notes: list[str] = []
