from hybrid_search import HybridPhotoSearch


def print_results(title, results):
    print()
    print("-" * 75)
    print(title)
    print("-" * 75)

    if not results:
        print("No results")
        return

    for index, result in enumerate(results, start=1):

        similarity = result["similarity"]

        if similarity is None:
            similarity_text = "N/A"
        else:
            similarity_text = f"{similarity:.4f}"

        print(
            f"{index:2}. "
            f"similarity={similarity_text} "
            f"photo_id={result['photo_id']} "
            f"filename={result['filename']} "
            f"date={result['date_taken']}"
        )


def main():

    print("=" * 75)
    print("PhotoAgent Hybrid Search Test")
    print("=" * 75)

    searcher = HybridPhotoSearch()

    # =========================================================
    # TEST 1
    # =========================================================

    print("\nTest 1: Semantic search")

    results = searcher.search(
        semantic_query="a photo of a person",
        n_results=5,
    )

    print_results(
        'Semantic: "a photo of a person"',
        results,
    )

    assert len(results) == 5

    for result in results:
        assert result["photo_id"] > 0
        assert result["filename"]
        assert result["path"]
        assert result["similarity"] is not None

    print("Semantic search through hybrid layer: OK")

    # =========================================================
    # TEST 2
    # =========================================================

    print("\nTest 2: Structured year filter")

    results = searcher.search(
        year=2022,
        n_results=20,
    )

    print_results(
        "Structured: year=2022",
        results,
    )

    assert len(results) > 0

    for result in results:

        assert result["date_taken"] is not None
        assert result["date_taken"].startswith("2022")

        assert result["similarity"] is None

    print("Year filtering: OK")

    # =========================================================
    # TEST 3
    # =========================================================

    print("\nTest 3: Person + year")

    results = searcher.search(
        person="Nisha",
        year=2022,
        n_results=20,
    )

    print_results(
        "Structured: person=Nisha + year=2022",
        results,
    )

    assert len(results) == 2

    for result in results:
        assert result["date_taken"].startswith("2022")
        assert result["similarity"] is None

    print("Person + year filtering: OK")

    # =========================================================
    # TEST 4
    # =========================================================

    print("\nTest 4: Semantic + year")

    results = searcher.search(
        semantic_query="a photo of a person",
        year=2022,
        n_results=10,
    )

    print_results(
        'Hybrid: "a photo of a person" + year=2022',
        results,
    )

    for result in results:

        assert result["date_taken"] is not None
        assert result["date_taken"].startswith("2022")
        assert result["similarity"] is not None

    print("Semantic + year filtering: OK")

    # =========================================================
    # TEST 5
    # =========================================================

    print("\nTest 5: Semantic + person")

    results = searcher.search(
        semantic_query="a photo of a person",
        person="Nisha",
        n_results=10,
    )

    print_results(
        'Hybrid: "a photo of a person" + person=Nisha',
        results,
    )

    assert len(results) > 0

    for result in results:
        assert result["similarity"] is not None

    print("Semantic + person filtering: OK")

    # =========================================================
    # TEST 6
    # =========================================================

    print("\nTest 6: Semantic + person + year")

    results = searcher.search(
        semantic_query="a photo of a person",
        person="Nisha",
        year=2022,
        n_results=10,
    )

    print_results(
        'Hybrid: semantic + Nisha + 2022',
        results,
    )

    assert len(results) == 2

    for result in results:
        assert result["date_taken"].startswith("2022")
        assert result["similarity"] is not None

    print("Semantic + person + year: OK")

    # =========================================================
    # TEST 7
    # =========================================================

    print("\nTest 7: Semantic ranking")

    results = searcher.search(
        semantic_query="a photo of a person",
        n_results=10,
    )

    similarities = [
        result["similarity"]
        for result in results
    ]

    assert similarities == sorted(
        similarities,
        reverse=True,
    )

    print("Semantic ranking: OK")

    # =========================================================
    # TEST 8
    # =========================================================

    print("\nTest 8: No matching structured candidates")

    results = searcher.search(
        semantic_query="a photo of a person",
        year=1900,
        n_results=10,
    )

    assert results == []

    print("Empty candidate intersection: OK")

    # =========================================================
    # TEST 9
    # =========================================================

    print("\nTest 9: Result limit")

    results = searcher.search(
        semantic_query="people",
        n_results=2,
    )

    assert len(results) == 2

    print("Result limit: OK")

    # =========================================================
    # FINAL
    # =========================================================

    print()
    print("=" * 75)
    print("ALL HYBRID SEARCH TESTS PASSED")
    print("=" * 75)


if __name__ == "__main__":
    main()