import asyncio
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from alpha_fox.dsp.waterfall_service import waterfall_service

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/waterfall")
async def waterfall_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    print("WATERFALL WS CONNECTED", flush=True)

    try:
        while True:
            frame = waterfall_service.get_frame()
            payload = frame.model_dump(mode="json")
            await websocket.send_json(payload)
            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        print("WATERFALL WS DISCONNECTED", flush=True)

    except Exception:
        print("WATERFALL WS ERROR", flush=True)
        traceback.print_exc()
