from pathlib import Path

from face_detection import detect_faces
from face_embeddings import FaceEmbedder
from database import save_face, delete_photo_faces


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def index_photo_faces(photo_path, photo_id, embedder):
    """
    Detect and store the current face results for one photo.
    """

    detected_faces = detect_faces(photo_path)

    # Remove results from any previous analysis.
    delete_photo_faces(photo_id)

    saved_count = 0

    for face_index, detected_face in enumerate(
        detected_faces,
        start=1,
    ):
        embedding = embedder.embed(detected_face)

        save_face(
            photo_id=photo_id,
            face_index=face_index,
            box=detected_face["box"],
            confidence=detected_face["confidence"],
            embedding=embedding.tobytes(),
        )

        saved_count += 1
    print(
        f"{photo_path.name}: "
        f"saved={saved_count}"
    )
    return saved_count

def index_all_faces(photo_records):
    """
    Index faces for every photo in the database.

    photo_records must contain:
        {
            "id": photo_id,
            "path": photo_path
        }
    """

    embedder = FaceEmbedder()

    total_faces = 0

    for photo in photo_records:
        photo_path = Path(photo["path"])

        if photo_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        print(f"Processing: {photo_path.name}")

        face_count = index_photo_faces(
            photo_path,
            photo["id"],
            embedder,
        )

        total_faces += face_count

        print(f"  Faces stored: {face_count}")

    return total_faces