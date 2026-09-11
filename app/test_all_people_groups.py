import sqlite3

from database import DATABASE_PATH


def main():
    connection = sqlite3.connect(DATABASE_PATH)

    rows = connection.execute(
        """
        SELECT
            faces.person_group_id,
            photos.filename,
            faces.face_index,
            faces.confidence
        FROM faces
        JOIN photos
            ON photos.id = faces.photo_id
        WHERE faces.person_group_id IS NOT NULL
        ORDER BY
            faces.person_group_id,
            photos.filename,
            faces.face_index
        """
    ).fetchall()

    connection.close()

    current_group = None

    for group_id, filename, face_index, confidence in rows:

        if group_id != current_group:
            current_group = group_id
            print()
            print(f"=== Person Group {group_id} ===")

        print(
            f"  {filename} | "
            f"face {face_index} | "
            f"confidence={confidence:.3f}"
        )


if __name__ == "__main__":
    main()
    