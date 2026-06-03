from enum import StrEnum

from pydantic import BaseModel, Field

from typing import Literal

RadioBackend = Literal["mock", "sim", "hamlib"]


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

    s_meter_raw: float | None = None

    tx_power_level: float | None = None
    af_gain: float | None = None
    rf_gain: float | None = None
    mic_gain: float | None = None
    key_speed_wpm: float | None = None

    rf_gain_experimental: bool = False


class RadioBackendInfo(BaseModel):
    active_backend: RadioBackend
    available_backends: list[RadioBackend]