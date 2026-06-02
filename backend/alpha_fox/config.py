from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


RadioBackend = Literal["mock", "sim", "hamlib"]


class HamlibSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 4532


class RadioSettings(BaseModel):
    backend: RadioBackend = "mock"
    name: str = "Mock Radio"
    hamlib: HamlibSettings = Field(default_factory=HamlibSettings)


class AppSettings(BaseModel):
    radio: RadioSettings = Field(default_factory=RadioSettings)


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        return {}

    return data


@lru_cache
def get_settings() -> AppSettings:
    config_path = Path(__file__).resolve().parents[2] / "configs" / "alpha_fox.local.yaml"
    data = _load_yaml(config_path)
    return AppSettings.model_validate(data)
