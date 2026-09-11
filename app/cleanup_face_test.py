import sqlite3

from database import DATABASE_PATH


TEST_PATH = r"D:\project\PhotoAgent\Images\IMG_20230722_204708.jpg"


connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

photo = cursor.execute(
    "SELECT id FROM photos WHERE path = ?",
    (TEST_PATH,),
).fetchone()

if photo is None:
    print("No test photo record found.")
else:
    photo_id = photo[0]

    deleted_faces = cursor.execute(
        "DELETE FROM faces WHERE photo_id = ?",
        (photo_id,),
    ).rowcount

    deleted_photo = cursor.execute(
        "DELETE FROM photos WHERE id = ?",
        (photo_id,),
    ).rowcount

    connection.commit()

    print(f"Deleted faces: {deleted_faces}")
    print(f"Deleted photos: {deleted_photo}")

connection.close()