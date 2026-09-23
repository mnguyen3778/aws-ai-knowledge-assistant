from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.membership_source import (
    NonProductionMembershipAuthoritySource as _MembershipSource,
)
from trusted_authorization.models import (
    AuthorityLookupResult as _AuthorityLookupResult,
    AuthorityLookupStatus as _AuthorityLookupStatus,
    AuthorityRecordState as _AuthorityRecordState,
    Membership as _Membership,
    RequestedAction as _RequestedAction,
    ResourceActionApplicability as _ResourceActionApplicability,
    ResourceClass as _ResourceClass,
)
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation as _ProtectedOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (
    NonProductionAssessmentSubmissionBusinessContext as _BusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult as _BusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus as _BusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_business_entity_currentness_establishment import (
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority as _UpstreamAuthority,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence as _UpstreamEvidence,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact as _UpstreamFact,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult as _UpstreamResult,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus as _UpstreamStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)


_BOUNDED_PRINCIPAL_ID = "principal-alpha"
_BOUNDED_BUSINESS_ENTITY_ID = "business-alpha"
_MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE = "non-production-membership-authority"
_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-membership-currentness-authority"
)
_MEMBERSHIP_GOVERNANCE_REFERENCE = "membership-authority-source-governance-v1"
_CURRENTNESS_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-membership-currentness-"
    "establishment-provenance"
)
_BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE = "non-production-business-entity-authority"
_BUSINESS_ENTITY_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-business-entity-currentness-authority"
)
_BUSINESS_ENTITY_GOVERNANCE_REFERENCE = "business-entity-authority-source-governance-v1"
_APPLICABILITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-action-applicability-authority"
)
_APPLICABILITY_GOVERNANCE_REFERENCE = "resource-action-applicability-governance-v1"
_RESOURCE_IDENTITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-identity-authority"
)
_RESOURCE_IDENTITY_GOVERNANCE_REFERENCE = (
    "resource-identity-authority-source-governance-v1"
)
_TARGET_AUTHORITY_REFERENCE = "non-production-assessment-submission-resource-target-authority"
_TARGET_GOVERNANCE_REFERENCE = (
    "trusted-authorization-resource-reference-provenance-governance-v1"
)


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionMembershipCurrentnessFact:
    principal_id: str
    business_entity_id: str
    membership_state: _AuthorityRecordState


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionMembershipCurrentnessEvidence:
    attempt_reference: str
    resource_reference: str
    resource_id: str
    principal_id: str
    engagement_reference: str
    business_entity_id: str
    protected_operation: _ProtectedOperation
    principal_authority_reference: str
    engagement_authority_reference: str
    engagement_establishment_provenance_reference: str
    participation_authority_reference: str
    participation_provenance_reference: str
    business_entity_authority_reference: str
    allocation_authority_reference: str
    allocation_provenance_reference: str
    binding_authority_reference: str
    binding_provenance_reference: str
    resource_class: _ResourceClass
    resource_lifecycle_state: _LifecycleState
    lifecycle_authority_reference: str
    lifecycle_provenance_reference: str
    target_authority_reference: str
    target_provenance_reference: str
    target_governance_reference: str
    resource_identity_state: _AuthorityRecordState
    resource_identity_authority_reference: str
    resource_identity_provenance_reference: str
    resource_identity_governance_reference: str
    requested_action: _RequestedAction
    applicability: _ResourceActionApplicability
    applicability_authority_reference: str
    applicability_provenance_reference: str
    applicability_governance_reference: str
    business_entity_state: _AuthorityRecordState
    business_entity_currentness_authority_reference: str
    business_entity_currentness_provenance_reference: str
    business_entity_governance_reference: str
    membership_state: _AuthorityRecordState
    membership_authority_reference: str
    membership_currentness_authority_reference: str
    membership_currentness_provenance_reference: str
    membership_governance_reference: str


