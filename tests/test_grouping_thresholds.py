import sqlite3

import numpy as np

from app.database import DATABASE_PATH
from app.person_grouping import cluster_faces


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

        faces.append(
            {
                "id": face_id,
                "filename": filename,
                "face_index": face_index,
                "confidence": confidence,
                "embedding": np.frombuffer(
                    embedding_blob,
                    dtype=np.float32,
                ),
            }
        )

    return faces


def main():
    faces = load_faces()

    print(f"Faces loaded: {len(faces)}")
    print()

    for similarity_threshold in [0.50, 0.55, 0.60, 0.65, 0.70]:
        distance_threshold = 1.0 - similarity_threshold

        groups = cluster_faces(
            faces,
            distance_threshold=distance_threshold,
        )

        sizes = sorted(
            [len(group["faces"]) for group in groups],
            reverse=True,
        )

        print(
            f"Similarity >= {similarity_threshold:.2f} "
            f"→ {len(groups)} groups "
            f"→ sizes: {sizes}"
        )


if __name__ == "__main__":
    main()