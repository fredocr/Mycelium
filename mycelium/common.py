"""Validation shared by the offline domain models."""

from datetime import datetime, timezone


class DomainError(ValueError):
    """An operation would violate a domain rule."""


def aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainError("A timezone-aware datetime is required")
    return value.astimezone(timezone.utc)


def nonempty(value: str) -> None:
    if not value.strip():
        raise DomainError("Text must not be empty")
