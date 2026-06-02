from enum import StrEnum

from pydantic import BaseModel, Field


class RadioMode(StrEnum):
    LSB = "LSB"
    USB = "USB"
    AM = "AM"
    CW = "CW"
    CWR = "CWR"
    NFM = "NFM"


class RadioStatus(BaseModel):
    connected: bool = True
    radio_name: str = "Mock Radio"
    frequency_hz: int = Field(default=14_074_000, ge=0)
    mode: RadioMode = RadioMode.USB
    ptt: bool = False
    vfo: str = "A"

    swr: float | None = 1.2
    power_watts: float | None = 0.0
    alc: float | None = 0.0
    voltage: float | None = 13.8