from image_embeddings import ImageEmbedder
from vector_store import PhotoVectorStore


class SemanticPhotoSearch:
    """
    Natural-language semantic search over indexed photos.

    Flow:
        text query
            ↓
        MobileCLIP2 text embedding
            ↓
        Chroma similarity search
            ↓
        SQLite-compatible result structure
    """

    def __init__(self):
        self.embedder = ImageEmbedder()
        self.store = PhotoVectorStore()

    def search(self, query, n_results=10):
        """
        Search indexed photos using a natural-language query.

        Returns a consistent result structure:

            {
                "photo_id": int,
                "filename": str,
                "path": str,
                "date_taken": str | None,
                "location_name": str | None,
                "camera": str | None,
                "similarity": float,
                "distance": float
            }
        """

        if not isinstance(query, str):
            raise TypeError("Query must be a string")

        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty")

        if n_results <= 0:
            raise ValueError(
                "n_results must be greater than zero"
            )

        if self.store.count() == 0:
            return []

        query_embedding = self.embedder.embed_text(query)

        raw_results = self.store.search_by_embedding(
            query_embedding,
            n_results=n_results,
        )

        results = []

        for result in raw_results:

            metadata = result.get("metadata", {})

            results.append(
                {
                    "photo_id": result["photo_id"],
                    "filename": metadata.get("filename"),
                    "path": metadata.get("path"),
                    "date_taken": metadata.get("date_taken"),
                    "location_name": metadata.get(
                        "location_name"
                    ),
                    "camera": metadata.get("camera"),
                    "similarity": result["similarity"],
                    "distance": result["distance"],
                }
            )

        return results


def semantic_search(query, n_results=10):
    """
    Convenience function for one-off semantic searches.
    """

    searcher = SemanticPhotoSearch()

    return searcher.search(
        query=query,
        n_results=n_results,
    )


if __name__ == "__main__":

    searcher = SemanticPhotoSearch()

    print("=" * 60)
    print("PhotoAgent Semantic Search")
    print("=" * 60)

    query = input("\nEnter a search query: ").strip()

    if not query:
        print("Query cannot be empty.")
        raise SystemExit(1)

    results = searcher.search(
        query,
        n_results=10,
    )

    print()
    print(f"Query: {query}")
    print(f"Results: {len(results)}")
    print()

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"{index:2}. "
            f"similarity={result['similarity']:.4f} "
            f"photo_id={result['photo_id']} "
            f"filename={result['filename']}"
        )

    print()
    print("=" * 60)