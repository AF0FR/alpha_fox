from alpha_fox.radio.base import Radio
from alpha_fox.radio.models import RadioMode, RadioStatus


class MockRadio(Radio):
    def __init__(self) -> None:
        self._status = RadioStatus(
            s_meter_raw=42,
            tx_power_level=0.20,
            af_gain=0.50,
            rf_gain=0.50,
            mic_gain=0.50,
            key_speed_wpm=20,
            rf_gain_experimental=False,
        )

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

    def set_tx_power_level(self, value: float) -> RadioStatus:
        self._status.tx_power_level = self._clamp_normalized(value)
        return self.get_status()

    def set_af_gain(self, value: float) -> RadioStatus:
        self._status.af_gain = self._clamp_normalized(value)
        return self.get_status()

    def set_rf_gain(self, value: float) -> RadioStatus:
        self._status.rf_gain = self._clamp_normalized(value)
        return self.get_status()

    def set_mic_gain(self, value: float) -> RadioStatus:
        self._status.mic_gain = self._clamp_normalized(value)
        return self.get_status()

    def set_key_speed(self, wpm: float) -> RadioStatus:
        self._status.key_speed_wpm = max(5.0, min(60.0, wpm))
        return self.get_status()

    @staticmethod
    def _clamp_normalized(value: float) -> float:
        return max(0.0, min(1.0, value))
