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
