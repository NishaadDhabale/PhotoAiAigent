import sqlite3
from database import DATABASE_PATH

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

print("Faces before cleanup:")

count_before = cursor.execute(
    "SELECT COUNT(*) FROM faces"
).fetchone()[0]

print(count_before)

deleted = cursor.execute("""
    DELETE FROM faces
    WHERE photo_id NOT IN (
        SELECT id FROM photos
    )
""").rowcount

connection.commit()

count_after = cursor.execute(
    "SELECT COUNT(*) FROM faces"
).fetchone()[0]

connection.close()

print(f"Deleted orphan faces: {deleted}")
print(f"Faces after cleanup: {count_after}")