import asyncio
import json

import websockets


async def main() -> None:
    uri = "ws://127.0.0.1:8000/ws/radio/status"

    try:
        async with websockets.connect(uri) as websocket:
            for _ in range(5):
                message = await websocket.recv()
                data = json.loads(message)
                print(json.dumps(data, indent=2))

    except KeyboardInterrupt:
        print("WebSocket test stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("WebSocket test stopped.")