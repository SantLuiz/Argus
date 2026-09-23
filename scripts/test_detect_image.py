import argparse
import os
import mimetypes
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Envia uma imagem para o endpoint /detect do ARGUS IC.")
    parser.add_argument("image_path", help="Caminho da imagem de teste.")
    parser.add_argument("--url", default=os.getenv("ARGUS_DETECT_URL"), help="URL do endpoint /detect.")
    args = parser.parse_args()

    if not args.url:
        raise SystemExit("Informe --url ou defina ARGUS_DETECT_URL.")

    image_path = Path(args.image_path)
    if not image_path.exists():
        raise SystemExit(f"Imagem nao encontrada: {image_path}")

    content_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"

    with image_path.open("rb") as image_file:
        response = requests.post(
            args.url,
            files={"image": (image_path.name, image_file, content_type)},
            timeout=30,
        )

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
