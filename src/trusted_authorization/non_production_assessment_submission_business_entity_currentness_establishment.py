from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.business_entity_source import (
    NonProductionBusinessEntityAuthoritySource as _BusinessEntitySource,
)
from trusted_authorization.models import (
    AuthorityLookupResult as _AuthorityLookupResult,
    AuthorityLookupStatus as _AuthorityLookupStatus,
    AuthorityRecordState as _AuthorityRecordState,
    BusinessEntity as _BusinessEntity,
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
from trusted_authorization.non_production_assessment_submission_resource_action_applicability_establishment import (
    NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority as _ApplicabilityAuthority,
    NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence as _ApplicabilityEvidence,
    NonProductionAssessmentSubmissionResourceActionApplicabilityFact as _ApplicabilityFact,
    NonProductionAssessmentSubmissionResourceActionApplicabilityResult as _ApplicabilityResult,
    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus as _ApplicabilityStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)


_BOUNDED_BUSINESS_ENTITY_ID = "business-alpha"
_BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE = (
    "non-production-business-entity-authority"
)
_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-business-entity-currentness-authority"
)
_BUSINESS_ENTITY_GOVERNANCE_REFERENCE = (
    "business-entity-authority-source-governance-v1"
)
_CURRENTNESS_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-business-entity-currentness-"
    "establishment-provenance"
)
_APPLICABILITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-action-applicability-authority"
)
_APPLICABILITY_GOVERNANCE_REFERENCE = (
    "resource-action-applicability-governance-v1"
)
_RESOURCE_IDENTITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-identity-authority"
)
_RESOURCE_IDENTITY_GOVERNANCE_REFERENCE = (
    "resource-identity-authority-source-governance-v1"
)
_TARGET_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-target-authority"
)
_TARGET_GOVERNANCE_REFERENCE = (
    "trusted-authorization-resource-reference-provenance-governance-v1"
)


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact:
    business_entity_id: str
    business_entity_state: _AuthorityRecordState


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence:
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


class NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus(_Enum):
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


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult:
    status: NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus
    business_entity_currentness_fact: (
        NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact | None
    ) = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence | None
    ) = None


@_dataclass(frozen=True, slots=True)
class _BusinessContextSnapshot:
    attempt_reference: str
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


@_dataclass(frozen=True, slots=True)
class _ApplicabilitySnapshot:
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


@_dataclass(frozen=True, slots=True)
class _BusinessEntitySnapshot:
    authority_reference: str
    state: _AuthorityRecordState
    business_entity_id: str


