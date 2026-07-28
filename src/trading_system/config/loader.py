"""Load configuration layers without accepting unversioned command-line overrides."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from trading_system.config.models import Settings


class UnsafeStartupError(RuntimeError):
    """Raised when configuration is invalid or would permit unsafe startup."""


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise UnsafeStartupError(f"unable to read configuration {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise UnsafeStartupError(f"configuration {path} must contain a mapping")
    return raw


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    merged = deepcopy(dict(base))
    for key, value in overlay.items():
        current = merged.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = deepcopy(value)
    return merged


def load_settings(
    environment_path: Path,
    market_path: Path,
    *,
    base_path: Path = Path("configs/base.yaml"),
) -> Settings:
    """Load base, environment, and market layers, rejecting unsafe combinations."""

    merged = _deep_merge(_read_yaml(base_path), _read_yaml(environment_path))
    merged = _deep_merge(merged, _read_yaml(market_path))
    try:
        return Settings.model_validate(merged)
    except ValidationError as exc:
        raise UnsafeStartupError("configuration rejected; startup remains halted") from exc
