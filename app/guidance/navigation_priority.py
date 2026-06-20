from app.detection.class_mapper import map_class
from app.schemas.detection import DetectionItem, NavigationHint


PROXIMITY_WEIGHT = {"very_near": 42, "near": 30, "medium": 14, "far": 0, "unknown": 0}
ZONE_WEIGHT = {"centro": 18, "esquerda": 7, "direita": 7}
ROLE_WEIGHT = {"acessibilidade": 12, "ponto_interesse": 10, "obstaculo": 7, "pessoa": 4, "baixa_prioridade": -28, "contexto": -40}
ROLE_ORDER = {"acessibilidade": 0, "ponto_interesse": 0, "obstaculo": 1, "pessoa": 1, "baixa_prioridade": 2, "contexto": 3}


class NavigationPriority:
    """Pontua deteccoes pela utilidade para navegacao indoor."""

    def prioritize(self, detections: list[DetectionItem]) -> list[DetectionItem]:
        prioritized = [self._score_detection(item) for item in detections]
        useful = [item for item in prioritized if item.semantic_role != "contexto"]
        return sorted(useful, key=self._sort_key)

    def build_hint(self, detections: list[DetectionItem]) -> NavigationHint:
        if not detections:
            return NavigationHint(instruction="Nenhum ponto de interesse ou obstaculo relevante detectado.")

        target = detections[0]
        direction = _direction_text(target.zone)
        distance = _distance_text(target.depth.proximity)

        if target.semantic_role == "acessibilidade" and target.class_name in {"piso tátil", "sinalização de acessibilidade"}:
            instruction = f"{_capitalize(target.class_name)} identificado {direction}."
        elif target.semantic_role == "acessibilidade":
            instruction = f"{_capitalize(target.class_name)} {direction}."
        elif target.semantic_role == "ponto_interesse":
            instruction = f"{_capitalize(target.class_name)} {direction}, {distance}."
        elif target.semantic_role == "obstaculo":
            instruction = f"{_capitalize(target.class_name)} {direction}, {distance}."
        elif target.semantic_role == "pessoa":
            instruction = f"Pessoa {direction}, {distance}."
        else:
            instruction = f"{_capitalize(target.class_name)} {direction}, {distance}."

        return NavigationHint(
            target_class_name=target.class_name,
            target_label_pt=target.class_name,
            target_class=target.normalized_class or target.class_name,
            target_found=True,
            direction=target.zone,
            action=_action_from_zone(target.zone),
            proximity=target.depth.proximity,
            distance_label=target.depth.label_pt,
            instruction=instruction,
        )

    def _score_detection(self, detection: DetectionItem) -> DetectionItem:
        class_info = map_class(detection.class_name)
        class_name = class_info.label_pt
        role = class_info.semantic_group
        score = (
            class_info.base_score
            + ROLE_WEIGHT.get(role, 0)
            + PROXIMITY_WEIGHT.get(detection.depth.proximity, 0)
            + ZONE_WEIGHT.get(detection.zone, 0)
            + detection.confidence * 10
        )

        if role == "baixa_prioridade" and not _is_path_obstacle(detection):
            score -= 35

        return detection.model_copy(
            update={
                "class_name": class_name,
                "raw_class_name": detection.raw_class_name or detection.class_name,
                "normalized_class": class_info.canonical_name,
                "label_pt": class_info.label_pt,
                "category": role,
                "priority_score": round(score, 3),
                "semantic_role": role,
                "navigation_score": round(score, 3),
                "priority": _priority_from_score(score, role),
            }
        )

    def _sort_key(self, detection: DetectionItem) -> tuple[int, float, int, float]:
        return (
            ROLE_ORDER.get(detection.semantic_role, 5),
            -detection.navigation_score,
            0 if detection.zone == "centro" else 1,
            -detection.confidence,
        )


def _priority_from_score(score: float, role: str) -> str:
    if role == "baixa_prioridade":
        return "baixa"
    if role in {"ponto_interesse", "acessibilidade"} or score >= 88:
        return "alta"
    if score >= 65:
        return "media"
    return "baixa"


def _is_path_obstacle(detection: DetectionItem) -> bool:
    return detection.zone == "centro" and detection.depth.proximity in {"very_near", "near"}


def _direction_text(zone: str) -> str:
    if zone == "esquerda":
        return "à esquerda"
    if zone == "direita":
        return "à direita"
    return "à frente"


def _distance_text(proximity: str) -> str:
    labels = {
        "very_near": "muito proximo",
        "near": "proximo",
        "medium": "distancia media",
        "far": "distante",
        "unknown": "distancia nao estimada",
    }
    return labels.get(proximity, "distancia aproximada")


def _action_from_zone(zone: str) -> str:
    if zone == "esquerda":
        return "slight_left"
    if zone == "direita":
        return "slight_right"
    return "forward"


def _capitalize(text: str) -> str:
    return text[:1].upper() + text[1:]
