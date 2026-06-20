import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from urllib.parse import urlencode

import cv2
import numpy as np
import requests


API_URL = "http://127.0.0.1:8000/detect"
OUTPUT_ROOT = Path("results") / "curl_runner"
IMAGE_PATH = r"tests\img_exemplo\[IA]corredor_elevador.jpg"

RUNS = 5
WARMUP_RUNS = 1
MODE = "exploration"
TARGET_CLASS = "door"


@dataclass(frozen=True)
class ModelBenchmarkConfig:
    name: str
    label: str
    use_open_vocab: bool = False
    mode: str = MODE
    target_class: str | None = None


MODEL_CONFIGS = [
    ModelBenchmarkConfig(
        name="yolo_generic",
        label="YOLO generico",
        use_open_vocab=False,
        mode=MODE,
        target_class=TARGET_CLASS if MODE == "navigation" else None,
    ),
    ModelBenchmarkConfig(
        name="yolo_open_vocab",
        label="YOLO + open-vocabulary",
        use_open_vocab=True,
        mode=MODE,
        target_class=TARGET_CLASS if MODE == "navigation" else None,
    ),
]


PROXIMITY_COLORS = {
    "very_near": (0, 0, 255),
    "near": (0, 140, 255),
    "medium": (0, 200, 255),
    "far": (0, 180, 0),
    "unknown": (160, 160, 160),
}


def main() -> None:
    image_path = Path(IMAGE_PATH)
    if not image_path.exists():
        raise SystemExit(f"Imagem nao encontrada: {image_path}")

    run_root = OUTPUT_ROOT / safe_stem(image_path)
    run_root.mkdir(parents=True, exist_ok=True)

    print(f"Imagem: {image_path}")
    print(f"Endpoint: {API_URL}")
    print(f"Modo: {MODE}")
    print(f"Warm-up por modelo: {WARMUP_RUNS} execucao(oes)")
    print(f"Benchmark por modelo: {RUNS} execucao(oes)")
    print(f"Saida: {run_root}\n")

    summaries = []
    for config in MODEL_CONFIGS:
        summaries.append(run_model_benchmark(image_path, run_root, config))

    write_json(run_root / "benchmark_comparativo.json", summaries)
    print_comparison_summary(summaries)


def run_model_benchmark(image_path: Path, run_root: Path, config: ModelBenchmarkConfig) -> dict:
    model_dir = run_root / config.name
    model_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== {config.label} ===")
    print(f"Pasta: {model_dir}")

    for index in range(WARMUP_RUNS):
        print(f"Warm-up {index + 1}/{WARMUP_RUNS}...")
        call_detect_api(image_path, config)

    benchmark_results = run_benchmark(image_path, config, RUNS)
    response_json = benchmark_results[-1]
    summary = build_benchmark_summary(config, benchmark_results)

    annotated_image = draw_detections(image_path, response_json.get("detections", []), config, summary)
    annotated_path = model_dir / f"{safe_stem(image_path)}_{config.name}_annotated.jpg"
    save_image(annotated_path, annotated_image)

    write_json(model_dir / "ultima_resposta.json", response_json)
    write_json(model_dir / "benchmark_resumo.json", summary)
    write_json(model_dir / "benchmark_execucoes.json", benchmark_results)

    print("\nJSON da ultima execucao:")
    print(json.dumps(response_json, ensure_ascii=False, indent=2))
    print_benchmark_summary(summary)
    print(f"Imagem anotada salva em: {annotated_path}\n")
    return summary


def call_detect_api(image_path: Path, config: ModelBenchmarkConfig) -> dict:
    content_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    url = build_url(config)

    with image_path.open("rb") as image_file:
        response = requests.post(
            url,
            files={"image": (image_path.name, image_file, content_type)},
            timeout=180,
        )

    if not response.ok:
        raise SystemExit(
            f"Erro ao chamar API ({config.label}): HTTP {response.status_code}\n{response.text}"
        )

    return response.json()


def build_url(config: ModelBenchmarkConfig) -> str:
    query = {
        "mode": config.mode,
        "use_open_vocab": str(config.use_open_vocab).lower(),
    }
    if config.target_class:
        query["target_class"] = config.target_class
    return f"{API_URL}?{urlencode(query)}"


def run_benchmark(image_path: Path, config: ModelBenchmarkConfig, runs: int) -> list[dict]:
    if runs <= 0:
        raise SystemExit("RUNS deve ser maior que zero.")

    results = []
    for index in range(runs):
        print(f"Execucao {index + 1}/{runs}...")
        response_json = call_detect_api(image_path, config)
        results.append(response_json)
        print_run_timing(index + 1, response_json)

    return results


def print_run_timing(index: int, response_json: dict) -> None:
    timing = response_json.get("processing_time_ms", {})
    detection_ms = timing.get("detection_ms", 0)
    depth_ms = timing.get("depth_ms", 0)
    total_ms = timing.get("total_ms", 0)
    detections_count = len(response_json.get("detections", []))

    print(
        f"  #{index}: deteccoes={detections_count} | "
        f"deteccao={detection_ms} ms | profundidade={depth_ms} ms | total={total_ms} ms"
    )


