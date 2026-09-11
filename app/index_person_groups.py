import sqlite3

import numpy as np

from database import DATABASE_PATH, update_face_group
from person_grouping import cluster_faces


DISTANCE_THRESHOLD = 0.40


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

    groups = cluster_faces(
        faces,
        distance_threshold=DISTANCE_THRESHOLD,
    )

    print(f"Person groups found: {len(groups)}")
    print()

    for group_number, group in enumerate(
        groups,
        start=1,
    ):
        print(
            f"Person Group {group_number}: "
            f"{len(group['faces'])} face(s)"
        )

        for face in group["faces"]:
            update_face_group(
                face["id"],
                group_number,
            )

            print(
                f"  {face['filename']} "
                f"(face {face['face_index']})"
            )

        print()

    print("Person groups saved to database.")


if __name__ == "__main__":
    main()