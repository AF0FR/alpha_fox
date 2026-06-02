from alpha_fox.radio.mock_radio import MockRadio
from alpha_fox.radio.models import RadioMode


def test_mock_radio_initial_status() -> None:
    radio = MockRadio()

    status = radio.get_status()

    assert status.connected is True
    assert status.radio_name == "Mock Radio"
    assert status.frequency_hz == 14_074_000
    assert status.mode == RadioMode.USB
    assert status.ptt is False


def test_mock_radio_set_frequency() -> None:
    radio = MockRadio()

    status = radio.set_frequency(7_074_000)

    assert status.frequency_hz == 7_074_000


def test_mock_radio_set_mode() -> None:
    radio = MockRadio()

    status = radio.set_mode(RadioMode.LSB)

    assert status.mode == RadioMode.LSB


def test_mock_radio_ptt_changes_meter_values() -> None:
    radio = MockRadio()

    tx_status = radio.set_ptt(True)

    assert tx_status.ptt is True
    assert tx_status.power_watts == 5.0
    assert tx_status.alc == 0.3

    rx_status = radio.set_ptt(False)

    assert rx_status.ptt is False
    assert rx_status.power_watts == 0.0
    assert rx_status.alc == 0.0
