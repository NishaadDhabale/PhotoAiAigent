from app.database import get_connection


def main():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            filename,
            latitude,
            longitude,
            location_name,
            location_source
        FROM photos
        WHERE location_name IS NOT NULL
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    print(f"Photos with locations: {len(rows)}")

    for row in rows:
        (
            photo_id,
            filename,
            latitude,
            longitude,
            location_name,
            location_source,
        ) = row

        print(
            f"{photo_id}: {filename} | "
            f"{latitude}, {longitude} | "
            f"{location_name} | "
            f"{location_source}"
        )


if __name__ == "__main__":
    main()
    