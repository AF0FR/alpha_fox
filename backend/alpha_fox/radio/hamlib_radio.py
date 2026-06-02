import socket
from dataclasses import dataclass

from alpha_fox.radio.base import Radio
from alpha_fox.radio.models import RadioMode, RadioStatus


@dataclass(frozen=True)
class HamlibConnectionSettings:
    host: str = "127.0.0.1"
    port: int = 4532
    timeout_seconds: float = 1.0


class HamlibRadio(Radio):
    def __init__(
        self,
        name: str,
        settings: HamlibConnectionSettings,
    ) -> None:
        self.name = name
        self.settings = settings
        self._last_status = RadioStatus(
            connected=False,
            radio_name=name,
            frequency_hz=0,
            mode=RadioMode.USB,
            ptt=False,
            vfo="A",
            swr=None,
            power_watts=None,
            alc=None,
            voltage=None,
        )

    def get_status(self) -> RadioStatus:
        try:
            frequency_hz = self._get_frequency()
            mode = self._get_mode()
            ptt = self._get_ptt()

            self._last_status = RadioStatus(
                connected=True,
                radio_name=self.name,
                frequency_hz=frequency_hz,
                mode=mode,
                ptt=ptt,
                vfo="A",
                swr=None,
                power_watts=None,
                alc=None,
                voltage=None,
            )

        except OSError:
            self._last_status.connected = False

        return self._last_status

    def set_frequency(self, frequency_hz: int) -> RadioStatus:
        self._send_command(f"F {frequency_hz}")
        return self.get_status()

    def set_mode(self, mode: RadioMode) -> RadioStatus:
        # Hamlib mode command format:
        # M <mode> <passband>
        # passband 0 lets backend choose default.
        self._send_command(f"M {mode.value} 0")
        return self.get_status()

    def set_ptt(self, enabled: bool) -> RadioStatus:
        self._send_command(f"T {1 if enabled else 0}")
        return self.get_status()

    def _get_frequency(self) -> int:
        response = self._send_command("f")
        return int(response.strip())

    def _get_mode(self) -> RadioMode:
        response = self._send_command("m")
        first_line = response.strip().splitlines()[0]
        normalized = first_line.strip().upper()

        try:
            return RadioMode(normalized)
        except ValueError:
            return RadioMode.USB

    def _get_ptt(self) -> bool:
        response = self._send_command("t")
        return response.strip().startswith("1")

    def _send_command(self, command: str) -> str:
        with socket.create_connection(
            (self.settings.host, self.settings.port),
            timeout=self.settings.timeout_seconds,
        ) as sock:
            sock.settimeout(self.settings.timeout_seconds)
            sock.sendall(f"{command}\n".encode("ascii"))

            chunks: list[bytes] = []

            while True:
                try:
                    chunk = sock.recv(4096)
                except TimeoutError:
                    break

                if not chunk:
                    break

                chunks.append(chunk)

                if b"\n" in chunk:
                    break

            response = b"".join(chunks).decode("ascii", errors="replace").strip()

        if response.startswith("RPRT -"):
            raise OSError(f"Hamlib command failed: {command}: {response}")

        return response
