from alpha_fox.config import get_settings
from alpha_fox.radio.base import Radio
from alpha_fox.radio.hamlib_radio import HamlibConnectionSettings, HamlibRadio
from alpha_fox.radio.mock_radio import MockRadio
from alpha_fox.radio.models import RadioBackend
from alpha_fox.radio.sim_radio import SimRadio


class RadioServiceManager:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._active_backend: RadioBackend = self._settings.radio.backend
        self._radio: Radio = self._create_radio(self._active_backend)

    @property
    def active_backend(self) -> RadioBackend:
        return self._active_backend

    @property
    def available_backends(self) -> list[RadioBackend]:
        return ["mock", "sim", "hamlib"]

    @property
    def radio(self) -> Radio:
        return self._radio

    def switch_backend(self, backend: RadioBackend) -> Radio:
        if backend not in self.available_backends:
            raise ValueError(f"Unsupported radio backend: {backend}")

        if backend == self._active_backend:
            return self._radio

        # Avoid blocking on disconnected Hamlib when switching away.
        # Still protect against switching while the current fast/local backend is keyed.
        if self._active_backend in {"mock", "sim"}:
            current_status = self._radio.get_status()

            if current_status.ptt:
                raise RuntimeError("Cannot switch radio backend while PTT is active.")

        self._active_backend = backend
        self._radio = self._create_radio(backend)

        return self._radio

    def _create_radio(self, backend: RadioBackend) -> Radio:
        if backend == "hamlib":
            return HamlibRadio(
                name=self._settings.radio.name or "Hamlib Radio",
                settings=HamlibConnectionSettings(
                    host=self._settings.radio.hamlib.host,
                    port=self._settings.radio.hamlib.port,
                    timeout_seconds=0.25,
                ),
            )

        if backend == "sim":
            return SimRadio()

        return MockRadio()


radio_manager = RadioServiceManager()