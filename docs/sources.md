# Primary references

Reviewed on 2026-10-14. These sources support specific design constraints, not a claim that Mycelium is compliant or that third-party internals are known. Recheck platform and legal requirements before a live integration. Project choices and pilot thresholds are proposals unless explicitly attributed below.

- **S1: Boardy, public product workflow.** Describes contextual discovery, both-side opt-in, introductions, and scheduling. Used as interaction-pattern inspiration only. https://www.boardy.ai/
- **S2: Telegram Bot FAQ.** Documents which updates bots receive, including the broader visibility of administrator bots. https://core.telegram.org/bots/faq
- **S3: Telegram Bot API, setWebhook.** Documents webhook authentication using the optional secret-token header. https://core.telegram.org/bots/api#setwebhook
- **S4: Google Calendar authorization scopes.** Distinguishes free/busy, event access, and app-created calendars; notes OAuth verification considerations. https://developers.google.com/workspace/calendar/api/auth
- **S5: RFC 5545.** Calendar content lines, UTF-8 folding, escaping, and event properties. The initial exporter implements a deliberately small single-event subset. https://www.rfc-editor.org/rfc/rfc5545.html
- **S6: PostgreSQL SELECT documentation.** Describes row locking and the queue-like use case for SKIP LOCKED; it is not a general consistency guarantee. https://www.postgresql.org/docs/current/sql-select.html
- **S7: Your Europe, data protection under GDPR.** Transparency, rights, consent, and privacy by design/default. https://europa.eu/youreurope/business/governance-and-sustainability/digital-and-data-compliance/data-protection-gdpr/index_en.htm
- **S8: European Commission, legal grounds for processing.** Discusses legal bases and valid consent, including unnecessary conditional processing. https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/legal-grounds-processing-data_en
- **S9: European Data Protection Board, Guidelines 05/2020.** Official entry point for consent guidance. https://www.edpb.europa.eu/documents/guideline/guidelines-052020-on-consent-under-regulation-2016679_en

Not verified here: Boardy's internal architecture; a particular WhatsApp business account's eligibility; availability of the Mycelium trademark/domain; institutional endorsement; a production vendor's contractual suitability. No product name or logo constitutes affiliation.
