from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.applicability import (
    APPLICABILITY_GOVERNANCE_VERSION as _GENERIC_APPLICABILITY_GOVERNANCE_REFERENCE,
    resolve_applicability as _resolve_applicability,
)
from trusted_authorization.models import (
    AuthorityRecordState as _AuthorityRecordState,
    RequestedAction as _RequestedAction,
    ResourceActionApplicability as _ResourceActionApplicability,
    ResourceClass as _ResourceClass,
)
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionApplicationOperationSelectionResult as _OperationSelectionResult,
    NonProductionApplicationOperationSelectionStatus as _OperationSelectionStatus,
    NonProductionProtectedApplicationOperation as _ProtectedOperation,
    resolve_non_production_application_operation_selection as _select_operation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (
    NonProductionAssessmentSubmissionBusinessContext as _BusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult as _BusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus as _BusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_identity_establishment import (
    NonProductionAssessmentSubmissionResourceIdentityAuthority as _ResourceIdentityAuthority,
    NonProductionAssessmentSubmissionResourceIdentityEvidence as _ResourceIdentityEvidence,
    NonProductionAssessmentSubmissionResourceIdentityFact as _ResourceIdentityFact,
    NonProductionAssessmentSubmissionResourceIdentityResult as _ResourceIdentityResult,
    NonProductionAssessmentSubmissionResourceIdentityStatus as _ResourceIdentityStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)
from trusted_authorization.non_production_resource_action_handoff import (
    NonProductionApplicationOperation as _ApplicationOperation,
    NonProductionResourceActionHandoffResult as _ResourceActionHandoffResult,
    NonProductionResourceActionHandoffStatus as _ResourceActionHandoffStatus,
    resolve_non_production_resource_action_handoff as _resolve_resource_action,
)


_APPLICABILITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-action-applicability-authority"
)
_APPLICABILITY_GOVERNANCE_REFERENCE = (
    "resource-action-applicability-governance-v1"
)
_APPLICABILITY_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-resource-action-applicability-"
    "establishment-provenance"
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
class NonProductionAssessmentSubmissionResourceActionApplicabilityFact:
    """Minimal bounded fact for one applicable Assessment Submission action."""

    resource_reference: str
    resource_id: str
    resource_class: _ResourceClass
    requested_action: _RequestedAction
    applicability: _ResourceActionApplicability


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence:
    """Complete bounded lineage for one applicability establishment event."""

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


