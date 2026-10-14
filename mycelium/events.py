"""Approved event exports and reminder planning, without external side effects."""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID

from .common import DomainError, aware, nonempty


class EventStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    CANCELLED = "cancelled"


def _escape(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return (value.replace("\\", "\\\\").replace("\n", "\\n")
            .replace(";", "\\;").replace(",", "\\,"))


def _fold(line: str) -> str:
    """Fold at 75 UTF-8 octets without splitting a Unicode code point."""
    lines: list[str] = []
    part = ""
    for char in line:
        if len((part + char).encode("utf-8")) > 75:
            lines.append(part)
            part = " "
        part += char
    lines.append(part)
    return "\r\n".join(lines)


def _stamp(value: datetime) -> str:
    return aware(value).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@dataclass(frozen=True, slots=True)
class Reminder:
    idempotency_key: str
    due_at: datetime


@dataclass(frozen=True, slots=True)
class Event:
    id: UUID
    chapter_id: UUID
    title: str
    location: str
    starts_at: datetime
    ends_at: datetime
    status: EventStatus = EventStatus.DRAFT
    version: int = 1

    def __post_init__(self) -> None:
        nonempty(self.title)
        nonempty(self.location)
        if aware(self.ends_at) <= aware(self.starts_at):
            raise DomainError("Event must end after it starts")
        if self.version < 1:
            raise DomainError("Event version must be positive")
        for value in (self.title, self.location):
            if any(ord(c) < 32 and c not in "\r\n\t" for c in value):
                raise DomainError("Unsupported control character in event text")

    def approve(self) -> "Event":
        """Call only after the application authorizes a chapter coordinator."""
        if self.status == EventStatus.CANCELLED:
            raise DomainError("Cancelled events cannot be approved")
        return replace(self, status=EventStatus.APPROVED)

    def cancel(self) -> "Event":
        return replace(self, status=EventStatus.CANCELLED)

    def to_ical(self, generated_at: datetime) -> str:
        """Export a single event, not a subscription feed or RSVP invitation."""
        if self.status != EventStatus.APPROVED:
            raise DomainError("Only approved events can be exported")
        lines = [
            "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Mycelium//Pilot//EN",
            "BEGIN:VEVENT", f"UID:{self.id}@mycelium.invalid",
            f"DTSTAMP:{_stamp(generated_at)}", f"SEQUENCE:{self.version - 1}",
            f"DTSTART:{_stamp(self.starts_at)}", f"DTEND:{_stamp(self.ends_at)}",
            f"SUMMARY:{_escape(self.title)}", f"LOCATION:{_escape(self.location)}",
            "STATUS:CONFIRMED", "END:VEVENT", "END:VCALENDAR",
        ]
        return "\r\n".join(_fold(line) for line in lines) + "\r\n"

    def plan_reminders(
        self, now: datetime, offsets: tuple[timedelta, ...] = (timedelta(days=1),),
    ) -> tuple[Reminder, ...]:
        aware(now)
        if any(offset <= timedelta(0) for offset in offsets):
            raise DomainError("Reminder offsets must be positive")
        if self.status != EventStatus.APPROVED:
            return ()
        plans = []
        start = self.starts_at.astimezone(timezone.utc)
        for offset in sorted(set(offsets), reverse=True):
            due = start - offset
            if due > now:
                key = f"event:{self.id}:v{self.version}:before:{offset.total_seconds()}"
                plans.append(Reminder(key, due))
        return tuple(plans)
