"""Run a synthetic, offline demonstration: python -m mycelium."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from .events import Event
from .introductions import Disclosure, Introduction, MemberSnapshot


def main() -> None:
    now = datetime(2030, 1, 1, 12, tzinfo=timezone.utc)
    community, chapter = UUID(int=1), UUID(int=2)
    left = MemberSnapshot(UUID(int=3), community, chapter, matching_enabled=True)
    right = MemberSnapshot(UUID(int=4), community, chapter, matching_enabled=True)
    proposal = Introduction(
        UUID(int=5), left, right,
        Disclosure("Example A", "Offers cloud mentoring", "a@example.invalid"),
        Disclosure("Example B", "Seeking cloud mentoring", "b@example.invalid"),
        "Discuss a voluntary mentoring session", now, now + timedelta(days=7),
    )
    proposal = proposal.approve(left.id, proposal.digest, now)
    proposal = proposal.approve(right.id, proposal.digest, now)
    plan = proposal.prepare_dispatch(left, right, now)
    print(f"Synthetic introduction ready: {plan.idempotency_key}")
    event = Event(UUID(int=6), chapter, "Synthetic community meetup", "Example venue",
                  now + timedelta(days=3), now + timedelta(days=3, hours=2)).approve()
    print(f"Reminder plans: {len(event.plan_reminders(now))}")
    print("Calendar export follows. No messages sent; no files written.")
    print(event.to_ical(now), end="")


if __name__ == "__main__":
    main()
