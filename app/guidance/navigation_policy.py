from app.detection.priority import LOW_PRIORITY_CLASSES, PERSON_CLASSES, POINT_OF_INTEREST_CLASSES, normalize_class_name
from app.schemas.detection import DetectionItem, NavigationHint


POINTS_OF_INTEREST = {
    "door": ("porta", "ponto_interesse", 100),
    "porta": ("porta", "ponto_interesse", 100),
    "doorway": ("passagem", "ponto_interesse", 95),
    "passage": ("passagem", "ponto_interesse", 95),
    "passagem": ("passagem", "ponto_interesse", 95),
    "corridor": ("corredor", "ponto_interesse", 90),
    "hallway": ("corredor", "ponto_interesse", 90),
    "corredor": ("corredor", "ponto_interesse", 90),
    "elevator": ("elevador", "ponto_interesse", 88),
    "elevador": ("elevador", "ponto_interesse", 88),
    "reception": ("recepcao", "ponto_interesse", 84),
    "recepcao": ("recepcao", "ponto_interesse", 84),
    "stairs": ("escada", "ponto_interesse", 92),
    "escada": ("escada", "ponto_interesse", 92),
    "step": ("degrau", "ponto_interesse", 92),
    "degrau": ("degrau", "ponto_interesse", 92),
    "ramp": ("rampa", "ponto_interesse", 86),
    "rampa": ("rampa", "ponto_interesse", 86),
    "handrail": ("corrimao", "ponto_interesse", 78),
    "corrimao": ("corrimao", "ponto_interesse", 78),
    "tactile paving": ("piso tatil", "ponto_interesse", 82),
    "piso tatil": ("piso tatil", "ponto_interesse", 82),
    "sign": ("sinalizacao", "ponto_interesse", 72),
    "sinalizacao": ("sinalizacao", "ponto_interesse", 72),
}

OBSTACLE_CLASSES = {
    "chair",
    "cadeira",
    "bench",
    "table",
    "mesa",
    "dining table",
    "couch",
    "sofa",
    "potted plant",
    "planta",
    "box",
    "caixa",
    "obstacle",
    "obstaculo",
}

PROXIMITY_WEIGHT = {"very_near": 45, "near": 30, "medium": 12, "far": 0, "unknown": 0}
ZONE_WEIGHT = {"centro": 16, "esquerda": 6, "direita": 6}
ROLE_RANK = {"ponto_interesse": 0, "obstaculo": 1, "pessoa": 1, "baixa_prioridade": 2, "contexto": 3}


def prepare_navigation_detections(detections: list[DetectionItem]) -> list[DetectionItem]:
    """Filtra e pontua deteccoes para navegacao assistida em ambiente interno."""

    prepared: list[DetectionItem] = []

    for detection in detections:
        normalized = _normalize_detection(detection)
        role, score = _role_and_score(normalized)
        if role == "contexto" and score <= 0:
            continue

        prepared.append(
            normalized.model_copy(
                update={
                    "semantic_role": role,
                    "navigation_score": round(score, 3),
                    "priority": _priority_from_score(score, role),
                }
            )
        )

    return sorted(prepared, key=_navigation_sort_key)


def build_navigation_hint(detections: list[DetectionItem]) -> NavigationHint:
    if not detections:
        return NavigationHint(instruction="Nenhum ponto de interesse ou obstaculo relevante detectado.")

    target = detections[0]
    label_pt = _label_pt(target.class_name)
    direction = _direction_text(target.zone)
    proximity = target.depth.label_pt

    if target.semantic_role == "ponto_interesse":
        instruction = f"Siga em direcao a {label_pt} {direction}, a distancia {proximity}."
    elif target.semantic_role == "obstaculo":
        instruction = f"Atenção: {label_pt} {direction}, {proximity}. Ajuste o trajeto."
    elif target.semantic_role == "pessoa":
        instruction = f"Pessoa {direction}, {proximity}. Mantenha atencao ao caminho."
    else:
        instruction = f"{label_pt.capitalize()} {direction}, {proximity}."

    return NavigationHint(
        target_class_name=target.class_name,
        target_label_pt=label_pt,
        direction=target.zone,
        proximity=target.depth.proximity,
        instruction=instruction,
    )


def _normalize_detection(detection: DetectionItem) -> DetectionItem:
    class_name = _label_pt(detection.class_name)
    return detection.model_copy(update={"class_name": class_name})


def _role_and_score(detection: DetectionItem) -> tuple[str, float]:
    class_name = _normalized_class(detection.class_name)
    if class_name in POINTS_OF_INTEREST:
        _, role, base_score = POINTS_OF_INTEREST[class_name]
    elif class_name in PERSON_CLASSES:
        role, base_score = "pessoa", 54
    elif class_name in OBSTACLE_CLASSES:
        role, base_score = "obstaculo", 48
    elif class_name in LOW_PRIORITY_CLASSES:
        role, base_score = "baixa_prioridade", 6
    else:
        role, base_score = "contexto", 0

    score = (
        base_score
        + PROXIMITY_WEIGHT.get(detection.depth.proximity, 0)
        + ZONE_WEIGHT.get(detection.zone, 0)
        + detection.confidence * 8
    )
    return role, score


def _navigation_sort_key(detection: DetectionItem) -> tuple[int, float, int, float]:
    return (
        ROLE_RANK.get(detection.semantic_role, 3),
        -detection.navigation_score,
        0 if detection.zone == "centro" else 1,
        -detection.confidence,
    )


def _priority_from_score(score: float, role: str) -> str:
    if role == "baixa_prioridade":
        return "baixa"
    if role == "ponto_interesse" or score >= 85:
        return "alta"
    if score >= 58:
        return "media"
    return "baixa"


def _is_person(class_name: str) -> bool:
    return _normalized_class(class_name) in PERSON_CLASSES


def _direction_text(zone: str) -> str:
    if zone == "esquerda":
        return "a esquerda"
    if zone == "direita":
        return "a direita"
    return "a frente"


def _label_pt(class_name: str) -> str:
    normalized = _normalized_class(class_name)
    if normalized in POINT_OF_INTEREST_CLASSES and normalized in POINTS_OF_INTEREST:
        return POINTS_OF_INTEREST[normalized][0]
    labels = {
        "person": "pessoa",
        "chair": "cadeira",
        "table": "mesa",
        "dining table": "mesa",
        "bench": "banco",
        "couch": "sofa",
        "potted plant": "planta",
        "backpack": "mochila",
        "handbag": "bolsa",
        "suitcase": "mala",
        "tie": "gravata",
        "umbrella": "guarda chuva",
        "bottle": "garrafa",
        "cup": "copo",
        "cell phone": "celular",
        "laptop": "notebook",
        "book": "livro",
        "remote": "controle remoto",
        "mouse": "mouse",
        "keyboard": "teclado",
        "box": "caixa",
        "obstacle": "obstaculo",
    }
    return labels.get(normalized, normalized)


def _normalized_class(class_name: str) -> str:
    return normalize_class_name(class_name)


from app.guidance.navigation_priority import NavigationPriority

_navigation_priority = NavigationPriority()


def prepare_navigation_detections(detections: list[DetectionItem]) -> list[DetectionItem]:
    return _navigation_priority.prioritize(detections)


def build_navigation_hint(detections: list[DetectionItem]) -> NavigationHint:
    return _navigation_priority.build_hint(detections)
