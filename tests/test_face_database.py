from pathlib import Path
import sqlite3

from app.face_detection import detect_faces
from app.face_embeddings import FaceEmbedder
from app.database import create_database, migrate_database, save_photo, save_face, DATABASE_PATH
from app.metadata import get_metadata


PHOTO_PATH = Path(
    r"D:\project\PhotoAgent\Images\IMG_20230722_204708.jpg"
)


create_database()
migrate_database()

print("Reading photo metadata...")
metadata = get_metadata(PHOTO_PATH)

photo_id = save_photo(metadata)

print(f"Photo ID: {photo_id}")

print("Detecting faces...")
detected_faces = detect_faces(PHOTO_PATH)

print(f"Detected faces: {len(detected_faces)}")

embedder = FaceEmbedder()

for index, detected_face in enumerate(detected_faces, start=1):
    embedding = embedder.embed(detected_face)

    save_face(
        photo_id=photo_id,
        face_index=index,
        box=detected_face["box"],
        confidence=detected_face["confidence"],
        embedding=embedding.tobytes(),
    )

print("Faces saved.")

connection = sqlite3.connect(DATABASE_PATH)

rows = connection.execute("""
    SELECT
        id,
        photo_id,
        face_index,
        x,
        y,
        width,
        height,
        confidence,
        length(embedding)
    FROM faces
    WHERE photo_id = ?
""", (photo_id,)).fetchall()

connection.close()

print("\nDatabase faces:")

for row in rows:
    print(row)