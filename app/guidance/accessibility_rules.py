from dataclasses import dataclass

from app.detection.priority import normalize_class_name


@dataclass(frozen=True)
class AccessibilityClass:
    canonical_name: str
    label_pt: str
    gender: str
    base_score: float


# Essas classes geralmente exigem um modelo customizado treinado com dataset
# proprio ou anotado no Roboflow; o YOLO generico em COCO tende a nao detecta-las.
ACCESSIBILITY_CLASSES: dict[str, AccessibilityClass] = {
    "ramp": AccessibilityClass("rampa", "rampa", "f", 98),
    "rampa": AccessibilityClass("rampa", "rampa", "f", 98),
    "handrail": AccessibilityClass("corrimao", "corrimão", "m", 92),
    "corrimao": AccessibilityClass("corrimao", "corrimão", "m", 92),
    "corrimão": AccessibilityClass("corrimao", "corrimão", "m", 92),
    "tactile paving": AccessibilityClass("piso tatil", "piso tátil", "m", 96),
    "tactile_paving": AccessibilityClass("piso tatil", "piso tátil", "m", 96),
    "piso tatil": AccessibilityClass("piso tatil", "piso tátil", "m", 96),
    "piso tátil": AccessibilityClass("piso tatil", "piso tátil", "m", 96),
    "accessibility sign": AccessibilityClass("sinalizacao de acessibilidade", "sinalização de acessibilidade", "f", 90),
    "accessibility_sign": AccessibilityClass("sinalizacao de acessibilidade", "sinalização de acessibilidade", "f", 90),
    "sinalizacao de acessibilidade": AccessibilityClass("sinalizacao de acessibilidade", "sinalização de acessibilidade", "f", 90),
    "sinalização de acessibilidade": AccessibilityClass("sinalizacao de acessibilidade", "sinalização de acessibilidade", "f", 90),
    "wheelchair ramp": AccessibilityClass("rampa acessivel", "rampa acessível", "f", 102),
    "wheelchair_ramp": AccessibilityClass("rampa acessivel", "rampa acessível", "f", 102),
    "rampa acessivel": AccessibilityClass("rampa acessivel", "rampa acessível", "f", 102),
    "rampa acessível": AccessibilityClass("rampa acessivel", "rampa acessível", "f", 102),
    "accessible entrance": AccessibilityClass("entrada acessivel", "entrada acessível", "f", 100),
    "accessible_entrance": AccessibilityClass("entrada acessivel", "entrada acessível", "f", 100),
    "entrada acessivel": AccessibilityClass("entrada acessivel", "entrada acessível", "f", 100),
    "entrada acessível": AccessibilityClass("entrada acessivel", "entrada acessível", "f", 100),
    "elevator": AccessibilityClass("elevador", "elevador", "m", 94),
    "elevador": AccessibilityClass("elevador", "elevador", "m", 94),
    "stairs": AccessibilityClass("escada", "escada", "f", 96),
    "escada": AccessibilityClass("escada", "escada", "f", 96),
    "step": AccessibilityClass("degrau", "degrau", "m", 92),
    "degrau": AccessibilityClass("degrau", "degrau", "m", 92),
}


def get_accessibility_class(class_name: str) -> AccessibilityClass | None:
    return ACCESSIBILITY_CLASSES.get(normalize_class_name(class_name))


def is_accessibility_class(class_name: str) -> bool:
    return get_accessibility_class(class_name) is not None