class NonProductionAssessmentSubmissionResourceActionApplicabilityStatus(_Enum):
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


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceActionApplicabilityResult:
    status: NonProductionAssessmentSubmissionResourceActionApplicabilityStatus
    applicability_fact: (
        NonProductionAssessmentSubmissionResourceActionApplicabilityFact | None
    ) = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence | None
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
class _ResourceIdentitySnapshot:
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
    retry_identity: tuple[object, ...]


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority:
    """Sequential in-memory Assessment Submission applicability proof."""

    __slots__ = (
        "_resource_identity_authority",
        "_applicabilities_by_attempt",
        "_applicabilities_by_resource_reference",
        "_applicabilities_by_resource_id",
        "_next_applicability_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._resource_identity_authority = _ResourceIdentityAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._applicabilities_by_attempt: dict[str, _ApplicabilitySnapshot] = {}
        self._applicabilities_by_resource_reference: dict[
            str, _ApplicabilitySnapshot
        ] = {}
        self._applicabilities_by_resource_id: dict[str, _ApplicabilitySnapshot] = {}
        self._next_applicability_provenance_index = 1

    def establish_assessment_submission_resource_action_applicability(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionResourceActionApplicabilityResult:
        captured_status, business_context = _business_context_snapshot(
            business_context_result
        )
        if captured_status is _CapturedStatus.MALFORMED:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                MALFORMED
            )
        if captured_status is _CapturedStatus.NOT_READY or business_context is None:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                BUSINESS_CONTEXT_NOT_READY
            )
        if (
            business_context.protected_operation
            is not _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                UNSUPPORTED_OPERATION
            )

        resource_identity_authority = self._resource_identity_authority
        if type(resource_identity_authority) is not _ResourceIdentityAuthority:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                MALFORMED
            )
        try:
            resource_identity_result = (
                _ResourceIdentityAuthority.
                establish_assessment_submission_resource_identity(
                    resource_identity_authority,
                    business_context_result=business_context_result,
                )
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                MALFORMED
            )

        identity_status, identity = _resource_identity_snapshot(
            resource_identity_result,
            business_context,
        )
        if identity_status is not None:
            return _failure(identity_status)
        if identity is None:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                MALFORMED
            )

        action_status, requested_action = _canonical_action(identity)
        if action_status is not None:
            return _failure(action_status)
        if requested_action is None:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                MALFORMED
            )

        applicability_status, applicability = _applicability_resolution(
            identity.resource_class,
            requested_action,
        )
        if applicability_status is not None:
            return _failure(applicability_status)
        if applicability is None:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                MALFORMED
            )

        retry_identity = _retry_identity(identity, requested_action, applicability)
        stored_for_attempt = self._applicabilities_by_attempt.get(
            identity.attempt_reference
        )
        if stored_for_attempt is not None:
            if stored_for_attempt.retry_identity != retry_identity:
                return _failure(
                    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                    MISMATCH
                )
            stored_for_resource = self._applicabilities_by_resource_reference.get(
                identity.resource_reference
            )
            stored_for_resource_id = self._applicabilities_by_resource_id.get(
                identity.resource_id
            )
            if (
                stored_for_resource is not stored_for_attempt
                or stored_for_resource_id is not stored_for_attempt
            ):
                return _failure(
                    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                    MISMATCH
                )
            return _success_output(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                REUSED,
                stored_for_attempt,
            )

        if (
            identity.resource_reference
            in self._applicabilities_by_resource_reference
            or identity.resource_id in self._applicabilities_by_resource_id
        ):
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                COLLISION
            )

        provenance_index = self._next_applicability_provenance_index
        provenance_reference = (
            f"{_APPLICABILITY_PROVENANCE_PREFIX}-{provenance_index}"
        )
        try:
            fact = _applicability_fact(identity, requested_action, applicability)
            evidence = _applicability_evidence(
                identity,
                requested_action,
                applicability,
                provenance_reference,
            )
            snapshot = _applicability_snapshot(evidence, retry_identity)
            if not _outputs_converge(fact, evidence, snapshot):
                return _failure(
                    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                    MALFORMED
                )
            output = _success_output(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                ESTABLISHED,
                snapshot,
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
                MALFORMED
            )

        self._applicabilities_by_attempt[identity.attempt_reference] = snapshot
        self._applicabilities_by_resource_reference[
            identity.resource_reference
        ] = snapshot
        self._applicabilities_by_resource_id[identity.resource_id] = snapshot
        self._next_applicability_provenance_index = provenance_index + 1
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
            attempt_reference=object.__getattribute__(context, "attempt_reference"),
            principal_id=object.__getattribute__(context, "principal_id"),
            engagement_reference=object.__getattribute__(
                context, "engagement_reference"
            ),
            business_entity_id=object.__getattribute__(context, "business_entity_id"),
            protected_operation=object.__getattribute__(context, "protected_operation"),
            principal_authority_reference=object.__getattribute__(
                context, "principal_authority_reference"
            ),
            engagement_authority_reference=object.__getattribute__(
                context, "engagement_authority_reference"
            ),
            engagement_establishment_provenance_reference=object.__getattribute__(
                context, "engagement_establishment_provenance_reference"
            ),
            participation_authority_reference=object.__getattribute__(
                context, "participation_authority_reference"
            ),
            participation_provenance_reference=object.__getattribute__(
                context, "participation_provenance_reference"
            ),
            business_entity_authority_reference=object.__getattribute__(
                context, "business_entity_authority_reference"
            ),
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if not _valid_business_context(snapshot):
        return (_CapturedStatus.MALFORMED, None)
    return (_CapturedStatus.READY, snapshot)