class NonProductionAssessmentSubmissionMembershipCurrentnessStatus(_Enum):
    ESTABLISHED = "ESTABLISHED"
    REUSED = "REUSED"
    MALFORMED = "MALFORMED"
    BUSINESS_CONTEXT_NOT_READY = "BUSINESS_CONTEXT_NOT_READY"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    MISMATCH = "MISMATCH"
    COLLISION = "COLLISION"
    ALLOCATION_UNAVAILABLE = "ALLOCATION_UNAVAILABLE"
    RESOURCE_IDENTITY_NOT_FOUND = "RESOURCE_IDENTITY_NOT_FOUND"
    RESOURCE_IDENTITY_AMBIGUOUS = "RESOURCE_IDENTITY_AMBIGUOUS"
    RESOURCE_IDENTITY_CONFLICTING = "RESOURCE_IDENTITY_CONFLICTING"
    RESOURCE_IDENTITY_STALE = "RESOURCE_IDENTITY_STALE"
    RESOURCE_IDENTITY_UNAVAILABLE = "RESOURCE_IDENTITY_UNAVAILABLE"
    APPLICABILITY_NOT_APPLICABLE = "APPLICABILITY_NOT_APPLICABLE"
    APPLICABILITY_UNRESOLVED = "APPLICABILITY_UNRESOLVED"
    BUSINESS_ENTITY_NOT_FOUND = "BUSINESS_ENTITY_NOT_FOUND"
    BUSINESS_ENTITY_AMBIGUOUS = "BUSINESS_ENTITY_AMBIGUOUS"
    BUSINESS_ENTITY_CONFLICTING = "BUSINESS_ENTITY_CONFLICTING"
    BUSINESS_ENTITY_STALE = "BUSINESS_ENTITY_STALE"
    BUSINESS_ENTITY_UNAVAILABLE = "BUSINESS_ENTITY_UNAVAILABLE"
    MEMBERSHIP_NOT_FOUND = "MEMBERSHIP_NOT_FOUND"
    MEMBERSHIP_AMBIGUOUS = "MEMBERSHIP_AMBIGUOUS"
    MEMBERSHIP_CONFLICTING = "MEMBERSHIP_CONFLICTING"
    MEMBERSHIP_STALE = "MEMBERSHIP_STALE"
    MEMBERSHIP_UNAVAILABLE = "MEMBERSHIP_UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionMembershipCurrentnessResult:
    status: NonProductionAssessmentSubmissionMembershipCurrentnessStatus
    membership_currentness_fact: (
        NonProductionAssessmentSubmissionMembershipCurrentnessFact | None
    ) = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionMembershipCurrentnessEvidence | None
    ) = None


@_dataclass(frozen=True, slots=True)
class _Snapshot:
    values: tuple[object, ...]


@_dataclass(frozen=True, slots=True)
class _CurrentnessSnapshot:
    evidence_values: tuple[object, ...]
    retry_identity: tuple[object, ...]


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class NonProductionAssessmentSubmissionMembershipCurrentnessAuthority:
    """Sequential bounded proof of current Assessment Submission Membership."""

    __slots__ = (
        "_business_entity_currentness_authority",
        "_membership_source",
        "_currentness_by_attempt",
        "_next_membership_currentness_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._business_entity_currentness_authority = _UpstreamAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._membership_source = _MembershipSource(
            (
                _Membership(
                    authority_reference=_MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE,
                    state=_AuthorityRecordState.ACTIVE,
                    principal_id=_BOUNDED_PRINCIPAL_ID,
                    business_entity_id=_BOUNDED_BUSINESS_ENTITY_ID,
                ),
            )
        )
        self._currentness_by_attempt: dict[str, _CurrentnessSnapshot] = {}
        self._next_membership_currentness_provenance_index = 1

    def establish_assessment_submission_membership_currentness(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionMembershipCurrentnessResult:
        captured_status, context = _business_context_snapshot(business_context_result)
        if captured_status is _CapturedStatus.MALFORMED:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED)
        if captured_status is _CapturedStatus.NOT_READY or context is None:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.BUSINESS_CONTEXT_NOT_READY)
        if _value(context, _BUSINESS_CONTEXT_FIELDS, "protected_operation") is not _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.UNSUPPORTED_OPERATION)

        upstream_authority = self._business_entity_currentness_authority
        if type(upstream_authority) is not _UpstreamAuthority:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED)
        try:
            upstream_result = _UpstreamAuthority.establish_assessment_submission_business_entity_currentness(
                upstream_authority,
                business_context_result=business_context_result,
            )
        except Exception:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED)

        upstream_status, upstream = _upstream_snapshot(upstream_result, context)
        if upstream_status is not None:
            return _failure(upstream_status)
        if upstream is None:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED)

        source = self._membership_source
        if type(source) is not _MembershipSource:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED)
        principal_id = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "principal_id")
        business_entity_id = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_id")
        try:
            lookup_result = _MembershipSource.resolve_membership(
                source,
                principal_id,
                business_entity_id,
            )
        except Exception:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MEMBERSHIP_UNAVAILABLE)

        lookup_status, membership = _membership_snapshot(
            lookup_result,
            principal_id,
            business_entity_id,
        )
        if lookup_status is not None:
            return _failure(lookup_status)
        if membership is None or not _membership_converges(upstream, membership):
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MISMATCH)

        retry_identity = upstream.values + membership.values + (
            _CURRENTNESS_AUTHORITY_REFERENCE,
            _MEMBERSHIP_GOVERNANCE_REFERENCE,
        )
        attempt_reference = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "attempt_reference")
        stored = self._currentness_by_attempt.get(attempt_reference)
        if stored is not None:
            if stored.retry_identity != retry_identity:
                return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MISMATCH)
            return _success_output(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.REUSED, stored)

        provenance_index = self._next_membership_currentness_provenance_index
        provenance_reference = f"{_CURRENTNESS_PROVENANCE_PREFIX}-{provenance_index}"
        try:
            evidence_values = upstream.values + (
                _membership_value(membership, "state"),
                _membership_value(membership, "authority_reference"),
                _CURRENTNESS_AUTHORITY_REFERENCE,
                provenance_reference,
                _MEMBERSHIP_GOVERNANCE_REFERENCE,
            )
            snapshot = _CurrentnessSnapshot(evidence_values, retry_identity)
            output = _success_output(
                NonProductionAssessmentSubmissionMembershipCurrentnessStatus.ESTABLISHED,
                snapshot,
            )
            if not _output_converges(output):
                return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED)
        except Exception:
            return _failure(NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED)

        self._currentness_by_attempt[attempt_reference] = snapshot
        self._next_membership_currentness_provenance_index = provenance_index + 1
        return output


