from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar


T = TypeVar("T")


class AuthorizationDecision(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class ReasonCategory(Enum):
    AUTHENTICATION_INVALID = "AUTHENTICATION_INVALID"
    PRINCIPAL_UNRESOLVED = "PRINCIPAL_UNRESOLVED"
    BUSINESS_ENTITY_INVALID = "BUSINESS_ENTITY_INVALID"
    BUSINESS_ENTITY_MISMATCH = "BUSINESS_ENTITY_MISMATCH"
    MEMBERSHIP_INVALID = "MEMBERSHIP_INVALID"
    SCOPE_INVALID = "SCOPE_INVALID"
    RESOURCE_UNRESOLVED = "RESOURCE_UNRESOLVED"
    RESOURCE_MISMATCH = "RESOURCE_MISMATCH"
    ACTION_UNSUPPORTED = "ACTION_UNSUPPORTED"
    ACTION_NOT_APPLICABLE = "ACTION_NOT_APPLICABLE"
    ENTITLEMENT_MISSING = "ENTITLEMENT_MISSING"
    ENTITLEMENT_NOT_APPLICABLE = "ENTITLEMENT_NOT_APPLICABLE"
    ENTITLEMENT_REVOKED = "ENTITLEMENT_REVOKED"
    AUTHORITY_UNAVAILABLE = "AUTHORITY_UNAVAILABLE"
    AUTHORIZATION_CONFLICT = "AUTHORIZATION_CONFLICT"
    STATE_STALE = "STATE_STALE"
    UNKNOWN_STATE = "UNKNOWN_STATE"


class RequestedAction(Enum):
    VIEW = "VIEW"
    DOWNLOAD = "DOWNLOAD"
    SUBMIT = "SUBMIT"
    EXPLAIN = "EXPLAIN"


class ResourceClass(Enum):
    EXECUTIVE_DASHBOARD = "EXECUTIVE_DASHBOARD"
    REPORT = "REPORT"
    ASSESSMENT_SUBMISSION = "ASSESSMENT_SUBMISSION"


class ResourceActionApplicability(Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNRESOLVED = "UNRESOLVED"


class AuthorityRecordState(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISABLED = "DISABLED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class AuthorityLookupStatus(Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTING = "CONFLICTING"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    MALFORMED = "MALFORMED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class AuthorityLookupResult(Generic[T]):
    status: AuthorityLookupStatus
    records: tuple[T, ...] = ()

    @classmethod
    def found(cls, record: T) -> "AuthorityLookupResult[T]":
        return cls(AuthorityLookupStatus.FOUND, (record,))

    @classmethod
    def missing(cls) -> "AuthorityLookupResult[T]":
        return cls(AuthorityLookupStatus.NOT_FOUND)

    @classmethod
    def unavailable(cls) -> "AuthorityLookupResult[T]":
        return cls(AuthorityLookupStatus.UNAVAILABLE)

    @classmethod
    def stale(cls) -> "AuthorityLookupResult[T]":
        return cls(AuthorityLookupStatus.STALE)

    @classmethod
    def ambiguous(cls, records: tuple[T, ...] = ()) -> "AuthorityLookupResult[T]":
        return cls(AuthorityLookupStatus.AMBIGUOUS, records)

    @classmethod
    def conflicting(cls, records: tuple[T, ...] = ()) -> "AuthorityLookupResult[T]":
        return cls(AuthorityLookupStatus.CONFLICTING, records)


@dataclass(frozen=True)
class TrustedSubjectEvidence:
    provider: str
    subject: str
    verified: bool


@dataclass(frozen=True)
class AuthorizationRequest:
    subject_evidence: TrustedSubjectEvidence | None
    resource_reference: str | None
    requested_action: RequestedAction | str | None
    governed_version_context: "GovernedVersionContext | None"
    correlation_id: str
    evaluation_context: str


@dataclass(frozen=True)
class GovernedVersionContext:
    authorization_semantics_version: str
    applicability_governance_version: str
    evaluation_context: str


@dataclass(frozen=True)
class AuthorityRecord:
    authority_reference: str
    state: AuthorityRecordState


@dataclass(frozen=True)
class PrincipalMapping(AuthorityRecord):
    subject_provider: str
    subject: str
    principal_id: str


@dataclass(frozen=True)
class BusinessEntity(AuthorityRecord):
    business_entity_id: str


@dataclass(frozen=True)
class Membership(AuthorityRecord):
    principal_id: str
    business_entity_id: str


@dataclass(frozen=True)
class GovernedResource(AuthorityRecord):
    resource_id: str
    resource_reference: str
    resource_class: ResourceClass
    business_entity_id: str


@dataclass(frozen=True)
class Entitlement(AuthorityRecord):
    principal_id: str
    business_entity_id: str
    resource_id: str
    action: RequestedAction


@dataclass(frozen=True)
class AuthorizationAuditEvidence:
    decision_id: str
    correlation_id: str
    evaluation_context: str
    principal_id: str | None
    business_entity_id: str | None
    resource_id: str | None
    resource_class: ResourceClass | None
    requested_action: RequestedAction | None
    applicability: ResourceActionApplicability
    authority_inputs: tuple[str, ...]
    decision: AuthorizationDecision
    reason: ReasonCategory | None
    semantics_version: str
    applicability_version: str

    def with_decision_id(self, decision_id: str) -> "AuthorizationAuditEvidence":
        return AuthorizationAuditEvidence(
            decision_id=decision_id,
            correlation_id=self.correlation_id,
            evaluation_context=self.evaluation_context,
            principal_id=self.principal_id,
            business_entity_id=self.business_entity_id,
            resource_id=self.resource_id,
            resource_class=self.resource_class,
            requested_action=self.requested_action,
            applicability=self.applicability,
            authority_inputs=self.authority_inputs,
            decision=self.decision,
            reason=self.reason,
            semantics_version=self.semantics_version,
            applicability_version=self.applicability_version,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "decisionId": self.decision_id,
            "correlationId": self.correlation_id,
            "evaluationContext": self.evaluation_context,
            "principalId": self.principal_id,
            "businessEntityId": self.business_entity_id,
            "resourceId": self.resource_id,
            "resourceClass": (
                self.resource_class.value
                if self.resource_class is not None
                else None
            ),
            "requestedAction": (
                self.requested_action.value
                if self.requested_action is not None
                else None
            ),
            "applicability": self.applicability.value,
            "authorityInputs": list(self.authority_inputs),
            "decision": self.decision.value,
            "reason": self.reason.value if self.reason is not None else None,
            "semanticsVersion": self.semantics_version,
            "applicabilityVersion": self.applicability_version,
        }


@dataclass(frozen=True)
class AuthorizationResult:
    decision: AuthorizationDecision
    reason: ReasonCategory | None
    audit_evidence: AuthorizationAuditEvidence
