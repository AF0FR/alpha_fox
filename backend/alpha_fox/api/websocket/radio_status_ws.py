import asyncio
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from alpha_fox.radio.service import radio_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/radio/status")
async def radio_status_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    print("RADIO STATUS WS CONNECTED", flush=True)

    try:
        while True:
            status = radio_manager.radio.get_status()
            payload = status.model_dump(mode="json")
            await websocket.send_json(payload)
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        print("RADIO STATUS WS DISCONNECTED", flush=True)

    except Exception:
        print("RADIO STATUS WS ERROR", flush=True)
        traceback.print_exc()
