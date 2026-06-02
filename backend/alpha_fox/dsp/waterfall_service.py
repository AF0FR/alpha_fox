import math
import random
import time

from alpha_fox.dsp.waterfall_frame import WaterfallFrame
from alpha_fox.radio.service import radio_manager


class MockWaterfallService:
    def __init__(self, bin_count: int = 512) -> None:
        self.bin_count = bin_count
        self._start_time = time.monotonic()

    def get_frame(self) -> WaterfallFrame:
        status = radio_manager.radio.get_status()
        elapsed = time.monotonic() - self._start_time

        bins: list[float] = []

        carrier_1 = int((math.sin(elapsed * 0.4) * 0.35 + 0.5) * self.bin_count)
        carrier_2 = int((math.sin(elapsed * 0.17 + 2.0) * 0.25 + 0.5) * self.bin_count)
        carrier_3 = int((math.sin(elapsed * 0.09 + 5.0) * 0.20 + 0.5) * self.bin_count)

        for i in range(self.bin_count):
            noise_floor = -105.0 + random.uniform(-8.0, 5.0)

            signal = 0.0
            signal += self._signal_peak(i, carrier_1, width=4, strength=55)
            signal += self._signal_peak(i, carrier_2, width=8, strength=38)
            signal += self._signal_peak(i, carrier_3, width=14, strength=26)

            bins.append(noise_floor + signal)

        return WaterfallFrame(
            center_frequency_hz=status.frequency_hz,
            sample_rate_hz=48_000,
            min_db=-120.0,
            max_db=-20.0,
            bins=bins,
        )

    @staticmethod
    def _signal_peak(index: int, center: int, width: int, strength: float) -> float:
        distance = abs(index - center)

        if distance > width:
            return 0.0

        return strength * (1.0 - distance / width)


waterfall_service = MockWaterfallService()