from fastapi.testclient import TestClient

from alpha_fox.main import app


def test_tx_arm_status_route() -> None:
    client = TestClient(app)

    response = client.get("/radio/tx-arm")

    assert response.status_code == 200
    assert "tx_armed" in response.json()


def test_ptt_on_requires_tx_arm() -> None:
    client = TestClient(app)

    client.post("/radio/tx-disarm")

    response = client.post("/radio/ptt", json={"enabled": True})

    assert response.status_code == 409
    assert "TX is not armed" in response.json()["detail"]


def test_ptt_on_allowed_after_tx_arm() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})
    client.post("/radio/frequency", json={"frequency_hz": 14_074_000})
    client.post("/radio/tx-disarm")

    client.post("/radio/tx-arm")
    response = client.post("/radio/ptt", json={"enabled": True})

    assert response.status_code == 200
    assert response.json()["ptt"] is True

    client.post("/radio/ptt", json={"enabled": False})
    client.post("/radio/tx-disarm")


def test_tx_disarm_releases_ptt() -> None:
    client = TestClient(app)

    client.post("/radio/tx-arm")
    client.post("/radio/ptt", json={"enabled": True})

    response = client.post("/radio/tx-disarm")

    assert response.status_code == 200
    assert response.json()["tx_armed"] is False

    status_response = client.get("/radio/status")
    assert status_response.json()["ptt"] is False


def test_ptt_blocks_tx_outside_amateur_band() -> None:
    client = TestClient(app)

    client.post("/radio/backend", json={"backend": "mock"})
    client.post("/radio/frequency", json={"frequency_hz": 27_185_000})
    client.post("/radio/tx-disarm")
    client.post("/radio/tx-arm")

    response = client.post("/radio/ptt", json={"enabled": True})

    assert response.status_code == 409
    assert "TX blocked" in response.json()["detail"]

    status_response = client.get("/radio/status")
    assert status_response.json()["ptt"] is False
