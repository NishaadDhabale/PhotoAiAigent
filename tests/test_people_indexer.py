import sqlite3

from app.database import DATABASE_PATH
from app.people_indexer import index_all_faces


connection = sqlite3.connect(DATABASE_PATH)

photos = connection.execute("""
    SELECT id, path
    FROM photos
    ORDER BY id
""").fetchall()

connection.close()

photo_records = [
    {
        "id": photo_id,
        "path": path,
    }
    for photo_id, path in photos
]

print(f"Photos to process: {len(photo_records)}")

total_faces = index_all_faces(photo_records)

print(f"\nTotal faces stored: {total_faces}")