import os
import cv2
import json
import numpy as np
from ultralytics import YOLO

# ===============================
# 1️⃣ Configuration
# ===============================

INPUT_IMAGE_PATH = "processed_images/Q1.jpg"
OUTPUT_DIR = "yolo_output"
COCO_OUTPUT_PATH = "yolo_coco_annotations.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load pretrained YOLOv8 model
model = YOLO("yolov8n.pt")  # lightweight version (good for real-time)

# ===============================
# 2️⃣ Run YOLO Detection
# ===============================

def run_yolo_detection(image_path):
    results = model(image_path)

    detections = []
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()

        for box, score, cls in zip(boxes, scores, classes):
            x1, y1, x2, y2 = box
            class_id = int(cls)
            confidence = float(score)

            detections.append({
                "bbox": [float(x1), float(y1), float(x2 - x1), float(y2 - y1)],
                "category_id": class_id,
                "confidence": confidence
            })

            # Draw bounding box
            cv2.rectangle(
                image,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (0, 255, 0),
                2
            )

            cv2.putText(
                image,
                f"{model.names[class_id]} {confidence:.2f}",
                (int(x1), int(y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    return image, detections, width, height


# ===============================
# 3️⃣ Save Annotated Image
# ===============================

def save_annotated_image(image):
    output_path = os.path.join(OUTPUT_DIR, "detected.jpg")
    cv2.imwrite(output_path, image)
    return output_path


# ===============================
# 4️⃣ Export COCO-style JSON
# ===============================

def save_coco_format(detections, width, height):

    coco_structure = {
        "images": [{
            "id": 1,
            "file_name": "detected.jpg",
            "width": width,
            "height": height
        }],
        "annotations": [],
        "categories": []
    }

    # Add category mapping
    for class_id, name in model.names.items():
        coco_structure["categories"].append({
            "id": class_id,
            "name": name
        })

    # Add annotations
    for idx, det in enumerate(detections):
        coco_structure["annotations"].append({
            "id": idx,
            "image_id": 1,
            "category_id": det["category_id"],
            "bbox": det["bbox"],
            "area": det["bbox"][2] * det["bbox"][3],
            "iscrowd": 0,
            "confidence": det["confidence"]
        })

    with open(COCO_OUTPUT_PATH, "w") as f:
        json.dump(coco_structure, f, indent=4)


# ===============================
# 🚀 Execute Pipeline
# ===============================

if __name__ == "__main__":

    annotated_img, detections, w, h = run_yolo_detection(INPUT_IMAGE_PATH)

    saved_img_path = save_annotated_image(annotated_img)

    save_coco_format(detections, w, h)

    print("✅ YOLO detection completed")
    print("✅ Annotated image saved at:", saved_img_path)
    print("✅ COCO-format detection file saved at:", COCO_OUTPUT_PATH)