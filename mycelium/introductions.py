"""Double opt-in transitions. No authentication, persistence, or sending.

The future application service must authenticate actors and load current member
snapshots from trusted storage. These objects are not an access-control API.
"""

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from uuid import UUID

from .common import DomainError, aware, nonempty


@dataclass(frozen=True, slots=True)
class MemberSnapshot:
    id: UUID
    community_id: UUID
    chapter_id: UUID
    revision: int = 1
    active: bool = True
    matching_enabled: bool = False
    cross_chapter_enabled: bool = False

    def __post_init__(self) -> None:
        if self.revision < 1:
            raise DomainError("Member revision must be positive")


def require_eligible(left: MemberSnapshot, right: MemberSnapshot) -> None:
    if left.id == right.id:
        raise DomainError("Cannot introduce a member to themselves")
    if left.community_id != right.community_id:
        raise DomainError("Cross-community introductions are not supported")
    if not all(m.active and m.matching_enabled for m in (left, right)):
        raise DomainError("Both members must be active and opted in")
    if left.chapter_id != right.chapter_id and not all(
        m.cross_chapter_enabled for m in (left, right)
    ):
        raise DomainError("Both members must allow cross-chapter matching")


@dataclass(frozen=True, slots=True, repr=False)
class Disclosure:
    """Exact recipient-facing card approved by its owner. Never log it."""

    name: str
    context: str
    contact: str

    def __post_init__(self) -> None:
        for value in (self.name, self.context, self.contact):
            nonempty(value)


class Status(str, Enum):
    PENDING = "pending"
    READY = "ready"
    DECLINED = "declined"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Approval:
    member_id: UUID
    proposal_digest: str
    at: datetime


@dataclass(frozen=True, slots=True)
class DispatchPlan:
    """Sensitive plan, not a sent message or durable outbox record."""

    idempotency_key: str
    left: Disclosure = field(repr=False)
    right: Disclosure = field(repr=False)
    purpose: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class Introduction:
    id: UUID
    left: MemberSnapshot
    right: MemberSnapshot
    left_card: Disclosure = field(repr=False)
    right_card: Disclosure = field(repr=False)
    purpose: str = field(repr=False)
    created_at: datetime
    expires_at: datetime
    version: int = 1
    approvals: tuple[Approval, ...] = ()
    status: Status = Status.PENDING

    def __post_init__(self) -> None:
        require_eligible(self.left, self.right)
        nonempty(self.purpose)
        if aware(self.expires_at) <= aware(self.created_at):
            raise DomainError("Expiry must follow creation")
        if self.version < 1:
            raise DomainError("Proposal version must be positive")

    @property
    def digest(self) -> str:
        payload = {
            "id": str(self.id), "version": self.version,
            "community": str(self.left.community_id),
            "left": str(self.left.id), "right": str(self.right.id),
            "left_revision": self.left.revision,
            "right_revision": self.right.revision,
            "left_card": asdict(self.left_card),
            "right_card": asdict(self.right_card),
            "purpose": self.purpose,
            "created": self.created_at.isoformat(),
            "expires": self.expires_at.isoformat(),
        }
        return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def _check_open(self, actor: UUID, now: datetime) -> None:
        if actor not in (self.left.id, self.right.id):
            raise DomainError("Actor is not a participant")
        if not self.created_at <= aware(now) < self.expires_at:
            raise DomainError("Proposal is not within its validity window")
        if self.status in (Status.CANCELLED, Status.DECLINED):
            raise DomainError("Proposal is closed")

    def approve(self, actor: UUID, digest: str, now: datetime) -> "Introduction":
        self._check_open(actor, now)
        if digest != self.digest:
            raise DomainError("Approval refers to an outdated proposal")
        if any(a.member_id == actor for a in self.approvals):
            return self
        approvals = self.approvals + (Approval(actor, digest, aware(now)),)
        status = Status.READY if len(approvals) == 2 else Status.PENDING
        return replace(self, approvals=approvals, status=status)

    def revise_card(
        self, actor: UUID, card: Disclosure, now: datetime
    ) -> "Introduction":
        self._check_open(actor, now)
        return replace(
            self,
            left_card=card if actor == self.left.id else self.left_card,
            right_card=card if actor == self.right.id else self.right_card,
            version=self.version + 1, approvals=(), status=Status.PENDING,
        )

    def close(self, actor: UUID, now: datetime, *, decline: bool = False) -> "Introduction":
        self._check_open(actor, now)
        status = Status.DECLINED if decline else Status.CANCELLED
        return replace(self, approvals=(), status=status)

    def prepare_dispatch(
        self, current_left: MemberSnapshot, current_right: MemberSnapshot,
        now: datetime,
    ) -> DispatchPlan:
        """Revalidate current state before producing any disclosure plan.

        Calling twice returns the same key, not an exactly-once delivery promise.
        Production needs transactional persistence and a dispatch-time recheck.
        """
        self._check_open(self.left.id, now)
        require_eligible(current_left, current_right)
        if current_left != self.left or current_right != self.right:
            raise DomainError("Member state changed; create a fresh proposal")
        actors = {a.member_id for a in self.approvals if a.proposal_digest == self.digest}
        if self.status != Status.READY or actors != {self.left.id, self.right.id}:
            raise DomainError("Both participants must approve this exact proposal")
        if any(not self.created_at <= a.at <= now for a in self.approvals):
            raise DomainError("Approval timestamp is invalid")
        return DispatchPlan(
            f"introduction:{self.id}:v{self.version}",
            self.left_card, self.right_card, self.purpose,
        )
