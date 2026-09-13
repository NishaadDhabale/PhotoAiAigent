from pathlib import Path

from app.face_detection import detect_faces
from app.face_embeddings import FaceEmbedder
from app.person_grouping import cluster_faces


PHOTO_FOLDER = Path(
    r"D:\project\PhotoAgent\Images"
)


def process_photo(photo_path, embedder):
    detected_faces = detect_faces(photo_path)

    records = []

    for index, detected_face in enumerate(
        detected_faces,
        start=1,
    ):
        embedding = embedder.embed(
            detected_face
        )

        records.append({
            "photo_path": str(photo_path),
            "face_index": index,
            "box": detected_face["box"],
            "confidence": detected_face["confidence"],
            "embedding": embedding,
        })

    return records


if __name__ == "__main__":

    embedder = FaceEmbedder()

    all_faces = []

    for photo_path in PHOTO_FOLDER.iterdir():

        if photo_path.suffix.lower() not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            continue

        print(
            f"Processing: {photo_path.name}"
        )

        face_records = process_photo(
            photo_path,
            embedder,
        )

        all_faces.extend(face_records)

        print(
            f"  Faces: {len(face_records)}"
        )

    print()
    print(
        f"Total detected faces: "
        f"{len(all_faces)}"
    )

    groups = cluster_faces(all_faces, distance_threshold=0.40)

    print(
        f"Person groups: {len(groups)}"
    )

    print()

    for group_number, group in enumerate(
        groups,
        start=1,
    ):
        print(
            f"Person Group {group_number}"
        )

        print(
            f"  Faces: "
            f"{len(group['faces'])}"
        )

        for face in group["faces"]:
            print(
                f"    "
                f"{Path(face['photo_path']).name}"
                f" "
                f"(face {face['face_index']}, "
                f"confidence "
                f"{face['confidence']:.3f})"
            )

        print()