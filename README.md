# Mycelium

**Less coordination work. More meaningful community connections.**

Mycelium is a privacy-first coordination system for communities. It helps people organize activities, discover relevant opportunities, and make mutually approved introductions through the channels they already use.

## Why this exists

A community can contain valuable knowledge, generous people, and shared interests while still struggling to act on them. Context sits in separate conversations. Introductions depend on someone remembering who can help. Events depend on volunteers repeatedly chasing dates, RSVPs, and follow-ups.

The problem is not a lack of connections. It is the effort needed to turn those connections into useful, sustained participation.

Mycelium aims to reduce that administrative burden without replacing the relationships, judgment, and trust that make a community valuable. Members should receive a clear benefit before they are asked for additional information or permissions.

## Initial pilot

The proposed first pilot is the Berlin chapter of the 28 Digital Alumni Network, using Telegram for initial interaction and calendar links for events. This is a proposed use case, not a claim of institutional endorsement, an approved deployment, or access to alumni data.

Start with three journeys:

1. **Organize a meetup:** a volunteer approves an event; members RSVP; the system handles appropriate reminders.
2. **Offer or ask for help:** a member chooses what professional context to share and confirms the resulting profile.
3. **Make an introduction:** the system proposes a relevant connection; both people approve the exact information to be shared before an introduction is sent.

WhatsApp, private calendar availability, AI-assisted matching, and cross-chapter discovery are later capabilities, not prerequisites for joining.

## Principles

- Participation in the community must not require participation in AI matching.
- Store confirmed, purpose-specific context rather than harvesting group conversations.
- Separate identity, profile visibility, communication preferences, and per-introduction approval.
- Let software handle repetitive coordination; keep people in charge of commitments and relationships.
- Treat AI output as a proposal, never as authorization.
- Prefer one small application and a relational database over a multi-agent or microservice platform.
- Measure useful connections and volunteer time saved, not message volume or data collected.

## Scope and status

This repository starts with the motivation and pilot boundaries. Architecture documentation and an executable, offline domain foundation are the next increments. There is no deployed service, live messaging integration, calendar connection, or production data processing in this initial commit.

The project is inspired by contextual, mutually approved introductions, including Boardy's publicly described product workflow. It is not affiliated with Boardy and does not reproduce or claim knowledge of Boardy's internal architecture.

**Non-goals:** scraping chat histories or contact lists, autonomous outreach, advertising profiles, automated hiring decisions, mandatory calendar access, or replacing existing community channels.

## Name and governance

Mycelium is a metaphor for connections that support a wider community, not a biological claim about how this software works.

Before any real-member pilot, the operator must establish the responsible data controller, appropriate legal bases, a privacy notice, access rules, processor agreements, security procedures, and institutional permissions. Privacy-first design is not a certification of GDPR compliance.

The software license has not yet been selected. A public repository alone should not be treated as an open-source license grant. Use synthetic examples only; never commit member records, contact details, credentials, or private conversations.
