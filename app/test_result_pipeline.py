import json

from agent.result_pipeline import (
    extract_photo_results,
)


def make_message(content):
    return type(
        "Message",
        (),
        {
            "content": content,
        },
    )()


def test_json_results():
    messages = [
        make_message(
            json.dumps(
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
        )
    ]

    results = extract_photo_results(messages)

    assert len(results) == 2
    assert results[0]["id"] == 187
    assert results[1]["id"] == 189

    print("✓ JSON pipeline")


def test_text_block_results():
    messages = [
        make_message(
            [
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
        )
    ]

    results = extract_photo_results(messages)

    assert len(results) == 2
    assert results[0]["id"] == 198
    assert results[1]["id"] == 199

    print("✓ Text-block pipeline")


def test_duplicates():
    messages = [
        make_message(
            json.dumps(
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
        )
    ]

    results = extract_photo_results(messages)

    assert len(results) == 1
    assert results[0]["id"] == 187

    print("✓ Duplicate normalization")


def test_invalid_content():
    messages = [
        make_message("Normal assistant text."),
        make_message("not JSON"),
    ]

    results = extract_photo_results(messages)

    assert results == []

    print("✓ Invalid content handling")


if __name__ == "__main__":
    test_json_results()
    test_text_block_results()
    test_duplicates()
    test_invalid_content()

    print()
    print("ALL RESULT PIPELINE TESTS PASSED")