from pathlib import Path

from database import get_all_photos
from image_embeddings import ImageEmbedder
from vector_store import PhotoVectorStore


def index_all_photos():
    """Generate and store embeddings for every photo in SQLite."""

    photos = get_all_photos()

    if not photos:
        print("No photos found in SQLite.")
        return

    print(f"Photos found in SQLite: {len(photos)}")

    embedder = ImageEmbedder()
    store = PhotoVectorStore()

    indexed = 0
    skipped = 0
    failed = 0

    print("\nStarting image indexing...\n")

    for number, photo in enumerate(photos, start=1):

        photo_id = photo["id"]
        filename = photo["filename"]
        path = Path(photo["path"])

        print(
            f"[{number}/{len(photos)}] "
            f"{filename}"
        )

        if not path.exists():
            print("  SKIPPED: file does not exist")
            skipped += 1
            continue

        try:
            embedding = embedder.embed_image(path)

            store.upsert_photo(
                photo_id=photo_id,
                embedding=embedding,
                filename=filename,
                path=str(path),
                date_taken=photo["date_taken"],
                location_name=photo["location_name"],
                camera=photo["camera"],
            )

            indexed += 1

            print("  Indexed successfully")

        except Exception as error:
            failed += 1

            print(
                f"  FAILED: {type(error).__name__}: {error}"
            )

    print("\n" + "=" * 60)
    print("IMAGE INDEXING COMPLETE")
    print("=" * 60)

    print(f"SQLite photos: {len(photos)}")
    print(f"Indexed:       {indexed}")
    print(f"Skipped:       {skipped}")
    print(f"Failed:        {failed}")
    print(f"Chroma count:  {store.count()}")
    print("=" * 60)


if __name__ == "__main__":
    index_all_photos()