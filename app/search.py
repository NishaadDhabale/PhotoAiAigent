from database import get_connection


def search_photos(
    person=None,
    year=None,
    start_date=None,
    end_date=None,
    location=None,
    camera=None,
    filename=None,
):
    """
    Search photos using any combination of structured filters.

    All filters are optional.
    """

    connection = get_connection()

    query = """
        SELECT DISTINCT
            photos.id,
            photos.filename,
            photos.path,
            photos.date_taken,
            photos.location_name,
            photos.camera
        FROM photos
    """

    joins = []
    conditions = []
    parameters = []

    # Person filter
    if person is not None:
        joins.append(
            """
            JOIN faces
                ON photos.id = faces.photo_id
            JOIN people
                ON people.person_group_id = faces.person_group_id
            """
        )

        conditions.append("people.name = ?")
        parameters.append(person.strip())

    # Year filter
    if year is not None:
        conditions.append(
            "photos.date_taken LIKE ?"
        )
        parameters.append(
            f"{int(year):04d}:%"
        )

    # Start date filter
    if start_date is not None:
        conditions.append(
            "photos.date_taken >= ?"
        )
        parameters.append(start_date)

    # End date filter
    if end_date is not None:
        conditions.append(
            "photos.date_taken <= ?"
        )
        parameters.append(end_date)

    # Location filter
    if location is not None:
        conditions.append(
            "photos.location_name LIKE ?"
        )
        parameters.append(
            f"%{location.strip()}%"
        )

    # Camera filter
    if camera is not None:
        conditions.append(
            "photos.camera LIKE ?"
        )
        parameters.append(
            f"%{camera.strip()}%"
        )

    # Filename filter
    if filename is not None:
        conditions.append(
            "photos.filename LIKE ?"
        )
        parameters.append(
            f"%{filename.strip()}%"
        )

    if joins:
        query += "\n".join(joins)

    if conditions:
        query += (
            "\nWHERE "
            + " AND ".join(conditions)
        )

    query += """
        ORDER BY
            photos.date_taken IS NULL,
            photos.date_taken
    """

    rows = connection.execute(
        query,
        parameters,
    ).fetchall()

    connection.close()

    return [
        {
            "photo_id": photo_id,
            "filename": filename,
            "path": path,
            "date_taken": date_taken,
            "location_name": location_name,
            "camera": camera,
        }
        for (
            photo_id,
            filename,
            path,
            date_taken,
            location_name,
            camera,
        ) in rows
    ]