from routed_detection_common import print_json
from app.routing.detection_plan import GeneralistFinding
from app.routing.scene_router import SceneRouter


def main() -> None:
    router = SceneRouter()
    findings = [
        GeneralistFinding(class_name="door", confidence=0.72, source_model="yoloe", bbox=[10, 10, 100, 200]),
        GeneralistFinding(class_name="tactile paving", confidence=0.45, source_model="classic_tactile"),
    ]
    plan = router.build_plan(mode="auto", target_class="door", findings=findings)
    print_json(plan)


if __name__ == "__main__":
    main()
