import asyncio
import json

import websockets


async def main() -> None:
    uri = "ws://127.0.0.1:8000/ws/ping"

    async with websockets.connect(uri) as websocket:
        for _ in range(5):
            message = await websocket.recv()
            print(json.dumps(json.loads(message), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
