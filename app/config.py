import os


OPEN_VOCAB_MODEL_PRIORITY = ["yoloe", "yolo_world"]

ENABLE_SEMANTIC_SEGMENTATION = False
ENABLE_OCR = False
ENABLE_TACTILE_SPECIALIST = True
ENABLE_CLASSIC_TACTILE = True

DEFAULT_MODE = "auto"

ARGUS_MVP_PROFILE = os.getenv("ARGUS_MVP_PROFILE", "false").strip().lower() in {"1", "true", "yes", "on"}
ARGUS_REQUIRE_READY_MODELS = os.getenv("ARGUS_REQUIRE_READY_MODELS", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
ARGUS_MAX_UPLOAD_BYTES = int(os.getenv("ARGUS_MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
ARGUS_MAX_DECODED_PIXELS = int(os.getenv("ARGUS_MAX_DECODED_PIXELS", str(12_000_000)))
ARGUS_DETECT_RETRY_AFTER_SECONDS = int(os.getenv("ARGUS_DETECT_RETRY_AFTER_SECONDS", "1"))
ARGUS_MVP_TARGET_CLASSES = {"door", "porta"}

OPEN_VOCAB_PROMPTS = [
    "door",
    "elevator",
    "elevator door",
    "stairs",
    "staircase",
    "reception desk",
    "reception area",
    "front desk",
    "tactile paving",
    "tactile floor",
    "guiding block",
    "warning block",
    "ramp",
    "accessibility ramp",
    "wheelchair ramp",
    "handrail",
    "accessibility sign",
    "entrance",
    "exit",
    "hallway",
    "corridor",
]

POI_CLASSES = ["door", "elevator", "stairs", "reception", "entrance", "exit", "hallway", "corridor"]
ACCESSIBILITY_CLASSES = ["tactile paving", "ramp", "wheelchair ramp", "handrail", "accessibility sign"]