def _business_context_snapshot(result: object) -> tuple[_CapturedStatus, _Snapshot | None]:
    if type(result) is not _BusinessContextResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        context = object.__getattribute__(result, "business_context")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not _BusinessContextStatus:
        return (_CapturedStatus.MALFORMED, None)
    if status is not _BusinessContextStatus.READY:
        return (_CapturedStatus.NOT_READY, None) if context is None else (_CapturedStatus.MALFORMED, None)
    if type(context) is not _BusinessContext:
        return (_CapturedStatus.MALFORMED, None)
    values = _capture(context, _BUSINESS_CONTEXT_FIELDS)
    if values is None:
        return (_CapturedStatus.MALFORMED, None)
    snapshot = _Snapshot(values)
    strings = values[:4] + values[5:]
    if not all(_has_value(value) for value in strings) or type(values[4]) is not _ProtectedOperation:
        return (_CapturedStatus.MALFORMED, None)
    return (_CapturedStatus.READY, snapshot)


def _upstream_snapshot(
    result: object,
    context: _Snapshot,
) -> tuple[NonProductionAssessmentSubmissionMembershipCurrentnessStatus | None, _Snapshot | None]:
    malformed = NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MALFORMED
    if type(result) is not _UpstreamResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        fact = object.__getattribute__(result, "business_entity_currentness_fact")
        evidence = object.__getattribute__(result, "establishment_evidence")
    except Exception:
        return (malformed, None)
    if type(status) is not _UpstreamStatus:
        return (malformed, None)
    if status not in (_UpstreamStatus.ESTABLISHED, _UpstreamStatus.REUSED):
        if fact is not None or evidence is not None:
            return (malformed, None)
        return (_mapped_upstream_failure(status) or malformed, None)
    if type(fact) is not _UpstreamFact or type(evidence) is not _UpstreamEvidence:
        return (malformed, None)
    fact_values = _capture(fact, _UPSTREAM_FACT_FIELDS)
    evidence_values = _capture(evidence, _UPSTREAM_EVIDENCE_FIELDS)
    if fact_values is None or evidence_values is None:
        return (malformed, None)
    snapshot = _Snapshot(evidence_values)
    if not _valid_upstream(snapshot):
        return (malformed, None)
    if fact_values != (
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_id"),
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_state"),
    ):
        return (NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MISMATCH, None)
    upstream_context = tuple(_value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, name) for name in _BUSINESS_CONTEXT_FIELDS)
    if context.values != upstream_context:
        return (NonProductionAssessmentSubmissionMembershipCurrentnessStatus.MISMATCH, None)
    return (None, snapshot)


