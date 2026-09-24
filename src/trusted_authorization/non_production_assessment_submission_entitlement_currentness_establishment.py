from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.entitlement_source import (
    NonProductionEntitlementAuthoritySource as _EntitlementSource,
)
from trusted_authorization.models import (
    AuthorityLookupResult as _AuthorityLookupResult,
    AuthorityLookupStatus as _AuthorityLookupStatus,
    AuthorityRecordState as _AuthorityRecordState,
    Entitlement as _Entitlement,
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
from trusted_authorization.non_production_assessment_submission_membership_currentness_establishment import (
    NonProductionAssessmentSubmissionMembershipCurrentnessAuthority as _UpstreamAuthority,
    NonProductionAssessmentSubmissionMembershipCurrentnessEvidence as _UpstreamEvidence,
    NonProductionAssessmentSubmissionMembershipCurrentnessFact as _UpstreamFact,
    NonProductionAssessmentSubmissionMembershipCurrentnessResult as _UpstreamResult,
    NonProductionAssessmentSubmissionMembershipCurrentnessStatus as _UpstreamStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)


_BOUNDED_PRINCIPAL_ID = "principal-alpha"
_BOUNDED_BUSINESS_ENTITY_ID = "business-alpha"
_BOUNDED_RESOURCE_ID = "resource-alpha"
_ENTITLEMENT_SOURCE_AUTHORITY_REFERENCE = "non-production-entitlement-authority"
_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-entitlement-currentness-authority"
)
_ENTITLEMENT_GOVERNANCE_REFERENCE = "entitlement-authority-source-governance-v1"
_CURRENTNESS_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-entitlement-currentness-"
    "establishment-provenance"
)
_MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE = "non-production-membership-authority"
_MEMBERSHIP_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-membership-currentness-authority"
)
_MEMBERSHIP_GOVERNANCE_REFERENCE = "membership-authority-source-governance-v1"
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
class NonProductionAssessmentSubmissionEntitlementCurrentnessFact:
    principal_id: str
    business_entity_id: str
    resource_id: str
    requested_action: _RequestedAction
    entitlement_state: _AuthorityRecordState


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence:
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
    entitlement_state: _AuthorityRecordState
    entitlement_authority_reference: str
    entitlement_currentness_authority_reference: str
    entitlement_currentness_provenance_reference: str
    entitlement_governance_reference: str


class NonProductionAssessmentSubmissionEntitlementCurrentnessStatus(_Enum):
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
    ENTITLEMENT_NOT_FOUND = "ENTITLEMENT_NOT_FOUND"
    ENTITLEMENT_AMBIGUOUS = "ENTITLEMENT_AMBIGUOUS"
    ENTITLEMENT_CONFLICTING = "ENTITLEMENT_CONFLICTING"
    ENTITLEMENT_STALE = "ENTITLEMENT_STALE"
    ENTITLEMENT_UNAVAILABLE = "ENTITLEMENT_UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionEntitlementCurrentnessResult:
    status: NonProductionAssessmentSubmissionEntitlementCurrentnessStatus
    entitlement_currentness_fact: (
        NonProductionAssessmentSubmissionEntitlementCurrentnessFact | None
    ) = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence | None
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


class NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority:
    """Sequential bounded proof of current Assessment Submission Entitlement."""

    __slots__ = (
        "_membership_currentness_authority",
        "_entitlement_source",
        "_entitlement_currentness_by_attempt",
        "_next_entitlement_currentness_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._membership_currentness_authority = _UpstreamAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._entitlement_source = _EntitlementSource(
            (
                _Entitlement(
                    authority_reference=_ENTITLEMENT_SOURCE_AUTHORITY_REFERENCE,
                    state=_AuthorityRecordState.ACTIVE,
                    principal_id=_BOUNDED_PRINCIPAL_ID,
                    business_entity_id=_BOUNDED_BUSINESS_ENTITY_ID,
                    resource_id=_BOUNDED_RESOURCE_ID,
                    action=_RequestedAction.SUBMIT,
                ),
            )
        )
        self._entitlement_currentness_by_attempt: dict[str, _CurrentnessSnapshot] = {}
        self._next_entitlement_currentness_provenance_index = 1

    def establish_assessment_submission_entitlement_currentness(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionEntitlementCurrentnessResult:
        captured_status, context = _business_context_snapshot(business_context_result)
        if captured_status is _CapturedStatus.MALFORMED:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED)
        if captured_status is _CapturedStatus.NOT_READY or context is None:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.BUSINESS_CONTEXT_NOT_READY)
        if _value(context, _BUSINESS_CONTEXT_FIELDS, "protected_operation") is not _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.UNSUPPORTED_OPERATION)

        upstream_authority = self._membership_currentness_authority
        if type(upstream_authority) is not _UpstreamAuthority:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED)
        try:
            upstream_result = _UpstreamAuthority.establish_assessment_submission_membership_currentness(
                upstream_authority,
                business_context_result=business_context_result,
            )
        except Exception:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED)

        upstream_status, upstream = _upstream_snapshot(upstream_result, context)
        if upstream_status is not None:
            return _failure(upstream_status)
        if upstream is None:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED)

        source = self._entitlement_source
        if type(source) is not _EntitlementSource:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED)
        principal_id = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "principal_id")
        business_entity_id = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_id")
        resource_id = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "resource_id")
        requested_action = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "requested_action")
        try:
            lookup_result = _EntitlementSource.resolve_entitlement(
                source,
                principal_id,
                business_entity_id,
                resource_id,
                requested_action,
            )
        except Exception:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.ENTITLEMENT_UNAVAILABLE)

        lookup_status, entitlement = _entitlement_snapshot(
            lookup_result,
            principal_id,
            business_entity_id,
            resource_id,
            requested_action,
        )
        if lookup_status is not None:
            return _failure(lookup_status)
        if entitlement is None or not _entitlement_converges(upstream, entitlement):
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MISMATCH)

        retry_identity = upstream.values + entitlement.values + (
            _CURRENTNESS_AUTHORITY_REFERENCE,
            _ENTITLEMENT_GOVERNANCE_REFERENCE,
        )
        attempt_reference = _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "attempt_reference")
        stored = self._entitlement_currentness_by_attempt.get(attempt_reference)
        if stored is not None:
            if stored.retry_identity != retry_identity:
                return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MISMATCH)
            return _success_output(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.REUSED, stored)

        provenance_index = self._next_entitlement_currentness_provenance_index
        provenance_reference = f"{_CURRENTNESS_PROVENANCE_PREFIX}-{provenance_index}"
        try:
            evidence_values = upstream.values + (
                _entitlement_value(entitlement, "state"),
                _entitlement_value(entitlement, "authority_reference"),
                _CURRENTNESS_AUTHORITY_REFERENCE,
                provenance_reference,
                _ENTITLEMENT_GOVERNANCE_REFERENCE,
            )
            snapshot = _CurrentnessSnapshot(evidence_values, retry_identity)
            output = _success_output(
                NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.ESTABLISHED,
                snapshot,
            )
            if not _output_converges(output):
                return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED)
        except Exception:
            return _failure(NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED)

        self._entitlement_currentness_by_attempt[attempt_reference] = snapshot
        self._next_entitlement_currentness_provenance_index = provenance_index + 1
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
) -> tuple[NonProductionAssessmentSubmissionEntitlementCurrentnessStatus | None, _Snapshot | None]:
    malformed = NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MALFORMED
    if type(result) is not _UpstreamResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        fact = object.__getattribute__(result, "membership_currentness_fact")
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
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "principal_id"),
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_id"),
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "membership_state"),
    ):
        return (NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MISMATCH, None)
    upstream_context = tuple(
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, name)
        for name in _BUSINESS_CONTEXT_FIELDS
    )
    if context.values != upstream_context:
        return (NonProductionAssessmentSubmissionEntitlementCurrentnessStatus.MISMATCH, None)
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
        and type(value("membership_state")) is _AuthorityRecordState
        and value("membership_state") is _AuthorityRecordState.ACTIVE
        and value("business_entity_authority_reference") == _BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE
        and value("target_authority_reference") == _TARGET_AUTHORITY_REFERENCE
        and value("target_governance_reference") == _TARGET_GOVERNANCE_REFERENCE
        and value("resource_identity_authority_reference") == _RESOURCE_IDENTITY_AUTHORITY_REFERENCE
        and value("resource_identity_governance_reference") == _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE
        and value("applicability_authority_reference") == _APPLICABILITY_AUTHORITY_REFERENCE
        and value("applicability_governance_reference") == _APPLICABILITY_GOVERNANCE_REFERENCE
        and value("business_entity_currentness_authority_reference") == _BUSINESS_ENTITY_CURRENTNESS_AUTHORITY_REFERENCE
        and value("business_entity_governance_reference") == _BUSINESS_ENTITY_GOVERNANCE_REFERENCE
        and value("membership_authority_reference") == _MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE
        and value("membership_currentness_authority_reference") == _MEMBERSHIP_CURRENTNESS_AUTHORITY_REFERENCE
        and value("membership_governance_reference") == _MEMBERSHIP_GOVERNANCE_REFERENCE
    )


