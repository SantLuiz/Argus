import numpy as np

from app.vision.midas_estimator import MidasEstimator, MidasRuntime


class FakeTensor:
    def __init__(self, value):
        self.value = np.array(value, dtype=np.float32)

    def to(self, device):
        return self

    def unsqueeze(self, dim):
        return self

    def squeeze(self):
        return self

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.value


class FakeNoGrad:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeFunctional:
    @staticmethod
    def interpolate(prediction, size, mode, align_corners):
        return prediction


class FakeTorch:
    class nn:
        functional = FakeFunctional()

    @staticmethod
    def no_grad():
        return FakeNoGrad()


class FakeModel:
    def __call__(self, input_batch):
        return FakeTensor([[2.0, 4.0], [6.0, 10.0]])


def fake_transform(image):
    assert image[0, 0].tolist() == [30, 20, 10]
    return FakeTensor(image)


def fake_runtime_loader(model_type, device_name):
    assert model_type == "MiDaS_small"
    assert device_name is None
    return MidasRuntime(
        torch=FakeTorch(),
        model=FakeModel(),
        transform=fake_transform,
        device="cpu",
    )


def test_midas_estimator_generates_normalized_depth_map_from_opencv_bgr_image() -> None:
    image = np.array(
        [
            [[10, 20, 30], [40, 50, 60]],
            [[70, 80, 90], [100, 110, 120]],
        ],
        dtype=np.uint8,
    )
    estimator = MidasEstimator(runtime_loader=fake_runtime_loader)

    depth_map = estimator.estimate_depth(image)

    assert depth_map.dtype == np.float32
    assert depth_map.shape == (2, 2)
    assert np.isclose(depth_map.min(), 0.0)
    assert np.isclose(depth_map.max(), 1.0)
