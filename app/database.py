import sqlite3
from pathlib import Path


DATABASE_PATH = Path(r"D:\project\PhotoAgent\data\photos.db")

def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)

    # Always enforce foreign keys.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection

def create_database():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            size_bytes INTEGER,
            width INTEGER,
            height INTEGER,
            date_taken TEXT,
            camera TEXT,
            latitude REAL,
            longitude REAL,
            location_name TEXT,
            location_source TEXT,
            location_confidence REAL
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        photo_id INTEGER NOT NULL,
        face_index INTEGER NOT NULL,
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        width INTEGER NOT NULL,
        height INTEGER NOT NULL,
        confidence REAL,
        embedding BLOB,
        person_group_id INTEGER,
        FOREIGN KEY (photo_id)
            REFERENCES photos(id)
            ON DELETE CASCADE,
        UNIQUE (photo_id, face_index)
    )
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        person_group_id INTEGER NOT NULL UNIQUE
    )
""")

    connection.commit()
    connection.close()


def migrate_database():
    connection = get_connection()
    cursor = connection.cursor()

    columns = cursor.execute(
        "PRAGMA table_info(faces)"
    ).fetchall()

    column_names = {column[1] for column in columns}

    if "confidence" not in column_names:
        cursor.execute(
            "ALTER TABLE faces ADD COLUMN confidence REAL"
        )

    foreign_keys = cursor.execute(
        "PRAGMA foreign_key_list(faces)"
    ).fetchall()

    delete_action = foreign_keys[0][6] if foreign_keys else None

    unique_indexes = cursor.execute(
        "PRAGMA index_list(faces)"
    ).fetchall()

    has_face_unique_constraint = False

    for index in unique_indexes:
        index_name = index[1]
        is_unique = index[2]

        if is_unique:
            index_columns = cursor.execute(
                f'PRAGMA index_info("{index_name}")'
            ).fetchall()

            indexed_columns = [
                column[2]
                for column in index_columns
            ]

            if indexed_columns == ["photo_id", "face_index"]:
                has_face_unique_constraint = True
                break

    needs_rebuild = (
        delete_action != "CASCADE"
        or not has_face_unique_constraint
    )

    if needs_rebuild:
        cursor.execute("""
            CREATE TABLE faces_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                photo_id INTEGER NOT NULL,
                face_index INTEGER NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                confidence REAL,
                embedding BLOB,
                person_group_id INTEGER,
                FOREIGN KEY (photo_id)
                    REFERENCES photos(id)
                    ON DELETE CASCADE,
                UNIQUE (photo_id, face_index)
            )
        """)

        cursor.execute("""
            INSERT INTO faces_new (
                id,
                photo_id,
                face_index,
                x,
                y,
                width,
                height,
                confidence,
                embedding,
                person_group_id
            )
            SELECT
                id,
                photo_id,
                face_index,
                x,
                y,
                width,
                height,
                confidence,
                embedding,
                person_group_id
            FROM faces
        """)

        cursor.execute("DROP TABLE faces")
        cursor.execute("ALTER TABLE faces_new RENAME TO faces")

    connection.commit()
    connection.close()

def save_photo(metadata, location=None):
    connection = get_connection()
    cursor = connection.cursor()

    gps = metadata["gps"]

    latitude = None
    longitude = None

    if gps:
        latitude = gps["latitude"]
        longitude = gps["longitude"]

    cursor.execute(
        """
        INSERT INTO photos (
            filename,
            path,
            size_bytes,
            width,
            height,
            date_taken,
            camera,
            latitude,
            longitude,
            location_name,
            location_source,
            location_confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            filename = excluded.filename,
            size_bytes = excluded.size_bytes,
            width = excluded.width,
            height = excluded.height,
            date_taken = excluded.date_taken,
            camera = excluded.camera,
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            location_name = excluded.location_name,
            location_source = excluded.location_source,
            location_confidence = excluded.location_confidence
        """,
        (
            metadata["filename"],
            metadata["path"],
            metadata["size_bytes"],
            metadata["width"],
            metadata["height"],
            metadata["date_taken"],
            metadata["camera"],
            latitude,
            longitude,
            location["city"] if location else None,
            location["source"] if location else None,
            location["confidence"] if location else None,
        ),
    )

    connection.commit()

    photo_id = cursor.execute(
        "SELECT id FROM photos WHERE path = ?",
        (metadata["path"],),
    ).fetchone()[0]

    connection.close()

    return photo_id

def save_face(
    photo_id,
    face_index,
    box,
    confidence,
    embedding=None,
    person_group_id=None,
):
    x, y, width, height = map(int, box)

    connection = get_connection()
    cursor = connection.cursor()

    existing = cursor.execute(
        """
        SELECT id
        FROM faces
        WHERE photo_id = ? AND face_index = ?
        """,
        (int(photo_id), int(face_index)),
    ).fetchone()

    if existing:
        cursor.execute(
            """
            UPDATE faces
            SET
                x = ?,
                y = ?,
                width = ?,
                height = ?,
                confidence = ?,
                embedding = ?,
                person_group_id = ?
            WHERE id = ?
            """,
            (
                x,
                y,
                width,
                height,
                float(confidence),
                embedding,
                person_group_id,
                existing[0],
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO faces (
                photo_id,
                face_index,
                x,
                y,
                width,
                height,
                confidence,
                embedding,
                person_group_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(photo_id),
                int(face_index),
                x,
                y,
                width,
                height,
                float(confidence),
                embedding,
                person_group_id,
            ),
        )

    connection.commit()
    connection.close()

def delete_photo_faces(photo_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM faces WHERE photo_id = ?",
        (int(photo_id),)
    )

    connection.commit()
    connection.close()



def update_face_group(face_id, person_group_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE faces
        SET person_group_id = ?
        WHERE id = ?
        """,
        (
            int(person_group_id),
            int(face_id),
        ),
    )

    connection.commit()
    connection.close()


