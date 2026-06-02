import asyncio
import json

import websockets


async def main() -> None:
    uri = "ws://127.0.0.1:8000/ws/waterfall"

    async with websockets.connect(uri) as websocket:
        for _ in range(5):
            message = await websocket.recv()
            data = json.loads(message)

            print(
                json.dumps(
                    {
                        "center_frequency_hz": data["center_frequency_hz"],
                        "sample_rate_hz": data["sample_rate_hz"],
                        "bin_count": len(data["bins"]),
                        "first_10_bins": data["bins"][:10],
                    },
                    indent=2,
                )
            )


if __name__ == "__main__":
    asyncio.run(main())