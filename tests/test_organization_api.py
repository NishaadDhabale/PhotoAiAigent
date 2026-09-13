from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_organization_preview():

    response = client.get(
        "/api/organization/preview"
    )

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "plan" in data

    summary = data["summary"]

    assert "photos" in summary
    assert "safe" in summary
    assert "conflicts" in summary
    assert "already_organized" in summary
    assert "missing_source" in summary

    assert isinstance(
        data["plan"],
        list,
    )


def test_organization_execute_requires_confirmation():

    response = client.post(
        "/api/organization/execute",
        json={
            "confirm": False,
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert "confirmation" in data["detail"].lower()


if __name__ == "__main__":

    test_organization_preview()
    print("✓ Organization preview API")

    test_organization_execute_requires_confirmation()
    print("✓ Organization confirmation protection")

    print("\nALL ORGANIZATION API TESTS PASSED")