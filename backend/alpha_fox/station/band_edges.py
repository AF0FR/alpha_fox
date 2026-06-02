from pydantic import BaseModel

from alpha_fox.station.bands import Band, find_band


class BandCheckResult(BaseModel):
    frequency_hz: int
    allowed: bool
    band_name: str | None = None
    lower_hz: int | None = None
    upper_hz: int | None = None
    message: str


def check_band_edges(frequency_hz: int) -> BandCheckResult:
    if frequency_hz <= 0:
        return BandCheckResult(
            frequency_hz=frequency_hz,
            allowed=False,
            message="Frequency must be greater than zero.",
        )

    band = find_band(frequency_hz)

    if band is None:
        return BandCheckResult(
            frequency_hz=frequency_hz,
            allowed=False,
            message="Frequency is outside supported amateur HF/6m band edges.",
        )

    return _allowed_result(frequency_hz, band)


def _allowed_result(frequency_hz: int, band: Band) -> BandCheckResult:
    return BandCheckResult(
        frequency_hz=frequency_hz,
        allowed=True,
        band_name=band.name,
        lower_hz=band.lower_hz,
        upper_hz=band.upper_hz,
        message=f"Frequency is inside the {band.name} amateur band.",
    )
