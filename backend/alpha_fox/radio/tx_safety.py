from pydantic import BaseModel


class TxSafetyStatus(BaseModel):
    tx_armed: bool
    message: str


class TxSafetyManager:
    def __init__(self) -> None:
        self._tx_armed = False

    @property
    def tx_armed(self) -> bool:
        return self._tx_armed

    def arm(self) -> TxSafetyStatus:
        self._tx_armed = True

        return TxSafetyStatus(
            tx_armed=True,
            message="TX armed.",
        )

    def disarm(self) -> TxSafetyStatus:
        self._tx_armed = False

        return TxSafetyStatus(
            tx_armed=False,
            message="TX disarmed.",
        )

    def status(self) -> TxSafetyStatus:
        return TxSafetyStatus(
            tx_armed=self._tx_armed,
            message="TX armed." if self._tx_armed else "TX disarmed.",
        )

    def require_armed(self) -> None:
        if not self._tx_armed:
            raise RuntimeError("TX is not armed. Arm TX before enabling PTT.")


tx_safety_manager = TxSafetyManager()