def _valid_business_context(context: _BusinessContextSnapshot) -> bool:
    return (
        _has_value(context.attempt_reference)
        and _has_value(context.principal_id)
        and _has_value(context.engagement_reference)
        and _has_value(context.business_entity_id)
        and type(context.protected_operation) is _ProtectedOperation
        and _has_value(context.principal_authority_reference)
        and _has_value(context.engagement_authority_reference)
        and _has_value(context.engagement_establishment_provenance_reference)
        and _has_value(context.participation_authority_reference)
        and _has_value(context.participation_provenance_reference)
        and _has_value(context.business_entity_authority_reference)
    )


def _resource_identity_snapshot(
    result: object,
    business_context: _BusinessContextSnapshot,
) -> tuple[
    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus | None,
    _ResourceIdentitySnapshot | None,
]:
    malformed = (
        NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.MALFORMED
    )
    if type(result) is not _ResourceIdentityResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        fact = object.__getattribute__(result, "resource_identity_fact")
        evidence = object.__getattribute__(result, "establishment_evidence")
    except Exception:
        return (malformed, None)
    if type(status) is not _ResourceIdentityStatus:
        return (malformed, None)

    mapped_failure = _mapped_resource_identity_failure(status)
    if mapped_failure is not None:
        if fact is not None or evidence is not None:
            return (malformed, None)
        return (mapped_failure, None)
    if status not in (
        _ResourceIdentityStatus.ESTABLISHED,
        _ResourceIdentityStatus.REUSED,
    ):
        return (malformed, None)
    if type(fact) is not _ResourceIdentityFact:
        return (malformed, None)
    if type(evidence) is not _ResourceIdentityEvidence:
        return (malformed, None)

    try:
        fact_values = (
            object.__getattribute__(fact, "resource_reference"),
            object.__getattribute__(fact, "resource_id"),
            object.__getattribute__(fact, "business_entity_id"),
            object.__getattribute__(fact, "resource_class"),
            object.__getattribute__(fact, "resource_lifecycle_state"),
        )
        identity = _ResourceIdentitySnapshot(
            **{
                name: object.__getattribute__(evidence, name)
                for name in _RESOURCE_IDENTITY_EVIDENCE_FIELDS
            }
        )
    except Exception:
        return (malformed, None)

    if not _valid_resource_identity_fact_values(fact_values):
        return (malformed, None)
    if not _valid_resource_identity(identity):
        return (malformed, None)
    if fact_values != (
        identity.resource_reference,
        identity.resource_id,
        identity.business_entity_id,
        identity.resource_class,
        identity.resource_lifecycle_state,
    ):
        return (
            NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
            MISMATCH,
            None,
        )
    if _business_context_identity(business_context) != _business_context_from_identity(
        identity
    ):
        return (
            NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.
            MISMATCH,
            None,
        )
    return (None, identity)


def _valid_resource_identity_fact_values(values: tuple[object, ...]) -> bool:
    return (
        len(values) == 5
        and _has_value(values[0])
        and _has_value(values[1])
        and _has_value(values[2])
        and type(values[3]) is _ResourceClass
        and values[3] is _ResourceClass.ASSESSMENT_SUBMISSION
        and type(values[4]) is _LifecycleState
        and values[4] is _LifecycleState.PROVISIONAL
    )


