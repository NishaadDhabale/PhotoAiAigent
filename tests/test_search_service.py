from app.search_service import PhotoSearchService


def print_results(title, results):
    print()
    print("-" * 75)
    print(title)
    print("-" * 75)

    if not results:
        print("No results")
        return

    for index, result in enumerate(results, start=1):

        similarity = result.get("similarity")

        if similarity is None:
            similarity_text = "N/A"
        else:
            similarity_text = f"{similarity:.4f}"

        print(
            f"{index:2}. "
            f"photo_id={result['photo_id']} "
            f"similarity={similarity_text} "
            f"filename={result['filename']}"
        )


def main():

    print("=" * 75)
    print("PhotoAgent Search Service Test")
    print("=" * 75)

    service = PhotoSearchService()

    # =========================================================
    # TEST 1
    # =========================================================

    print("\nTest 1: Service initialization")

    assert service.semantic_searcher is not None
    assert service.hybrid_searcher is not None

    print("Service initialization: OK")

    # =========================================================
    # TEST 2
    # =========================================================

    print("\nTest 2: Structured search")

    results = service.structured_search(
        year=2022
    )

    print_results(
        "Structured search: year=2022",
        results,
    )

    assert len(results) == 6

    for result in results:
        assert result["photo_id"] > 0
        assert result["date_taken"].startswith("2022")

    print("Structured search service: OK")

    # =========================================================
    # TEST 3
    # =========================================================

    print("\nTest 3: Person search")

    results = service.structured_search(
        person="Nisha"
    )

    print_results(
        "Structured search: person=Nisha",
        results,
    )

    assert len(results) == 5

    print("Person search service: OK")

    # =========================================================
    # TEST 4
    # =========================================================

    print("\nTest 4: Semantic search")

    results = service.semantic_search(
        query="a photo of a person",
        n_results=5,
    )

    print_results(
        'Semantic search: "a photo of a person"',
        results,
    )

    assert len(results) == 5

    for result in results:
        assert result["similarity"] is not None

    print("Semantic search service: OK")

    # =========================================================
    # TEST 5
    # =========================================================

    print("\nTest 5: Hybrid search")

    results = service.hybrid_search(
        semantic_query="a photo of a person",
        person="Nisha",
        year=2022,
        n_results=10,
    )

    print_results(
        "Hybrid: semantic + Nisha + 2022",
        results,
    )

    assert len(results) == 2

    for result in results:
        assert result["date_taken"].startswith("2022")
        assert result["similarity"] is not None

    print("Hybrid search service: OK")

    # =========================================================
    # TEST 6
    # =========================================================

    print("\nTest 6: Service result consistency")

    direct_results = service.structured_search(
        person="Nisha",
        year=2022,
    )

    hybrid_results = service.hybrid_search(
        semantic_query="a photo of a person",
        person="Nisha",
        year=2022,
        n_results=10,
    )

    direct_ids = {
        result["photo_id"]
        for result in direct_results
    }

    hybrid_ids = {
        result["photo_id"]
        for result in hybrid_results
    }

    assert hybrid_ids.issubset(direct_ids)

    print(
        "Hybrid results are subset of structured candidates: OK"
    )

    # =========================================================
    # TEST 7
    # =========================================================

    print("\nTest 7: Semantic ranking")

    results = service.semantic_search(
        query="an outdoor scene",
        n_results=5,
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

    print("\nTest 8: Empty semantic query")

    try:
        service.semantic_search(
            query=""
        )

        raise AssertionError(
            "Empty semantic query should fail"
        )

    except ValueError:
        pass

    print("Empty semantic query validation: OK")

    # =========================================================
    # TEST 9
    # =========================================================

    print("\nTest 9: Convenience functions")

    from app.search_service import (
        structured_photo_search,
        semantic_photo_search,
        hybrid_photo_search,
    )

    structured = structured_photo_search(
        year=2022
    )

    semantic = semantic_photo_search(
        query="people",
        n_results=3,
    )

    hybrid = hybrid_photo_search(
        semantic_query="people",
        year=2022,
        n_results=3,
    )

    assert len(structured) == 6
    assert len(semantic) == 3
    assert len(hybrid) <= 3

    print("Convenience functions: OK")

    # =========================================================
    # FINAL
    # =========================================================

    print()
    print("=" * 75)
    print("ALL SEARCH SERVICE TESTS PASSED")
    print("=" * 75)


if __name__ == "__main__":
    main()
    