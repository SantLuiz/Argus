"""Prepara os dois modelos do benchmark móvel sem alterar o ambiente do backend.

O export do YOLO deve ser executado com ``--export-python`` apontando para um
Python de ambiente virtual separado, no qual Ultralytics e suas dependências de
exportação já tenham sido instaladas pelo pesquisador.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "mobile"
MANIFEST_PATH = MODEL_DIR / "benchmark_manifest.json"
ASSET_DIR = ROOT / "app_flutter" / "assets" / "mobile_models"
EFFICIENTDET_URL = (
    "https://storage.googleapis.com/mediapipe-models/object_detector/"
    "efficientdet_lite0/int8/latest/efficientdet_lite0.tflite"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tensor_manifest(path: Path) -> tuple[dict | None, list[dict] | None]:
    """Lê tensores quando LiteRT/TensorFlow está disponível; não instala nada."""
    interpreter_type = None
    try:
        from ai_edge_litert.interpreter import Interpreter  # type: ignore

        interpreter_type = Interpreter
    except ImportError:
        try:
            from tensorflow.lite import Interpreter  # type: ignore

            interpreter_type = Interpreter
        except ImportError:
            return None, None
    interpreter = interpreter_type(model_path=str(path))
    interpreter.allocate_tensors()

    def describe(detail: dict) -> dict:
        quantization = detail.get("quantization_parameters", {})
        scales = quantization.get("scales", [])
        zero_points = quantization.get("zero_points", [])
        return {
            "name": detail["name"],
            "shape": [int(value) for value in detail["shape"]],
            "dtype": str(detail["dtype"]),
            "quantization": {
                "scales": [float(value) for value in scales],
                "zero_points": [int(value) for value in zero_points],
            },
        }

    inputs = interpreter.get_input_details()
    outputs = interpreter.get_output_details()
    return describe(inputs[0]), [describe(item) for item in outputs]


def record_artifact(entry: dict, artifact: Path) -> None:
    model_input, outputs = tensor_manifest(artifact)
    entry.update(
        status="prepared" if model_input is not None else "prepared_uninspected",
        sha256=sha256(artifact),
        size_bytes=artifact.stat().st_size,
        input=model_input,
        outputs=outputs,
    )
    if model_input is None:
        entry["inspection_note"] = (
            "Instale ai-edge-litert ou TensorFlow no ambiente de preparação para "
            "registrar os tensores; o arquivo e seu hash foram verificados."
        )


def download_efficientdet(destination: Path) -> None:
    request = urllib.request.Request(
        EFFICIENTDET_URL, headers={"User-Agent": "ARGUS-IC-model-preparation/1"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200:
            raise RuntimeError(f"download respondeu HTTP {response.status}")
        with tempfile.NamedTemporaryFile(delete=False, dir=destination.parent) as tmp:
            shutil.copyfileobj(response, tmp)
            temporary = Path(tmp.name)
    if temporary.stat().st_size < 1024:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("arquivo baixado é pequeno demais para ser um modelo")
    temporary.replace(destination)


def export_yolov8(export_python: Path, checkpoint: Path, destination: Path) -> None:
    if not checkpoint.is_file():
        raise FileNotFoundError(f"checkpoint local não encontrado: {checkpoint}")
    code = (
        "from pathlib import Path; from ultralytics import YOLO; import shutil, sys; "
        "model=YOLO(sys.argv[1]); "
        "result=Path(model.export(format='tflite', imgsz=320, batch=1, "
        "half=False, int8=False, nms=False, device='cpu')); "
        "files=list(result.rglob('*float32*.tflite')) if result.is_dir() else [result]; "
        "assert files, f'export não produziu TFLite FP32 em {result}'; "
        "shutil.copy2(files[0], sys.argv[2])"
    )
    environment = os.environ.copy()
    environment["YOLO_AUTOINSTALL"] = "False"
    subprocess.run(
        [str(export_python), "-c", code, str(checkpoint), str(destination)],
        check=True,
        cwd=ROOT,
        env=environment,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate", choices=("all", "efficientdet", "yolo"), default="all"
    )
    parser.add_argument("--export-python", type=Path)
    parser.add_argument(
        "--yolo-checkpoint", type=Path, default=ROOT / "models" / "yolo" / "yolov8n.pt"
    )
    parser.add_argument("--no-copy-assets", action="store_true")
    args = parser.parse_args()

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    operations = []
    if args.candidate in ("all", "efficientdet"):
        operations.append(
            (
                "efficientdet_lite0",
                MODEL_DIR / "efficientdet_lite0_int8.tflite",
                lambda path: download_efficientdet(path),
            )
        )
    if args.candidate in ("all", "yolo"):
        if args.export_python is None:
            failures.append("yolov8n: informe --export-python de um ambiente separado")
        else:
            operations.append(
                (
                    "yolov8n",
                    MODEL_DIR / "yolov8n_float32_320.tflite",
                    lambda path: export_yolov8(
                        args.export_python.resolve(), args.yolo_checkpoint.resolve(), path
                    ),
                )
            )

    for name, artifact, operation in operations:
        entry = manifest["candidates"][name]
        try:
            operation(artifact)
            record_artifact(entry, artifact)
            if not args.no_copy_assets:
                shutil.copy2(artifact, ASSET_DIR / artifact.name)
        except Exception as error:  # cada candidato falha de forma independente
            entry["status"] = "blocked"
            entry["error"] = f"{type(error).__name__}: {error}"
            failures.append(f"{name}: {error}")

    manifest["generated_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    for failure in failures:
        print(f"BLOQUEADO: {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
