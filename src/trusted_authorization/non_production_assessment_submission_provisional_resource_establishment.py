from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import ResourceClass as _ResourceClass
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation as _ProtectedOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (
    NonProductionAssessmentSubmissionBusinessContext as _BusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult as _BusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus as _BusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_allocation_binding import (
    NonProductionAssessmentSubmissionAttemptResourceBindingEvidence as _BindingEvidence,
    NonProductionAssessmentSubmissionResourceAllocationBindingAuthority as _AllocationBindingAuthority,
    NonProductionAssessmentSubmissionResourceAllocationBindingResult as _AllocationBindingResult,
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus as _AllocationBindingStatus,
    NonProductionAssessmentSubmissionResourceAllocationEvidence as _AllocationEvidence,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)


_LIFECYCLE_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-lifecycle-establishment-authority"
)
_LIFECYCLE_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-provisional-resource-establishment-"
    "provenance"
)


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionProvisionalResourceFact:
    """Minimal non-effective provisional Assessment Submission resource fact."""

    resource_reference: str
    business_entity_id: str
    resource_class: _ResourceClass
    lifecycle_state: _LifecycleState


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence:
    """Bounded evidence for one provisional resource establishment event."""

    attempt_reference: str
    resource_reference: str
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
    lifecycle_state: _LifecycleState
    lifecycle_authority_reference: str
    lifecycle_provenance_reference: str


class NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus(
    _Enum
):
    ESTABLISHED = "ESTABLISHED"
    REUSED = "REUSED"
    MALFORMED = "MALFORMED"
    BUSINESS_CONTEXT_NOT_READY = "BUSINESS_CONTEXT_NOT_READY"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    MISMATCH = "MISMATCH"
    COLLISION = "COLLISION"
    ALLOCATION_UNAVAILABLE = "ALLOCATION_UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult:
    status: NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus
    provisional_resource: (
        NonProductionAssessmentSubmissionProvisionalResourceFact | None
    ) = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence
        | None
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
class _UpstreamSnapshot:
    attempt_reference: str
    resource_reference: str
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


