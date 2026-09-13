from app.database import get_connection


def main():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                f.person_group_id AS group_id,
                COUNT(*) AS face_count,
                COUNT(DISTINCT f.photo_id) AS photo_count
            FROM faces f
            WHERE f.person_group_id IS NOT NULL
            GROUP BY f.person_group_id
            ORDER BY f.person_group_id
            """
        ).fetchall()

        print("\n=== PEOPLE GROUPS ===")

        for row in rows:
            print(
                f"group={row['group_id']} "
                f"faces={row['face_count']} "
                f"photos={row['photo_count']}"
            )

        assert len(rows) == 17

        nisha = conn.execute(
            """
            SELECT
                p.name,
                p.person_group_id,
                COUNT(DISTINCT f.photo_id) AS photo_count
            FROM people p
            JOIN faces f
                ON f.person_group_id = p.person_group_id
            WHERE p.name = 'Nisha'
            GROUP BY p.person_group_id
            """
        ).fetchone()

        assert nisha is not None
        assert int(nisha["person_group_id"]) == 1
        assert int(nisha["photo_count"]) == 5

        print("\n=== NISHA ===")
        print(
            f"name={nisha['name']} "
            f"group={nisha['person_group_id']} "
            f"photos={nisha['photo_count']}"
        )

        print("\nALL PEOPLE DATABASE TESTS PASSED")

    finally:
        conn.close()


if __name__ == "__main__":
    main()