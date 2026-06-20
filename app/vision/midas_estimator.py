from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class MidasRuntime:
    torch: Any
    model: Any
    transform: Callable[[np.ndarray], Any]
    device: Any


class MidasEstimator:
    """Estimador de profundidade monocular baseado em MiDaS.

    A saida e um mapa relativo normalizado entre 0 e 1, no tamanho original da
    imagem OpenCV. O valor nao deve ser interpretado como distancia em metros.
    """

    def __init__(
        self,
        model_type: str = "MiDaS_small",
        device: str | None = None,
        runtime_loader: Callable[[str, str | None], MidasRuntime] | None = None,
    ) -> None:
        self.model_type = model_type
        self.device_name = device
        self._runtime_loader = runtime_loader or _load_midas_runtime
        self._runtime: MidasRuntime | None = None

    def estimate_depth(self, image: np.ndarray) -> np.ndarray:
        """Gera um mapa de profundidade monocular relativo para uma imagem OpenCV."""

        rgb_image = _opencv_to_rgb(image)
        runtime = self._load_runtime()

        input_batch = runtime.transform(rgb_image).to(runtime.device)

        with runtime.torch.no_grad():
            prediction = runtime.model(input_batch)
            prediction = runtime.torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=rgb_image.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        depth_map = prediction.detach().cpu().numpy().astype(np.float32)
        return _normalize_depth_map(depth_map)

    def _load_runtime(self) -> MidasRuntime:
        if self._runtime is None:
            self._runtime = self._runtime_loader(self.model_type, self.device_name)
        return self._runtime


def _load_midas_runtime(model_type: str, device_name: str | None) -> MidasRuntime:
    import torch

    device = torch.device(device_name or ("cuda" if torch.cuda.is_available() else "cpu"))
    model = torch.hub.load("intel-isl/MiDaS", model_type)
    model.to(device)
    model.eval()

    transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    transform = transforms.small_transform if model_type == "MiDaS_small" else transforms.dpt_transform

    return MidasRuntime(torch=torch, model=model, transform=transform, device=device)


def _opencv_to_rgb(image: np.ndarray) -> np.ndarray:
    if not isinstance(image, np.ndarray):
        raise TypeError("MidasEstimator espera uma imagem OpenCV numpy.ndarray.")

    if image.ndim == 2:
        return np.repeat(image[:, :, None], 3, axis=2)

    if image.ndim != 3:
        raise ValueError("Imagem OpenCV deve ter 2 ou 3 dimensoes.")

    channels = image.shape[2]
    if channels == 3:
        return image[:, :, ::-1]
    if channels == 4:
        return image[:, :, [2, 1, 0]]

    raise ValueError("Imagem OpenCV deve ter 1, 3 ou 4 canais.")


def _normalize_depth_map(depth_map: np.ndarray) -> np.ndarray:
    min_value = float(np.min(depth_map))
    max_value = float(np.max(depth_map))

    if max_value == min_value:
        return np.zeros_like(depth_map, dtype=np.float32)

    normalized = (depth_map - min_value) / (max_value - min_value)
    return normalized.astype(np.float32)