def _valid_upstream(upstream: _Snapshot) -> bool:
    value = lambda name: _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, name)
    strings = tuple(value(name) for name in _UPSTREAM_STRING_FIELDS)
    return (
        all(_has_value(item) for item in strings)
        and value("resource_reference") == value("resource_id")
        and type(value("protected_operation")) is _ProtectedOperation
        and value("protected_operation") is _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        and type(value("resource_class")) is _ResourceClass
        and value("resource_class") is _ResourceClass.ASSESSMENT_SUBMISSION
        and type(value("resource_lifecycle_state")) is _LifecycleState
        and value("resource_lifecycle_state") is _LifecycleState.PROVISIONAL
        and type(value("resource_identity_state")) is _AuthorityRecordState
        and value("resource_identity_state") is _AuthorityRecordState.ACTIVE
        and type(value("requested_action")) is _RequestedAction
        and value("requested_action") is _RequestedAction.SUBMIT
        and type(value("applicability")) is _ResourceActionApplicability
        and value("applicability") is _ResourceActionApplicability.APPLICABLE
        and type(value("business_entity_state")) is _AuthorityRecordState
        and value("business_entity_state") is _AuthorityRecordState.ACTIVE
        and value("business_entity_authority_reference") == _BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE
        and value("target_authority_reference") == _TARGET_AUTHORITY_REFERENCE
        and value("target_governance_reference") == _TARGET_GOVERNANCE_REFERENCE
        and value("resource_identity_authority_reference") == _RESOURCE_IDENTITY_AUTHORITY_REFERENCE
        and value("resource_identity_governance_reference") == _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE
        and value("applicability_authority_reference") == _APPLICABILITY_AUTHORITY_REFERENCE
        and value("applicability_governance_reference") == _APPLICABILITY_GOVERNANCE_REFERENCE
        and value("business_entity_currentness_authority_reference") == _BUSINESS_ENTITY_CURRENTNESS_AUTHORITY_REFERENCE
        and value("business_entity_governance_reference") == _BUSINESS_ENTITY_GOVERNANCE_REFERENCE
    )


def _mapped_upstream_failure(status: _UpstreamStatus) -> NonProductionAssessmentSubmissionMembershipCurrentnessStatus | None:
    output = NonProductionAssessmentSubmissionMembershipCurrentnessStatus
    return {
        _UpstreamStatus.MALFORMED: output.MALFORMED,
        _UpstreamStatus.BUSINESS_CONTEXT_NOT_READY: output.BUSINESS_CONTEXT_NOT_READY,
        _UpstreamStatus.UNSUPPORTED_OPERATION: output.UNSUPPORTED_OPERATION,
        _UpstreamStatus.MISMATCH: output.MISMATCH,
        _UpstreamStatus.COLLISION: output.COLLISION,
        _UpstreamStatus.ALLOCATION_UNAVAILABLE: output.ALLOCATION_UNAVAILABLE,
        _UpstreamStatus.RESOURCE_IDENTITY_NOT_FOUND: output.RESOURCE_IDENTITY_NOT_FOUND,
        _UpstreamStatus.RESOURCE_IDENTITY_AMBIGUOUS: output.RESOURCE_IDENTITY_AMBIGUOUS,
        _UpstreamStatus.RESOURCE_IDENTITY_CONFLICTING: output.RESOURCE_IDENTITY_CONFLICTING,
        _UpstreamStatus.RESOURCE_IDENTITY_STALE: output.RESOURCE_IDENTITY_STALE,
        _UpstreamStatus.RESOURCE_IDENTITY_UNAVAILABLE: output.RESOURCE_IDENTITY_UNAVAILABLE,
        _UpstreamStatus.APPLICABILITY_NOT_APPLICABLE: output.APPLICABILITY_NOT_APPLICABLE,
        _UpstreamStatus.APPLICABILITY_UNRESOLVED: output.APPLICABILITY_UNRESOLVED,
        _UpstreamStatus.BUSINESS_ENTITY_NOT_FOUND: output.BUSINESS_ENTITY_NOT_FOUND,
        _UpstreamStatus.BUSINESS_ENTITY_AMBIGUOUS: output.BUSINESS_ENTITY_AMBIGUOUS,
        _UpstreamStatus.BUSINESS_ENTITY_CONFLICTING: output.BUSINESS_ENTITY_CONFLICTING,
        _UpstreamStatus.BUSINESS_ENTITY_STALE: output.BUSINESS_ENTITY_STALE,
        _UpstreamStatus.BUSINESS_ENTITY_UNAVAILABLE: output.BUSINESS_ENTITY_UNAVAILABLE,
    }.get(status)


