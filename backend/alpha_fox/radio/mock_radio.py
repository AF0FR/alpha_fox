from alpha_fox.radio.base import Radio
from alpha_fox.radio.models import RadioMode, RadioStatus


class MockRadio(Radio):
    def __init__(self) -> None:
        self._status = RadioStatus()

    def get_status(self) -> RadioStatus:
        return self._status

    def set_frequency(self, frequency_hz: int) -> RadioStatus:
        self._status.frequency_hz = frequency_hz
        return self._status

    def set_mode(self, mode: RadioMode) -> RadioStatus:
        self._status.mode = mode
        return self._status

    def set_ptt(self, enabled: bool) -> RadioStatus:
        self._status.ptt = enabled

        if enabled:
            self._status.power_watts = 5.0
            self._status.alc = 0.3
        else:
            self._status.power_watts = 0.0
            self._status.alc = 0.0

        return self._status
