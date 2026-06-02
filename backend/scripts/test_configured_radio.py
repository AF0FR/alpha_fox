import json

from alpha_fox.config import get_settings
from alpha_fox.radio.service import radio_service


def main() -> None:
    settings = get_settings()

    print("Configured radio backend:")
    print(json.dumps(settings.model_dump(), indent=2))

    print("\nCurrent radio status:")
    print(json.dumps(radio_service.get_status().model_dump(), indent=2))


if __name__ == "__main__":
    main()
