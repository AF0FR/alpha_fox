import math
import random
import time

from alpha_fox.radio.base import Radio
from alpha_fox.radio.models import RadioMode, RadioStatus


class SimRadio(Radio):
    """
    A more realistic fake radio.

    Unlike MockRadio, this simulates:
    - delayed frequency changes
    - changing RX/TX meter values
    - SWR variation by band
    - voltage sag during TX
    - basic band-edge validation
    """

    def __init__(self) -> None:
        self._created_at = time.monotonic()
        self._target_frequency_hz = 14_074_000
        self._status = RadioStatus(
            connected=True,
            radio_name="Simulated Radio",
            frequency_hz=14_074_000,
            mode=RadioMode.USB,
            ptt=False,
            vfo="A",
            swr=1.1,
            power_watts=0.0,
            alc=0.0,
            voltage=13.8,
        )

    def get_status(self) -> RadioStatus:
        self._update_frequency_motion()
        self._update_meters()
        return self._status

    def set_frequency(self, frequency_hz: int) -> RadioStatus:
        self._validate_frequency(frequency_hz)
        self._target_frequency_hz = frequency_hz
        self._update_frequency_motion()
        return self.get_status()

    def set_mode(self, mode: RadioMode) -> RadioStatus:
        self._status.mode = mode
        return self.get_status()

    def set_ptt(self, enabled: bool) -> RadioStatus:
        if enabled:
            self._validate_can_transmit()

        self._status.ptt = enabled
        return self.get_status()

    def _update_frequency_motion(self) -> None:
        current = self._status.frequency_hz
        target = self._target_frequency_hz

        if current == target:
            return

        delta = target - current
        step = max(25, abs(delta) // 4)

        if abs(delta) <= step:
            self._status.frequency_hz = target
            return

        self._status.frequency_hz = current + step if delta > 0 else current - step

    def _update_meters(self) -> None:
        elapsed = time.monotonic() - self._created_at
        base_swr = self._estimate_swr(self._status.frequency_hz)

        if self._status.ptt:
            self._status.power_watts = round(18.0 + math.sin(elapsed * 2.0) * 1.5, 1)
            self._status.alc = round(0.25 + random.uniform(-0.04, 0.04), 2)
            self._status.voltage = round(13.2 + random.uniform(-0.08, 0.05), 2)
            self._status.swr = round(base_swr + random.uniform(-0.03, 0.05), 2)
        else:
            self._status.power_watts = 0.0
            self._status.alc = 0.0
            self._status.voltage = round(13.8 + random.uniform(-0.03, 0.03), 2)
            self._status.swr = round(base_swr + random.uniform(-0.02, 0.03), 2)

    def _estimate_swr(self, frequency_hz: int) -> float:
        mhz = frequency_hz / 1_000_000

        if 3.5 <= mhz <= 4.0:
            return 1.8
        if 7.0 <= mhz <= 7.3:
            return 1.35
        if 10.1 <= mhz <= 10.15:
            return 1.25
        if 14.0 <= mhz <= 14.35:
            return 1.15
        if 18.068 <= mhz <= 18.168:
            return 1.4
        if 21.0 <= mhz <= 21.45:
            return 1.55
        if 28.0 <= mhz <= 29.7:
            return 1.7

        return 3.5

    def _validate_frequency(self, frequency_hz: int) -> None:
        if frequency_hz <= 0:
            raise ValueError("Frequency must be greater than zero.")

        if frequency_hz > 60_000_000:
            raise ValueError("Simulated radio only supports HF/6m frequencies.")

    def _validate_can_transmit(self) -> None:
        if self._status.swr is not None and self._status.swr > 3.0:
            raise RuntimeError("Cannot transmit: simulated SWR is too high.")