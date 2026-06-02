from pydantic import BaseModel


class Band(BaseModel):
    name: str
    lower_hz: int
    upper_hz: int


AMATEUR_BANDS: list[Band] = [
    Band(name="160m", lower_hz=1_800_000, upper_hz=2_000_000),
    Band(name="80m", lower_hz=3_500_000, upper_hz=4_000_000),
    Band(name="60m", lower_hz=5_330_500, upper_hz=5_406_400),
    Band(name="40m", lower_hz=7_000_000, upper_hz=7_300_000),
    Band(name="30m", lower_hz=10_100_000, upper_hz=10_150_000),
    Band(name="20m", lower_hz=14_000_000, upper_hz=14_350_000),
    Band(name="17m", lower_hz=18_068_000, upper_hz=18_168_000),
    Band(name="15m", lower_hz=21_000_000, upper_hz=21_450_000),
    Band(name="12m", lower_hz=24_890_000, upper_hz=24_990_000),
    Band(name="10m", lower_hz=28_000_000, upper_hz=29_700_000),
    Band(name="6m", lower_hz=50_000_000, upper_hz=54_000_000),
]


def find_band(frequency_hz: int) -> Band | None:
    for band in AMATEUR_BANDS:
        if band.lower_hz <= frequency_hz <= band.upper_hz:
            return band

    return None


def is_in_amateur_band(frequency_hz: int) -> bool:
    return find_band(frequency_hz) is not None
