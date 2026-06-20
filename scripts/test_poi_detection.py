from pathlib import Path

from routed_detection_common import DEFAULT_IMAGE, print_json, run_pipeline


def main() -> None:
    image_path = Path(DEFAULT_IMAGE)
    result = run_pipeline(image_path, mode="poi", target_class="door", use_open_vocab=True)
    print_json(result)


if __name__ == "__main__":
    main()