def _mapped_resource_identity_failure(
    status: _ResourceIdentityStatus,
) -> NonProductionAssessmentSubmissionResourceActionApplicabilityStatus | None:
    output = NonProductionAssessmentSubmissionResourceActionApplicabilityStatus
    mapping = {
        _ResourceIdentityStatus.MALFORMED: output.MALFORMED,
        _ResourceIdentityStatus.BUSINESS_CONTEXT_NOT_READY: (
            output.BUSINESS_CONTEXT_NOT_READY
        ),
        _ResourceIdentityStatus.UNSUPPORTED_OPERATION: output.UNSUPPORTED_OPERATION,
        _ResourceIdentityStatus.MISMATCH: output.MISMATCH,
        _ResourceIdentityStatus.COLLISION: output.COLLISION,
        _ResourceIdentityStatus.ALLOCATION_UNAVAILABLE: output.ALLOCATION_UNAVAILABLE,
        _ResourceIdentityStatus.RESOURCE_IDENTITY_NOT_FOUND: (
            output.RESOURCE_IDENTITY_NOT_FOUND
        ),
        _ResourceIdentityStatus.RESOURCE_IDENTITY_AMBIGUOUS: (
            output.RESOURCE_IDENTITY_AMBIGUOUS
        ),
        _ResourceIdentityStatus.RESOURCE_IDENTITY_CONFLICTING: (
            output.RESOURCE_IDENTITY_CONFLICTING
        ),
        _ResourceIdentityStatus.RESOURCE_IDENTITY_STALE: (
            output.RESOURCE_IDENTITY_STALE
        ),
        _ResourceIdentityStatus.RESOURCE_IDENTITY_UNAVAILABLE: (
            output.RESOURCE_IDENTITY_UNAVAILABLE
        ),
    }
    return mapping.get(status)


def _valid_resource_identity(identity: _ResourceIdentitySnapshot) -> bool:
    string_fields = (
        identity.attempt_reference,
        identity.resource_reference,
        identity.resource_id,
        identity.principal_id,
        identity.engagement_reference,
        identity.business_entity_id,
        identity.principal_authority_reference,
        identity.engagement_authority_reference,
        identity.engagement_establishment_provenance_reference,
        identity.participation_authority_reference,
        identity.participation_provenance_reference,
        identity.business_entity_authority_reference,
        identity.allocation_authority_reference,
        identity.allocation_provenance_reference,
        identity.binding_authority_reference,
        identity.binding_provenance_reference,
        identity.lifecycle_authority_reference,
        identity.lifecycle_provenance_reference,
        identity.target_authority_reference,
        identity.target_provenance_reference,
        identity.target_governance_reference,
        identity.resource_identity_authority_reference,
        identity.resource_identity_provenance_reference,
        identity.resource_identity_governance_reference,
    )
    return (
        all(_has_value(value) for value in string_fields)
        and identity.resource_reference == identity.resource_id
        and type(identity.protected_operation) is _ProtectedOperation
        and identity.protected_operation
        is _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        and type(identity.resource_class) is _ResourceClass
        and identity.resource_class is _ResourceClass.ASSESSMENT_SUBMISSION
        and type(identity.resource_lifecycle_state) is _LifecycleState
        and identity.resource_lifecycle_state is _LifecycleState.PROVISIONAL
        and type(identity.resource_identity_state) is _AuthorityRecordState
        and identity.resource_identity_state is _AuthorityRecordState.ACTIVE
        and identity.target_authority_reference == _TARGET_AUTHORITY_REFERENCE
        and identity.target_governance_reference == _TARGET_GOVERNANCE_REFERENCE
        and identity.resource_identity_authority_reference
        == _RESOURCE_IDENTITY_AUTHORITY_REFERENCE
        and identity.resource_identity_governance_reference
        == _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE
    )