def _membership_snapshot(
    result: object,
    principal_id: object,
    business_entity_id: object,
) -> tuple[NonProductionAssessmentSubmissionMembershipCurrentnessStatus | None, _Snapshot | None]:
    output = NonProductionAssessmentSubmissionMembershipCurrentnessStatus
    if type(result) is not _AuthorityLookupResult:
        return (output.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        records = object.__getattribute__(result, "records")
    except Exception:
        return (output.MALFORMED, None)
    if type(status) is not _AuthorityLookupStatus or type(records) is not tuple:
        return (output.MALFORMED, None)
    mapping = {
        _AuthorityLookupStatus.NOT_FOUND: output.MEMBERSHIP_NOT_FOUND,
        _AuthorityLookupStatus.AMBIGUOUS: output.MEMBERSHIP_AMBIGUOUS,
        _AuthorityLookupStatus.CONFLICTING: output.MEMBERSHIP_CONFLICTING,
        _AuthorityLookupStatus.STALE: output.MEMBERSHIP_STALE,
        _AuthorityLookupStatus.UNAVAILABLE: output.MEMBERSHIP_UNAVAILABLE,
        _AuthorityLookupStatus.MALFORMED: output.MALFORMED,
        _AuthorityLookupStatus.UNSUPPORTED: output.MALFORMED,
    }
    if status in (_AuthorityLookupStatus.AMBIGUOUS, _AuthorityLookupStatus.CONFLICTING):
        if len(records) < 2:
            return (output.MALFORMED, None)
        snapshots = []
        for record in records:
            if type(record) is not _Membership:
                return (output.MALFORMED, None)
            values = _capture(record, _MEMBERSHIP_FIELDS)
            if values is None:
                return (output.MALFORMED, None)
            snapshot = _Snapshot(values)
            if (
                not _has_value(_membership_value(snapshot, "authority_reference"))
                or type(_membership_value(snapshot, "state")) is not _AuthorityRecordState
                or not _has_value(_membership_value(snapshot, "principal_id"))
                or not _has_value(_membership_value(snapshot, "business_entity_id"))
            ):
                return (output.MALFORMED, None)
            snapshots.append(snapshot)
        identities = {snapshot.values for snapshot in snapshots}
        membership_keys = {
            (
                _membership_value(snapshot, "principal_id"),
                _membership_value(snapshot, "business_entity_id"),
            )
            for snapshot in snapshots
        }
        if membership_keys != {(principal_id, business_entity_id)}:
            return (output.MALFORMED, None)
        if (status is _AuthorityLookupStatus.AMBIGUOUS) != (len(identities) == 1):
            return (output.MALFORMED, None)
        return (mapping[status], None)
    if status is not _AuthorityLookupStatus.FOUND:
        return (output.MALFORMED, None) if records else (mapping.get(status, output.MALFORMED), None)
    if len(records) != 1 or type(records[0]) is not _Membership:
        return (output.MALFORMED, None)
    values = _capture(records[0], _MEMBERSHIP_FIELDS)
    if values is None:
        return (output.MALFORMED, None)
    snapshot = _Snapshot(values)
    if (
        not _has_value(_membership_value(snapshot, "authority_reference"))
        or type(_membership_value(snapshot, "state")) is not _AuthorityRecordState
        or not _has_value(_membership_value(snapshot, "principal_id"))
        or not _has_value(_membership_value(snapshot, "business_entity_id"))
        or _membership_value(snapshot, "state") is not _AuthorityRecordState.ACTIVE
    ):
        return (output.MALFORMED, None)
    return (None, snapshot)


def _membership_converges(upstream: _Snapshot, membership: _Snapshot) -> bool:
    return (
        _membership_value(membership, "principal_id") == _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "principal_id")
        and _membership_value(membership, "business_entity_id") == _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_id")
        and _membership_value(membership, "authority_reference") == _MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE
        and _membership_value(membership, "state") is _AuthorityRecordState.ACTIVE
    )


