from fastapi.testclient import TestClient

from alpha_fox.main import app


def test_app_status_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/app/status")

    assert response.status_code == 200

    data = response.json()

    assert data["app"] == "alpha_fox"
    assert data["backend"] == "running"
    assert data["active_radio_backend"] in data["available_radio_backends"]
    assert "mock" in data["available_radio_backends"]
    assert "sim" in data["available_radio_backends"]
    assert "hamlib" in data["available_radio_backends"]
    assert isinstance(data["radio_connected"], bool)
