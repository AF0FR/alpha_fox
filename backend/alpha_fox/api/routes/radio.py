from fastapi import APIRouter
from pydantic import BaseModel, Field

from alpha_fox.radio.models import RadioMode, RadioStatus
from alpha_fox.radio.service import radio_service

router = APIRouter(prefix="/radio", tags=["radio"])


class FrequencyRequest(BaseModel):
    frequency_hz: int = Field(..., ge=0)


class ModeRequest(BaseModel):
    mode: RadioMode


class PttRequest(BaseModel):
    enabled: bool


@router.get("/status", response_model=RadioStatus)
def get_radio_status() -> RadioStatus:
    return radio_service.get_status()


@router.post("/frequency", response_model=RadioStatus)
def set_frequency(request: FrequencyRequest) -> RadioStatus:
    return radio_service.set_frequency(request.frequency_hz)


@router.post("/mode", response_model=RadioStatus)
def set_mode(request: ModeRequest) -> RadioStatus:
    return radio_service.set_mode(request.mode)


@router.post("/ptt", response_model=RadioStatus)
def set_ptt(request: PttRequest) -> RadioStatus:
    return radio_service.set_ptt(request.enabled)