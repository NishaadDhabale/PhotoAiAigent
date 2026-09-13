from pathlib import Path

from app.face_detection import detect_faces

PHOTO_FOLDER = Path(r"D:\project\PhotoAgent\Images")


if __name__ == "__main__":
    total_faces = 0

    for photo_path in sorted(PHOTO_FOLDER.iterdir()):
        if photo_path.suffix.lower() not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            continue

        faces = detect_faces(photo_path)

        if not faces:
            continue

        print(f"\n{photo_path.name}")

        for index, face in enumerate(faces, start=1):
            print(
                f"  Face {index}: "
                f"confidence={face['confidence']:.3f}, "
                f"box={face['box']}"
            )

        total_faces += len(faces)

    print(f"\nTotal faces: {total_faces}")