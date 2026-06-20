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
    def analyze(self, image, image_name=None):
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
