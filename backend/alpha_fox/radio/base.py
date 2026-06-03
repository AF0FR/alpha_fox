from abc import ABC, abstractmethod

from alpha_fox.radio.models import RadioMode, RadioStatus


class Radio(ABC):
    @abstractmethod
    def get_status(self) -> RadioStatus:
        raise NotImplementedError()

    @abstractmethod
    def set_frequency(self, frequency_hz: int) -> RadioStatus:
        raise NotImplementedError()

    @abstractmethod
    def set_mode(self, mode: RadioMode) -> RadioStatus:
        raise NotImplementedError()

    @abstractmethod
    def set_ptt(self, enabled: bool) -> RadioStatus:
        raise NotImplementedError()

    def set_tx_power_level(self, value: float) -> RadioStatus:
        raise NotImplementedError("TX power control is not supported by this radio backend.")

    def set_af_gain(self, value: float) -> RadioStatus:
        raise NotImplementedError("AF gain control is not supported by this radio backend.")

    def set_rf_gain(self, value: float) -> RadioStatus:
        raise NotImplementedError("RF gain control is not supported by this radio backend.")

    def set_mic_gain(self, value: float) -> RadioStatus:
        raise NotImplementedError("Mic gain control is not supported by this radio backend.")

    def set_key_speed(self, wpm: float) -> RadioStatus:
        raise NotImplementedError("Key speed control is not supported by this radio backend.")
