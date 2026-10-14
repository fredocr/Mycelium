# Architecture: a small application with explicit trust boundaries

Status: target design. The initial Python code implements offline domain rules only. Authentication, database storage, webhooks, workers, and external delivery are not implemented.

## 1. Decision: modular monolith, not an agent platform

Use one Python application with separable domain modules and one PostgreSQL database when persistence is introduced. The API and worker can run as separate processes from the same codebase. Start with one community and one chapter; maintain community and chapter scope from the first persistent schema.

```text
Telegram / small web interface / later channel adapters
                         |
             verified identity + request limits
                         |
               application use cases
                         |
       membership | events | permissions | introductions
                         |
        PostgreSQL transaction + durable outbox
                         |
              worker + final policy check
                         |
             messaging / calendar adapters

Optional AI: allowed profile projection -> suggestion -> human/member approval
```

No Redis, Kafka, graph database, vector service, multi-agent framework, or n8n dependency in the initial foundation. A future n8n adapter may help volunteers configure non-sensitive workflows, but must call the same application API. It must not bypass authorization or write member records directly. PostgreSQL is a target, not a shipped dependency.

## 2. Boundaries

| Module | Owns | Must not do |
| --- | --- | --- |
| Membership | Verified channel links, community membership, scoped coordinator roles | Merge people by name or expose all community profiles |
| Permissions | Purpose-specific grants, visibility, current restrictions, evidence | Treat a model response or group membership as permission |
| Events | Draft/approval/cancellation, RSVP state, task ownership | Promise spending, publish unapproved details, reveal attendee lists |
| Introductions | Proposals, exact disclosure versions, both-side approvals, expiry | Share contacts after one approval or after withdrawal |
| Matching | Filter eligible needs/offers, explain relevance | Search excluded profiles or infer sensitive attributes |
| Delivery | Outbox, retry policy, quiet hours, delivery status | Invent permission or equate queued with delivered |
| AI adapter | Structured extraction and optional reranking | Receive the whole database or execute tools autonomously |

Keep channel identifiers and OAuth tokens outside profile-search projections. Volunteers do not need unrestricted access to private needs or contact details.

## 3. Identity and authorization

A Telegram username, email address in a message, or client-supplied `member_id` is not authentication. Bind provider identities through a verified onboarding flow. Resolve the actor server-side. Linking a second channel requires proof of control of both identities, with expiring, single-use tokens.

Use membership records scoped to a community, with separate chapter memberships and role assignments. The same person may participate in multiple communities without those communities sharing their profiles. Cross-community matching remains unsupported. Cross-chapter matching within one community requires explicit permission from both participants.

The offline `MemberSnapshot` is a trusted-input domain object, not authentication, a consent ledger, or a public API request schema. A caller who controls Python objects can construct arbitrary state. Production adapters must not deserialize arbitrary member snapshots from requests.

## 4. Minimal persistent model, planned

| Records | Important fields or constraints |
| --- | --- |
| communities, chapters | Chapter belongs to exactly one community |
| memberships, role_assignments | Community-scoped identity; explicit chapter access; active state |
| channel_links | Verified provider identifier; restricted access; no name-based deduplication |
| permission_events | Purpose, grant/withdraw event, notice version, effective time, evidence reference |
| profile_facts, needs, offers | Member-confirmed value, source, visibility, expiry, revision |
| events, rsvps, volunteer_tasks | Owner, status, version, UTC instant and relevant IANA timezone |
| introductions, approvals | Participant IDs, immutable disclosure snapshot, digest, timestamps, expiry |
| processed_updates | Unique provider/update ID for replay protection |
| outbox, delivery_attempts | Scoped recipient, action ID, due time, state, retry and provider references |
| audit_events, deletion_jobs | Restricted, minimal records and explicit retention |

Use foreign keys, uniqueness constraints, and migration tests. When adding row-level security, test with the actual application role, not an owner or bypass role. Application authorization remains necessary. No SQL migration is presented as production-ready in this foundation.

## 5. Introduction protocol

1. Member deliberately submits an active need and permitted disclosure.
2. Eligibility filters run before any candidate data reaches an AI model or requester.
3. A coordinator reviews the first pilot proposals. Only owner-authorized teaser fields are shown before mutual approval. A unique employer or role may identify somebody, so do not call teasers anonymous by default.
4. Each participant sees their own exact disclosure, the purpose, recipient context permitted for the teaser, and expiry. The server records approval bound to an immutable proposal digest. The digest is neither authentication nor a secret capability.
5. Changing either disclosure resets both approvals. Changing purpose, participants, membership permissions, or relevant profile revision requires a fresh proposal.
6. Before enqueue and again immediately before dispatch, reload current membership, permissions, blocks, expiry, and proposal state.
7. Only then prepare the minimum approved contact exchange. Record separately whether delivery was attempted, accepted by a provider, or confirmed by a participant.

