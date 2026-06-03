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


def _unsupported_to_http(exc: NotImplementedError) -> HTTPException:
    return HTTPException(status_code=501, detail=str(exc))

router = APIRouter(prefix="/radio", tags=["radio"])


class FrequencyRequest(BaseModel):
    frequency_hz: int = Field(..., ge=0)


class ModeRequest(BaseModel):
    mode: RadioMode


class PttRequest(BaseModel):
    enabled: bool


class BackendRequest(BaseModel):
    backend: RadioBackend


class NormalizedLevelRequest(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0)


class KeySpeedRequest(BaseModel):
    wpm: float = Field(..., ge=5.0, le=60.0)


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

            current_status = radio_manager.radio.get_status()
            band_check = check_band_edges(current_status.frequency_hz)

            if not band_check.allowed:
                tx_safety_manager.disarm()
                raise RuntimeError(
                    f"TX blocked: {band_check.message}"
                )

        radio_status = radio_manager.radio.set_ptt(request.enabled)

        if not radio_status.ptt:
            tx_safety_manager.disarm()

        return radio_status

    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/tx-power", response_model=RadioStatus)
def set_tx_power(request: NormalizedLevelRequest) -> RadioStatus:
    try:
        return radio_manager.radio.set_tx_power_level(request.value)
    except NotImplementedError as exc:
        raise _unsupported_to_http(exc) from exc
    except OSError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/af-gain", response_model=RadioStatus)
def set_af_gain(request: NormalizedLevelRequest) -> RadioStatus:
    try:
        return radio_manager.radio.set_af_gain(request.value)
    except NotImplementedError as exc:
        raise _unsupported_to_http(exc) from exc
    except OSError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/rf-gain", response_model=RadioStatus)
def set_rf_gain(request: NormalizedLevelRequest) -> RadioStatus:
    try:
        return radio_manager.radio.set_rf_gain(request.value)
    except NotImplementedError as exc:
        raise _unsupported_to_http(exc) from exc
    except OSError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/mic-gain", response_model=RadioStatus)
def set_mic_gain(request: NormalizedLevelRequest) -> RadioStatus:
    try:
        return radio_manager.radio.set_mic_gain(request.value)
    except NotImplementedError as exc:
        raise _unsupported_to_http(exc) from exc
    except OSError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/key-speed", response_model=RadioStatus)
def set_key_speed(request: KeySpeedRequest) -> RadioStatus:
    try:
        return radio_manager.radio.set_key_speed(request.wpm)
    except NotImplementedError as exc:
        raise _unsupported_to_http(exc) from exc
    except OSError as exc:
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