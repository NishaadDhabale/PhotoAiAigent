from pathlib import Path

from database import get_all_photos
from vector_store import PhotoVectorStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_DB = PROJECT_ROOT / "data" / "chroma"


def main():
    print("=" * 60)
    print("PhotoAgent Real Photo Index Test")
    print("=" * 60)

    # ---------------------------------------------------------
    # SQLite
    # ---------------------------------------------------------

    photos = get_all_photos()

    print(f"\nSQLite photos: {len(photos)}")

    assert len(photos) > 0, "SQLite contains no photos"

    # ---------------------------------------------------------
    # Chroma
    # ---------------------------------------------------------

    store = PhotoVectorStore(
        db_path=VECTOR_DB,
    )

    count = store.count()

    print(f"Chroma embeddings: {count}")

    # ---------------------------------------------------------
    # Verify every SQLite photo has an embedding
    # ---------------------------------------------------------

    missing = []

    for photo in photos:
        photo_id = photo["id"]

        stored = store.get_photo(photo_id)

        if stored is None:
            missing.append(photo_id)

    if missing:
        print("\nMissing embeddings:")

        for photo_id in missing:
            print(f"  {photo_id}")

    assert not missing, (
        f"{len(missing)} SQLite photos "
        "do not have embeddings"
    )

    # ---------------------------------------------------------
    # Verify count
    # ---------------------------------------------------------

    assert count == len(photos), (
        f"SQLite has {len(photos)} photos but "
        f"Chroma has {count} embeddings"
    )

    print("\nEvery SQLite photo has a Chroma embedding: OK")

    # ---------------------------------------------------------
    # Verify metadata
    # ---------------------------------------------------------

    checked = photos[0]

    stored = store.get_photo(
        checked["id"]
    )

    assert stored["metadata"]["photo_id"] == checked["id"]

    assert (
        stored["metadata"]["filename"]
        == checked["filename"]
    )

    assert (
        stored["metadata"]["path"]
        == checked["path"]
    )

    print("SQLite → Chroma metadata consistency: OK")

    # ---------------------------------------------------------
    # Verify embedding dimension
    # ---------------------------------------------------------

    embedding = stored["embedding"]

    assert len(embedding) == 512

    print("Embedding dimension: 512")

    # ---------------------------------------------------------
    # Search using a real stored embedding
    # ---------------------------------------------------------

    results = store.search_by_embedding(
        embedding=embedding,
        n_results=5,
    )

    assert len(results) > 0

    print("\nSimilarity search using real photo:")

    for result in results:
        metadata = result["metadata"]

        print(
            f"  photo_id={result['photo_id']} "
            f"similarity={result['similarity']:.4f} "
            f"filename={metadata.get('filename')}"
        )

    # The image should find itself.
    assert results[0]["photo_id"] == checked["id"]

    assert results[0]["similarity"] > 0.99

    print("\nSelf-similarity: OK")

    print("\n" + "=" * 60)
    print("ALL REAL PHOTO INDEX TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()