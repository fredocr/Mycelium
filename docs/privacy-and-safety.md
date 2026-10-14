# Privacy and safety design

Status: engineering requirements and proposed policies, not a privacy notice, legal opinion, or compliance certification. Use synthetic data until the live-pilot gates are satisfied.

## Governance before collection

Identify the legal operator and controller before enrolling real members. Determine whether the central alumni organization and chapter act independently or jointly; do not assume a chapter is a separate legal entity. Document processor relationships, access responsibilities, permitted branding, and the incident contact.

Hosting or developing the system does not give a technology provider permission to reuse alumni data for sales, fundraising, advertising, or model training. Community data must not flow into an unrelated commercial CRM.

Determine a legal basis for each processing purpose. Consent is not the only possible basis, but optional profile matching must not be bundled into unrelated community participation. Where consent is relied on, it needs to be specific, informed, freely given, and withdrawable. See the EU guidance in [S7-S9](sources.md).

## Separate choices

| Choice | Proposed default |
| --- | --- |
| View ordinary chapter event information | No matching profile required |
| Receive event-specific updates after RSVP | Explain requested communications and channel choice |
| Store a professional need or offer | Explicit member submission and confirmation |
| Be discoverable for matching | Off |
| Receive proactive suggestions | Off; separate from a one-time requested search |
| Permit cross-chapter discovery | Off |
| Share contact details with a particular person | Require per-introduction approval |
| Connect personal calendar availability | Off and optional |
| Retain raw conversational history | Off |
| Train models or use data for unrelated commercial outreach | Not a supported use |

These product settings do not themselves establish a legal basis. Record the approved purpose, applicable basis, notice version, and permission evidence in the future service.

## Proposed data handling

Collect the minimum required to fulfill the requested service. A networking fact should carry provenance, confirmation time, visibility, and expiry. AI inferences cannot silently become verified facts. Do not import chat histories or scrape LinkedIn/contact lists.

Use explicit private submissions for profile information. Even private bot messages pass through the messaging provider. Explain the actual processing chain rather than implying local hosting makes every channel private or EU-only.

Proposed starting retention settings, to be approved and justified by the controller:

- Raw conversations: not retained by Mycelium by default. Provider retention requires a separate assessment.
- Active needs/offers: expire after 90 days unless renewed.
- Introduction proposals: expire after seven days unless a different window is shown and agreed.
- Detailed delivery diagnostics: minimize and remove after 30 days unless an incident requires a justified hold.
- Encrypted backups: proposed 30-day rolling window, with tested expiry and restore-time deletion replay.
- Permission and audit evidence: retain only for a documented accountability purpose and justified period, not indefinitely by default.

These are proposed policies, not statutory deadlines or implemented deletion jobs.

## Member controls

Provide understandable commands or web controls for viewing and correcting a profile, pausing matching, withdrawing an optional permission, disconnecting a channel/calendar, requesting access/export, and requesting erasure. Withdrawal must stop pending matching and future optional messages without removing access to unrelated community activities.

Erasure must cover primary records, search indexes/embeddings, cached projections, queued messages, workflow logs, and processors where applicable. Handle backups through expiry and deletion replay after restoration. Some evidence may require restricted retention under an identified legal obligation or claim; do not promise unconditional instantaneous deletion of everything.

## Threats and required defenses

| Threat | Required defense before a live pilot |
| --- | --- |
| A forged request claims to be another member | Verified actor mapping; never trust a submitted member ID |
| Someone approves an old disclosure | Version/digest binding and re-approval after changes |
| Consent is withdrawn after a job is queued | Current-state checks, queue cancellation, dispatch serialization |
| Two workers send the same introduction | Transactional outbox, leases, delivery keys, ambiguous-result handling |
| A volunteer queries another chapter | Scoped role checks and tested storage access policies |
| A teaser identifies a private member | Owner-controlled teaser fields; no anonymity promise |
| A profile contains prompt injection | Treat text as data; constrained model outputs; no direct AI tools |
| Sensitive data leaks through logs | Body/token redaction, minimal projections, restricted diagnostics |
| A calendar title injects properties | Text escaping, CRLF handling, UTF-8-safe line folding |
| A shared feed leaks personal information | Explicit event visibility; no attendee list or private notes |
| A departing volunteer retains access | Role removal, credential review, documented handover |

## Required live-pilot gates

Name the controller and accountable operator; approve purpose/legal-basis mapping and member notice; screen whether a DPIA and other applicable obligations require further work; review vendor agreements and transfers; establish scoped authentication; test withdrawal and deletion; configure encrypted transport, secret management, backups, and monitoring; set an abuse-report channel and incident procedure.

EU hosting, a consent checkbox, or a double opt-in workflow does not independently establish GDPR compliance. These are engineering inputs to a broader operational assessment [S7-S9](sources.md).
