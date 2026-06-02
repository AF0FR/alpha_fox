import json
from urllib import request


BASE_URL = "http://127.0.0.1:8000"


def get(path: str) -> dict:
    with request.urlopen(f"{BASE_URL}{path}") as response:
        return json.loads(response.read().decode("utf-8"))


def post(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")

    req = request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def print_response(title: str, data: dict) -> None:
    print(f"\n{title}")
    print(json.dumps(data, indent=2))


def main() -> None:
    print_response("Initial status", get("/radio/status"))

    print_response(
        "Set frequency",
        post("/radio/frequency", {"frequency_hz": 7_074_000}),
    )

    print_response(
        "Set mode",
        post("/radio/mode", {"mode": "LSB"}),
    )

    print_response(
        "PTT on",
        post("/radio/ptt", {"enabled": True}),
    )

    print_response(
        "PTT off",
        post("/radio/ptt", {"enabled": False}),
    )


if __name__ == "__main__":
    main()