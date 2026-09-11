from pathlib import Path
import sqlite3

from database import DATABASE_PATH
from scanner import scan_photos


IMAGE_FOLDER = Path(r"D:\project\PhotoAgent\Images")


disk_photos = scan_photos(str(IMAGE_FOLDER))

connection = sqlite3.connect(DATABASE_PATH)

database_paths = {
    Path(row[0]).resolve()
    for row in connection.execute(
        "SELECT path FROM photos"
    ).fetchall()
}

connection.close()

disk_paths = {
    photo.resolve()
    for photo in disk_photos
}

missing_from_database = disk_paths - database_paths
missing_from_disk = database_paths - disk_paths

print(f"Images on disk: {len(disk_paths)}")
print(f"Photos in database: {len(database_paths)}")

print("\nImages missing from database:")

for path in sorted(missing_from_database):
    print(f"  {path}")

print("\nDatabase entries missing from disk:")

for path in sorted(missing_from_disk):
    print(f"  {path}")