from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from neuer_radar.core.models import Source, UserProfile


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML object in {path}")
    return data


def load_profile(path: Path) -> UserProfile:
    return UserProfile.model_validate(_read_yaml(path))


def load_sources(path: Path) -> list[Source]:
    data = _read_yaml(path)
    raw_sources = data.get("sources", [])
    if not isinstance(raw_sources, list):
        raise ValueError("sources must be a list")
    return [Source.model_validate(item) for item in raw_sources]
