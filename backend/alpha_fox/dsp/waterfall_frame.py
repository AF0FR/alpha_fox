from pydantic import BaseModel, Field


class WaterfallFrame(BaseModel):
    center_frequency_hz: int = 14_074_000
    sample_rate_hz: int = 48_000
    min_db: float = -120.0
    max_db: float = -20.0
    bins: list[float] = Field(default_factory=list)