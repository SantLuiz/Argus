from app.detection.class_mapper import map_class
from app.navigation.navigation_state import (
    ACTION_FORWARD,
    ACTION_SEARCH,
    ACTION_SLIGHT_LEFT,
    ACTION_SLIGHT_RIGHT,
    ACTION_STOP,
)
from app.navigation.target_selector import TargetSelector
from app.schemas.detection import DetectionItem, NavigationHint


class LocalNavigator:
    """Navegacao local simples baseada apenas no frame atual.

    Este modulo nao implementa SLAM, mapa 3D nem rota global. Ele apenas traduz
    deteccao + posicao horizontal + profundidade relativa em uma orientacao curta.
    """

    def __init__(self, target_selector: TargetSelector | None = None) -> None:
        self.target_selector = target_selector or TargetSelector()

    def navigate(self, detections: list[DetectionItem], target_class: str | None) -> NavigationHint:
        safety_obstacle = _center_very_near_obstacle(detections)
        if safety_obstacle is not None:
            label = safety_obstacle.label_pt or safety_obstacle.class_name
            return NavigationHint(
                target_class=target_class,
                target_found=False,
                target_class_name=label,
                target_label_pt=label,
                direction="centro",
                action=ACTION_STOP,
                proximity=safety_obstacle.depth.proximity,
                distance_label=safety_obstacle.depth.label_pt,
                instruction=f"{_capitalize(label)} proximo a frente. Pare.",
            )

        target = self.target_selector.select(detections, target_class)
        if target is None:
            label = _target_label(target_class)
            return NavigationHint(
                target_class=target_class,
                target_found=False,
                action=ACTION_SEARCH,
                instruction=f"{label} nao encontrado. Gire lentamente para procurar.",
            )

        label = target.label_pt or target.class_name
        action = _action_for_zone(target.zone)
        return NavigationHint(
            target_class=target.normalized_class or target_class,
            target_found=True,
            target_class_name=target.class_name,
            target_label_pt=label,
            direction=action,
            action=action,
            proximity=target.depth.proximity,
            distance_label=target.depth.label_pt,
            instruction=f"{_capitalize(label)} {_direction_text(action)}, {_action_text(action)}.",
        )


def _center_very_near_obstacle(detections: list[DetectionItem]) -> DetectionItem | None:
    obstacles = [
        detection
        for detection in detections
        if detection.zone == "centro"
        and detection.depth.proximity == "very_near"
        and detection.semantic_role in {"obstaculo", "pessoa", "baixa_prioridade"}
    ]
    if not obstacles:
        return None
    return sorted(obstacles, key=lambda item: (-item.depth.relative_value, -item.navigation_score))[0]


def _target_label(target_class: str | None) -> str:
    if not target_class:
        return "Alvo"
    return _capitalize(map_class(target_class).label_pt)


def _action_for_zone(zone: str) -> str:
    if zone == "esquerda":
        return ACTION_SLIGHT_LEFT
    if zone == "direita":
        return ACTION_SLIGHT_RIGHT
    return ACTION_FORWARD


def _direction_text(action: str) -> str:
    if action == ACTION_SLIGHT_LEFT:
        return "a esquerda"
    if action == ACTION_SLIGHT_RIGHT:
        return "a direita"
    return "a frente"


def _action_text(action: str) -> str:
    if action == ACTION_SLIGHT_LEFT:
        return "vire levemente a esquerda"
    if action == ACTION_SLIGHT_RIGHT:
        return "vire levemente a direita"
    return "siga em frente"


def _capitalize(text: str) -> str:
    return text[:1].upper() + text[1:]