def _canonical_action(
    identity: _ResourceIdentitySnapshot,
) -> tuple[
    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus | None,
    _RequestedAction | None,
]:
    malformed = (
        NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.MALFORMED
    )
    mismatch = (
        NonProductionAssessmentSubmissionResourceActionApplicabilityStatus.MISMATCH
    )
    try:
        selection = _select_operation(
            protected_operation=identity.protected_operation,
        )
    except Exception:
        return (malformed, None)
    if type(selection) is not _OperationSelectionResult:
        return (malformed, None)
    try:
        selection_status = object.__getattribute__(selection, "status")
        application_operation = object.__getattribute__(
            selection, "selected_application_operation"
        )
    except Exception:
        return (malformed, None)
    if type(selection_status) is not _OperationSelectionStatus:
        return (malformed, None)
    if selection_status is not _OperationSelectionStatus.READY:
        return (malformed, None)
    if type(application_operation) is not _ApplicationOperation:
        return (malformed, None)
    if application_operation is not _ApplicationOperation.SUBMIT_ASSESSMENT:
        return (mismatch, None)

    try:
        handoff = _resolve_resource_action(
            resource_reference=identity.resource_reference,
            operation=application_operation,
        )
    except Exception:
        return (malformed, None)
    if type(handoff) is not _ResourceActionHandoffResult:
        return (malformed, None)
    try:
        handoff_status = object.__getattribute__(handoff, "status")
        resource_reference = object.__getattribute__(handoff, "resource_reference")
        requested_action = object.__getattribute__(handoff, "requested_action")
    except Exception:
        return (malformed, None)
    if type(handoff_status) is not _ResourceActionHandoffStatus:
        return (malformed, None)
    if handoff_status is not _ResourceActionHandoffStatus.READY:
        return (malformed, None)
    if not _has_value(resource_reference):
        return (malformed, None)
    if resource_reference != identity.resource_reference:
        return (mismatch, None)
    if type(requested_action) is not _RequestedAction:
        return (malformed, None)
    if requested_action is not _RequestedAction.SUBMIT:
        return (mismatch, None)
    return (None, requested_action)


def _applicability_resolution(
    resource_class: _ResourceClass,
    requested_action: _RequestedAction,
) -> tuple[
    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus | None,
    _ResourceActionApplicability | None,
]:
    output = NonProductionAssessmentSubmissionResourceActionApplicabilityStatus
    if _GENERIC_APPLICABILITY_GOVERNANCE_REFERENCE != (
        _APPLICABILITY_GOVERNANCE_REFERENCE
    ):
        return (output.APPLICABILITY_UNRESOLVED, None)
    try:
        applicability = _resolve_applicability(resource_class, requested_action)
    except Exception:
        return (output.APPLICABILITY_UNRESOLVED, None)
    if type(applicability) is not _ResourceActionApplicability:
        return (output.MALFORMED, None)
    if applicability is _ResourceActionApplicability.NOT_APPLICABLE:
        return (output.APPLICABILITY_NOT_APPLICABLE, None)
    if applicability is _ResourceActionApplicability.UNRESOLVED:
        return (output.APPLICABILITY_UNRESOLVED, None)
    if applicability is not _ResourceActionApplicability.APPLICABLE:
        return (output.MALFORMED, None)
    return (None, applicability)


def _applicability_fact(
    identity: _ResourceIdentitySnapshot,
    requested_action: _RequestedAction,
    applicability: _ResourceActionApplicability,
) -> NonProductionAssessmentSubmissionResourceActionApplicabilityFact:
    return NonProductionAssessmentSubmissionResourceActionApplicabilityFact(
        resource_reference=identity.resource_reference,
        resource_id=identity.resource_id,
        resource_class=identity.resource_class,
        requested_action=requested_action,
        applicability=applicability,
    )


def _applicability_evidence(
    identity: _ResourceIdentitySnapshot,
    requested_action: _RequestedAction,
    applicability: _ResourceActionApplicability,
    provenance_reference: str,
) -> NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence:
    return NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence(
        **{
            name: object.__getattribute__(identity, name)
            for name in _RESOURCE_IDENTITY_EVIDENCE_FIELDS
        },
        requested_action=requested_action,
        applicability=applicability,
        applicability_authority_reference=_APPLICABILITY_AUTHORITY_REFERENCE,
        applicability_provenance_reference=provenance_reference,
        applicability_governance_reference=_APPLICABILITY_GOVERNANCE_REFERENCE,
    )


def _applicability_snapshot(
    evidence: NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence,
    retry_identity: tuple[object, ...],
) -> _ApplicabilitySnapshot:
    return _ApplicabilitySnapshot(
        **{
            name: object.__getattribute__(evidence, name)
            for name in _APPLICABILITY_EVIDENCE_FIELDS
        },
        retry_identity=retry_identity,
    )