@_dataclass(frozen=True, slots=True)
class _CurrentnessSnapshot:
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
    retry_identity: tuple[object, ...]


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority:
    """Sequential bounded proof of current Assessment Submission B authority."""

    __slots__ = (
        "_applicability_authority",
        "_business_entity_source",
        "_currentness_by_attempt",
        "_next_business_entity_currentness_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._applicability_authority = _ApplicabilityAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._business_entity_source = _BusinessEntitySource(
            (
                _BusinessEntity(
                    authority_reference=_BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE,
                    state=_AuthorityRecordState.ACTIVE,
                    business_entity_id=_BOUNDED_BUSINESS_ENTITY_ID,
                ),
            )
        )
        self._currentness_by_attempt: dict[str, _CurrentnessSnapshot] = {}
        self._next_business_entity_currentness_provenance_index = 1

    def establish_assessment_submission_business_entity_currentness(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult:
        captured_status, context = _business_context_snapshot(business_context_result)
        if captured_status is _CapturedStatus.MALFORMED:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                MALFORMED
            )
        if captured_status is _CapturedStatus.NOT_READY or context is None:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                BUSINESS_CONTEXT_NOT_READY
            )
        if (
            context.protected_operation
            is not _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                UNSUPPORTED_OPERATION
            )

        applicability_authority = self._applicability_authority
        if type(applicability_authority) is not _ApplicabilityAuthority:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                MALFORMED
            )
        try:
            applicability_result = (
                _ApplicabilityAuthority.
                establish_assessment_submission_resource_action_applicability(
                    applicability_authority,
                    business_context_result=business_context_result,
                )
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                MALFORMED
            )

        applicability_status, applicability = _applicability_snapshot(
            applicability_result,
            context,
        )
        if applicability_status is not None:
            return _failure(applicability_status)
        if applicability is None:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                MALFORMED
            )

        business_entity_source = self._business_entity_source
        if type(business_entity_source) is not _BusinessEntitySource:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                MALFORMED
            )
        try:
            lookup_result = _BusinessEntitySource.resolve_business_entity(
                business_entity_source,
                applicability.business_entity_id,
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                BUSINESS_ENTITY_UNAVAILABLE
            )

        lookup_status, business_entity = _business_entity_snapshot(lookup_result)
        if lookup_status is not None:
            return _failure(lookup_status)
        if business_entity is None or not _current_business_entity_converges(
            applicability,
            business_entity,
        ):
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                MISMATCH
            )

        retry_identity = _retry_identity(applicability, business_entity)
        stored = self._currentness_by_attempt.get(applicability.attempt_reference)
        if stored is not None:
            if stored.retry_identity != retry_identity:
                return _failure(
                    NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                    MISMATCH
                )
            return _success_output(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.REUSED,
                stored,
            )

        provenance_index = (
            self._next_business_entity_currentness_provenance_index
        )
        provenance_reference = f"{_CURRENTNESS_PROVENANCE_PREFIX}-{provenance_index}"
        try:
            fact = _currentness_fact(business_entity)
            evidence = _currentness_evidence(
                applicability,
                business_entity,
                provenance_reference,
            )
            snapshot = _currentness_snapshot(evidence, retry_identity)
            if not _outputs_converge(fact, evidence, snapshot):
                return _failure(
                    NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                    MALFORMED
                )
            output = _success_output(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                ESTABLISHED,
                snapshot,
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.
                MALFORMED
            )

        self._currentness_by_attempt[applicability.attempt_reference] = snapshot
        self._next_business_entity_currentness_provenance_index = (
            provenance_index + 1
        )
        return output


