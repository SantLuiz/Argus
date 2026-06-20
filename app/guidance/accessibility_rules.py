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
    "curb ramp": AccessibilityClass("rampa de acesso", "rampa de acesso", "f", 98),
    "rampa de acesso": AccessibilityClass("rampa de acesso", "rampa de acesso", "f", 98),
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


ACCESSIBILITY_CLASSES.update(
    {
        "tactile-paving": AccessibilityClass("piso tatil", "piso tátil", "m", 96),
        "left turn tactile paving": AccessibilityClass(
            "piso tatil direcional esquerda", "piso tátil direcional à esquerda", "m", 98
        ),
        "right turn tactile paving": AccessibilityClass(
            "piso tatil direcional direita", "piso tátil direcional à direita", "m", 98
        ),
        "stop tactile paving": AccessibilityClass("piso tatil alerta", "piso tátil de alerta", "m", 100),
        "straight tactile paving": AccessibilityClass("piso tatil direcional", "piso tátil direcional", "m", 98),
        "disability sign": AccessibilityClass(
            "sinalizacao de acessibilidade", "sinalização de acessibilidade", "f", 90
        ),
        "stair": AccessibilityClass("escada", "escada", "f", 96),
        "downstair": AccessibilityClass("escada", "escada", "f", 96),
        "upstair": AccessibilityClass("escada", "escada", "f", 96),
    }
)


def get_accessibility_class(class_name: str) -> AccessibilityClass | None:
    return ACCESSIBILITY_CLASSES.get(normalize_class_name(class_name))


def is_accessibility_class(class_name: str) -> bool:
    return get_accessibility_class(class_name) is not None
