from app.schemas.detection import DetectionItem, NavigationHint


class MessageGenerator:
    """Gera uma mensagem curta e util para audio."""

    def generate(self, detections: list[DetectionItem], navigation: NavigationHint) -> str:
        if not detections or navigation.target_class_name is None:
            return "Nenhum ponto de interesse ou obstaculo relevante detectado."

        target = detections[0]
        if self._has_clear_path_to_interest(target, detections):
            return f"Caminho livre em direcao a {target.class_name}."

        return navigation.instruction

    def _has_clear_path_to_interest(self, target: DetectionItem, detections: list[DetectionItem]) -> bool:
        if target.semantic_role not in {"ponto_interesse", "acessibilidade"}:
            return False
        if target.zone != "centro":
            return False
        if target.depth.proximity not in {"medium", "far"}:
            return False

        return not any(
            item.semantic_role in {"obstaculo", "pessoa"}
            and item.zone == "centro"
            and item.depth.proximity in {"very_near", "near"}
            for item in detections[1:]
        )
