import sqlite3

from app.database import DATABASE_PATH


connection = sqlite3.connect(DATABASE_PATH)

photo_count = connection.execute(
    "SELECT COUNT(*) FROM photos"
).fetchone()[0]

face_count = connection.execute(
    "SELECT COUNT(*) FROM faces"
).fetchone()[0]

print(f"Photos in database: {photo_count}")
print(f"Faces in database: {face_count}")

print("\nPhotos with stored faces:")

photos = connection.execute("""
    SELECT
        p.id,
        p.filename,
        COUNT(f.id) AS face_count
    FROM photos p
    LEFT JOIN faces f
        ON p.id = f.photo_id
    GROUP BY p.id, p.filename
    HAVING COUNT(f.id) > 0
    ORDER BY p.id
""").fetchall()

for photo_id, filename, face_count_for_photo in photos:
    print(
        f"Photo ID {photo_id}: "
        f"{filename} -> {face_count_for_photo} faces"
    )

connection.close()