def get_photos_by_person_group(person_group_id):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT DISTINCT
            photos.id,
            photos.filename,
            photos.path
        FROM photos
        JOIN faces
            ON photos.id = faces.photo_id
        WHERE faces.person_group_id = ?
        ORDER BY photos.date_taken
        """,
        (int(person_group_id),),
    ).fetchall()

    connection.close()

    return rows


def create_person(person_group_id, name=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO people (
            name,
            person_group_id
        )
        VALUES (?, ?)
        """,
        (
            name,
            int(person_group_id),
        ),
    )

    connection.commit()

    person_id = cursor.lastrowid

    connection.close()

    return person_id


def get_person_by_group(person_group_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT id, name, person_group_id
        FROM people
        WHERE person_group_id = ?
        """,
        (int(person_group_id),),
    ).fetchone()

    connection.close()

    return row


def update_person_name(person_id, name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE people
        SET name = ?
        WHERE id = ?
        """,
        (
            name,
            int(person_id),
        ),
    )

    connection.commit()

    updated = cursor.rowcount

    connection.close()

    return updated


def get_photos_by_person_name(name):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT DISTINCT
            photos.id,
            photos.filename,
            photos.path
        FROM people
        JOIN faces
            ON people.person_group_id = faces.person_group_id
        JOIN photos
            ON photos.id = faces.photo_id
        WHERE people.name = ?
        ORDER BY photos.date_taken
        """,
        (name,),
    ).fetchall()

    connection.close()

    return rows


def get_people():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            name,
            person_group_id
        FROM people
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return rows


def get_unidentified_groups():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            faces.person_group_id,
            COUNT(*) AS face_count
        FROM faces
        LEFT JOIN people
            ON people.person_group_id = faces.person_group_id
        WHERE people.id IS NULL
        GROUP BY faces.person_group_id
        ORDER BY faces.person_group_id
        """
    ).fetchall()

    connection.close()

    return rows

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
          AND faces.id = (
              SELECT f2.id
              FROM faces AS f2
              WHERE f2.person_group_id = faces.person_group_id
              ORDER BY f2.confidence DESC, f2.id ASC
              LIMIT 1
          )
        ORDER BY faces.person_group_id
        """
    ).fetchall()

    connection.close()

    return rows


def discover_people():
    connection = get_connection()

    known_people = connection.execute(
        """
        SELECT
            id,
            name,
            person_group_id
        FROM people
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    unidentified_groups = get_unidentified_group_representatives()

    return {
        "known_people": known_people,
        "unidentified_groups": unidentified_groups,
    }


def delete_person(person_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM people
        WHERE id = ?
        """,
        (int(person_id),),
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted

def person_group_exists(person_group_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT 1
        FROM faces
        WHERE person_group_id = ?
        LIMIT 1
        """,
        (int(person_group_id),),
    ).fetchone()

    connection.close()

    return row is not None


def get_person(person_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            id,
            name,
            person_group_id
        FROM people
        WHERE id = ?
        """,
        (int(person_id),),
    ).fetchone()

    connection.close()

    return row

def get_photos_by_person_name_and_year(name, year):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT DISTINCT
            photos.id,
            photos.filename,
            photos.path
        FROM people
        JOIN faces
            ON people.person_group_id = faces.person_group_id
        JOIN photos
            ON photos.id = faces.photo_id
        WHERE people.name = ?
          AND photos.date_taken LIKE ?
        ORDER BY photos.date_taken
        """,
        (
            name,
            f"{int(year):04d}:%",
        ),
    ).fetchall()

    connection.close()

    return rows


def get_photos_by_person_name_and_date_range(
    name,
    start_date,
    end_date,
):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT DISTINCT
            photos.id,
            photos.filename,
            photos.path
        FROM people
        JOIN faces
            ON people.person_group_id = faces.person_group_id
        JOIN photos
            ON photos.id = faces.photo_id
        WHERE people.name = ?
          AND photos.date_taken >= ?
          AND photos.date_taken <= ?
        ORDER BY photos.date_taken
        """,
        (
            name,
            start_date,
            end_date,
        ),
    ).fetchall()

    connection.close()

    return rows


def get_all_photos():
    """Return all photos stored in the SQLite database."""

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            filename,
            path,
            date_taken,
            camera,
            location_name
        FROM photos
        ORDER BY id
    """)

    photos = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return photos

def get_photos_by_ids(photo_ids):
    """
    Return photos whose IDs are in photo_ids.

    The returned list preserves the order supplied by photo_ids.
    """

    if not photo_ids:
        return []

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    placeholders = ",".join(
        "?" for _ in photo_ids
    )

    cursor = connection.cursor()

    cursor.execute(
        f"""
        SELECT
            id,
            filename,
            path,
            date_taken,
            camera,
            location_name
        FROM photos
        WHERE id IN ({placeholders})
        """,
        [int(photo_id) for photo_id in photo_ids],
    )

    rows = {
        row["id"]: dict(row)
        for row in cursor.fetchall()
    }

    connection.close()

    return [
        rows[int(photo_id)]
        for photo_id in photo_ids
        if int(photo_id) in rows
    ]