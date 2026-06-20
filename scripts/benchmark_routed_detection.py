from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean
from time import perf_counter

from routed_detection_common import DEFAULT_IMAGE, run_pipeline


CONFIGS = [
    {"name": "fast", "mode": "fast"},
    {"name": "poi", "mode": "poi", "use_open_vocab": True},
    {"name": "tactile", "mode": "tactile", "use_open_vocab": True, "use_classic_tactile": True},
    {"name": "auto", "mode": "auto"},
    {"name": "auto_ocr", "mode": "auto", "use_ocr": True},
    {"name": "auto_segformer", "mode": "auto", "use_semantic_segmentation": True},
]


def main() -> None:
    image_path = Path(DEFAULT_IMAGE)
    output_path = Path("results/evaluation/routed_detection_benchmark.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for config in CONFIGS:
        timings = []
        results = []
        for _ in range(3):
            start = perf_counter()
            result = run_pipeline(image_path, **{key: value for key, value in config.items() if key != "name"})
            timings.append((perf_counter() - start) * 1000)
            results.append(result)
        last = results[-1]
        detections = last.detections
        rows.append(
            {
                "config": config["name"],
                "mode": last.mode,
                "models_called": ",".join(last.models_called),
                "poi_detected": sum(1 for item in detections if item.semantic_role == "ponto_interesse"),
                "tactile_detected": sum(1 for item in detections if item.normalized_class == "piso tatil"),
                "corroborated": sum(1 for item in detections if item.corroborated),
                "message": last.message,
                "api_total_time_ms": last.processing_time_ms.total_ms,
                "wall_time_avg_ms": round(mean(timings), 2),
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Benchmark salvo em: {output_path}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()

