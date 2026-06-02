import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from alpha_fox.dsp.waterfall_service import waterfall_service

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/waterfall")
async def waterfall_websocket(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            frame = waterfall_service.get_frame()
            await websocket.send_json(frame.model_dump())
            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        return