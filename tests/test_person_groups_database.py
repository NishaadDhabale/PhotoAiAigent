import sqlite3

from app.database import DATABASE_PATH


def main():
    connection = sqlite3.connect(DATABASE_PATH)

    total_faces = connection.execute(
        "SELECT COUNT(*) FROM faces"
    ).fetchone()[0]

    grouped_faces = connection.execute(
        """
        SELECT COUNT(*)
        FROM faces
        WHERE person_group_id IS NOT NULL
        """
    ).fetchone()[0]

    group_rows = connection.execute(
        """
        SELECT
            person_group_id,
            COUNT(*) AS face_count
        FROM faces
        WHERE person_group_id IS NOT NULL
        GROUP BY person_group_id
        ORDER BY person_group_id
        """
    ).fetchall()

    connection.close()

    print(f"Total faces: {total_faces}")
    print(f"Faces assigned to groups: {grouped_faces}")
    print(f"Person groups: {len(group_rows)}")
    print()

    for group_id, face_count in group_rows:
        print(
            f"Group {group_id}: "
            f"{face_count} face(s)"
        )


if __name__ == "__main__":
    main()