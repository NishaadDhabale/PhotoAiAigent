import json

from agent.tools import (
    structured_photo_search_tool,
    semantic_photo_search_tool,
    hybrid_photo_search_tool,
)


def parse_result(response):
    """
    Parse a tool response and verify it is valid JSON.
    """
    data = json.loads(response)

    assert isinstance(data, dict)
    assert "count" in data
    assert "results" in data

    assert isinstance(data["count"], int)
    assert isinstance(data["results"], list)

    return data


def test_structured_search():
    print("Test 1: Structured search")

    response = structured_photo_search_tool(
        year=2022
    )

    data = parse_result(response)

    assert data["count"] == 6
    assert len(data["results"]) == 6

    for result in data["results"]:
        assert "id" in result
        assert "filename" in result
        assert "path" in result

    print("Structured search: OK")


def test_structured_person_search():
    print("\nTest 2: Structured person search")

    response = structured_photo_search_tool(
        person="Nisha"
    )

    data = parse_result(response)

    assert data["count"] == 5
    assert len(data["results"]) == 5

    print("Structured person search: OK")


def test_semantic_search():
    print("\nTest 3: Semantic search")

    response = semantic_photo_search_tool(
        query="outdoor scene",
        n_results=5,
    )

    data = parse_result(response)

    assert data["count"] == 5
    assert len(data["results"]) == 5

    for result in data["results"]:
        assert "id" in result
        assert "filename" in result
        assert "path" in result
        assert "similarity" in result

    print("Semantic search: OK")


def test_hybrid_search():
    print("\nTest 4: Hybrid search")

    response = hybrid_photo_search_tool(
        semantic_query="outdoor scene",
        year=2022,
        n_results=5,
    )

    data = parse_result(response)

    assert data["count"] <= 5
    assert len(data["results"]) <= 5

    for result in data["results"]:
        assert "id" in result
        assert "filename" in result
        assert "path" in result
        assert "similarity" in result

    print("Hybrid search: OK")


def test_hybrid_person_year():
    print("\nTest 5: Hybrid person + year")

    response = hybrid_photo_search_tool(
        person="Nisha",
        year=2022,
        n_results=10,
    )

    data = parse_result(response)

    assert data["count"] == 2
    assert len(data["results"]) == 2

    print("Hybrid person + year: OK")


def test_empty_structured_search():
    print("\nTest 6: Empty structured search")

    response = structured_photo_search_tool()

    data = parse_result(response)

    assert data["count"] == 27
    assert len(data["results"]) == 27

    print("Empty structured search: OK")


def test_empty_semantic_query():
    print("\nTest 7: Empty semantic query")

    response = semantic_photo_search_tool(
        query=""
    )

    data = parse_result(response)

    assert data["count"] == 0
    assert data["results"] == []
    assert "error" in data

    print("Empty semantic query: OK")


def test_invalid_semantic_limit():
    print("\nTest 8: Invalid semantic limit")

    response = semantic_photo_search_tool(
        query="people",
        n_results=0,
    )

    data = parse_result(response)

    assert data["count"] == 0
    assert data["results"] == []
    assert "error" in data

    print("Invalid semantic limit: OK")


def test_invalid_large_limit():
    print("\nTest 9: Invalid large limit")

    response = semantic_photo_search_tool(
        query="people",
        n_results=101,
    )

    data = parse_result(response)

    assert data["count"] == 0
    assert data["results"] == []
    assert "error" in data

    print("Invalid large limit: OK")


def test_json_photo_fields():
    print("\nTest 10: JSON photo fields")

    response = structured_photo_search_tool(
        year=2022
    )

    data = parse_result(response)

    first = data["results"][0]

    assert isinstance(first["id"], int)
    assert isinstance(first["filename"], str)
    assert isinstance(first["path"], str)

    print("JSON photo fields: OK")

def main():
    print("=" * 60)
    print("PhotoAgent Agent Tools Test")
    print("=" * 60)

    test_structured_search()
    test_structured_person_search()
    test_semantic_search()
    test_hybrid_search()
    test_hybrid_person_year()
    test_empty_structured_search()
    test_empty_semantic_query()
    test_invalid_semantic_limit()
    test_invalid_large_limit()
    test_json_photo_fields()

    print("\n" + "=" * 60)
    print("ALL AGENT TOOL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()