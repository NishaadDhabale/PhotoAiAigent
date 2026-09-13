from pathlib import Path

from app.face_detection import detect_faces
from app.face_embeddings import FaceEmbedder
from app.face_embeddings import cosine_similarity


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
            "photo": photo_path.name,
            "face_index": index,
            "confidence": detected_face["confidence"],
            "embedding": embedding,
        })

    return records


if __name__ == "__main__":

    print("Loading embedding model...")

    embedder = FaceEmbedder()

    print("Model loaded.\n")

    all_faces = []

    for photo_path in PHOTO_FOLDER.iterdir():

        if photo_path.suffix.lower() not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            continue

        faces = process_photo(
            photo_path,
            embedder,
        )

        all_faces.extend(faces)

    print(
        f"Total faces: {len(all_faces)}"
    )

    similarities = []

    for i in range(len(all_faces)):

        for j in range(i + 1, len(all_faces)):

            similarity = cosine_similarity(
                all_faces[i]["embedding"],
                all_faces[j]["embedding"],
            )

            similarities.append({
                "similarity": similarity,
                "face_a": all_faces[i],
                "face_b": all_faces[j],
            })

    similarities.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    print("\nTop face matches:\n")

    for match in similarities[:30]:

        face_a = match["face_a"]
        face_b = match["face_b"]

        print(
            f"{match['similarity']:.3f} | "
            f"{face_a['photo']} "
            f"(face {face_a['face_index']}) "
            f"<-> "
            f"{face_b['photo']} "
            f"(face {face_b['face_index']})"
        )