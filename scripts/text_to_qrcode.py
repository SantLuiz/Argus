from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_TEXT = """REFERÊNCIAS

GONZALEZ, Rafael C.; WOODS, Richard E. Processamento digital de imagens. 3. ed. São Paulo: Pearson Prentice Hall, 2010.

OPENCV. OpenCV: Open Source Computer Vision Library. Documentação oficial. Acesso em: 20 jun. 2026.

ULTRALYTICS. Ultralytics YOLO Docs: object detection and computer vision models. Documentação oficial. Acesso em: 20 jun. 2026.

RANFTL, René; BOCHKOVSKIY, Alexey; KOLTUN, Vladlen. Vision Transformers for Dense Prediction. Proceedings of the IEEE/CVF International Conference on Computer Vision, 2021.

XIE, Enze et al. SegFormer: Simple and Efficient Design for Semantic Segmentation with Transformers. Advances in Neural Information Processing Systems, 2021.
"""
DEFAULT_OUTPUT = Path("results") / "qrcode.png"


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import qrcode
    except ImportError as exc:
        raise SystemExit(
            "Dependencia ausente: instale com `pip install qrcode[pil]` "
            "ou atualize o venv com `pip install -r requirements.txt`."
        ) from exc

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=args.box_size,
        border=args.border,
    )
    qr.add_data(args.text)
    qr.make(fit=True)

    image = qr.make_image(fill_color=args.fill_color, back_color=args.back_color)
    image.save(output_path)
    print(f"QR Code salvo em: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera um QR Code a partir de um texto.")
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Texto que sera codificado no QR Code.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Caminho da imagem PNG gerada.")
    parser.add_argument("--box-size", type=int, default=10, help="Tamanho dos blocos do QR Code.")
    parser.add_argument("--border", type=int, default=4, help="Margem em blocos ao redor do QR Code.")
    parser.add_argument("--fill-color", default="black", help="Cor dos blocos.")
    parser.add_argument("--back-color", default="white", help="Cor do fundo.")
    return parser.parse_args()


if __name__ == "__main__":
    main()

