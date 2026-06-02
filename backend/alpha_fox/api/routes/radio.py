from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from alpha_fox.radio.models import (
    RadioBackend,
    RadioBackendInfo,
    RadioMode,
    RadioStatus,
)
from alpha_fox.radio.service import radio_manager
from alpha_fox.station.band_edges import BandCheckResult, check_band_edges
from alpha_fox.radio.tx_safety import TxSafetyStatus, tx_safety_manager

router = APIRouter(prefix="/radio", tags=["radio"])


class FrequencyRequest(BaseModel):
    frequency_hz: int = Field(..., ge=0)


class ModeRequest(BaseModel):
    mode: RadioMode


class PttRequest(BaseModel):
    enabled: bool


class BackendRequest(BaseModel):
    backend: RadioBackend


@router.get("/backend", response_model=RadioBackendInfo)
def get_radio_backend() -> RadioBackendInfo:
    return RadioBackendInfo(
        active_backend=radio_manager.active_backend,
        available_backends=radio_manager.available_backends,
    )


@router.post("/backend", response_model=RadioBackendInfo)
def set_radio_backend(request: BackendRequest) -> RadioBackendInfo:
    try:
        radio_status = radio_manager.radio.get_status()

        if radio_status.ptt:
            radio_manager.radio.set_ptt(False)

        tx_safety_manager.disarm()
        radio_manager.switch_backend(request.backend)

    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RadioBackendInfo(
        active_backend=radio_manager.active_backend,
        available_backends=radio_manager.available_backends,
    )


@router.get("/status", response_model=RadioStatus)
def get_radio_status() -> RadioStatus:
    return radio_manager.radio.get_status()


@router.post("/frequency", response_model=RadioStatus)
def set_frequency(request: FrequencyRequest) -> RadioStatus:
    band_check = check_band_edges(request.frequency_hz)

    if not band_check.allowed:
        raise HTTPException(status_code=400, detail=band_check.message)

    try:
        return radio_manager.radio.set_frequency(request.frequency_hz)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/band-check/{frequency_hz}", response_model=BandCheckResult)
def check_frequency_band(frequency_hz: int) -> BandCheckResult:
    return check_band_edges(frequency_hz)



@router.post("/mode", response_model=RadioStatus)
def set_mode(request: ModeRequest) -> RadioStatus:
    return radio_manager.radio.set_mode(request.mode)


@router.post("/ptt", response_model=RadioStatus)
def set_ptt(request: PttRequest) -> RadioStatus:
    try:
        if request.enabled:
            tx_safety_manager.require_armed()

        radio_status = radio_manager.radio.set_ptt(request.enabled)

        if not radio_status.ptt:
            tx_safety_manager.disarm()

        return radio_status

    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/tx-arm", response_model=TxSafetyStatus)
def get_tx_arm_status() -> TxSafetyStatus:
    return tx_safety_manager.status()


@router.post("/tx-arm", response_model=TxSafetyStatus)
def arm_tx() -> TxSafetyStatus:
    return tx_safety_manager.arm()


@router.post("/tx-disarm", response_model=TxSafetyStatus)
def disarm_tx() -> TxSafetyStatus:
    radio_status = radio_manager.radio.get_status()

    if radio_status.ptt:
        radio_manager.radio.set_ptt(False)

    return tx_safety_manager.disarm()