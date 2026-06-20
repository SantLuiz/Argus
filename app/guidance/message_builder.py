from app.schemas.detection import DetectionItem, NavigationHint

CLASS_INFO_PT = {
    "person": ("Pessoa", "f"),
    "pessoa": ("Pessoa", "f"),
    "chair": ("Cadeira", "f"),
    "cadeira": ("Cadeira", "f"),
    "table": ("Mesa", "f"),
    "mesa": ("Mesa", "f"),
    "door": ("Porta", "f"),
    "porta": ("Porta", "f"),
    "obstacle": ("Obstaculo", "m"),
    "obstaculo": ("Obstaculo", "m"),
    "banco": ("Banco", "m"),
    "sofa": ("Sofa", "m"),
    "planta": ("Planta", "f"),
    "stairs": ("Escada", "f"),
    "escada": ("Escada", "f"),
    "step": ("Degrau", "m"),
    "degrau": ("Degrau", "m"),
    "backpack": ("Mochila", "f"),
    "mochila": ("Mochila", "f"),
    "handbag": ("Bolsa", "f"),
    "bolsa": ("Bolsa", "f"),
    "suitcase": ("Mala", "f"),
    "mala": ("Mala", "f"),
    "bottle": ("Garrafa", "f"),
    "garrafa": ("Garrafa", "f"),
    "cup": ("Copo", "m"),
    "copo": ("Copo", "m"),
    "cell phone": ("Celular", "m"),
    "celular": ("Celular", "m"),
    "laptop": ("Notebook", "m"),
    "notebook": ("Notebook", "m"),
    "book": ("Livro", "m"),
    "livro": ("Livro", "m"),
    "remote": ("Controle remoto", "m"),
    "controle remoto": ("Controle remoto", "m"),
    "keyboard": ("Teclado", "m"),
    "teclado": ("Teclado", "m"),
    "box": ("Caixa", "f"),
    "caixa": ("Caixa", "f"),
    "corredor": ("Corredor", "m"),
    "passagem": ("Passagem", "f"),
    "elevador": ("Elevador", "m"),
    "recepcao": ("Recepcao", "f"),
    "rampa": ("Rampa", "f"),
    "corrimao": ("Corrimao", "m"),
    "piso tatil": ("Piso tatil", "m"),
    "sinalizacao": ("Sinalizacao", "f"),
}

ZONE_LABELS_PT = {
    "esquerda": "a esquerda",
    "centro": "ao centro",
    "direita": "a direita",
}

PROXIMITY_TEXT_PT = {
    "very_near": {"m": "muito proximo", "f": "muito proxima"},
    "near": {"m": "proximo", "f": "proxima"},
    "medium": {"m": "a media distancia", "f": "a media distancia"},
    "far": {"m": "distante", "f": "distante"},
    "unknown": {"m": "com distancia nao estimada", "f": "com distancia nao estimada"},
}

PROXIMITY_ORDER = {"very_near": 0, "near": 1, "medium": 2, "far": 3, "unknown": 4}
ZONE_ORDER = {"centro": 0, "esquerda": 1, "direita": 1}
PRIORITY_ORDER = {"alta": 0, "media": 1, "baixa": 2}
ROLE_ORDER = {"ponto_interesse": 0, "obstaculo": 1, "pessoa": 2, "baixa_prioridade": 3, "contexto": 4}
MAX_ITEMS_IN_MESSAGE = 3


def build_guidance_message(detections: list[DetectionItem], navigation: NavigationHint | None = None) -> str:
    if navigation is not None and navigation.target_class_name is not None:
        context = _context_phrase(detections, navigation.target_class_name)
        return f"{navigation.instruction}{context}"

    if not detections:
        return "Nenhum ponto de interesse ou obstaculo relevante detectado."

    ordered = sorted(detections, key=_message_sort_key)
    phrases = [_phrase_for_detection(item) for item in ordered[:MAX_ITEMS_IN_MESSAGE]]

    if len(detections) > MAX_ITEMS_IN_MESSAGE:
        phrases.append("Ha outros objetos detectados na cena")

    return ". ".join(phrases) + "."


def _phrase_for_detection(detection: DetectionItem) -> str:
    class_name, gender = _class_info(detection.class_name)
    proximity = _proximity_text(detection.depth.proximity, detection.depth.label_pt, gender)
    zone = ZONE_LABELS_PT.get(detection.zone, detection.zone)
    return f"{class_name} {zone}, {proximity}"


def _message_sort_key(detection: DetectionItem) -> tuple[int, int, int, float]:
    return (
        ROLE_ORDER.get(detection.semantic_role, 3),
        PROXIMITY_ORDER.get(detection.depth.proximity, PROXIMITY_ORDER["unknown"]),
        ZONE_ORDER.get(detection.zone, 2),
        PRIORITY_ORDER.get(detection.priority, 3),
        -detection.confidence,
    )


def _class_info(class_name: str) -> tuple[str, str]:
    normalized = class_name.strip().lower()
    if normalized in CLASS_INFO_PT:
        return CLASS_INFO_PT[normalized]

    return class_name.capitalize(), "m"


def _proximity_text(proximity: str, fallback_label: str, gender: str) -> str:
    labels = PROXIMITY_TEXT_PT.get(proximity)
    if labels is None:
        return fallback_label

    return labels.get(gender, labels["m"])


def _context_phrase(detections: list[DetectionItem], target_class_name: str) -> str:
    extras = [item for item in detections if item.class_name != target_class_name]
    if not extras:
        return ""

    ordered = sorted(extras, key=_message_sort_key)
    relevant = [item for item in ordered if item.semantic_role in {"obstaculo", "pessoa"}][:1]
    if not relevant:
        return ""

    return f" {_phrase_for_detection(relevant[0])}."
