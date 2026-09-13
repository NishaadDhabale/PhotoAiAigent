from pathlib import Path
from app.scanner import scan_photos
from app.face_detection import detect_faces


IMAGE_FOLDER = Path(r"D:\project\PhotoAgent\Images")


def main():
    photos = scan_photos(IMAGE_FOLDER)

    total_faces = 0

    print(f"Images found: {len(photos)}")
    print()

    for photo_path in photos:
        try:
            faces = detect_faces(photo_path)
            face_count = len(faces)
            total_faces += face_count

            print(f"{photo_path.name}: {face_count}")

        except Exception as error:
            print(f"{photo_path.name}: ERROR - {error}")

    print()
    print(f"Total faces detected: {total_faces}")


if __name__ == "__main__":
    main()