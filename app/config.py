OPEN_VOCAB_MODEL_PRIORITY = ["yoloe", "yolo_world"]

ENABLE_SEMANTIC_SEGMENTATION = False
ENABLE_OCR = False
ENABLE_TACTILE_SPECIALIST = True
ENABLE_CLASSIC_TACTILE = True

DEFAULT_MODE = "auto"

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

