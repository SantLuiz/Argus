from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


YOLO_MODELS = {
    "general": "yolov8n.pt",
    "open_vocab_primary": "yoloe-11s-seg.pt",
    "open_vocab_fallback": "yolov8s-world.pt",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa e aquece os modelos locais do ARGUS.")
    parser.add_argument("--models-dir", default="models", help="Diretorio base dos modelos.")
    parser.add_argument("--skip-yolo", action="store_true", help="Nao preparar modelos Ultralytics.")
    parser.add_argument("--skip-midas", action="store_true", help="Nao preparar cache local do MiDaS.")
    args = parser.parse_args()

    repo_root = Path.cwd()
    models_dir = (repo_root / args.models_dir).resolve()
    yolo_dir = models_dir / "yolo"
    torch_dir = models_dir / "torch"
    yolo_dir.mkdir(parents=True, exist_ok=True)
    torch_dir.mkdir(parents=True, exist_ok=True)

    os.environ["TORCH_HOME"] = str(torch_dir)

    if not args.skip_yolo:
        prepare_yolo_models(yolo_dir)

    if not args.skip_midas:
        prepare_midas(torch_dir)

    print("")
    print("Modelos preparados.")
    print(f"ARGUS_YOLO_MODEL_PATH={yolo_dir / YOLO_MODELS['general']}")
    print(f"ARGUS_YOLOE_MODEL_PATH={yolo_dir / YOLO_MODELS['open_vocab_primary']}")
    print(f"ARGUS_YOLO_WORLD_MODEL_PATH={yolo_dir / YOLO_MODELS['open_vocab_fallback']}")
    print(f"TORCH_HOME={torch_dir}")


def prepare_yolo_models(yolo_dir: Path) -> None:
    from ultralytics import YOLO

    original_cwd = Path.cwd()
    try:
        os.chdir(yolo_dir)
        for label, file_name in YOLO_MODELS.items():
            destination = yolo_dir / file_name
            if destination.exists():
                print(f"YOLO {label}: usando {destination}")
                YOLO(str(destination))
                continue

            print(f"YOLO {label}: baixando {file_name}")
            model = YOLO(file_name)
            resolved = resolve_ultralytics_weight(model, yolo_dir, file_name)
            if resolved != destination:
                shutil.copy2(resolved, destination)
            YOLO(str(destination))
            print(f"YOLO {label}: salvo em {destination}")
    finally:
        os.chdir(original_cwd)


def resolve_ultralytics_weight(model: object, yolo_dir: Path, file_name: str) -> Path:
    candidates = [
        yolo_dir / file_name,
        Path(getattr(model, "ckpt_path", "")),
        Path(getattr(model, "model_name", "")),
    ]

    for candidate in candidates:
        if candidate and candidate.exists() and candidate.is_file():
            return candidate.resolve()

    matches = list(yolo_dir.rglob(file_name))
    if matches:
        return matches[0].resolve()

    raise FileNotFoundError(f"Ultralytics nao deixou {file_name} em um caminho conhecido.")


def prepare_midas(torch_dir: Path) -> None:
    import torch

    torch.hub.set_dir(str(torch_dir / "hub"))
    print(f"MiDaS: preparando cache em {torch_dir}")
    model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
    model.eval()
    transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    _ = transforms.small_transform
    print("MiDaS: cache pronto.")


if __name__ == "__main__":
    main()
