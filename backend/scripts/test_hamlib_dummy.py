from alpha_fox.radio.hamlib_radio import HamlibConnectionSettings, HamlibRadio
from alpha_fox.radio.models import RadioMode


def main() -> None:
    radio = HamlibRadio(
        name="Hamlib Dummy Rig",
        settings=HamlibConnectionSettings(
            host="127.0.0.1",
            port=4532,
            timeout_seconds=1.0,
        ),
    )

    print("Initial status:")
    print(radio.get_status().model_dump())

    print("\nSet frequency to 14.074 MHz:")
    print(radio.set_frequency(14_074_000).model_dump())

    print("\nSet mode to USB:")
    print(radio.set_mode(RadioMode.USB).model_dump())

    print("\nPTT on:")
    print(radio.set_ptt(True).model_dump())

    print("\nPTT off:")
    print(radio.set_ptt(False).model_dump())


if __name__ == "__main__":
    main()
