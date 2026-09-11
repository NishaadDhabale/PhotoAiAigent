import sqlite3

import numpy as np

from database import DATABASE_PATH
from face_embeddings import cosine_similarity


def load_faces():
    connection = sqlite3.connect(DATABASE_PATH)

    rows = connection.execute(
        """
        SELECT
            faces.id,
            photos.filename,
            faces.face_index,
            faces.confidence,
            faces.embedding
        FROM faces
        JOIN photos
            ON faces.photo_id = photos.id
        ORDER BY faces.id
        """
    ).fetchall()

    connection.close()

    faces = []

    for row in rows:
        (
            face_id,
            filename,
            face_index,
            confidence,
            embedding_blob,
        ) = row

        embedding = np.frombuffer(
            embedding_blob,
            dtype=np.float32,
        )

        faces.append(
            {
                "id": face_id,
                "filename": filename,
                "face_index": face_index,
                "confidence": confidence,
                "embedding": embedding,
            }
        )

    return faces


def main():
    faces = load_faces()

    print(f"Faces loaded: {len(faces)}")
    print()

    matches = []

    for i in range(len(faces)):
        for j in range(i + 1, len(faces)):
            similarity = cosine_similarity(
                faces[i]["embedding"],
                faces[j]["embedding"],
            )

            matches.append(
                (
                    similarity,
                    faces[i],
                    faces[j],
                )
            )

    matches.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    print("Top 30 face similarities:")
    print()

    for similarity, face_a, face_b in matches[:30]:
        print(
            f"{similarity:.3f} | "
            f"{face_a['filename']} "
            f"(face {face_a['face_index']})"
            f"  <->  "
            f"{face_b['filename']} "
            f"(face {face_b['face_index']})"
        )


if __name__ == "__main__":
    main()