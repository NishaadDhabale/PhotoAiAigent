from pathlib import Path
import os
import subprocess

from database import get_connection


def validate_photo(photo_id: int):
    """
    Return the photo path stored in SQLite.

    Raises:
        ValueError: if the photo does not exist in the database
                    or the actual file is missing.
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id, filename, path
            FROM photos
            WHERE id = ?
            """,
            (int(photo_id),),
        ).fetchone()

    finally:
        connection.close()

    if row is None:
        raise ValueError(
            f"Photo {photo_id} was not found."
        )

    photo_path = Path(row[2])

    if not photo_path.is_file():
        raise ValueError(
            f"Photo file does not exist: {photo_path}"
        )

    return {
        "id": int(row[0]),
        "filename": row[1],
        "path": str(photo_path),
    }


def open_photo(photo_id: int):
    """
    Open the actual photo using the Windows default
    application.
    """

    photo = validate_photo(photo_id)

    if os.name != "nt":
        raise RuntimeError(
            "Opening photos directly is currently supported only on Windows."
        )

    os.startfile(photo["path"])

    return photo


def open_photo_location(photo_id: int):
    """
    Open Windows Explorer with the requested photo selected.
    """

    photo = validate_photo(photo_id)

    if os.name != "nt":
        raise RuntimeError(
            "Opening file locations directly is currently supported only on Windows."
        )

    photo_path = str(Path(photo["path"]).resolve())

    subprocess.Popen(
        [
            "explorer.exe",
            "/select,",
            photo_path,
        ]
    )

    return photo