from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from statistics import mean
import sys

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.detection_pipeline import DetectionPipeline


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    args = _parse_args()
    image_paths = _list_images(args.image_dir)
    if not image_paths:
        raise SystemExit(f"Nenhuma imagem encontrada em {args.image_dir}.")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pipeline = DetectionPipeline()
    rows: list[dict[str, object]] = []
    modes = [False, True] if args.compare_open_vocab else [args.use_open_vocab]

    for image_path in image_paths:
        image = _read_image(image_path)
        for use_open_vocab in modes:
            result = pipeline.analyze(
                image,
                image_name=image_path.name,
                mode=args.mode,
                target_class=args.target_class,
                use_open_vocab=use_open_vocab,
            )
            rows.append(_row_from_result(result, use_open_vocab))

    _write_csv(output_path, rows)
    _print_summary(rows, output_path)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Avalia o pipeline ARGUS IC para navegacao indoor.")
    parser.add_argument("--image-dir", default="tests/img_exemplo", help="Pasta com imagens locais.")
    parser.add_argument("--output", default="results/evaluation/navigation_detection_report.csv", help="CSV de saida.")
    parser.add_argument("--mode", choices=["exploration", "navigation"], default="exploration")
    parser.add_argument("--target-class", default=None, help="Classe alvo para mode=navigation. Ex.: door, elevator.")
    parser.add_argument("--use-open-vocab", action="store_true", help="Executa o detector open-vocabulary experimental.")
    parser.add_argument(
        "--compare-open-vocab",
        action="store_true",
        help="Roda cada imagem duas vezes: sem e com open-vocabulary.",
    )
    return parser.parse_args()


def _list_images(image_dir: str) -> list[Path]:
    root = Path(image_dir)
    return sorted(path for path in root.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)


def _read_image(path: Path) -> np.ndarray:
    data = np.fromfile(path, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Nao foi possivel abrir a imagem: {path}")
    return image


def _row_from_result(result, use_open_vocab: bool) -> dict[str, object]:
    detections = result.detections
    raw = result.raw_detections or []
    suppressed_count = max(len(raw) - len(detections), 0)
    return {
        "image_name": result.image_name,
        "use_open_vocab": use_open_vocab,
        "mode": result.mode,
        "raw_detection_count": len(raw),
        "filtered_detection_count": len(detections),
        "poi_detected": _count_role(detections, "ponto_interesse"),
        "accessibility_detected": _count_role(detections, "acessibilidade"),
        "obstacles_detected": _count_role(detections, "obstaculo") + _count_role(detections, "pessoa"),
        "suppressed_generic_objects": suppressed_count,
        "message": result.message,
        "detection_time_ms": result.processing_time_ms.detection_ms,
        "depth_time_ms": result.processing_time_ms.depth_ms,
        "total_time_ms": result.processing_time_ms.total_ms,
        "classes": ",".join(item.normalized_class or item.class_name for item in detections),
    }


def _count_role(detections, role: str) -> int:
    return sum(1 for item in detections if item.semantic_role == role)


def _write_csv(output_path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "image_name",
        "use_open_vocab",
        "mode",
        "raw_detection_count",
        "filtered_detection_count",
        "poi_detected",
        "accessibility_detected",
        "obstacles_detected",
        "suppressed_generic_objects",
        "message",
        "detection_time_ms",
        "depth_time_ms",
        "total_time_ms",
        "classes",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _print_summary(rows: list[dict[str, object]], output_path: Path) -> None:
    class_counter = Counter()
    message_counter = Counter(str(row["message"]) for row in rows)
    for row in rows:
        class_counter.update(filter(None, str(row["classes"]).split(",")))

    print(f"Total de execucoes: {len(rows)}")
    print(f"Media de objetos brutos: {_mean(rows, 'raw_detection_count'):.2f}")
    print(f"Media de objetos filtrados: {_mean(rows, 'filtered_detection_count'):.2f}")
    print(f"Media de tempo total: {_mean(rows, 'total_time_ms'):.2f} ms")
    print(f"Classes mais detectadas: {class_counter.most_common(8)}")
    print(f"Mensagens mais comuns: {message_counter.most_common(5)}")
    print(f"CSV gerado em: {output_path}")


def _mean(rows: list[dict[str, object]], field: str) -> float:
    return mean(float(row[field]) for row in rows) if rows else 0.0


if __name__ == "__main__":
    main()