def _retry_identity(
    identity: _ResourceIdentitySnapshot,
    requested_action: _RequestedAction,
    applicability: _ResourceActionApplicability,
) -> tuple[object, ...]:
    return tuple(
        object.__getattribute__(identity, name)
        for name in _RESOURCE_IDENTITY_EVIDENCE_FIELDS
    ) + (
        requested_action,
        applicability,
        _APPLICABILITY_AUTHORITY_REFERENCE,
        _APPLICABILITY_GOVERNANCE_REFERENCE,
    )


def _outputs_converge(
    fact: NonProductionAssessmentSubmissionResourceActionApplicabilityFact,
    evidence: NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence,
    snapshot: _ApplicabilitySnapshot,
) -> bool:
    return (
        type(fact)
        is NonProductionAssessmentSubmissionResourceActionApplicabilityFact
        and type(evidence)
        is NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence
        and fact.resource_reference == snapshot.resource_reference
        and fact.resource_id == snapshot.resource_id
        and fact.resource_class is snapshot.resource_class
        and fact.requested_action is snapshot.requested_action
        and fact.applicability is snapshot.applicability
        and evidence.attempt_reference == snapshot.attempt_reference
        and evidence.resource_reference == snapshot.resource_reference
        and evidence.resource_id == snapshot.resource_id
        and evidence.requested_action is snapshot.requested_action
        and evidence.applicability is snapshot.applicability
        and evidence.applicability_authority_reference
        == _APPLICABILITY_AUTHORITY_REFERENCE
        and evidence.applicability_governance_reference
        == _APPLICABILITY_GOVERNANCE_REFERENCE
        and _has_value(evidence.applicability_provenance_reference)
    )


def _success_output(
    status: NonProductionAssessmentSubmissionResourceActionApplicabilityStatus,
    snapshot: _ApplicabilitySnapshot,
) -> NonProductionAssessmentSubmissionResourceActionApplicabilityResult:
    fact = NonProductionAssessmentSubmissionResourceActionApplicabilityFact(
        resource_reference=snapshot.resource_reference,
        resource_id=snapshot.resource_id,
        resource_class=snapshot.resource_class,
        requested_action=snapshot.requested_action,
        applicability=snapshot.applicability,
    )
    evidence = NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence(
        **{
            name: object.__getattribute__(snapshot, name)
            for name in _APPLICABILITY_EVIDENCE_FIELDS
        }
    )
    return NonProductionAssessmentSubmissionResourceActionApplicabilityResult(
        status=status,
        applicability_fact=fact,
        establishment_evidence=evidence,
    )


def _failure(
    status: NonProductionAssessmentSubmissionResourceActionApplicabilityStatus,
) -> NonProductionAssessmentSubmissionResourceActionApplicabilityResult:
    return NonProductionAssessmentSubmissionResourceActionApplicabilityResult(
        status=status
    )


def _business_context_identity(
    context: _BusinessContextSnapshot,
) -> tuple[object, ...]:
    return (
        context.attempt_reference,
        context.principal_id,
        context.engagement_reference,
        context.business_entity_id,
        context.protected_operation,
        context.principal_authority_reference,
        context.engagement_authority_reference,
        context.engagement_establishment_provenance_reference,
        context.participation_authority_reference,
        context.participation_provenance_reference,
        context.business_entity_authority_reference,
    )


def _business_context_from_identity(
    identity: _ResourceIdentitySnapshot,
) -> tuple[object, ...]:
    return (
        identity.attempt_reference,
        identity.principal_id,
        identity.engagement_reference,
        identity.business_entity_id,
        identity.protected_operation,
        identity.principal_authority_reference,
        identity.engagement_authority_reference,
        identity.engagement_establishment_provenance_reference,
        identity.participation_authority_reference,
        identity.participation_provenance_reference,
        identity.business_entity_authority_reference,
    )


def _has_value(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and bool(value.strip())
    )


_RESOURCE_IDENTITY_EVIDENCE_FIELDS = (
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
)

_APPLICABILITY_EVIDENCE_FIELDS = _RESOURCE_IDENTITY_EVIDENCE_FIELDS + (
    "requested_action",
    "applicability",
    "applicability_authority_reference",
    "applicability_provenance_reference",
    "applicability_governance_reference",
)