def _success_output(
    status: NonProductionAssessmentSubmissionMembershipCurrentnessStatus,
    snapshot: _CurrentnessSnapshot,
) -> NonProductionAssessmentSubmissionMembershipCurrentnessResult:
    values = dict(zip(_CURRENTNESS_EVIDENCE_FIELDS, snapshot.evidence_values, strict=True))
    fact = NonProductionAssessmentSubmissionMembershipCurrentnessFact(
        principal_id=values["principal_id"],
        business_entity_id=values["business_entity_id"],
        membership_state=values["membership_state"],
    )
    evidence = NonProductionAssessmentSubmissionMembershipCurrentnessEvidence(**values)
    return NonProductionAssessmentSubmissionMembershipCurrentnessResult(
        status=status,
        membership_currentness_fact=fact,
        establishment_evidence=evidence,
    )


def _output_converges(result: NonProductionAssessmentSubmissionMembershipCurrentnessResult) -> bool:
    fact = result.membership_currentness_fact
    evidence = result.establishment_evidence
    return (
        type(fact) is NonProductionAssessmentSubmissionMembershipCurrentnessFact
        and type(evidence) is NonProductionAssessmentSubmissionMembershipCurrentnessEvidence
        and fact.principal_id == evidence.principal_id
        and fact.business_entity_id == evidence.business_entity_id
        and fact.membership_state is evidence.membership_state
        and evidence.membership_state is _AuthorityRecordState.ACTIVE
        and evidence.membership_authority_reference == _MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE
        and evidence.membership_currentness_authority_reference == _CURRENTNESS_AUTHORITY_REFERENCE
        and _has_value(evidence.membership_currentness_provenance_reference)
        and evidence.membership_governance_reference == _MEMBERSHIP_GOVERNANCE_REFERENCE
    )


def _failure(status: NonProductionAssessmentSubmissionMembershipCurrentnessStatus) -> NonProductionAssessmentSubmissionMembershipCurrentnessResult:
    return NonProductionAssessmentSubmissionMembershipCurrentnessResult(status=status)


def _capture(value: object, fields: tuple[str, ...]) -> tuple[object, ...] | None:
    try:
        return tuple(object.__getattribute__(value, name) for name in fields)
    except Exception:
        return None


def _value(snapshot: _Snapshot, fields: tuple[str, ...], name: str) -> object:
    return snapshot.values[fields.index(name)]


def _membership_value(snapshot: _Snapshot, name: str) -> object:
    return _value(snapshot, _MEMBERSHIP_FIELDS, name)


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value and bool(value.strip())


_BUSINESS_CONTEXT_FIELDS = (
    "attempt_reference", "principal_id", "engagement_reference", "business_entity_id",
    "protected_operation", "principal_authority_reference", "engagement_authority_reference",
    "engagement_establishment_provenance_reference", "participation_authority_reference",
    "participation_provenance_reference", "business_entity_authority_reference",
)
_UPSTREAM_FACT_FIELDS = ("business_entity_id", "business_entity_state")
_UPSTREAM_EVIDENCE_FIELDS = (
    "attempt_reference", "resource_reference", "resource_id", "principal_id",
    "engagement_reference", "business_entity_id", "protected_operation",
    "principal_authority_reference", "engagement_authority_reference",
    "engagement_establishment_provenance_reference", "participation_authority_reference",
    "participation_provenance_reference", "business_entity_authority_reference",
    "allocation_authority_reference", "allocation_provenance_reference",
    "binding_authority_reference", "binding_provenance_reference", "resource_class",
    "resource_lifecycle_state", "lifecycle_authority_reference", "lifecycle_provenance_reference",
    "target_authority_reference", "target_provenance_reference", "target_governance_reference",
    "resource_identity_state", "resource_identity_authority_reference",
    "resource_identity_provenance_reference", "resource_identity_governance_reference",
    "requested_action", "applicability", "applicability_authority_reference",
    "applicability_provenance_reference", "applicability_governance_reference",
    "business_entity_state", "business_entity_currentness_authority_reference",
    "business_entity_currentness_provenance_reference", "business_entity_governance_reference",
)
_MEMBERSHIP_FIELDS = ("authority_reference", "state", "principal_id", "business_entity_id")
_CURRENTNESS_EVIDENCE_FIELDS = _UPSTREAM_EVIDENCE_FIELDS + (
    "membership_state", "membership_authority_reference",
    "membership_currentness_authority_reference",
    "membership_currentness_provenance_reference", "membership_governance_reference",
)
_UPSTREAM_STRING_FIELDS = tuple(
    name for name in _UPSTREAM_EVIDENCE_FIELDS
    if name not in {
        "protected_operation", "resource_class", "resource_lifecycle_state",
        "resource_identity_state", "requested_action", "applicability", "business_entity_state",
    }
)
