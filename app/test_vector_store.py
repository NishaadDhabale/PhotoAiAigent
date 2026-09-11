from pathlib import Path
import shutil

import numpy as np

from image_embeddings import ImageEmbedder
from vector_store import PhotoVectorStore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_DB = PROJECT_ROOT / "data" / "chroma_test"


def main():
    print("=" * 60)
    print("PhotoAgent Vector Store Tests")
    print("=" * 60)

    # ---------------------------------------------------------
    # Clean test database
    # ---------------------------------------------------------

    if TEST_DB.exists():
        shutil.rmtree(TEST_DB)

    print(f"\nTest database: {TEST_DB}")

    # ---------------------------------------------------------
    # Find images
    # ---------------------------------------------------------

    image_dir = PROJECT_ROOT / "Images"

    images = sorted(
        [
            path
            for path in image_dir.rglob("*")
            if path.suffix.lower()
            in {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
                ".heic",
                ".heif",
            }
        ]
    )

    assert len(images) >= 2, "Need at least two images"

    image_a = images[0]
    image_b = images[1]

    print(f"\nImage A: {image_a.name}")
    print(f"Image B: {image_b.name}")

    # ---------------------------------------------------------
    # Create embeddings
    # ---------------------------------------------------------

    print("\nLoading MobileCLIP2-S0...")

    embedder = ImageEmbedder()

    embedding_a = embedder.embed_image(image_a)
    embedding_b = embedder.embed_image(image_b)

    assert embedding_a.shape == (512,)
    assert embedding_b.shape == (512,)

    print("Embedding dimension: 512")
    print("Embedding generation: OK")

    # ---------------------------------------------------------
    # Create vector store
    # ---------------------------------------------------------

    store = PhotoVectorStore(
        db_path=TEST_DB,
    )

    assert store.count() == 0

    print("Initial vector count: 0")

    # ---------------------------------------------------------
    # Test single insert
    # ---------------------------------------------------------

    store.upsert_photo(
        photo_id=1001,
        embedding=embedding_a,
        filename=image_a.name,
        path=str(image_a),
    )

    assert store.count() == 1

    print("Single upsert: OK")

    # ---------------------------------------------------------
    # Test second insert
    # ---------------------------------------------------------

    store.upsert_photo(
        photo_id=1002,
        embedding=embedding_b,
        filename=image_b.name,
        path=str(image_b),
    )

    assert store.count() == 2

    print("Second upsert: OK")

    # ---------------------------------------------------------
    # Test duplicate upsert
    # ---------------------------------------------------------

    store.upsert_photo(
        photo_id=1001,
        embedding=embedding_a,
        filename=image_a.name,
        path=str(image_a),
    )

    assert store.count() == 2

    print("Duplicate upsert does not create duplicate: OK")

    # ---------------------------------------------------------
    # Test retrieval
    # ---------------------------------------------------------

    stored = store.get_photo(1001)

    assert stored is not None
    assert stored["photo_id"] == 1001
    assert stored["metadata"]["filename"] == image_a.name

    stored_embedding = np.asarray(
        stored["embedding"],
        dtype=np.float32,
    )

    assert stored_embedding.shape == (512,)

    print("Photo retrieval: OK")

    # ---------------------------------------------------------
    # Test similarity search
    # ---------------------------------------------------------

    results = store.search_by_embedding(
        embedding_a,
        n_results=2,
    )

    assert len(results) == 2

    print("\nSimilarity search results:")

    for result in results:
        print(
            f"  photo_id={result['photo_id']} "
            f"similarity={result['similarity']:.4f} "
            f"filename={result['metadata'].get('filename')}"
        )

    # Querying with image A should return image A first.
    assert results[0]["photo_id"] == 1001

    # Its similarity with itself should be approximately 1.
    assert results[0]["similarity"] > 0.99

    print("Similarity search: OK")

    # ---------------------------------------------------------
    # Test persistence
    # ---------------------------------------------------------

    print("\nReopening vector database...")

    store_reopened = PhotoVectorStore(
        db_path=TEST_DB,
    )

    assert store_reopened.count() == 2

    print("Persistence: OK")

    persisted = store_reopened.get_photo(1001)

    assert persisted is not None
    assert persisted["photo_id"] == 1001
    assert persisted["metadata"]["filename"] == image_a.name

    print("Persisted metadata: OK")

    # ---------------------------------------------------------
    # Test search after reopening
    # ---------------------------------------------------------

    reopened_results = store_reopened.search_by_embedding(
        embedding_a,
        n_results=2,
    )

    assert len(reopened_results) == 2
    assert reopened_results[0]["photo_id"] == 1001

    print("Search after reopening: OK")

    # ---------------------------------------------------------
    # Test different query
    # ---------------------------------------------------------

    results_b = store_reopened.search_by_embedding(
        embedding_b,
        n_results=2,
    )

    assert results_b[0]["photo_id"] == 1002
    assert results_b[0]["similarity"] > 0.99

    print("Second image similarity search: OK")

    # ---------------------------------------------------------
    # Final
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("ALL VECTOR STORE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()