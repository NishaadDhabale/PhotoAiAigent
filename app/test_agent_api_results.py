import ast
import json

from agent.result_normalizer import normalize_photo_results


def extract_raw_results(response_messages):
    raw_results = []

    for item in response_messages:
        content = getattr(item, "content", None)

        if not content:
            continue

        if isinstance(content, str):
            try:
                parsed = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                try:
                    parsed = ast.literal_eval(content)
                except (ValueError, SyntaxError):
                    continue

            if isinstance(parsed, list):
                raw_results.extend(parsed)

            elif isinstance(parsed, dict):
                raw_results.append(parsed)

        elif isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue

                block_text = block.get("text")

                if not block_text:
                    continue

                try:
                    parsed = json.loads(block_text)
                except (json.JSONDecodeError, TypeError):
                    try:
                        parsed = ast.literal_eval(block_text)
                    except (ValueError, SyntaxError):
                        continue

                if isinstance(parsed, list):
                    raw_results.extend(parsed)

                elif isinstance(parsed, dict):
                    raw_results.append(parsed)

    return raw_results


def test_json_result():
    messages = [
        type(
            "Message",
            (),
            {
                "content": json.dumps(
                    [
                        {
                            "photo_id": 187,
                            "filename": "nisha1.jpg",
                            "path": r"D:\project\PhotoAgent\Images\nisha1.jpg",
                        },
                        {
                            "photo_id": 189,
                            "filename": "nisha2.jpg",
                            "path": r"D:\project\PhotoAgent\Images\nisha2.jpg",
                        },
                    ]
                )
            },
        )()
    ]

    raw = extract_raw_results(messages)
    results = normalize_photo_results(raw)

    assert len(results) == 2
    assert results[0]["id"] == 187
    assert results[1]["id"] == 189

    print("✓ JSON results extracted")


def test_dict_result():
    messages = [
        type(
            "Message",
            (),
            {
                "content": json.dumps(
                    {
                        "photo_id": 190,
                        "filename": "nisha3.jpg",
                        "path": r"D:\project\PhotoAgent\Images\nisha3.jpg",
                    }
                )
            },
        )()
    ]

    raw = extract_raw_results(messages)
    results = normalize_photo_results(raw)

    assert len(results) == 1
    assert results[0]["id"] == 190

    print("✓ Dictionary result extracted")


def test_text_block_results():
    messages = [
        type(
            "Message",
            (),
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            [
                                {
                                    "photo_id": 198,
                                    "filename": "photo1.jpg",
                                    "path": r"D:\project\PhotoAgent\Images\photo1.jpg",
                                },
                                {
                                    "photo_id": 199,
                                    "filename": "photo2.jpg",
                                    "path": r"D:\project\PhotoAgent\Images\photo2.jpg",
                                },
                            ]
                        ),
                    }
                ]
            },
        )()
    ]

    raw = extract_raw_results(messages)
    results = normalize_photo_results(raw)

    assert len(results) == 2
    assert results[0]["id"] == 198
    assert results[1]["id"] == 199

    print("✓ Text-block results extracted")


def test_invalid_content_is_ignored():
    messages = [
        type(
            "Message",
            (),
            {
                "content": "This is just normal AI text."
            },
        )(),
        type(
            "Message",
            (),
            {
                "content": "not valid json or python"
            },
        )(),
    ]

    raw = extract_raw_results(messages)

    assert raw == []

    print("✓ Invalid content safely ignored")


def test_duplicate_results_are_normalized():
    messages = [
        type(
            "Message",
            (),
            {
                "content": json.dumps(
                    [
                        {
                            "photo_id": 187,
                            "filename": "nisha1.jpg",
                            "path": r"D:\project\PhotoAgent\Images\nisha1.jpg",
                        },
                        {
                            "photo_id": 187,
                            "filename": "nisha1.jpg",
                            "path": r"D:\project\PhotoAgent\Images\nisha1.jpg",
                        },
                    ]
                )
            },
        )()
    ]

    raw = extract_raw_results(messages)
    results = normalize_photo_results(raw)

    assert len(results) == 1
    assert results[0]["id"] == 187

    print("✓ Duplicate results normalized")


if __name__ == "__main__":
    test_json_result()
    test_dict_result()
    test_text_block_results()
    test_invalid_content_is_ignored()
    test_duplicate_results_are_normalized()

    print()
    print("ALL AGENT API RESULT TESTS PASSED")