```text
PENDING -> one approval -> PENDING -> second approval -> READY
    |                         |                         |
    +-------------------- decline/cancel --------------+

READY -> policy recheck -> durable dispatch -> delivery result  [future]
Expiry blocks approval and dispatch from either open state.
A changed disclosure returns an open proposal to PENDING.
```

The initial code ends at a `DispatchPlan`. It does not send, persist, or declare an introduction completed. `repr` suppression is a logging precaution, not encryption or access control.

## 6. Reliable side effects

For the live pilot, commit state changes and outbox records in one database transaction. Deduplicate incoming updates using the provider update ID. Workers claim eligible jobs under a lease; PostgreSQL documents queue-like uses of `SKIP LOCKED` [S6](sources.md).

Delivery is at-least-once processing with application-level deduplication, not a blanket exactly-once guarantee. Use provider idempotency keys where supported. Where a provider timeout leaves delivery uncertain, record `unknown` and reconcile or escalate instead of blindly resending a sensitive introduction. Store per-recipient delivery status when a two-person exchange can partially succeed.

Withdrawal closes pending work and suppresses future delivery. Serialize permission changes and dispatch reservations in the application. An external delivery already in flight cannot reliably be recalled. Explain this boundary honestly; keep the reservation-to-send interval short and reconcile failures.

For reminders, the durable key must include event version, recipient, channel, and reminder type. The offline event planner returns only an event-level planning key. It does not prove recipient eligibility or suppress duplicate provider deliveries.

## 7. Channel and calendar approach

**Telegram first:** privacy mode enabled, bot not a group administrator, explicit command allowlist, private profile onboarding, and a verified mapping of allowed group IDs to chapters. Telegram documents that admin bots can receive ordinary group messages despite privacy mode [S2](sources.md). Drop irrelevant updates before persistence and avoid logging message bodies. Bot conversations are not a place for sensitive disclosures.

The future webhook verifies `X-Telegram-Bot-Api-Secret-Token`, limits body size, deduplicates update IDs, and validates callback ownership. Telegram documents webhook secret tokens [S3](sources.md). Do not place personal data in callback payloads. Creating a bot or obtaining a chat ID is not authorization to message everyone.

**Calendars:** begin with an approved event export and later a chapter calendar or permissioned subscription feed. A downloaded `.ics` file is not a subscription and does not automatically propagate cancellations or updates. The initial exporter omits attendee and organizer contacts and follows a small RFC 5545 subset [S5](sources.md).

Later, offer optional free/busy access for scheduling. Google's `calendar.freebusy` scope is separate from event-writing permissions; `calendar.app.created` applies to secondary calendars created by the application, not arbitrary personal events [S4](sources.md). Do not assume this removes OAuth verification requirements.

Store real instants in UTC and preserve the event's IANA timezone for display and recurrence. Define daylight-saving ambiguity, rescheduling, cancellation, and overdue-reminder behavior before supporting recurring events. The offline planner skips overdue reminders rather than replaying them.

**WhatsApp later:** use only a supported, reviewed integration. Do not base the pilot on unofficial WhatsApp Web automation or assume APIs can read an existing large alumni group. Reverify current platform eligibility, messaging rules, consent, and pricing at implementation time.

## 8. AI only after a manual baseline

Initially use explicit tags, active needs/offers, and coordinator judgment. Introduce structured extraction after members can review and correct it. Evaluate AI suggestions against that baseline before adding semantic search.

The model receives only eligible, purpose-limited projections. Names, contacts, raw conversations, and calendar contents are excluded unless genuinely necessary and authorized. Treat submitted text as untrusted data, not instructions. Validate outputs against a schema and require source fact IDs. Unknown facts remain unknown. AI failure falls back to manual workflows.

Do not train on member data, infer sensitive characteristics, rank member worth, or turn lack of responsiveness into a hidden reputation score. Provider contracts, retention, subprocessors, and transfer assessments remain launch requirements.

## 9. Implementation status

Implemented offline: immutable introduction transitions, matching eligibility rules, proposal digests, withdrawal/expiry revalidation, approved event export, reminder planning, synthetic demo, and unit tests.

Not implemented: verified users, full permission evidence, persistent state, UI, webhooks, RSVP storage, worker, real notifications, calendar OAuth, AI, deletion/export service, backups, or operational security. Passing domain tests is not production readiness or GDPR certification.
