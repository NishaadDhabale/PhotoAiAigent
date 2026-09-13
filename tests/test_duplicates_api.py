from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_duplicates_endpoint_exists():
    response = client.get(
        "/api/duplicates"
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    assert response.status_code == 200

    data = response.json()

    assert "total_photos" in data
    assert "exact_group_count" in data
    assert "exact_duplicate_photo_count" in data
    assert "near_duplicate_count" in data
    assert "threshold" in data
    assert "exact_groups" in data
    assert "near_duplicates" in data

    print("✓ Duplicate API endpoint")


def test_duplicates_dataset_count():
    response = client.get(
        "/api/duplicates"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_photos"] == 27

    print("✓ Duplicate API sees 27 photos")


def test_duplicate_response_structure():
    response = client.get(
        "/api/duplicates"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data["exact_groups"],
        list,
    )

    assert isinstance(
        data["near_duplicates"],
        list,
    )

    assert isinstance(
        data["threshold"],
        float,
    )

    print("✓ Duplicate response structure")


def test_current_dataset_has_no_duplicates():
    response = client.get(
        "/api/duplicates"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["exact_group_count"] == 0
    assert data[
        "exact_duplicate_photo_count"
    ] == 0
    assert data["near_duplicate_count"] == 0

    print(
        "✓ Current dataset has no duplicates"
    )


if __name__ == "__main__":
    test_duplicates_endpoint_exists()
    test_duplicates_dataset_count()
    test_duplicate_response_structure()
    test_current_dataset_has_no_duplicates()

    print()
    print("ALL DUPLICATE API TESTS PASSED")