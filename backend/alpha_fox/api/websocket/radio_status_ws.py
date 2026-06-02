import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from alpha_fox.radio.service import radio_service

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/radio/status")
async def radio_status_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            status = radio_service.get_status()
            await websocket.send_json(status.model_dump())
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        return