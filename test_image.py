import argparse
import json
from pathlib import Path

from app.vision.yolo_detector import YoloDetector


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Testa o detector YOLO do ARGUS IC em uma imagem local."
    )
    parser.add_argument("image_path", help="Caminho da imagem local.")
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="Caminho ou nome do modelo YOLO. Padrao: yolov8n.pt.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confianca minima para manter deteccoes. Padrao: 0.25.",
    )
    args = parser.parse_args()

    image_path = Path(args.image_path)
    if not image_path.exists():
        raise SystemExit(f"Imagem nao encontrada: {image_path}")

    try:
        import cv2
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "OpenCV nao esta instalado no ambiente atual. "
            "Instale com: pip install opencv-python"
        ) from exc

    image = cv2.imread(str(image_path))
    if image is None:
        raise SystemExit(f"Nao foi possivel ler a imagem: {image_path}")

    detector = YoloDetector(model_path=args.model, confidence_threshold=args.conf)
    detections = detector.detect(image)

    output = {
        "image": str(image_path),
        "model": args.model,
        "confidence_threshold": args.conf,
        "detections_count": len(detections),
        "detections": [detection.model_dump() for detection in detections],
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
