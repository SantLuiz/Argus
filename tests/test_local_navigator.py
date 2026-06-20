from app.navigation.local_navigator import LocalNavigator
from app.schemas.detection import DepthInfo, DetectionItem


def detection(class_name, zone="centro", proximity="medium", role="ponto_interesse", score=100.0):
    return DetectionItem(
        class_name=class_name,
        raw_class_name=class_name,
        normalized_class=class_name,
        label_pt=class_name,
        category=role,
        confidence=0.80,
        bbox=[0, 0, 100, 100],
        zone=zone,
        depth=DepthInfo(relative_value=0.5, proximity=proximity, label_pt="medio"),
        priority="alta",
        semantic_role=role,
        navigation_score=score,
        priority_score=score,
    )


def test_local_navigator_guides_to_visible_target() -> None:
    navigator = LocalNavigator()

    hint = navigator.navigate([detection("porta", zone="esquerda")], target_class="door")

    assert hint.target_found is True
    assert hint.action == "slight_left"
    assert hint.instruction == "Porta a esquerda, vire levemente a esquerda."


def test_local_navigator_searches_when_target_is_missing() -> None:
    navigator = LocalNavigator()

    hint = navigator.navigate([detection("pessoa", role="pessoa")], target_class="elevator")

    assert hint.target_found is False
    assert hint.action == "search"
    assert "Gire lentamente" in hint.instruction


def test_local_navigator_stops_for_very_near_center_obstacle() -> None:
    navigator = LocalNavigator()
    obstacle = detection("obstaculo", proximity="very_near", role="obstaculo", score=120.0)

    hint = navigator.navigate([obstacle, detection("porta")], target_class="door")

    assert hint.action == "stop"
    assert hint.instruction == "Obstaculo proximo a frente. Pare."