def _business_context_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _BusinessContextSnapshot | None]:
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
        if context is not None:
            return (_CapturedStatus.MALFORMED, None)
        return (_CapturedStatus.NOT_READY, None)
    if type(context) is not _BusinessContext:
        return (_CapturedStatus.MALFORMED, None)
    try:
        snapshot = _BusinessContextSnapshot(
            **{
                name: object.__getattribute__(context, name)
                for name in _BUSINESS_CONTEXT_FIELDS
            }
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if not _valid_business_context(snapshot):
        return (_CapturedStatus.MALFORMED, None)
    return (_CapturedStatus.READY, snapshot)


def _valid_business_context(context: _BusinessContextSnapshot) -> bool:
    string_fields = tuple(
        object.__getattribute__(context, name)
        for name in _BUSINESS_CONTEXT_FIELDS
        if name != "protected_operation"
    )
    return (
        all(_has_value(value) for value in string_fields)
        and type(context.protected_operation) is _ProtectedOperation
    )


def _applicability_snapshot(
    result: object,
    context: _BusinessContextSnapshot,
) -> tuple[
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus | None,
    _ApplicabilitySnapshot | None,
]:
    malformed = (
        NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.MALFORMED
    )
    if type(result) is not _ApplicabilityResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        fact = object.__getattribute__(result, "applicability_fact")
        evidence = object.__getattribute__(result, "establishment_evidence")
    except Exception:
        return (malformed, None)
    if type(status) is not _ApplicabilityStatus:
        return (malformed, None)
    if status not in (_ApplicabilityStatus.ESTABLISHED, _ApplicabilityStatus.REUSED):
        if fact is not None or evidence is not None:
            return (malformed, None)
        return (_mapped_applicability_failure(status) or malformed, None)
    if type(fact) is not _ApplicabilityFact or type(evidence) is not _ApplicabilityEvidence:
        return (malformed, None)
    try:
        fact_values = tuple(
            object.__getattribute__(fact, name) for name in _APPLICABILITY_FACT_FIELDS
        )
        evidence_values = {
            name: object.__getattribute__(evidence, name)
            for name in _APPLICABILITY_EVIDENCE_FIELDS
        }
        snapshot = _ApplicabilitySnapshot(**evidence_values)
    except Exception:
        return (malformed, None)
    if not _valid_applicability(snapshot):
        return (malformed, None)
    if (
        fact_values
        != (
            snapshot.resource_reference,
            snapshot.resource_id,
            snapshot.resource_class,
            snapshot.requested_action,
            snapshot.applicability,
        )
        or _business_context_identity(context)
        != _business_context_from_applicability(snapshot)
    ):
        return (
            NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus.MISMATCH,
            None,
        )
    return (None, snapshot)


def _valid_applicability(applicability: _ApplicabilitySnapshot) -> bool:
    string_fields = tuple(
        object.__getattribute__(applicability, name)
        for name in _APPLICABILITY_STRING_FIELDS
    )
    return (
        all(_has_value(value) for value in string_fields)
        and applicability.resource_reference == applicability.resource_id
        and type(applicability.protected_operation) is _ProtectedOperation
        and applicability.protected_operation
        is _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        and type(applicability.resource_class) is _ResourceClass
        and applicability.resource_class is _ResourceClass.ASSESSMENT_SUBMISSION
        and type(applicability.resource_lifecycle_state) is _LifecycleState
        and applicability.resource_lifecycle_state is _LifecycleState.PROVISIONAL
        and type(applicability.resource_identity_state) is _AuthorityRecordState
        and applicability.resource_identity_state is _AuthorityRecordState.ACTIVE
        and type(applicability.requested_action) is _RequestedAction
        and applicability.requested_action is _RequestedAction.SUBMIT
        and type(applicability.applicability) is _ResourceActionApplicability
        and applicability.applicability
        is _ResourceActionApplicability.APPLICABLE
        and applicability.business_entity_authority_reference
        == _BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE
        and applicability.target_authority_reference == _TARGET_AUTHORITY_REFERENCE
        and applicability.target_governance_reference == _TARGET_GOVERNANCE_REFERENCE
        and applicability.resource_identity_authority_reference
        == _RESOURCE_IDENTITY_AUTHORITY_REFERENCE
        and applicability.resource_identity_governance_reference
        == _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE
        and applicability.applicability_authority_reference
        == _APPLICABILITY_AUTHORITY_REFERENCE
        and applicability.applicability_governance_reference
        == _APPLICABILITY_GOVERNANCE_REFERENCE
    )


def _mapped_applicability_failure(
    status: _ApplicabilityStatus,
) -> NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus | None:
    output = NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus
    mapping = {
        _ApplicabilityStatus.MALFORMED: output.MALFORMED,
        _ApplicabilityStatus.BUSINESS_CONTEXT_NOT_READY: (
            output.BUSINESS_CONTEXT_NOT_READY
        ),
        _ApplicabilityStatus.UNSUPPORTED_OPERATION: output.UNSUPPORTED_OPERATION,
        _ApplicabilityStatus.MISMATCH: output.MISMATCH,
        _ApplicabilityStatus.COLLISION: output.COLLISION,
        _ApplicabilityStatus.ALLOCATION_UNAVAILABLE: output.ALLOCATION_UNAVAILABLE,
        _ApplicabilityStatus.RESOURCE_IDENTITY_NOT_FOUND: (
            output.RESOURCE_IDENTITY_NOT_FOUND
        ),
        _ApplicabilityStatus.RESOURCE_IDENTITY_AMBIGUOUS: (
            output.RESOURCE_IDENTITY_AMBIGUOUS
        ),
        _ApplicabilityStatus.RESOURCE_IDENTITY_CONFLICTING: (
            output.RESOURCE_IDENTITY_CONFLICTING
        ),
        _ApplicabilityStatus.RESOURCE_IDENTITY_STALE: (
            output.RESOURCE_IDENTITY_STALE
        ),
        _ApplicabilityStatus.RESOURCE_IDENTITY_UNAVAILABLE: (
            output.RESOURCE_IDENTITY_UNAVAILABLE
        ),
        _ApplicabilityStatus.APPLICABILITY_NOT_APPLICABLE: (
            output.APPLICABILITY_NOT_APPLICABLE
        ),
        _ApplicabilityStatus.APPLICABILITY_UNRESOLVED: (
            output.APPLICABILITY_UNRESOLVED
        ),
    }
    return mapping.get(status)


def _business_entity_snapshot(
    result: object,
) -> tuple[
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus | None,
    _BusinessEntitySnapshot | None,
]:
    output = NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus
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
        _AuthorityLookupStatus.NOT_FOUND: output.BUSINESS_ENTITY_NOT_FOUND,
        _AuthorityLookupStatus.AMBIGUOUS: output.BUSINESS_ENTITY_AMBIGUOUS,
        _AuthorityLookupStatus.CONFLICTING: output.BUSINESS_ENTITY_CONFLICTING,
        _AuthorityLookupStatus.STALE: output.BUSINESS_ENTITY_STALE,
        _AuthorityLookupStatus.UNAVAILABLE: output.BUSINESS_ENTITY_UNAVAILABLE,
        _AuthorityLookupStatus.MALFORMED: output.MALFORMED,
        _AuthorityLookupStatus.UNSUPPORTED: output.MALFORMED,
    }
    if status is not _AuthorityLookupStatus.FOUND:
        return (mapping.get(status, output.MALFORMED), None)
    if len(records) != 1 or type(records[0]) is not _BusinessEntity:
        return (output.MALFORMED, None)
    record = records[0]
    try:
        snapshot = _BusinessEntitySnapshot(
            authority_reference=object.__getattribute__(record, "authority_reference"),
            state=object.__getattribute__(record, "state"),
            business_entity_id=object.__getattribute__(record, "business_entity_id"),
        )
    except Exception:
        return (output.MALFORMED, None)
    if (
        not _has_value(snapshot.authority_reference)
        or type(snapshot.state) is not _AuthorityRecordState
        or not _has_value(snapshot.business_entity_id)
    ):
        return (output.MALFORMED, None)
    if snapshot.state is not _AuthorityRecordState.ACTIVE:
        return (output.MALFORMED, None)
    return (None, snapshot)


