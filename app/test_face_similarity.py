from pathlib import Path

from face_detection import detect_faces
from face_embeddings import FaceEmbedder, cosine_similarity


PHOTO_FOLDER = Path(
    r"D:\project\PhotoAgent\Images"
)


def get_first_face_embedding(
    photo_path,
    embedder,
):
    detected_faces = detect_faces(photo_path)

    if not detected_faces:
        return None

    return embedder.embed(
        detected_faces[0]
    )


if __name__ == "__main__":

    embedder = FaceEmbedder()

    photos = [
        PHOTO_FOLDER / "IMG_20220124_213235.jpg",
        PHOTO_FOLDER / "IMG_20220124_213300.jpg",
        PHOTO_FOLDER / "IMG_20220411_211053.jpg",
        PHOTO_FOLDER / "IMG_20220411_211223.jpg",
        PHOTO_FOLDER / "IMG_20220831_171451.jpg",
        PHOTO_FOLDER / "IMG_20220831_171511.jpg",
        PHOTO_FOLDER / "IMG_20230722_204708.jpg",
        PHOTO_FOLDER / "Mr Aman Pathan.jpg",
        PHOTO_FOLDER / "nishha.jpg",
        PHOTO_FOLDER / "WhatsApp Image 2023-11-20 at 12.21.16_525163d3.jpg",
    ]

    embeddings = {}

    for photo in photos:

        if not photo.exists():
            print(f"Missing: {photo.name}")
            continue

        print(f"Processing: {photo.name}")

        embedding = get_first_face_embedding(
            photo,
            embedder,
        )

        if embedding is None:
            print("  No face detected.")
            continue

        embeddings[photo.name] = embedding

        print(
            f"  Embedding shape: {embedding.shape}"
        )

    print("\nPairwise similarities\n")

    names = list(embeddings.keys())

    for i in range(len(names)):
        for j in range(i + 1, len(names)):

            name_a = names[i]
            name_b = names[j]

            similarity = cosine_similarity(
                embeddings[name_a],
                embeddings[name_b],
            )

            print(
                f"{similarity:.3f}  "
                f"{name_a}  <->  {name_b}"
            )