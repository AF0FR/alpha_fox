from fastapi.testclient import TestClient

from alpha_fox.main import app


def test_radio_connection_test_returns_mock_status() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.get("/radio/connection-test")

    assert response.status_code == 200

    body = response.json()

    assert body["connected"] is True
    assert body["backend"] == "mock"
    assert body["radio_name"] == "Mock Radio"
    assert body["frequency_hz"] > 0
    assert body["mode"] == "USB"
    assert body["ptt"] is False
    assert body["errors"] == []

    assert body["levels"]["s_meter_raw"] == 42
    assert body["levels"]["swr"] == 1.2
    assert body["levels"]["alc"] == 0.0
    assert body["levels"]["tx_power_level"] == 0.2
    assert body["levels"]["af_gain"] == 0.5
    assert body["levels"]["rf_gain"] == 0.5
    assert body["levels"]["mic_gain"] == 0.5
    assert body["levels"]["key_speed_wpm"] == 20