def _current_business_entity_converges(
    applicability: _ApplicabilitySnapshot,
    business_entity: _BusinessEntitySnapshot,
) -> bool:
    return (
        business_entity.business_entity_id == applicability.business_entity_id
        and business_entity.authority_reference
        == _BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE
        and applicability.business_entity_authority_reference
        == business_entity.authority_reference
        and business_entity.state is _AuthorityRecordState.ACTIVE
    )


def _retry_identity(
    applicability: _ApplicabilitySnapshot,
    business_entity: _BusinessEntitySnapshot,
) -> tuple[object, ...]:
    return tuple(
        object.__getattribute__(applicability, name)
        for name in _APPLICABILITY_EVIDENCE_FIELDS
    ) + (
        business_entity.state,
        _CURRENTNESS_AUTHORITY_REFERENCE,
        _BUSINESS_ENTITY_GOVERNANCE_REFERENCE,
    )


def _currentness_fact(
    business_entity: _BusinessEntitySnapshot,
) -> NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact:
    return NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact(
        business_entity_id=business_entity.business_entity_id,
        business_entity_state=business_entity.state,
    )


def _currentness_evidence(
    applicability: _ApplicabilitySnapshot,
    business_entity: _BusinessEntitySnapshot,
    provenance_reference: str,
) -> NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence:
    return NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence(
        **{
            name: object.__getattribute__(applicability, name)
            for name in _APPLICABILITY_EVIDENCE_FIELDS
        },
        business_entity_state=business_entity.state,
        business_entity_currentness_authority_reference=(
            _CURRENTNESS_AUTHORITY_REFERENCE
        ),
        business_entity_currentness_provenance_reference=provenance_reference,
        business_entity_governance_reference=(
            _BUSINESS_ENTITY_GOVERNANCE_REFERENCE
        ),
    )


def _currentness_snapshot(
    evidence: NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence,
    retry_identity: tuple[object, ...],
) -> _CurrentnessSnapshot:
    return _CurrentnessSnapshot(
        **{
            name: object.__getattribute__(evidence, name)
            for name in _CURRENTNESS_EVIDENCE_FIELDS
        },
        retry_identity=retry_identity,
    )


