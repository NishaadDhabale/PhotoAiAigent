from pathlib import Path

import cv2

from face_detection import detect_faces
from face_embeddings import FaceEmbedder


def extract_faces(photo_path: Path, detected_faces, embedder):
    image = cv2.imread(str(photo_path))

    if image is None:
        return []

    face_records = []

    for index, detected_face in enumerate(
        detected_faces,
        start=1,
    ):
        x, y, width, height = detected_face["box"]
        confidence = detected_face["confidence"]

        face = image[
            y:y + height,
            x:x + width
        ]

        if face.size == 0:
            continue

        embedding = embedder.embed(
            detected_face
        )

        face_records.append({
            "photo_path": str(photo_path),
            "face_index": index,
            "box": (x, y, width, height),
            "confidence": confidence,
            "crop": face,
            "embedding": embedding,
        })

    return face_records


if __name__ == "__main__":

    test_photo = Path(
        r"D:\project\PhotoAgent\Images\IMG_20230722_204708.jpg"
    )

    print("Loading embedding model...")

    embedder = FaceEmbedder()

    print("Model loaded.")

    detected_faces = detect_faces(
        test_photo
    )

    print(
        f"Detected faces: {len(detected_faces)}"
    )

    face_records = extract_faces(
        test_photo,
        detected_faces,
        embedder,
    )

    print(
        f"Created face records: "
        f"{len(face_records)}"
    )

    for face_record in face_records:

        print(
            f"Face {face_record['face_index']}: "
            f"confidence="
            f"{face_record['confidence']:.3f}, "
            f"embedding="
            f"{face_record['embedding'].shape}"
        )