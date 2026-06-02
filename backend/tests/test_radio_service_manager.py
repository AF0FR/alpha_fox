from alpha_fox.radio.mock_radio import MockRadio
from alpha_fox.radio.service import RadioServiceManager
from alpha_fox.radio.sim_radio import SimRadio


def test_radio_service_manager_starts_with_configured_backend() -> None:
    manager = RadioServiceManager()

    assert manager.active_backend in manager.available_backends


def test_radio_service_manager_available_backends() -> None:
    manager = RadioServiceManager()

    assert manager.available_backends == ["mock", "sim", "hamlib"]


def test_radio_service_manager_switches_to_mock() -> None:
    manager = RadioServiceManager()

    radio = manager.switch_backend("mock")

    assert manager.active_backend == "mock"
    assert isinstance(radio, MockRadio)


def test_radio_service_manager_switches_to_sim() -> None:
    manager = RadioServiceManager()

    radio = manager.switch_backend("sim")

    assert manager.active_backend == "sim"
    assert isinstance(radio, SimRadio)


def test_radio_service_manager_rejects_unknown_backend() -> None:
    manager = RadioServiceManager()

    try:
        manager.switch_backend("bad")  # type: ignore[arg-type]
    except ValueError as exc:
        assert "Unsupported radio backend" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
