from pathlib import Path

from face_detection import detect_faces


IMAGE_PATH = Path(
    r"D:\project\PhotoAgent\Images\IMG_20230722_204708.jpg"
)


for run_number in range(1, 4):
    faces = detect_faces(IMAGE_PATH)

    print(f"\nRun {run_number}")
    print(f"Face count: {len(faces)}")

    for index, face in enumerate(faces, start=1):
        print(
            f"  Face {index}: "
            f"box={face['box']}, "
            f"confidence={face['confidence']:.3f}"
        )