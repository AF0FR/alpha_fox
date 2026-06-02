import pytest

from alpha_fox.radio.tx_safety import TxSafetyManager


def test_tx_safety_starts_disarmed() -> None:
    manager = TxSafetyManager()

    status = manager.status()

    assert status.tx_armed is False
    assert status.message == "TX disarmed."


def test_tx_safety_can_arm() -> None:
    manager = TxSafetyManager()

    status = manager.arm()

    assert status.tx_armed is True
    assert manager.tx_armed is True


def test_tx_safety_can_disarm() -> None:
    manager = TxSafetyManager()

    manager.arm()
    status = manager.disarm()

    assert status.tx_armed is False
    assert manager.tx_armed is False


def test_tx_safety_requires_arm_before_tx() -> None:
    manager = TxSafetyManager()

    with pytest.raises(RuntimeError, match="TX is not armed"):
        manager.require_armed()


def test_tx_safety_allows_tx_when_armed() -> None:
    manager = TxSafetyManager()

    manager.arm()
    manager.require_armed()
