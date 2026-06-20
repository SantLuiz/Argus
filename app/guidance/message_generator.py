from app.schemas.detection import DetectionItem, NavigationHint


class MessageGenerator:
    """Gera uma mensagem curta e util para audio."""

    def generate(self, detections: list[DetectionItem], navigation: NavigationHint, mode: str = "exploration") -> str:
        if not detections or navigation.target_class_name is None:
            if mode == "navigation":
                return navigation.instruction
            return "Nenhum ponto de interesse ou obstaculo relevante detectado."

        if mode == "navigation":
            return navigation.instruction

        safety_message = self._safety_message(detections)
        if safety_message:
            return safety_message

        target = detections[0]
        if self._has_clear_path_to_interest(target, detections):
            return f"Caminho livre em direcao a {target.class_name}."

        messages = [navigation.instruction]
        secondary = self._secondary_information(target, detections)
        if secondary:
            messages.append(secondary)
        return " ".join(messages[:2])

    def _safety_message(self, detections: list[DetectionItem]) -> str | None:
        for item in detections:
            if (
                item.zone == "centro"
                and item.depth.proximity == "very_near"
                and item.semantic_role in {"obstaculo", "pessoa", "baixa_prioridade"}
            ):
                label = item.label_pt or item.class_name
                return f"{label.capitalize()} muito proximo a frente. Pare."
        return None

    def _secondary_information(self, target: DetectionItem, detections: list[DetectionItem]) -> str | None:
        for item in detections[1:]:
            if item == target:
                continue
            if item.semantic_role not in {"acessibilidade", "ponto_interesse", "obstaculo", "pessoa"}:
                if not (item.zone == "centro" and item.depth.proximity == "very_near"):
                    continue
            return _short_sentence(item)
        return None

    def _has_clear_path_to_interest(self, target: DetectionItem, detections: list[DetectionItem]) -> bool:
        if target.semantic_role != "ponto_interesse":
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


def _short_sentence(item: DetectionItem) -> str:
    label = item.label_pt or item.class_name
    direction = {"esquerda": "a esquerda", "direita": "a direita"}.get(item.zone, "a frente")
    if item.semantic_role == "acessibilidade":
        return f"{label.capitalize()} {direction}."
    return f"{label.capitalize()} {direction}, {item.depth.label_pt}."
