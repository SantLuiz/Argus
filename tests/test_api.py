from io import BytesIO

from fastapi.testclient import TestClient
import numpy as np
from PIL import Image

import app.routes.detect as detect_route
from app.main import app
from app.schemas.detection import AudioPayload, DepthInfo, DetectionItem, DetectionResponse, ProcessingTime


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["project"] == "ARGUS IC"


class FakePipeline:
    def analyze(self, image, image_name=None, mode="exploration", target_class=None, use_open_vocab=False):
        return DetectionResponse(
            detections=[
                DetectionItem(
                    class_name="person",
                    confidence=0.90,
                    bbox=[10, 20, 100, 200],
                    zone="centro",
                    depth=DepthInfo(relative_value=0.75, proximity="near", label_pt="proximo"),
                    priority="alta",
                )
            ],
            message="Pessoa ao centro, proxima.",
            audio=AudioPayload(text="Pessoa ao centro, proxima."),
            processing_time_ms=ProcessingTime(detection_ms=1, depth_ms=1, total_ms=2),
            mode=mode,
            use_open_vocab=use_open_vocab,
            image_name=image_name,
            notes=["teste"],
        )


def test_detect_accepts_image_upload(monkeypatch) -> None:
    monkeypatch.setattr(detect_route, "detection_pipeline", FakePipeline())
    monkeypatch.setattr(detect_route, "load_image_cv2", lambda image_bytes: np.zeros((10, 10, 3), dtype=np.uint8))

    image_buffer = BytesIO()
    Image.new("RGB", (320, 240), color=(255, 255, 255)).save(image_buffer, format="PNG")
    image_buffer.seek(0)

    response = client.post(
        "/detect",
        files={"image": ("teste.png", image_buffer, "image/png")},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["detections"]
    assert data["message"]
    assert data["audio"]["language"] == "pt-BR"
    assert data["detections"][0]["depth"]["proximity"] == "near"
    assert data["image_name"] == "teste.png"


def test_detect_accepts_navigation_query_params(monkeypatch) -> None:
    monkeypatch.setattr(detect_route, "detection_pipeline", FakePipeline())
    monkeypatch.setattr(detect_route, "load_image_cv2", lambda image_bytes: np.zeros((10, 10, 3), dtype=np.uint8))

    image_buffer = BytesIO()
    Image.new("RGB", (320, 240), color=(255, 255, 255)).save(image_buffer, format="PNG")
    image_buffer.seek(0)

    response = client.post(
        "/detect?mode=navigation&target_class=door&use_open_vocab=true",
        files={"image": ("teste.png", image_buffer, "image/png")},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["mode"] == "navigation"
    assert data["use_open_vocab"] is True


def test_detect_rejects_navigation_without_target(monkeypatch) -> None:
    monkeypatch.setattr(detect_route, "detection_pipeline", FakePipeline())

    image_buffer = BytesIO()
    Image.new("RGB", (320, 240), color=(255, 255, 255)).save(image_buffer, format="PNG")
    image_buffer.seek(0)

    response = client.post(
        "/detect?mode=navigation",
        files={"image": ("teste.png", image_buffer, "image/png")},
    )

    assert response.status_code == 400
