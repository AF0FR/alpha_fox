import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/ping")
async def ping_websocket(websocket: WebSocket) -> None:
    await websocket.accept()
    print("PING WS CONNECTED", flush=True)

    count = 0

    try:
        while True:
            await websocket.send_json({
                "type": "ping",
                "count": count,
            })
            count += 1
            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        print("PING WS DISCONNECTED", flush=True)
