import math
import random
import time

from alpha_fox.dsp.waterfall_frame import WaterfallFrame
from alpha_fox.radio.service import radio_manager


class MockWaterfallService:
    """
    Mock waterfall source that simulates a G90-like 48 kHz spectrum window.

    This is a spectrum-domain approximation, not a true FM demodulator.

    Goals:
    - 48 kHz total source span, like a G90-style +/-24 kHz scope.
    - One visible FM-like occupied signal on 20m.
    - Wider than a CW carrier, narrower than a full SSB-looking blob.
    - Strong enough to survive the frontend sharpness/contrast curve.
    """

    def __init__(self, bin_count: int = 1024) -> None:
        self.bin_count = bin_count
        self._start_time = time.monotonic()

    def get_frame(self) -> WaterfallFrame:
        status = radio_manager.radio.get_status()
        elapsed = time.monotonic() - self._start_time

        sample_rate_hz = 48_000
        bins: list[float] = []

        fm_offset_hz = 0

        fm_center_bin = self._frequency_offset_to_bin(
            offset_hz=fm_offset_hz,
            sample_rate_hz=sample_rate_hz,
        )

        # Approximate visible occupied bandwidth.
        # This creates about a 7 kHz wide FM-like signal.
        occupied_half_width_hz = 3_500
        occupied_half_width_bins = max(
            3,
            int((occupied_half_width_hz / sample_rate_hz) * self.bin_count),
        )

        modulation_phase = math.sin(elapsed * 2.4)
        modulation_phase_2 = math.sin(elapsed * 5.6 + 1.2)
        modulation_phase_3 = math.sin(elapsed * 8.3 + 2.4)

        for i in range(self.bin_count):
            noise_floor = self._noise_floor(i)

            fm_signal = self._fm_like_signal(
                index=i,
                center_bin=fm_center_bin,
                half_width_bins=occupied_half_width_bins,
                modulation_phase=modulation_phase,
                modulation_phase_2=modulation_phase_2,
                modulation_phase_3=modulation_phase_3,
            )

            bins.append(noise_floor + fm_signal)

        return WaterfallFrame(
            center_frequency_hz=status.frequency_hz,
            sample_rate_hz=sample_rate_hz,
            min_db=-120.0,
            max_db=-35.0,
            bins=bins,
        )

    def _frequency_offset_to_bin(self, offset_hz: int, sample_rate_hz: int) -> int:
        ratio = (offset_hz + sample_rate_hz / 2) / sample_rate_hz
        bin_index = int(ratio * self.bin_count)

        return max(0, min(self.bin_count - 1, bin_index))

    def _noise_floor(self, index: int) -> float:
        passband_position = index / max(1, self.bin_count - 1)
        passband_ripple = math.sin(passband_position * math.tau * 3.0) * 1.5

        return -110.0 + passband_ripple + random.uniform(-3.0, 2.0)

    def _fm_like_signal(
        self,
        index: int,
        center_bin: int,
        half_width_bins: int,
        modulation_phase: float,
        modulation_phase_2: float,
        modulation_phase_3: float,
    ) -> float:
        distance = abs(index - center_bin)

        # Soft side skirts outside the occupied FM region.
        if distance > half_width_bins:
            skirt_distance = distance - half_width_bins
            skirt_width = half_width_bins * 1.2

            if skirt_distance > skirt_width:
                return 0.0

            return max(0.0, 10.0 * (1.0 - skirt_distance / skirt_width))

        normalized_distance = distance / max(1, half_width_bins)

        # A flat-ish top makes it look like occupied bandwidth instead of a single carrier.
        flat_top = max(0.0, 1.0 - normalized_distance**4)

        # FM side energy often makes the occupied shape look a little stronger near shoulders.
        shoulder_left = math.exp(-((normalized_distance - 0.55) ** 2) / 0.035)
        shoulder_right = math.exp(-((normalized_distance - 0.82) ** 2) / 0.025)

        internal_texture = (
            0.80
            + 0.10 * math.sin(index * 0.18 + modulation_phase * 3.0)
            + 0.08 * math.sin(index * 0.41 + modulation_phase_2 * 4.0)
            + 0.05 * math.sin(index * 0.73 + modulation_phase_3 * 5.0)
        )

        body = 42.0 * flat_top * internal_texture
        shoulders = 10.0 * shoulder_left + 7.0 * shoulder_right

        return max(0.0, body + shoulders)


waterfall_service = MockWaterfallService()