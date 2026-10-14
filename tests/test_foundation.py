"""Safety-oriented tests using only synthetic identities and offline state."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest
from uuid import UUID
from zoneinfo import ZoneInfo

from mycelium.common import DomainError
from mycelium.events import Event
from mycelium.introductions import Disclosure, Introduction, MemberSnapshot, Status

NOW = datetime(2030, 1, 1, 12, tzinfo=timezone.utc)


class IntroductionTests(unittest.TestCase):
    def setUp(self):
        self.a = MemberSnapshot(UUID(int=1), UUID(int=10), UUID(int=20), matching_enabled=True)
        self.b = replace(self.a, id=UUID(int=2))
        self.p = Introduction(
            UUID(int=30), self.a, self.b,
            Disclosure("Example A", "Offers mentoring", "a@example.invalid"),
            Disclosure("Example B", "Seeks mentoring", "b@example.invalid"),
            "Mentoring", NOW, NOW + timedelta(days=7),
        )

    def ready(self):
        p = self.p.approve(self.a.id, self.p.digest, NOW)
        return p.approve(self.b.id, p.digest, NOW)

    def test_matching_is_off_by_default(self):
        self.assertFalse(MemberSnapshot(UUID(int=1), UUID(int=2), UUID(int=3)).matching_enabled)

    def test_two_approvals_required(self):
        with self.assertRaises(DomainError):
            self.p.prepare_dispatch(self.a, self.b, NOW)
        p = self.p.approve(self.a.id, self.p.digest, NOW)
        with self.assertRaises(DomainError):
            p.prepare_dispatch(self.a, self.b, NOW)

    def test_double_opt_in_allows_plan(self):
        plan = self.ready().prepare_dispatch(self.a, self.b, NOW)
        self.assertEqual(plan.left.name, "Example A")

    def test_repeat_approval_does_not_count_twice(self):
        p = self.p.approve(self.a.id, self.p.digest, NOW)
        self.assertIs(p.approve(self.a.id, p.digest, NOW), p)
        self.assertEqual(p.status, Status.PENDING)

    def test_repeat_plan_has_stable_key(self):
        p = self.ready()
        self.assertEqual(p.prepare_dispatch(self.a, self.b, NOW).idempotency_key,
                         p.prepare_dispatch(self.a, self.b, NOW).idempotency_key)

    def test_unrelated_actor_rejected(self):
        with self.assertRaises(DomainError):
            self.p.approve(UUID(int=999), self.p.digest, NOW)

    def test_wrong_digest_rejected(self):
        with self.assertRaises(DomainError):
            self.p.approve(self.a.id, "outdated", NOW)

    def test_revision_resets_both_approvals(self):
        p = self.ready().revise_card(self.a.id, Disclosure("Example A", "Updated", "a@example.invalid"), NOW)
        self.assertEqual(p.approvals, ())
        self.assertEqual(p.version, 2)
        with self.assertRaises(DomainError):
            p.approve(self.b.id, self.p.digest, NOW)

    def test_decline_is_terminal(self):
        p = self.p.close(self.b.id, NOW, decline=True)
        with self.assertRaises(DomainError):
            p.approve(self.a.id, p.digest, NOW)

    def test_cancel_blocks_dispatch(self):
        p = self.ready().close(self.a.id, NOW)
        with self.assertRaises(DomainError):
            p.prepare_dispatch(self.a, self.b, NOW)

    def test_withdrawal_blocks_ready_plan(self):
        with self.assertRaises(DomainError):
            self.ready().prepare_dispatch(self.a, replace(self.b, matching_enabled=False), NOW)

    def test_deactivation_blocks_ready_plan(self):
        with self.assertRaises(DomainError):
            self.ready().prepare_dispatch(replace(self.a, active=False), self.b, NOW)

    def test_member_revision_change_requires_new_proposal(self):
        with self.assertRaises(DomainError):
            self.ready().prepare_dispatch(self.a, replace(self.b, revision=2), NOW)

    def test_wrong_member_snapshot_rejected(self):
        with self.assertRaises(DomainError):
            self.ready().prepare_dispatch(self.a, replace(self.b, id=UUID(int=999)), NOW)

    def test_expiry_blocks_approval_and_dispatch(self):
        with self.assertRaises(DomainError):
            self.p.approve(self.a.id, self.p.digest, self.p.expires_at)
        with self.assertRaises(DomainError):
            self.ready().prepare_dispatch(self.a, self.b, self.p.expires_at)

    def test_before_creation_rejected(self):
        with self.assertRaises(DomainError):
            self.p.approve(self.a.id, self.p.digest, NOW - timedelta(seconds=1))

    def test_cross_community_rejected(self):
        with self.assertRaises(DomainError):
            replace(self.p, right=replace(self.b, community_id=UUID(int=11)))

    def test_cross_chapter_needs_both_permissions(self):
        b = replace(self.b, chapter_id=UUID(int=21), cross_chapter_enabled=True)
        with self.assertRaises(DomainError):
            replace(self.p, right=b)
        p = replace(self.p, left=replace(self.a, cross_chapter_enabled=True), right=b)
        self.assertEqual(p.right.chapter_id, b.chapter_id)

    def test_self_match_rejected(self):
        with self.assertRaises(DomainError):
            replace(self.p, right=self.a)

    def test_naive_datetimes_rejected(self):
        with self.assertRaises(DomainError):
            self.p.approve(self.a.id, self.p.digest, NOW.replace(tzinfo=None))
        with self.assertRaises(DomainError):
            replace(self.p, expires_at=NOW.replace(tzinfo=None))

    def test_nonpositive_revision_rejected(self):
        with self.assertRaises(DomainError):
            replace(self.a, revision=0)

    def test_empty_disclosure_rejected(self):
        with self.assertRaises(DomainError):
            Disclosure("Example A", " ", "a@example.invalid")

    def test_repr_excludes_contact_cards(self):
        self.assertNotIn("a@example.invalid", repr(self.ready()))
        self.assertNotIn("a@example.invalid", repr(self.ready().prepare_dispatch(self.a, self.b, NOW)))


class EventTests(unittest.TestCase):
    def setUp(self):
        self.event = Event(UUID(int=40), UUID(int=20), "Synthetic meetup", "Example venue",
                           NOW + timedelta(days=3), NOW + timedelta(days=3, hours=2))

    def test_draft_cannot_export_or_plan_reminders(self):
        with self.assertRaises(DomainError):
            self.event.to_ical(NOW)
        self.assertEqual(self.event.plan_reminders(NOW), ())

    def test_approved_event_exports_without_attendees(self):
        ics = self.event.approve().to_ical(NOW)
        self.assertIn("DTSTART:20300104T120000Z\r\n", ics)
        self.assertNotIn("ATTENDEE", ics)
        self.assertNotIn("ORGANIZER", ics)
        self.assertTrue(ics.endswith("END:VCALENDAR\r\n"))

    def test_invalid_times_rejected(self):
        with self.assertRaises(DomainError):
            replace(self.event, ends_at=self.event.starts_at)
        with self.assertRaises(DomainError):
            replace(self.event, starts_at=NOW.replace(tzinfo=None))

    def test_newline_injection_is_escaped(self):
        event = replace(self.event, title="Meetup\r\nATTENDEE:someone").approve()
        ics = event.to_ical(NOW)
        self.assertNotIn("\r\nATTENDEE:", ics)
        self.assertIn("SUMMARY:Meetup\\nATTENDEE:someone", ics)

    def test_utf8_folding_and_text_escaping(self):
        title = "\u00e9" * 80 + ", meeting; \\"
        ics = replace(self.event, title=title).approve().to_ical(NOW)
        self.assertTrue(all(len(line.encode()) <= 75 for line in ics.split("\r\n")))
        unfolded = ics.replace("\r\n ", "")
        self.assertIn("\u00e9" * 80 + "\\, meeting\\; \\\\" , unfolded)

    def test_cancelled_event_cannot_reapprove(self):
        event = self.event.approve().cancel()
        with self.assertRaises(DomainError):
            event.approve()
        with self.assertRaises(DomainError):
            event.to_ical(NOW)
        self.assertEqual(event.plan_reminders(NOW), ())

    def test_reminder_plan_deduplicates_offsets(self):
        offsets = (timedelta(days=1), timedelta(days=1), timedelta(hours=1))
        plans = self.event.approve().plan_reminders(NOW, offsets)
        self.assertEqual(len(plans), 2)
        self.assertLess(plans[0].due_at, plans[1].due_at)
        self.assertNotEqual(plans[0].idempotency_key, plans[1].idempotency_key)

    def test_late_reminders_not_replayed(self):
        self.assertEqual(self.event.approve().plan_reminders(self.event.starts_at), ())

    def test_invalid_offset_rejected(self):
        with self.assertRaises(DomainError):
            self.event.approve().plan_reminders(NOW, (timedelta(0),))

    def test_timezone_converted_to_utc(self):
        local = timezone(timedelta(hours=2))
        event = replace(self.event, starts_at=datetime(2030, 1, 4, 14, tzinfo=local)).approve()
        self.assertIn("DTSTART:20300104T120000Z", event.to_ical(NOW))

    def test_daylight_saving_fold_compares_real_instants(self):
        berlin = ZoneInfo("Europe/Berlin")
        event = replace(
            self.event,
            starts_at=datetime(2030, 10, 27, 2, 30, tzinfo=berlin, fold=0),
            ends_at=datetime(2030, 10, 27, 2, 15, tzinfo=berlin, fold=1),
        ).approve()
        ics = event.to_ical(NOW)
        self.assertIn("DTSTART:20301027T003000Z", ics)
        self.assertIn("DTEND:20301027T011500Z", ics)

    def test_control_characters_rejected(self):
        with self.assertRaises(DomainError):
            replace(self.event, title="Unsafe\x00title")


if __name__ == "__main__":
    unittest.main()
