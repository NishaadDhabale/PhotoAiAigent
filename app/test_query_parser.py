from query_parser import parse_query


def show(label, query):
    result = parse_query(query)

    print(f"\n{label}")
    print(f"  query:    {query}")
    print(f"  person:   {result.person}")
    print(f"  year:     {result.year}")
    print(f"  camera:   {result.camera}")
    print(f"  filename: {result.filename}")
    print(f"  semantic: {result.semantic_query}")

    return result


def test_nisha():
    result = show("PERSON", "Nisha")

    assert result.person == "Nisha"
    assert result.year is None
    assert result.semantic_query is None


def test_year():
    result = show("YEAR", "photos from 2022")

    assert result.year == 2022
    assert result.person is None


def test_person_and_year():
    result = show("PERSON + YEAR", "Nisha from 2022")

    assert result.person == "Nisha"
    assert result.year == 2022


def test_person_semantic():
    result = show("PERSON + SEMANTIC", "Nisha at the beach")

    assert result.person == "Nisha"
    assert result.semantic_query == "at the beach"


def test_semantic_only():
    result = show("SEMANTIC", "photos at the beach")

    assert result.person is None
    assert result.year is None
    assert result.semantic_query == "at the beach"


def test_camera():
    result = show("CAMERA", "photos taken with vivo")

    assert result.camera == "vivo"


def test_filename():
    result = show(
        "FILENAME",
        "filename IMG_20220124_213235.jpg",
    )

    assert result.filename == "IMG_20220124_213235.jpg"


def test_empty():
    result = show("EMPTY", "")

    assert result.original == ""
    assert result.semantic_query is None
    assert result.person is None


if __name__ == "__main__":
    tests = [
        test_nisha,
        test_year,
        test_person_and_year,
        test_person_semantic,
        test_semantic_only,
        test_camera,
        test_filename,
        test_empty,
    ]

    for test in tests:
        test()

    print("\nALL QUERY PARSER TESTS PASSED")