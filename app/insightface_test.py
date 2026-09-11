from pathlib import Path

import cv2
from insightface.app import FaceAnalysis


PHOTO_PATH = Path(
    r"D:\project\PhotoAgent\Images\IMG_20230722_204708.jpg"
)

print("Loading InsightFace model...")

app = FaceAnalysis(
    name="buffalo_l",
    providers=[
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    ],
)

app.prepare(
    ctx_id=0,
    det_size=(640, 640),
)

print("Model loaded.")

image = cv2.imread(str(PHOTO_PATH))

if image is None:
    raise RuntimeError(f"Could not read image: {PHOTO_PATH}")

faces = app.get(image)

print(f"Detected faces: {len(faces)}")

for index, face in enumerate(faces, start=1):
    print(
        f"Face {index}: "
        f"bbox={face.bbox.astype(int).tolist()}, "
        f"det_score={face.det_score:.3f}"
    )