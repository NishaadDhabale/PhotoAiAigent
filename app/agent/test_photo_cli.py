import json
from types import SimpleNamespace

from agent.cli import (
    extract_photo_results,
    _parse_tool_content,
    _collect_photo_dicts,
)
from photo_result import PhotoResult
from agent.result_manager import PhotoResultManager


# ------------------------------------------------------------
# Test helpers
# ------------------------------------------------------------

def make_photo(photo_id, filename=None, similarity=None):
    return {
        "id": photo_id,
        "filename": filename or f"photo_{photo_id}.jpg",
        "path": f"D:/project/PhotoAgent/Images/photo_{photo_id}.jpg",
        "date_taken": "2022-01-01 12:00:00",
        "camera": "Test Camera",
        "latitude": 19.0,
        "longitude": 73.0,
        "location_name": "Test Location",
        "similarity": similarity,
    }


def make_message(content):
    """
    Mimics the part of a LangChain message object
    that extract_photo_results() uses.
    """
    return SimpleNamespace(content=content)


# ------------------------------------------------------------
# Test 1: Parse JSON tool content
# ------------------------------------------------------------

def test_parse_json_tool_content():
    data = {
        "count": 2,
        "results": [
            make_photo(1),
            make_photo(2),
        ],
    }

    parsed = _parse_tool_content(json.dumps(data))

    assert isinstance(parsed, dict)
    assert parsed["count"] == 2
    assert len(parsed["results"]) == 2

    print("JSON tool content: OK")


# ------------------------------------------------------------
# Test 2: Parse Python-literal style content
# ------------------------------------------------------------

def test_parse_literal_tool_content():
    data = {
        "count": 1,
        "results": [
            make_photo(10),
        ],
    }

    parsed = _parse_tool_content(str(data))

    assert isinstance(parsed, dict)
    assert parsed["count"] == 1
    assert parsed["results"][0]["id"] == 10

    print("Literal tool content: OK")


# ------------------------------------------------------------
# Test 3: Collect photo dictionaries recursively
# ------------------------------------------------------------

def test_collect_photo_dicts():
    nested = {
        "count": 2,
        "results": [
            make_photo(1),
            {
                "wrapper": {
                    "photo": make_photo(2),
                }
            },
        ],
    }

    found = []

    _collect_photo_dicts(nested, found)

    ids = {item["id"] for item in found}

    assert 1 in ids
    assert 2 in ids

    print("Recursive photo collection: OK")


# ------------------------------------------------------------
# Test 4: Extract normal tool results
# ------------------------------------------------------------

def test_extract_photo_results():
    response = {
        "messages": [
            make_message("I found two photos."),

            make_message(
                json.dumps({
                    "count": 2,
                    "results": [
                        make_photo(101, similarity=0.91),
                        make_photo(102, similarity=0.84),
                    ],
                })
            ),
        ]
    }

    results = extract_photo_results(response)

    assert len(results) == 2

    assert all(
        isinstance(photo, PhotoResult)
        for photo in results
    )

    assert [photo.id for photo in results] == [101, 102]

    print("Normal result extraction: OK")


# ------------------------------------------------------------
# Test 5: Duplicate results are removed
# ------------------------------------------------------------

def test_duplicate_results_removed():
    response = {
        "messages": [
            make_message(
                json.dumps({
                    "count": 2,
                    "results": [
                        make_photo(1, similarity=0.91),
                        make_photo(2, similarity=0.82),
                    ],
                })
            ),

            make_message(
                json.dumps({
                    "count": 2,
                    "results": [
                        make_photo(2, similarity=0.82),
                        make_photo(3, similarity=0.75),
                    ],
                })
            ),
        ]
    }

    results = extract_photo_results(response)

    ids = [photo.id for photo in results]

    assert ids == [1, 2, 3]
    assert len(ids) == len(set(ids))

    print("Duplicate removal: OK")


# ------------------------------------------------------------
# Test 6: Multiple tool calls are combined
# ------------------------------------------------------------

def test_multiple_tool_results():
    response = {
        "messages": [
            make_message(
                json.dumps({
                    "count": 2,
                    "results": [
                        make_photo(11),
                        make_photo(12),
                    ],
                })
            ),

            make_message(
                json.dumps({
                    "count": 2,
                    "results": [
                        make_photo(13),
                        make_photo(14),
                    ],
                })
            ),
        ]
    }

    results = extract_photo_results(response)

    assert len(results) == 4
    assert [photo.id for photo in results] == [11, 12, 13, 14]

    print("Multiple tool results: OK")


# ------------------------------------------------------------
# Test 7: Empty result response
# ------------------------------------------------------------

def test_empty_results():
    response = {
        "messages": [
            make_message(
                json.dumps({
                    "count": 0,
                    "results": [],
                })
            )
        ]
    }

    results = extract_photo_results(response)

    assert results == []

    print("Empty result handling: OK")


# ------------------------------------------------------------
# Test 8: Result manager receives extracted results
# ------------------------------------------------------------

def test_result_manager_integration():
    response = {
        "messages": [
            make_message(
                json.dumps({
                    "count": 2,
                    "results": [
                        make_photo(21),
                        make_photo(22),
                    ],
                })
            )
        ]
    }

    results = extract_photo_results(response)

    manager = PhotoResultManager()

    manager.set_results(results)

    assert len(manager) == 2
    assert manager.get(1).id == 21
    assert manager.get(2).id == 22

    print("Result manager integration: OK")


# ------------------------------------------------------------
# Test 9: Similarity is preserved
# ------------------------------------------------------------

def test_similarity_preserved():
    response = {
        "messages": [
            make_message(
                json.dumps({
                    "count": 2,
                    "results": [
                        make_photo(31, similarity=0.987),
                        make_photo(32, similarity=0.654),
                    ],
                })
            )
        ]
    }

    results = extract_photo_results(response)

    assert len(results) == 2

    assert results[0].similarity == 0.987
    assert results[1].similarity == 0.654

    print("Similarity preservation: OK")


# ------------------------------------------------------------
# Test 10: Assistant text does not become a photo
# ------------------------------------------------------------

def test_assistant_text_ignored():
    response = {
        "messages": [
            make_message(
                "I found a beautiful outdoor photo for you."
            )
        ]
    }

    results = extract_photo_results(response)

    assert results == []

    print("Assistant text filtering: OK")


# ------------------------------------------------------------
# Run complete grouped suite
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("PhotoAgent Agent Result Handling Test")
    print("=" * 60)

    tests = [
        test_parse_json_tool_content,
        test_parse_literal_tool_content,
        test_collect_photo_dicts,
        test_extract_photo_results,
        test_duplicate_results_removed,
        test_multiple_tool_results,
        test_empty_results,
        test_result_manager_integration,
        test_similarity_preserved,
        test_assistant_text_ignored,
    ]

    for test in tests:
        test()

    print()
    print("=" * 60)
    print("ALL AGENT RESULT HANDLING TESTS PASSED")
    print("=" * 60)