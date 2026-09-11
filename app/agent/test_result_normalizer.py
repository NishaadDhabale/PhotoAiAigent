from agent.result_normalizer import (
    normalize_photo_dict,
    normalize_photo_results,
)


def test_id_format():
    print("Test 1: Existing id format")

    row = {
        "id": 101,
        "filename": "photo.jpg",
        "path": r"D:\Photos\photo.jpg",
    }

    result = normalize_photo_dict(row)

    assert result["id"] == 101
    assert result["filename"] == "photo.jpg"
    assert result["path"] == r"D:\Photos\photo.jpg"

    print("Existing id format: OK")


def test_photo_id_format():
    print("\nTest 2: SearchService photo_id format")

    row = {
        "photo_id": 202,
        "filename": "photo2.jpg",
        "path": r"D:\Photos\photo2.jpg",
    }

    result = normalize_photo_dict(row)

    assert result["id"] == 202
    assert "photo_id" not in result

    print("SearchService photo_id format: OK")


def test_metadata_preservation():
    print("\nTest 3: Metadata preservation")

    row = {
        "photo_id": 303,
        "filename": "metadata.jpg",
        "path": r"D:\Photos\metadata.jpg",
        "date_taken": "2022-01-01",
        "camera": "Camera X",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "location_name": "Mumbai",
        "similarity": 0.7654,
    }

    result = normalize_photo_dict(row)

    assert result["id"] == 303
    assert result["date_taken"] == "2022-01-01"
    assert result["camera"] == "Camera X"
    assert result["latitude"] == 19.0760
    assert result["longitude"] == 72.8777
    assert result["location_name"] == "Mumbai"
    assert result["similarity"] == 0.7654

    print("Metadata preservation: OK")


def test_invalid_missing_id():
    print("\nTest 4: Missing id")

    row = {
        "filename": "bad.jpg",
        "path": r"D:\Photos\bad.jpg",
    }

    try:
        normalize_photo_dict(row)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    print("Missing id handling: OK")


def test_invalid_missing_filename():
    print("\nTest 5: Missing filename")

    row = {
        "id": 401,
        "path": r"D:\Photos\bad.jpg",
    }

    try:
        normalize_photo_dict(row)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    print("Missing filename handling: OK")


def test_invalid_missing_path():
    print("\nTest 6: Missing path")

    row = {
        "id": 402,
        "filename": "bad.jpg",
    }

    try:
        normalize_photo_dict(row)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    print("Missing path handling: OK")


def test_invalid_id():
    print("\nTest 7: Invalid id")

    row = {
        "id": "not-a-number",
        "filename": "bad.jpg",
        "path": r"D:\Photos\bad.jpg",
    }

    try:
        normalize_photo_dict(row)
        assert False, "Expected ValueError"
    except ValueError:
        pass

    print("Invalid id handling: OK")


def test_duplicate_removal():
    print("\nTest 8: Duplicate removal")

    rows = [
        {
            "photo_id": 501,
            "filename": "one.jpg",
            "path": r"D:\Photos\one.jpg",
        },
        {
            "photo_id": 501,
            "filename": "one.jpg",
            "path": r"D:\Photos\one.jpg",
        },
        {
            "photo_id": 502,
            "filename": "two.jpg",
            "path": r"D:\Photos\two.jpg",
        },
    ]

    results = normalize_photo_results(rows)

    assert len(results) == 2
    assert results[0]["id"] == 501
    assert results[1]["id"] == 502

    print("Duplicate removal: OK")


def test_invalid_rows_are_skipped():
    print("\nTest 9: Invalid rows are skipped")

    rows = [
        {
            "photo_id": 601,
            "filename": "valid.jpg",
            "path": r"D:\Photos\valid.jpg",
        },
        {
            "filename": "invalid.jpg",
            "path": r"D:\Photos\invalid.jpg",
        },
        {
            "photo_id": 602,
            "filename": "valid2.jpg",
            "path": r"D:\Photos\valid2.jpg",
        },
    ]

    results = normalize_photo_results(rows)

    assert len(results) == 2
    assert results[0]["id"] == 601
    assert results[1]["id"] == 602

    print("Invalid row handling: OK")


def test_empty_results():
    print("\nTest 10: Empty results")

    results = normalize_photo_results([])

    assert results == []

    print("Empty results: OK")


def main():
    print("=" * 60)
    print("PhotoAgent Result Normalization Test")
    print("=" * 60)

    test_id_format()
    test_photo_id_format()
    test_metadata_preservation()
    test_invalid_missing_id()
    test_invalid_missing_filename()
    test_invalid_missing_path()
    test_invalid_id()
    test_duplicate_removal()
    test_invalid_rows_are_skipped()
    test_empty_results()

    print("\n" + "=" * 60)
    print("ALL RESULT NORMALIZATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()