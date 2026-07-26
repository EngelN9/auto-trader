"""Minimal immutable domain event contracts for repository bootstrap."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from trading_system.config.models import EnvironmentMode


def compute_payload_checksum(payload: dict[str, Any]) -> str:
    """Return a deterministic SHA-256 over a canonical JSON payload."""

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class DomainEvent(BaseModel):
    """Common immutable envelope required by every future event."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID
    schema_version: str
    source: str
    venue: str
    symbol: str
    correlation_id: UUID
    causation_id: UUID
    event_time_utc: datetime
    ingest_time_utc: datetime
    sequence_number: int
    payload_checksum: str

    @field_validator("event_time_utc", "ingest_time_utc")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise ValueError("event timestamps must be timezone-aware UTC")
        return value

    @field_validator("sequence_number")
    @classmethod
    def require_non_negative_sequence(cls, value: int) -> int:
        if value < 0:
            raise ValueError("sequence_number cannot be negative")
        return value

    @field_validator("payload_checksum")
    @classmethod
    def require_sha256(cls, value: str) -> str:
        if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
            raise ValueError("payload_checksum must be a lowercase SHA-256 hex digest")
        return value


class Heartbeat(DomainEvent):
    service: str
    status: str
    mode: EnvironmentMode