@_dataclass(frozen=True, slots=True)
class _LifecycleSnapshot:
    provisional_resource: NonProductionAssessmentSubmissionProvisionalResourceFact
    establishment_evidence: (
        NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence
    )
    lineage_identity: tuple[object, ...]


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority:
    """Sequential in-memory non-production provisional-resource proof.

    This authority privately owns the exact allocation/binding authority. Its
    state is instance-local and is not persistent, concurrent, distributed,
    crash-recoverable, runtime-integrated, or production authority.
    """

    __slots__ = (
        "_allocation_binding_authority",
        "_establishments_by_attempt",
        "_establishments_by_resource_reference",
        "_next_lifecycle_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._allocation_binding_authority = _AllocationBindingAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._establishments_by_attempt: dict[str, _LifecycleSnapshot] = {}
        self._establishments_by_resource_reference: dict[
            str, _LifecycleSnapshot
        ] = {}
        self._next_lifecycle_provenance_index = 1

    def establish_assessment_submission_provisional_resource(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult:
        captured_status, business_context = _business_context_snapshot(
            business_context_result
        )
        if captured_status is _CapturedStatus.MALFORMED:
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                MALFORMED
            )
        if captured_status is _CapturedStatus.NOT_READY or business_context is None:
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                BUSINESS_CONTEXT_NOT_READY
            )
        if (
            business_context.protected_operation
            is not _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                UNSUPPORTED_OPERATION
            )

        allocation_binding_authority = self._allocation_binding_authority
        if type(allocation_binding_authority) is not _AllocationBindingAuthority:
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                MALFORMED
            )
        try:
            upstream_result = (
                _AllocationBindingAuthority.
                establish_assessment_submission_resource_allocation_binding(
                    allocation_binding_authority,
                    business_context_result=business_context_result,
                )
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                MALFORMED
            )

        upstream_status, upstream = _upstream_snapshot(
            upstream_result,
            business_context,
        )
        if upstream_status is not None:
            return _failure(upstream_status)
        if upstream is None:
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                MALFORMED
            )

        identity = _lineage_identity(upstream)
        stored_for_attempt = self._establishments_by_attempt.get(
            upstream.attempt_reference
        )
        if stored_for_attempt is not None:
            if stored_for_attempt.lineage_identity != identity:
                return _failure(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                    MISMATCH
                )
            stored_for_resource = self._establishments_by_resource_reference.get(
                upstream.resource_reference
            )
            if stored_for_resource is not stored_for_attempt:
                return _failure(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                    MISMATCH
                )
            return _success_output(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                REUSED,
                stored_for_attempt,
            )

        if (
            upstream.resource_reference
            in self._establishments_by_resource_reference
        ):
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                COLLISION
            )

        provenance_index = self._next_lifecycle_provenance_index
        lifecycle_provenance_reference = (
            f"{_LIFECYCLE_PROVENANCE_PREFIX}-{provenance_index}"
        )
        try:
            provisional_resource = (
                NonProductionAssessmentSubmissionProvisionalResourceFact(
                    resource_reference=upstream.resource_reference,
                    business_entity_id=upstream.business_entity_id,
                    resource_class=_ResourceClass.ASSESSMENT_SUBMISSION,
                    lifecycle_state=_LifecycleState.PROVISIONAL,
                )
            )
            establishment_evidence = (
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence(
                    attempt_reference=upstream.attempt_reference,
                    resource_reference=upstream.resource_reference,
                    principal_id=upstream.principal_id,
                    engagement_reference=upstream.engagement_reference,
                    business_entity_id=upstream.business_entity_id,
                    protected_operation=upstream.protected_operation,
                    principal_authority_reference=(
                        upstream.principal_authority_reference
                    ),
                    engagement_authority_reference=(
                        upstream.engagement_authority_reference
                    ),
                    engagement_establishment_provenance_reference=(
                        upstream.engagement_establishment_provenance_reference
                    ),
                    participation_authority_reference=(
                        upstream.participation_authority_reference
                    ),
                    participation_provenance_reference=(
                        upstream.participation_provenance_reference
                    ),
                    business_entity_authority_reference=(
                        upstream.business_entity_authority_reference
                    ),
                    allocation_authority_reference=(
                        upstream.allocation_authority_reference
                    ),
                    allocation_provenance_reference=(
                        upstream.allocation_provenance_reference
                    ),
                    binding_authority_reference=(
                        upstream.binding_authority_reference
                    ),
                    binding_provenance_reference=(
                        upstream.binding_provenance_reference
                    ),
                    resource_class=_ResourceClass.ASSESSMENT_SUBMISSION,
                    lifecycle_state=_LifecycleState.PROVISIONAL,
                    lifecycle_authority_reference=_LIFECYCLE_AUTHORITY_REFERENCE,
                    lifecycle_provenance_reference=lifecycle_provenance_reference,
                )
            )
            snapshot = _LifecycleSnapshot(
                provisional_resource=provisional_resource,
                establishment_evidence=establishment_evidence,
                lineage_identity=identity,
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                MALFORMED
            )

        self._establishments_by_attempt[upstream.attempt_reference] = snapshot
        self._establishments_by_resource_reference[
            upstream.resource_reference
        ] = snapshot
        self._next_lifecycle_provenance_index = provenance_index + 1

        return _success_output(
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
            ESTABLISHED,
            snapshot,
        )


def _business_context_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _BusinessContextSnapshot | None]:
    if type(result) is not _BusinessContextResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        business_context = object.__getattribute__(result, "business_context")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not _BusinessContextStatus:
        return (_CapturedStatus.MALFORMED, None)
    if status is not _BusinessContextStatus.READY:
        if business_context is not None:
            return (_CapturedStatus.MALFORMED, None)
        return (_CapturedStatus.NOT_READY, None)
    if type(business_context) is not _BusinessContext:
        return (_CapturedStatus.MALFORMED, None)
    try:
        snapshot = _BusinessContextSnapshot(
            attempt_reference=object.__getattribute__(
                business_context, "attempt_reference"
            ),
            principal_id=object.__getattribute__(business_context, "principal_id"),
            engagement_reference=object.__getattribute__(
                business_context, "engagement_reference"
            ),
            business_entity_id=object.__getattribute__(
                business_context, "business_entity_id"
            ),
            protected_operation=object.__getattribute__(
                business_context, "protected_operation"
            ),
            principal_authority_reference=object.__getattribute__(
                business_context, "principal_authority_reference"
            ),
            engagement_authority_reference=object.__getattribute__(
                business_context, "engagement_authority_reference"
            ),
            engagement_establishment_provenance_reference=object.__getattribute__(
                business_context,
                "engagement_establishment_provenance_reference",
            ),
            participation_authority_reference=object.__getattribute__(
                business_context, "participation_authority_reference"
            ),
            participation_provenance_reference=object.__getattribute__(
                business_context, "participation_provenance_reference"
            ),
            business_entity_authority_reference=object.__getattribute__(
                business_context, "business_entity_authority_reference"
            ),
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(snapshot.attempt_reference)
        or not _has_value(snapshot.principal_id)
        or not _has_value(snapshot.engagement_reference)
        or not _has_value(snapshot.business_entity_id)
        or type(snapshot.protected_operation) is not _ProtectedOperation
        or not _has_value(snapshot.principal_authority_reference)
        or not _has_value(snapshot.engagement_authority_reference)
        or not _has_value(
            snapshot.engagement_establishment_provenance_reference
        )
        or not _has_value(snapshot.participation_authority_reference)
        or not _has_value(snapshot.participation_provenance_reference)
        or not _has_value(snapshot.business_entity_authority_reference)
    ):
        return (_CapturedStatus.MALFORMED, None)
    return (_CapturedStatus.READY, snapshot)


