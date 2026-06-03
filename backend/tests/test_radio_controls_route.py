from fastapi.testclient import TestClient

from alpha_fox.main import app


def test_set_tx_power_level_updates_mock_radio() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/tx-power", json={"value": 0.42})

    assert response.status_code == 200
    assert response.json()["tx_power_level"] == 0.42


def test_set_af_gain_updates_mock_radio() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/af-gain", json={"value": 0.55})

    assert response.status_code == 200
    assert response.json()["af_gain"] == 0.55


def test_set_rf_gain_updates_mock_radio() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/rf-gain", json={"value": 0.43})

    assert response.status_code == 200
    assert response.json()["rf_gain"] == 0.43


def test_set_mic_gain_updates_mock_radio() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/mic-gain", json={"value": 0.65})

    assert response.status_code == 200
    assert response.json()["mic_gain"] == 0.65


def test_set_key_speed_updates_mock_radio() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/key-speed", json={"wpm": 25})

    assert response.status_code == 200
    assert response.json()["key_speed_wpm"] == 25


def test_normalized_level_rejects_too_low_value() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/af-gain", json={"value": -0.01})

    assert response.status_code == 422


def test_normalized_level_rejects_too_high_value() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/af-gain", json={"value": 1.01})

    assert response.status_code == 422


def test_key_speed_rejects_too_low_value() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/key-speed", json={"wpm": 4})

    assert response.status_code == 422


def test_key_speed_rejects_too_high_value() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})

    response = client.post("/radio/key-speed", json={"wpm": 61})

    assert response.status_code == 422