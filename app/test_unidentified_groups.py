from database import get_unidentified_groups


def main():
    groups = get_unidentified_groups()

    print(f"Unidentified groups: {len(groups)}")

    for group_id, face_count in groups:
        print(
            f"Group {group_id}: "
            f"{face_count} face(s)"
        )


if __name__ == "__main__":
    main()


def get_unidentified_group_representatives():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            faces.person_group_id,
            faces.id AS face_id,
            photos.id AS photo_id,
            photos.filename,
            photos.path,
            faces.face_index,
            faces.confidence
        FROM faces
        JOIN photos
            ON photos.id = faces.photo_id
        LEFT JOIN people
            ON people.person_group_id = faces.person_group_id
        WHERE people.id IS NULL
        GROUP BY faces.person_group_id
        ORDER BY faces.person_group_id
        """
    ).fetchall()

    connection.close()

    return rows