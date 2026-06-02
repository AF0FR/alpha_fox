from fastapi import APIRouter
from pydantic import BaseModel

from alpha_fox.radio.service import radio_manager


class AppStatus(BaseModel):
    app: str
    backend: str
    active_radio_backend: str
    available_radio_backends: list[str]
    radio_connected: bool


router = APIRouter(prefix="/app", tags=["app"])


@router.get("/status", response_model=AppStatus)
def get_app_status() -> AppStatus:
    radio_status = radio_manager.radio.get_status()

    return AppStatus(
        app="alpha_fox",
        backend="running",
        active_radio_backend=radio_manager.active_backend,
        available_radio_backends=radio_manager.available_backends,
        radio_connected=radio_status.connected,
    )
