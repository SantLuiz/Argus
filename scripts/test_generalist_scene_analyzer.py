from pathlib import Path

from routed_detection_common import DEFAULT_IMAGE, print_json, read_image
from app.routing.generalist_scene_analyzer import GeneralistSceneAnalyzer


def main() -> None:
    image_path = Path(DEFAULT_IMAGE)
    analyzer = GeneralistSceneAnalyzer()
    findings = analyzer.analyze(read_image(image_path), use_open_vocab=True, use_semantic_segmentation=False)
    print_json(
        {
            "image": str(image_path),
            "findings": [finding.model_dump() for finding in findings],
            "notes": analyzer.last_notes,
        }
    )


if __name__ == "__main__":
    main()
