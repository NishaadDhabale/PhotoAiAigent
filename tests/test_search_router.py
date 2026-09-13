from app.search_router import SearchRouter


def photo_ids(results):
    return [int(photo["photo_id"]) for photo in results]


def main():
    router = SearchRouter()

    print("\n=== NISHA ===")
    results = router.search("Nisha", 10)
    ids = photo_ids(results)

    print(ids)

    assert len(results) == 5
    assert set(ids) == {187, 189, 190, 198, 199}


    print("\n=== 2022 ===")
    results = router.search("photos from 2022", 10)

    print(photo_ids(results))

    assert len(results) == 6


    print("\n=== NISHA + 2022 ===")
    results = router.search("Nisha from 2022", 10)

    ids = photo_ids(results)

    print(ids)

    assert len(results) == 2
    assert set(ids) == {189, 190}


    print("\n=== NISHA + SEMANTIC ===")
    results = router.search("Nisha at the beach", 10)

    ids = photo_ids(results)

    print(ids)

    # The important thing here is that the result set is restricted
    # to Nisha's known photos. Semantic ranking happens inside that set.
    assert set(ids).issubset({187, 189, 190, 198, 199})


    print("\n=== SEMANTIC ===")
    results = router.search("photos at the beach", 10)

    print(photo_ids(results))

    assert len(results) <= 10


    print("\nALL SEARCH ROUTER TESTS PASSED")


if __name__ == "__main__":
    main()