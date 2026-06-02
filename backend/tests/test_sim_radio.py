import pytest

from alpha_fox.radio.models import RadioMode
from alpha_fox.radio.sim_radio import SimRadio


def test_sim_radio_initial_status() -> None:
    radio = SimRadio()

    status = radio.get_status()

    assert status.connected is True
    assert status.radio_name == "Simulated Radio"
    assert status.frequency_hz == 14_074_000
    assert status.mode == RadioMode.USB
    assert status.ptt is False


def test_sim_radio_set_mode() -> None:
    radio = SimRadio()

    status = radio.set_mode(RadioMode.CW)

    assert status.mode == RadioMode.CW


def test_sim_radio_rejects_zero_frequency() -> None:
    radio = SimRadio()

    with pytest.raises(ValueError, match="Frequency must be greater than zero"):
        radio.set_frequency(0)


def test_sim_radio_rejects_above_6m_frequency() -> None:
    radio = SimRadio()

    with pytest.raises(ValueError, match="HF/6m"):
        radio.set_frequency(70_000_000)


def test_sim_radio_frequency_moves_toward_target() -> None:
    radio = SimRadio()

    original = radio.get_status().frequency_hz
    status = radio.set_frequency(7_074_000)

    assert status.frequency_hz != original
    assert status.frequency_hz < original


def test_sim_radio_ptt_sets_tx_meter_values() -> None:
    radio = SimRadio()

    status = radio.set_ptt(True)

    assert status.ptt is True
    assert status.power_watts is not None
    assert status.power_watts > 0
    assert status.alc is not None
    assert status.alc > 0
    assert status.voltage is not None
    assert status.voltage < 13.8


def test_sim_radio_high_swr_blocks_ptt() -> None:
    radio = SimRadio()
    radio.set_frequency(55_000_000)

    with pytest.raises(RuntimeError, match="SWR is too high"):
        radio.set_ptt(True)