def _upstream_snapshot(
    result: object,
    business_context: _BusinessContextSnapshot,
) -> tuple[
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus | None,
    _UpstreamSnapshot | None,
]:
    malformed = (
        NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
        MALFORMED
    )
    if type(result) is not _AllocationBindingResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        allocation = object.__getattribute__(result, "allocation_evidence")
        binding = object.__getattribute__(result, "binding_evidence")
    except Exception:
        return (malformed, None)
    if type(status) is not _AllocationBindingStatus:
        return (malformed, None)

    failure_status = _mapped_upstream_failure(status)
    if failure_status is not None:
        if allocation is not None or binding is not None:
            return (malformed, None)
        return (failure_status, None)
    if status not in (
        _AllocationBindingStatus.READY,
        _AllocationBindingStatus.REUSED,
    ):
        return (malformed, None)
    if type(allocation) is not _AllocationEvidence:
        return (malformed, None)
    if type(binding) is not _BindingEvidence:
        return (malformed, None)

    try:
        allocation_resource_reference = object.__getattribute__(
            allocation, "resource_reference"
        )
        allocation_resource_class = object.__getattribute__(
            allocation, "resource_class"
        )
        allocation_authority_reference = object.__getattribute__(
            allocation, "allocation_authority_reference"
        )
        allocation_provenance_reference = object.__getattribute__(
            allocation, "allocation_provenance_reference"
        )
        upstream = _UpstreamSnapshot(
            attempt_reference=object.__getattribute__(
                binding, "attempt_reference"
            ),
            resource_reference=object.__getattribute__(
                binding, "resource_reference"
            ),
            principal_id=object.__getattribute__(binding, "principal_id"),
            engagement_reference=object.__getattribute__(
                binding, "engagement_reference"
            ),
            business_entity_id=object.__getattribute__(
                binding, "business_entity_id"
            ),
            protected_operation=object.__getattribute__(
                binding, "protected_operation"
            ),
            principal_authority_reference=object.__getattribute__(
                binding, "principal_authority_reference"
            ),
            engagement_authority_reference=object.__getattribute__(
                binding, "engagement_authority_reference"
            ),
            engagement_establishment_provenance_reference=object.__getattribute__(
                binding,
                "engagement_establishment_provenance_reference",
            ),
            participation_authority_reference=object.__getattribute__(
                binding, "participation_authority_reference"
            ),
            participation_provenance_reference=object.__getattribute__(
                binding, "participation_provenance_reference"
            ),
            business_entity_authority_reference=object.__getattribute__(
                binding, "business_entity_authority_reference"
            ),
            allocation_authority_reference=object.__getattribute__(
                binding, "allocation_authority_reference"
            ),
            allocation_provenance_reference=object.__getattribute__(
                binding, "allocation_provenance_reference"
            ),
            binding_authority_reference=object.__getattribute__(
                binding, "binding_authority_reference"
            ),
            binding_provenance_reference=object.__getattribute__(
                binding, "binding_provenance_reference"
            ),
        )
    except Exception:
        return (malformed, None)

    if (
        not _has_value(allocation_resource_reference)
        or type(allocation_resource_class) is not _ResourceClass
        or allocation_resource_class is not _ResourceClass.ASSESSMENT_SUBMISSION
        or not _has_value(allocation_authority_reference)
        or not _has_value(allocation_provenance_reference)
        or not _valid_upstream_snapshot(upstream)
        or upstream.resource_reference != allocation_resource_reference
        or upstream.allocation_authority_reference
        != allocation_authority_reference
        or upstream.allocation_provenance_reference
        != allocation_provenance_reference
        or _business_context_identity_from_upstream(upstream)
        != _business_context_identity(business_context)
    ):
        return (malformed, None)
    return (None, upstream)


def _mapped_upstream_failure(
    status: _AllocationBindingStatus,
) -> NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus | None:
    mapping = {
        _AllocationBindingStatus.MALFORMED: (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
            MALFORMED
        ),
        _AllocationBindingStatus.BUSINESS_CONTEXT_NOT_READY: (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
            BUSINESS_CONTEXT_NOT_READY
        ),
        _AllocationBindingStatus.UNSUPPORTED_OPERATION: (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
            UNSUPPORTED_OPERATION
        ),
        _AllocationBindingStatus.MISMATCH: (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
            MISMATCH
        ),
        _AllocationBindingStatus.COLLISION: (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
            COLLISION
        ),
        _AllocationBindingStatus.ALLOCATION_UNAVAILABLE: (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
            ALLOCATION_UNAVAILABLE
        ),
    }
    return mapping.get(status)


