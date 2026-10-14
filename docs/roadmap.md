# Roadmap and acceptance gates

This is a delivery sequence, not a promised calendar schedule. Do not enable a later stage simply because a planned week has arrived.

## Foundation: current scope

Mission, architecture, privacy boundaries, offline domain models, a synthetic CLI demonstration, and automated tests. No accounts, credentials, real-member data, deployments, or external notifications.

The foundation should run with Python 3.11+ and its standard library. Test locally with `python -m unittest discover -s tests -v`; run `python -m mycelium` for the synthetic demonstration.

## Milestone 1: one approved event, end to end

Build verified coordinator/member identities, community and chapter scoping, PostgreSQL migrations, RSVP state, a Telegram adapter, and a transactional outbox worker. Connect only a chapter-controlled bot. Keep profile matching disabled.

Acceptance:

- Coordinator approval is required before publication. No member can impersonate a coordinator by submitting an ID.
- Replayed webhook updates do not duplicate RSVPs or jobs.
- A restart preserves state and scheduled reminders.
- A cancelled/rescheduled event suppresses obsolete reminders and clearly communicates updates to eligible recipients.
- Each reminder checks current RSVP, channel preference, event version, quiet hours, and cancellation immediately before dispatch.
- A member can attend without providing a professional profile or calendar access.
- Complete one event cycle and compare actual volunteer work with the manual baseline.
- All privacy and operational launch gates are complete before enrolling real members.

## Milestone 2: a small, reviewed introduction pilot

Add member-confirmed needs/offers, purpose-specific permission evidence, profile controls, rate limits, blocking/reporting, and a coordinator review queue. Start with explicit tags and human judgment rather than an LLM.

Acceptance:

- Both members approve their exact permitted disclosure before contact exchange.
- A changed disclosure invalidates old approvals.
- Withdrawal or expiry after approval prevents unsent disclosures.
- Partial delivery and provider timeouts are visible; uncertain deliveries are not blindly retried.
- A declined introduction does not disclose a private reason or become a negative reputation score.
- Review the first 10 proposals and report raw counts at each stage, including feedback response counts.

## Milestone 3: assistance, not autonomous control

Add conversational extraction, optional semantic matching, and private suggestions only after the manual workflow is useful. Review the actual AI provider contract and processing settings before sending member information.

Acceptance:

- Members confirm extracted facts before use.
- Candidate eligibility is applied before model access.
- Suggestions identify supporting approved facts and do not invent relationships.
- Adversarial profile text cannot disclose other profiles or trigger a tool action.
- A failed/unavailable model leaves events and manually reviewed introductions operational.
- Demonstrate usefulness beyond the manual baseline without increasing unwanted contact.

## Milestone 4: additional channels and chapters

Reverify WhatsApp's current supported capabilities and rules before implementation. Add optional free/busy calendar access only after user value and permission boundaries are clear. Cross-chapter discovery is opt-in; cross-community data sharing requires a separate governance and architecture decision.

Do not add independent chapter databases or a graph database until a concrete requirement justifies the operating cost.

## Pilot scorecard

| Measure | Definition |
| --- | --- |
| Coordination effort | Recorded volunteer minutes per comparable event |
| Introduction acceptance | Both-side approvals divided by eligible proposals actually sent |
| Meeting follow-through | Participant-confirmed meetings divided by mutually accepted introductions |
| Usefulness | Useful ratings divided by feedback responses, shown alongside response rate |
| Member burden | Suggestions per member, declines, pauses, opt-outs, unwanted-contact reports |
| Reliability | Duplicate deliveries, overdue jobs, failed/unknown sends, cancellation failures |

Any unauthorized disclosure pauses introduction delivery pending investigation. Low participation calls for product discovery, not more aggressive collection or messaging.

## Decisions still open

Institutional authorization, legal operator/controller, software license, hosting and processor selection, membership verification, support ownership, approved retention periods, budget, and the date/participant group for a real pilot. None should be inferred from the existence of this public repository.
