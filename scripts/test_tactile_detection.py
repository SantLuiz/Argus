from pathlib import Path

from routed_detection_common import DEFAULT_IMAGE, print_json, run_pipeline


def main() -> None:
    image_path = Path(DEFAULT_IMAGE)
    result = run_pipeline(
        image_path,
        mode="tactile",
        use_open_vocab=True,
        use_tactile_specialist=True,
        use_classic_tactile=True,
    )
    print_json(result)


if __name__ == "__main__":
    main()

