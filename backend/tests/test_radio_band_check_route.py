from fastapi.testclient import TestClient

from alpha_fox.main import app


def test_radio_band_check_route_allows_20m() -> None:
    client = TestClient(app)

    response = client.get("/radio/band-check/14074000")

    assert response.status_code == 200

    data = response.json()

    assert data["allowed"] is True
    assert data["band_name"] == "20m"


def test_radio_band_check_route_rejects_invalid_frequency() -> None:
    client = TestClient(app)

    response = client.get("/radio/band-check/70000000")

    assert response.status_code == 200

    data = response.json()

    assert data["allowed"] is False


def test_set_frequency_rejects_out_of_band_frequency() -> None:
    client = TestClient(app)

    response = client.post(
        "/radio/frequency",
        json={"frequency_hz": 70_000_000},
    )

    assert response.status_code == 400
    assert "outside supported amateur" in response.json()["detail"]