def _outputs_converge(
    fact: NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact,
    evidence: NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence,
    snapshot: _CurrentnessSnapshot,
) -> bool:
    return (
        type(fact) is NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact
        and type(evidence)
        is NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence
        and fact.business_entity_id == snapshot.business_entity_id
        and fact.business_entity_state is snapshot.business_entity_state
        and evidence.business_entity_id == snapshot.business_entity_id
        and evidence.business_entity_state is _AuthorityRecordState.ACTIVE
        and evidence.business_entity_authority_reference
        == _BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE
        and evidence.business_entity_currentness_authority_reference
        == _CURRENTNESS_AUTHORITY_REFERENCE
        and _has_value(
            evidence.business_entity_currentness_provenance_reference
        )
        and evidence.business_entity_governance_reference
        == _BUSINESS_ENTITY_GOVERNANCE_REFERENCE
    )


def _success_output(
    status: NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus,
    snapshot: _CurrentnessSnapshot,
) -> NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult:
    fact = NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact(
        business_entity_id=snapshot.business_entity_id,
        business_entity_state=snapshot.business_entity_state,
    )
    evidence = NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence(
        **{
            name: object.__getattribute__(snapshot, name)
            for name in _CURRENTNESS_EVIDENCE_FIELDS
        }
    )
    return NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(
        status=status,
        business_entity_currentness_fact=fact,
        establishment_evidence=evidence,
    )


def _failure(
    status: NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus,
) -> NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult:
    return NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(
        status=status
    )


def _business_context_identity(
    context: _BusinessContextSnapshot,
) -> tuple[object, ...]:
    return tuple(
        object.__getattribute__(context, name) for name in _BUSINESS_CONTEXT_FIELDS
    )


def _business_context_from_applicability(
    applicability: _ApplicabilitySnapshot,
) -> tuple[object, ...]:
    return tuple(
        object.__getattribute__(applicability, name)
        for name in _BUSINESS_CONTEXT_FIELDS
    )


def _has_value(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and bool(value.strip())
    )


_BUSINESS_CONTEXT_FIELDS = (
    "attempt_reference",
    "principal_id",
    "engagement_reference",
    "business_entity_id",
    "protected_operation",
    "principal_authority_reference",
    "engagement_authority_reference",
    "engagement_establishment_provenance_reference",
    "participation_authority_reference",
    "participation_provenance_reference",
    "business_entity_authority_reference",
)

_APPLICABILITY_FACT_FIELDS = (
    "resource_reference",
    "resource_id",
    "resource_class",
    "requested_action",
    "applicability",
)

_APPLICABILITY_EVIDENCE_FIELDS = (
    "attempt_reference",
    "resource_reference",
    "resource_id",
    "principal_id",
    "engagement_reference",
    "business_entity_id",
    "protected_operation",
    "principal_authority_reference",
    "engagement_authority_reference",
    "engagement_establishment_provenance_reference",
    "participation_authority_reference",
    "participation_provenance_reference",
    "business_entity_authority_reference",
    "allocation_authority_reference",
    "allocation_provenance_reference",
    "binding_authority_reference",
    "binding_provenance_reference",
    "resource_class",
    "resource_lifecycle_state",
    "lifecycle_authority_reference",
    "lifecycle_provenance_reference",
    "target_authority_reference",
    "target_provenance_reference",
    "target_governance_reference",
    "resource_identity_state",
    "resource_identity_authority_reference",
    "resource_identity_provenance_reference",
    "resource_identity_governance_reference",
    "requested_action",
    "applicability",
    "applicability_authority_reference",
    "applicability_provenance_reference",
    "applicability_governance_reference",
)

_CURRENTNESS_EVIDENCE_FIELDS = _APPLICABILITY_EVIDENCE_FIELDS + (
    "business_entity_state",
    "business_entity_currentness_authority_reference",
    "business_entity_currentness_provenance_reference",
    "business_entity_governance_reference",
)

_APPLICABILITY_STRING_FIELDS = tuple(
    name
    for name in _APPLICABILITY_EVIDENCE_FIELDS
    if name
    not in {
        "protected_operation",
        "resource_class",
        "resource_lifecycle_state",
        "resource_identity_state",
        "requested_action",
        "applicability",
    }
)