def _mapped_upstream_failure(
    status: _UpstreamStatus,
) -> NonProductionAssessmentSubmissionEntitlementCurrentnessStatus | None:
    output = NonProductionAssessmentSubmissionEntitlementCurrentnessStatus
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
        _UpstreamStatus.MEMBERSHIP_NOT_FOUND: output.MEMBERSHIP_NOT_FOUND,
        _UpstreamStatus.MEMBERSHIP_AMBIGUOUS: output.MEMBERSHIP_AMBIGUOUS,
        _UpstreamStatus.MEMBERSHIP_CONFLICTING: output.MEMBERSHIP_CONFLICTING,
        _UpstreamStatus.MEMBERSHIP_STALE: output.MEMBERSHIP_STALE,
        _UpstreamStatus.MEMBERSHIP_UNAVAILABLE: output.MEMBERSHIP_UNAVAILABLE,
    }.get(status)


def _entitlement_snapshot(
    result: object,
    principal_id: object,
    business_entity_id: object,
    resource_id: object,
    requested_action: object,
) -> tuple[NonProductionAssessmentSubmissionEntitlementCurrentnessStatus | None, _Snapshot | None]:
    output = NonProductionAssessmentSubmissionEntitlementCurrentnessStatus
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
        _AuthorityLookupStatus.NOT_FOUND: output.ENTITLEMENT_NOT_FOUND,
        _AuthorityLookupStatus.AMBIGUOUS: output.ENTITLEMENT_AMBIGUOUS,
        _AuthorityLookupStatus.CONFLICTING: output.ENTITLEMENT_CONFLICTING,
        _AuthorityLookupStatus.STALE: output.ENTITLEMENT_STALE,
        _AuthorityLookupStatus.UNAVAILABLE: output.ENTITLEMENT_UNAVAILABLE,
        _AuthorityLookupStatus.MALFORMED: output.MALFORMED,
        _AuthorityLookupStatus.UNSUPPORTED: output.MALFORMED,
    }
    if status in (_AuthorityLookupStatus.AMBIGUOUS, _AuthorityLookupStatus.CONFLICTING):
        if len(records) < 2:
            return (output.MALFORMED, None)
        snapshots = []
        for record in records:
            snapshot = _entitlement_record_snapshot(record)
            if snapshot is None:
                return (output.MALFORMED, None)
            snapshots.append(snapshot)
        identities = {snapshot.values for snapshot in snapshots}
        keys = {
            (
                _entitlement_value(snapshot, "principal_id"),
                _entitlement_value(snapshot, "business_entity_id"),
                _entitlement_value(snapshot, "resource_id"),
                _entitlement_value(snapshot, "action"),
            )
            for snapshot in snapshots
        }
        if keys != {(principal_id, business_entity_id, resource_id, requested_action)}:
            return (output.MALFORMED, None)
        if (status is _AuthorityLookupStatus.AMBIGUOUS) != (len(identities) == 1):
            return (output.MALFORMED, None)
        return (mapping[status], None)
    if status is not _AuthorityLookupStatus.FOUND:
        return (output.MALFORMED, None) if records else (mapping.get(status, output.MALFORMED), None)
    if len(records) != 1:
        return (output.MALFORMED, None)
    snapshot = _entitlement_record_snapshot(records[0])
    if snapshot is None or _entitlement_value(snapshot, "state") is not _AuthorityRecordState.ACTIVE:
        return (output.MALFORMED, None)
    return (None, snapshot)


def _entitlement_record_snapshot(record: object) -> _Snapshot | None:
    if type(record) is not _Entitlement:
        return None
    values = _capture(record, _ENTITLEMENT_FIELDS)
    if values is None:
        return None
    snapshot = _Snapshot(values)
    if (
        not _has_value(_entitlement_value(snapshot, "authority_reference"))
        or type(_entitlement_value(snapshot, "state")) is not _AuthorityRecordState
        or not _has_value(_entitlement_value(snapshot, "principal_id"))
        or not _has_value(_entitlement_value(snapshot, "business_entity_id"))
        or not _has_value(_entitlement_value(snapshot, "resource_id"))
        or type(_entitlement_value(snapshot, "action")) is not _RequestedAction
    ):
        return None
    return snapshot


