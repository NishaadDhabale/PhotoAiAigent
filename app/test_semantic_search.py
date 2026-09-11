from semantic_search import SemanticPhotoSearch


def print_results(title, results):
    print()
    print("-" * 70)
    print(title)
    print("-" * 70)

    if not results:
        print("No results")
        return

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print(
            f"{index:2}. "
            f"similarity={result['similarity']:.4f} "
            f"photo_id={result['photo_id']} "
            f"filename={metadata.get('filename')}"
        )


def main():
    print("=" * 70)
    print("PhotoAgent Semantic Search Test")
    print("=" * 70)

    searcher = SemanticPhotoSearch()

    # ---------------------------------------------------------
    # TEST 1: Vector database contains real photos
    # ---------------------------------------------------------

    count = searcher.store.count()

    print(f"\nIndexed photos: {count}")

    assert count == 27, (
        f"Expected 27 indexed photos, found {count}"
    )

    print("Indexed photo count: OK")

    # ---------------------------------------------------------
    # TEST 2: Basic semantic search
    # ---------------------------------------------------------

    query = "a photo of a person"

    results = searcher.search(
        query,
        n_results=5,
    )

    print_results(
        f'Test query: "{query}"',
        results,
    )

    assert len(results) == 5, (
        f"Expected 5 results, got {len(results)}"
    )

    print("Basic semantic search: OK")

    # ---------------------------------------------------------
    # TEST 3: Query returns valid result structure
    # ---------------------------------------------------------

    first = results[0]

    assert "photo_id" in first
    assert "similarity" in first
    assert "distance" in first
    assert "metadata" in first

    assert isinstance(first["photo_id"], int)
    assert isinstance(first["similarity"], float)
    assert isinstance(first["distance"], float)
    assert isinstance(first["metadata"], dict)

    print("Result structure: OK")

    # ---------------------------------------------------------
    # TEST 4: Similarities are ordered
    # ---------------------------------------------------------

    similarities = [
        result["similarity"]
        for result in results
    ]

    assert similarities == sorted(
        similarities,
        reverse=True,
    )

    print("Similarity ranking order: OK")

    # ---------------------------------------------------------
    # TEST 5: Different natural-language queries
    # ---------------------------------------------------------

    test_queries = [
        "people",
        "a person",
        "a group of people",
        "an outdoor scene",
        "a family photo",
    ]

    print()
    print("=" * 70)
    print("Semantic Query Exploration")
    print("=" * 70)

    for query in test_queries:
        results = searcher.search(
            query,
            n_results=3,
        )

        print_results(
            f'Query: "{query}"',
            results,
        )

        assert len(results) == 3

        similarities = [
            result["similarity"]
            for result in results
        ]

        assert similarities == sorted(
            similarities,
            reverse=True,
        )

    print("\nMultiple semantic queries: OK")

    # ---------------------------------------------------------
    # TEST 6: Empty query validation
    # ---------------------------------------------------------

    try:
        searcher.search("")
        raise AssertionError(
            "Empty query should raise ValueError"
        )
    except ValueError:
        pass

    print("Empty query validation: OK")

    # ---------------------------------------------------------
    # TEST 7: Whitespace query validation
    # ---------------------------------------------------------

    try:
        searcher.search("   ")
        raise AssertionError(
            "Whitespace query should raise ValueError"
        )
    except ValueError:
        pass

    print("Whitespace query validation: OK")

    # ---------------------------------------------------------
    # TEST 8: Non-string query validation
    # ---------------------------------------------------------

    try:
        searcher.search(None)
        raise AssertionError(
            "Non-string query should raise TypeError"
        )
    except TypeError:
        pass

    print("Non-string query validation: OK")

    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("ALL SEMANTIC SEARCH TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
    