def build_benchmark_summary(config: ModelBenchmarkConfig, results: list[dict]) -> dict:
    detection_times = []
    depth_times = []
    total_times = []
    detections_counts = []
    messages = []

    for result in results:
        timing = result.get("processing_time_ms", {})
        detection_times.append(float(timing.get("detection_ms", 0)))
        depth_times.append(float(timing.get("depth_ms", 0)))
        total_times.append(float(timing.get("total_ms", 0)))
        detections_counts.append(len(result.get("detections", [])))
        messages.append(result.get("message", ""))

    last_result = results[-1] if results else {}
    return {
        "model_name": config.name,
        "model_label": config.label,
        "mode": config.mode,
        "target_class": config.target_class,
        "use_open_vocab": config.use_open_vocab,
        "runs": len(results),
        "avg_detection_ms": round(mean(detection_times), 2) if detection_times else 0,
        "avg_depth_ms": round(mean(depth_times), 2) if depth_times else 0,
        "avg_total_ms": round(mean(total_times), 2) if total_times else 0,
        "avg_detections": round(mean(detections_counts), 2) if detections_counts else 0,
        "last_message": last_result.get("message", ""),
        "last_detection_count": len(last_result.get("detections", [])),
        "notes": last_result.get("notes", []),
        "messages": messages,
    }


def print_benchmark_summary(summary: dict) -> None:
    print("\nResumo do benchmark:")
    print(f"  Modelo: {summary['model_label']}")
    print(f"  Execucoes medidas: {summary['runs']}")
    print(f"  Tempo medio de deteccao: {summary['avg_detection_ms']:.2f} ms")
    print(f"  Tempo medio de profundidade: {summary['avg_depth_ms']:.2f} ms")
    print(f"  Tempo medio total do pipeline: {summary['avg_total_ms']:.2f} ms")
    print(f"  Media de deteccoes por imagem: {summary['avg_detections']:.2f}")
    print(f"  Mensagem final: {summary['last_message']}")


def print_comparison_summary(summaries: list[dict]) -> None:
    print("=== Comparativo final ===")
    for summary in summaries:
        print(
            f"{summary['model_label']}: total medio={summary['avg_total_ms']:.2f} ms | "
            f"deteccoes={summary['avg_detections']:.2f} | mensagem='{summary['last_message']}'"
        )


def draw_detections(image_path: Path, detections: list[dict], config: ModelBenchmarkConfig, summary: dict) -> np.ndarray:
    image = load_image(image_path)
    draw_header(image, config, summary)

    for detection in detections:
        bbox = detection.get("bbox", [])
        if len(bbox) != 4:
            continue

        x1, y1, x2, y2 = [int(value) for value in bbox]
        depth = detection.get("depth", {})
        proximity = depth.get("proximity", "unknown")
        color = PROXIMITY_COLORS.get(proximity, PROXIMITY_COLORS["unknown"])

        label = build_label(detection)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness=2)
        draw_label(image, label, x1, y1, color)

    return image


def draw_header(image: np.ndarray, config: ModelBenchmarkConfig, summary: dict) -> None:
    lines = [
        config.label,
        f"modo={config.mode} | open_vocab={config.use_open_vocab}",
        f"total medio={summary['avg_total_ms']:.2f} ms | deteccoes={summary['avg_detections']:.2f}",
    ]
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.58
    thickness = 1
    padding = 8
    line_height = 22
    width = max(cv2.getTextSize(line, font, scale, thickness)[0][0] for line in lines) + padding * 2
    height = line_height * len(lines) + padding

    cv2.rectangle(image, (0, 0), (width, height), (20, 20, 20), thickness=cv2.FILLED)
    for index, line in enumerate(lines):
        y = padding + line_height * (index + 1) - 6
        cv2.putText(image, line, (padding, y), font, scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)


def build_label(detection: dict) -> str:
    class_name = detection.get("label_pt") or detection.get("class_name", "objeto")
    confidence = detection.get("confidence", 0.0)
    depth = detection.get("depth", {})
    proximity_label = depth.get("label_pt", "sem profundidade")
    zone = detection.get("zone", "sem posicao")

    return f"{class_name} {confidence:.2f} | {proximity_label} | {zone}"


def draw_label(image: np.ndarray, label: str, x: int, y: int, color: tuple[int, int, int]) -> None:
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.55
    thickness = 1
    padding = 5

    text_size, baseline = cv2.getTextSize(label, font, scale, thickness)
    text_width, text_height = text_size
    label_y = max(y, text_height + padding * 2 + 70)

    cv2.rectangle(
        image,
        (x, label_y - text_height - padding * 2),
        (x + text_width + padding * 2, label_y + baseline),
        color,
        thickness=cv2.FILLED,
    )
    cv2.putText(
        image,
        label,
        (x + padding, label_y - padding),
        font,
        scale,
        (255, 255, 255),
        thickness,
        lineType=cv2.LINE_AA,
    )


def load_image(image_path: Path) -> np.ndarray:
    image_bytes = np.fromfile(str(image_path), dtype=np.uint8)
    image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f"Nao foi possivel ler a imagem: {image_path}")
    return image


def save_image(output_path: Path, image: np.ndarray) -> None:
    extension = output_path.suffix or ".jpg"
    success, encoded_image = cv2.imencode(extension, image)
    if not success:
        raise SystemExit(f"Nao foi possivel salvar a imagem anotada: {output_path}")

    encoded_image.tofile(str(output_path))


def write_json(output_path: Path, payload: object) -> None:
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_stem(path: Path) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in path.stem)


if __name__ == "__main__":
    main()
