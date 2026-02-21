import os
import cv2
import json
import numpy as np
from skimage import exposure
import torch
from torchvision import transforms

# ===============================
# 1️⃣ Configuration
# ===============================

INPUT_IMAGE_PATH = "FotosExemplos/quarto_1.jpg"          # Raw captured image
PROCESSED_DIR = "processed_images"      # Folder to store treated images
COCO_JSON_PATH = "annotations.json"     # COCO-style annotation file
IMAGE_SIZE = (416, 416)                 # Standard size for CNN input

os.makedirs(PROCESSED_DIR, exist_ok=True)

# ===============================
# 2️⃣ Image Capture & Preprocessing
# ===============================

def preprocess_image(image_path):
    # Load image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image not found or cannot be loaded.")

    # Convert BGR → RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize (standardization for CNN input)
    image_resized = cv2.resize(image_rgb, IMAGE_SIZE)

    # Noise reduction (Gaussian Blur)
    image_blur = cv2.GaussianBlur(image_resized, (5, 5), 0)

    # Contrast enhancement (CLAHE)
    image_lab = cv2.cvtColor(image_blur, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(image_lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l_clahe = clahe.apply(l)

    image_lab = cv2.merge((l_clahe, a, b))
    image_enhanced = cv2.cvtColor(image_lab, cv2.COLOR_LAB2RGB)

    # Normalize (0-1 range)
    image_normalized = image_enhanced / 255.0

    return image_normalized


# ===============================
# 3️⃣ Save Processed Image
# ===============================

def save_processed_image(image_array, filename):
    save_path = os.path.join(PROCESSED_DIR, filename)

    # Convert back to 0-255 for storage
    image_to_save = (image_array * 255).astype(np.uint8)
    cv2.imwrite(save_path, cv2.cvtColor(image_to_save, cv2.COLOR_RGB2BGR))

    return save_path


# ===============================
# 4️⃣ Create COCO-style Annotation Structure
# ===============================

def create_coco_annotation(image_id, file_name, width, height):
    coco_format = {
        "images": [
            {
                "id": image_id,
                "file_name": file_name,
                "width": width,
                "height": height
            }
        ],
        "annotations": [],
        "categories": [
            {"id": 1, "name": "obstacle"},
            {"id": 2, "name": "person"},
            {"id": 3, "name": "door"},
            {"id": 4, "name": "stairs"}
        ]
    }

    with open(COCO_JSON_PATH, "w") as f:
        json.dump(coco_format, f, indent=4)


# ===============================
# 5️⃣ Prepare Tensor for CNN
# ===============================

def prepare_tensor(image_array):
    transform = transforms.Compose([
        transforms.ToTensor()
    ])

    tensor = transform((image_array * 255).astype(np.uint8))
    tensor = tensor.unsqueeze(0)  # Add batch dimension

    return tensor


# ===============================
# 🚀 Pipeline Execution
# ===============================

if __name__ == "__main__":

    processed_image = preprocess_image(INPUT_IMAGE_PATH)

    saved_path = save_processed_image(processed_image, "treated_input.jpg")

    height, width, _ = processed_image.shape
    create_coco_annotation(
        image_id=1,
        file_name="treated_input.jpg",
        width=width,
        height=height
    )

    cnn_tensor = prepare_tensor(processed_image)

    print("✅ Image processed and saved at:", saved_path)
    print("✅ COCO annotation file created:", COCO_JSON_PATH)
    print("✅ Tensor shape ready for CNN:", cnn_tensor.shape)