def _valid_upstream_snapshot(upstream: _UpstreamSnapshot) -> bool:
    return (
        _has_value(upstream.attempt_reference)
        and _has_value(upstream.resource_reference)
        and _has_value(upstream.principal_id)
        and _has_value(upstream.engagement_reference)
        and _has_value(upstream.business_entity_id)
        and type(upstream.protected_operation) is _ProtectedOperation
        and upstream.protected_operation
        is _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        and _has_value(upstream.principal_authority_reference)
        and _has_value(upstream.engagement_authority_reference)
        and _has_value(upstream.engagement_establishment_provenance_reference)
        and _has_value(upstream.participation_authority_reference)
        and _has_value(upstream.participation_provenance_reference)
        and _has_value(upstream.business_entity_authority_reference)
        and _has_value(upstream.allocation_authority_reference)
        and _has_value(upstream.allocation_provenance_reference)
        and _has_value(upstream.binding_authority_reference)
        and _has_value(upstream.binding_provenance_reference)
    )


def _business_context_identity(
    business_context: _BusinessContextSnapshot,
) -> tuple[object, ...]:
    return (
        business_context.attempt_reference,
        business_context.principal_id,
        business_context.engagement_reference,
        business_context.business_entity_id,
        business_context.protected_operation,
        business_context.principal_authority_reference,
        business_context.engagement_authority_reference,
        business_context.engagement_establishment_provenance_reference,
        business_context.participation_authority_reference,
        business_context.participation_provenance_reference,
        business_context.business_entity_authority_reference,
    )


def _business_context_identity_from_upstream(
    upstream: _UpstreamSnapshot,
) -> tuple[object, ...]:
    return (
        upstream.attempt_reference,
        upstream.principal_id,
        upstream.engagement_reference,
        upstream.business_entity_id,
        upstream.protected_operation,
        upstream.principal_authority_reference,
        upstream.engagement_authority_reference,
        upstream.engagement_establishment_provenance_reference,
        upstream.participation_authority_reference,
        upstream.participation_provenance_reference,
        upstream.business_entity_authority_reference,
    )


def _lineage_identity(upstream: _UpstreamSnapshot) -> tuple[object, ...]:
    return (
        *_business_context_identity_from_upstream(upstream),
        upstream.resource_reference,
        upstream.allocation_authority_reference,
        upstream.allocation_provenance_reference,
        upstream.binding_authority_reference,
        upstream.binding_provenance_reference,
    )


def _success_output(
    status: NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus,
    snapshot: _LifecycleSnapshot,
) -> NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult:
    resource = snapshot.provisional_resource
    evidence = snapshot.establishment_evidence
    return NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult(
        status=status,
        provisional_resource=(
            NonProductionAssessmentSubmissionProvisionalResourceFact(
                resource_reference=resource.resource_reference,
                business_entity_id=resource.business_entity_id,
                resource_class=resource.resource_class,
                lifecycle_state=resource.lifecycle_state,
            )
        ),
        establishment_evidence=(
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence(
                attempt_reference=evidence.attempt_reference,
                resource_reference=evidence.resource_reference,
                principal_id=evidence.principal_id,
                engagement_reference=evidence.engagement_reference,
                business_entity_id=evidence.business_entity_id,
                protected_operation=evidence.protected_operation,
                principal_authority_reference=(
                    evidence.principal_authority_reference
                ),
                engagement_authority_reference=(
                    evidence.engagement_authority_reference
                ),
                engagement_establishment_provenance_reference=(
                    evidence.engagement_establishment_provenance_reference
                ),
                participation_authority_reference=(
                    evidence.participation_authority_reference
                ),
                participation_provenance_reference=(
                    evidence.participation_provenance_reference
                ),
                business_entity_authority_reference=(
                    evidence.business_entity_authority_reference
                ),
                allocation_authority_reference=(
                    evidence.allocation_authority_reference
                ),
                allocation_provenance_reference=(
                    evidence.allocation_provenance_reference
                ),
                binding_authority_reference=evidence.binding_authority_reference,
                binding_provenance_reference=(
                    evidence.binding_provenance_reference
                ),
                resource_class=evidence.resource_class,
                lifecycle_state=evidence.lifecycle_state,
                lifecycle_authority_reference=(
                    evidence.lifecycle_authority_reference
                ),
                lifecycle_provenance_reference=(
                    evidence.lifecycle_provenance_reference
                ),
            )
        ),
    )


def _failure(
    status: NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus,
) -> NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult:
    return NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult(
        status=status,
        provisional_resource=None,
        establishment_evidence=None,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value
