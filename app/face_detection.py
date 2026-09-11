import os
from pathlib import Path

import torch

torch_lib_path = os.path.join(torch.__path__[0], "lib")
os.add_dll_directory(torch_lib_path)

import onnxruntime as ort
import cv2
from insightface.app import FaceAnalysis

ort.preload_dlls(directory=torch_lib_path)

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=[
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    ],
)

face_app.prepare(
    ctx_id=0,
    det_size=(640, 640),
)

def detect_faces(photo_path: Path):
    image = cv2.imread(str(photo_path))

    if image is None:
        return []

    image_height, image_width = image.shape[:2]

    faces = face_app.get(image)

    face_records = []

    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)

        # Clip the bounding box to the actual image boundaries.
        x1 = max(0, min(x1, image_width))
        y1 = max(0, min(y1, image_height))
        x2 = max(0, min(x2, image_width))
        y2 = max(0, min(y2, image_height))

        width = x2 - x1
        height = y2 - y1

        # Ignore invalid boxes.
        if width <= 0 or height <= 0:
            continue

        face_records.append({
            "box": (x1, y1, width, height),
            "confidence": float(face.det_score),
            "embedding": face.embedding,
        })

    return face_records

def analyze_photo(photo_path: Path):
    faces = detect_faces(photo_path)

    return {
        "photo_path": str(photo_path),
        "face_count": len(faces),
        "faces": faces,
    }


if __name__ == "__main__":
    test_folder = Path(
        r"D:\project\PhotoAgent\Images"
    )

    for photo in test_folder.iterdir():

        if photo.suffix.lower() not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            continue

        result = analyze_photo(photo)

        print(
            f"{photo.name}: "
            f"{result['face_count']} face(s)"
        )

        for face in result["faces"]:
            print(
                f"    Box: {face['box']}, "
                f"Confidence: {face['confidence']:.3f}"
            )