def _entitlement_converges(upstream: _Snapshot, entitlement: _Snapshot) -> bool:
    return (
        _entitlement_value(entitlement, "principal_id") == _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "principal_id")
        and _entitlement_value(entitlement, "business_entity_id") == _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_id")
        and _entitlement_value(entitlement, "resource_id") == _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "resource_id")
        and _entitlement_value(entitlement, "action") is _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, "requested_action")
        and _entitlement_value(entitlement, "authority_reference") == _ENTITLEMENT_SOURCE_AUTHORITY_REFERENCE
        and _entitlement_value(entitlement, "state") is _AuthorityRecordState.ACTIVE
    )


def _success_output(
    status: NonProductionAssessmentSubmissionEntitlementCurrentnessStatus,
    snapshot: _CurrentnessSnapshot,
) -> NonProductionAssessmentSubmissionEntitlementCurrentnessResult:
    values = dict(zip(_CURRENTNESS_EVIDENCE_FIELDS, snapshot.evidence_values, strict=True))
    fact = NonProductionAssessmentSubmissionEntitlementCurrentnessFact(
        principal_id=values["principal_id"],
        business_entity_id=values["business_entity_id"],
        resource_id=values["resource_id"],
        requested_action=values["requested_action"],
        entitlement_state=values["entitlement_state"],
    )
    evidence = NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence(**values)
    return NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
        status=status,
        entitlement_currentness_fact=fact,
        establishment_evidence=evidence,
    )


def _output_converges(
    result: NonProductionAssessmentSubmissionEntitlementCurrentnessResult,
) -> bool:
    fact = result.entitlement_currentness_fact
    evidence = result.establishment_evidence
    return (
        type(fact) is NonProductionAssessmentSubmissionEntitlementCurrentnessFact
        and type(evidence) is NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence
        and fact.principal_id == evidence.principal_id
        and fact.business_entity_id == evidence.business_entity_id
        and fact.resource_id == evidence.resource_id
        and fact.requested_action is evidence.requested_action
        and fact.entitlement_state is evidence.entitlement_state
        and evidence.entitlement_state is _AuthorityRecordState.ACTIVE
        and evidence.entitlement_authority_reference == _ENTITLEMENT_SOURCE_AUTHORITY_REFERENCE
        and evidence.entitlement_currentness_authority_reference == _CURRENTNESS_AUTHORITY_REFERENCE
        and _has_value(evidence.entitlement_currentness_provenance_reference)
        and evidence.entitlement_governance_reference == _ENTITLEMENT_GOVERNANCE_REFERENCE
    )


def _failure(
    status: NonProductionAssessmentSubmissionEntitlementCurrentnessStatus,
) -> NonProductionAssessmentSubmissionEntitlementCurrentnessResult:
    return NonProductionAssessmentSubmissionEntitlementCurrentnessResult(status=status)


def _capture(value: object, fields: tuple[str, ...]) -> tuple[object, ...] | None:
    try:
        return tuple(object.__getattribute__(value, name) for name in fields)
    except Exception:
        return None


def _value(snapshot: _Snapshot, fields: tuple[str, ...], name: str) -> object:
    return snapshot.values[fields.index(name)]


def _entitlement_value(snapshot: _Snapshot, name: str) -> object:
    return _value(snapshot, _ENTITLEMENT_FIELDS, name)


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value and bool(value.strip())


_BUSINESS_CONTEXT_FIELDS = (
    "attempt_reference", "principal_id", "engagement_reference", "business_entity_id",
    "protected_operation", "principal_authority_reference", "engagement_authority_reference",
    "engagement_establishment_provenance_reference", "participation_authority_reference",
    "participation_provenance_reference", "business_entity_authority_reference",
)
_UPSTREAM_FACT_FIELDS = ("principal_id", "business_entity_id", "membership_state")
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
    "membership_state", "membership_authority_reference",
    "membership_currentness_authority_reference",
    "membership_currentness_provenance_reference", "membership_governance_reference",
)
_ENTITLEMENT_FIELDS = (
    "authority_reference", "state", "principal_id", "business_entity_id",
    "resource_id", "action",
)
_CURRENTNESS_EVIDENCE_FIELDS = _UPSTREAM_EVIDENCE_FIELDS + (
    "entitlement_state", "entitlement_authority_reference",
    "entitlement_currentness_authority_reference",
    "entitlement_currentness_provenance_reference", "entitlement_governance_reference",
)
_UPSTREAM_STRING_FIELDS = tuple(
    name for name in _UPSTREAM_EVIDENCE_FIELDS
    if name not in {
        "protected_operation", "resource_class", "resource_lifecycle_state",
        "resource_identity_state", "requested_action", "applicability",
        "business_entity_state", "membership_state",
    }
)
