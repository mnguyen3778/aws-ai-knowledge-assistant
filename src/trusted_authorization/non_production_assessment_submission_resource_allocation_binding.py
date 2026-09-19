from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import ResourceClass as _ResourceClass
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation as _NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (
    NonProductionAssessmentSubmissionBusinessContext as _NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult as _NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus as _NonProductionAssessmentSubmissionBusinessContextStatus,
)


_ALLOCATION_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-allocation-authority"
)
_BINDING_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-attempt-resource-binding-authority"
)
_RESOURCE_REFERENCE_PREFIX = "non-production-assessment-submission-resource"
_ALLOCATION_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-resource-allocation-provenance"
)
_BINDING_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-attempt-resource-binding-provenance"
)


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceAllocationEvidence:
    """Bounded non-production evidence for an Assessment Submission R allocation."""

    resource_reference: str
    resource_class: _ResourceClass
    allocation_authority_reference: str
    allocation_provenance_reference: str


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionAttemptResourceBindingEvidence:
    """Bounded non-production evidence for immutable A -> R binding."""

    attempt_reference: str
    resource_reference: str
    principal_id: str
    engagement_reference: str
    business_entity_id: str
    protected_operation: _NonProductionProtectedApplicationOperation
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


class NonProductionAssessmentSubmissionResourceAllocationBindingStatus(_Enum):
    READY = "READY"
    REUSED = "REUSED"
    MALFORMED = "MALFORMED"
    BUSINESS_CONTEXT_NOT_READY = "BUSINESS_CONTEXT_NOT_READY"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    MISMATCH = "MISMATCH"
    COLLISION = "COLLISION"
    ALLOCATION_UNAVAILABLE = "ALLOCATION_UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceAllocationBindingResult:
    status: NonProductionAssessmentSubmissionResourceAllocationBindingStatus
    allocation_evidence: (
        NonProductionAssessmentSubmissionResourceAllocationEvidence | None
    ) = None
    binding_evidence: (
        NonProductionAssessmentSubmissionAttemptResourceBindingEvidence | None
    ) = None


@_dataclass(frozen=True, slots=True)
class _BusinessContextSnapshot:
    attempt_reference: str
    principal_id: str
    engagement_reference: str
    business_entity_id: str
    protected_operation: _NonProductionProtectedApplicationOperation
    principal_authority_reference: str
    engagement_authority_reference: str
    engagement_establishment_provenance_reference: str
    participation_authority_reference: str
    participation_provenance_reference: str
    business_entity_authority_reference: str


@_dataclass(frozen=True, slots=True)
class _AuthoritySnapshot:
    allocation: NonProductionAssessmentSubmissionResourceAllocationEvidence
    binding: NonProductionAssessmentSubmissionAttemptResourceBindingEvidence
    business_context_identity: tuple[object, ...]


class NonProductionAssessmentSubmissionResourceAllocationBindingAuthority:
    """Sequential in-memory non-production allocation + A -> R binding proof.

    State is local to this authority instance. It is not persistent,
    distributed, thread-safe, crash-recoverable, runtime-integrated, or
    production authority.
    """

    __slots__ = (
        "_bindings_by_attempt",
        "_bindings_by_resource_reference",
        "_candidate_resource_references",
        "_next_candidate_index",
        "_next_default_index",
        "_next_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        if (
            candidate_resource_references is not None
            and type(candidate_resource_references) is not tuple
        ):
            candidate_resource_references = ("",)
        self._candidate_resource_references = candidate_resource_references
        self._next_candidate_index = 0
        self._next_default_index = 1
        self._next_provenance_index = 1
        self._bindings_by_attempt: dict[str, _AuthoritySnapshot] = {}
        self._bindings_by_resource_reference: dict[str, _AuthoritySnapshot] = {}

    def establish_assessment_submission_resource_allocation_binding(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionResourceAllocationBindingResult:
        status, business_context = _business_context_snapshot(
            business_context_result
        )
        if status is _CapturedStatus.MALFORMED:
            return _result(
                NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                MALFORMED
            )
        if status is _CapturedStatus.NOT_READY or business_context is None:
            return _result(
                NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                BUSINESS_CONTEXT_NOT_READY
            )
        if (
            business_context.protected_operation
            is not _NonProductionProtectedApplicationOperation.
            PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _result(
                NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                UNSUPPORTED_OPERATION
            )

        identity = _business_context_identity(business_context)
        stored_for_attempt = self._bindings_by_attempt.get(
            business_context.attempt_reference
        )
        if stored_for_attempt is not None:
            if stored_for_attempt.business_context_identity != identity:
                return _result(
                    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                    MISMATCH
                )
            return NonProductionAssessmentSubmissionResourceAllocationBindingResult(
                status=(
                    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                    REUSED
                ),
                allocation_evidence=_allocation_output(stored_for_attempt.allocation),
                binding_evidence=_binding_output(stored_for_attempt.binding),
            )

        candidate_status, resource_reference = self._candidate_resource_reference()
        if candidate_status is not _CandidateStatus.READY:
            if candidate_status is _CandidateStatus.UNAVAILABLE:
                return _result(
                    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                    ALLOCATION_UNAVAILABLE
                )
            return _result(
                NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                MALFORMED
            )

        if resource_reference in self._bindings_by_resource_reference:
            return _result(
                NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                COLLISION
            )

        provenance_index = self._next_provenance_index
        allocation_provenance_reference = (
            f"{_ALLOCATION_PROVENANCE_PREFIX}-{provenance_index}"
        )
        binding_provenance_reference = (
            f"{_BINDING_PROVENANCE_PREFIX}-{provenance_index}"
        )
        allocation = NonProductionAssessmentSubmissionResourceAllocationEvidence(
            resource_reference=resource_reference,
            resource_class=_ResourceClass.ASSESSMENT_SUBMISSION,
            allocation_authority_reference=_ALLOCATION_AUTHORITY_REFERENCE,
            allocation_provenance_reference=allocation_provenance_reference,
        )
        binding = NonProductionAssessmentSubmissionAttemptResourceBindingEvidence(
            attempt_reference=business_context.attempt_reference,
            resource_reference=resource_reference,
            principal_id=business_context.principal_id,
            engagement_reference=business_context.engagement_reference,
            business_entity_id=business_context.business_entity_id,
            protected_operation=business_context.protected_operation,
            principal_authority_reference=(
                business_context.principal_authority_reference
            ),
            engagement_authority_reference=(
                business_context.engagement_authority_reference
            ),
            engagement_establishment_provenance_reference=(
                business_context.engagement_establishment_provenance_reference
            ),
            participation_authority_reference=(
                business_context.participation_authority_reference
            ),
            participation_provenance_reference=(
                business_context.participation_provenance_reference
            ),
            business_entity_authority_reference=(
                business_context.business_entity_authority_reference
            ),
            allocation_authority_reference=(
                allocation.allocation_authority_reference
            ),
            allocation_provenance_reference=(
                allocation.allocation_provenance_reference
            ),
            binding_authority_reference=_BINDING_AUTHORITY_REFERENCE,
            binding_provenance_reference=binding_provenance_reference,
        )
        snapshot = _AuthoritySnapshot(
            allocation=allocation,
            binding=binding,
            business_context_identity=identity,
        )

        self._bindings_by_attempt[business_context.attempt_reference] = snapshot
        self._bindings_by_resource_reference[resource_reference] = snapshot
        self._next_provenance_index += 1

        return NonProductionAssessmentSubmissionResourceAllocationBindingResult(
            status=(
                NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
                READY
            ),
            allocation_evidence=_allocation_output(allocation),
            binding_evidence=_binding_output(binding),
        )

    def _candidate_resource_reference(self) -> tuple["_CandidateStatus", str | None]:
        if self._candidate_resource_references is not None:
            if self._next_candidate_index >= len(self._candidate_resource_references):
                return (_CandidateStatus.UNAVAILABLE, None)
            candidate = self._candidate_resource_references[
                self._next_candidate_index
            ]
            if not _has_value(candidate):
                return (_CandidateStatus.MALFORMED, None)
            self._next_candidate_index += 1
            return (_CandidateStatus.READY, candidate)

        candidate = f"{_RESOURCE_REFERENCE_PREFIX}-{self._next_default_index}"
        self._next_default_index += 1
        return (_CandidateStatus.READY, candidate)


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class _CandidateStatus(_Enum):
    READY = "READY"
    UNAVAILABLE = "UNAVAILABLE"
    MALFORMED = "MALFORMED"


def _business_context_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _BusinessContextSnapshot | None]:
    if type(result) is not _NonProductionAssessmentSubmissionBusinessContextResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        business_context = object.__getattribute__(result, "business_context")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not _NonProductionAssessmentSubmissionBusinessContextStatus:
        return (_CapturedStatus.MALFORMED, None)
    if status is not _NonProductionAssessmentSubmissionBusinessContextStatus.READY:
        if business_context is not None:
            return (_CapturedStatus.MALFORMED, None)
        return (_CapturedStatus.NOT_READY, None)
    if type(business_context) is not _NonProductionAssessmentSubmissionBusinessContext:
        return (_CapturedStatus.MALFORMED, None)
    try:
        attempt_reference = object.__getattribute__(
            business_context,
            "attempt_reference",
        )
        principal_id = object.__getattribute__(business_context, "principal_id")
        engagement_reference = object.__getattribute__(
            business_context,
            "engagement_reference",
        )
        business_entity_id = object.__getattribute__(
            business_context,
            "business_entity_id",
        )
        protected_operation = object.__getattribute__(
            business_context,
            "protected_operation",
        )
        principal_authority_reference = object.__getattribute__(
            business_context,
            "principal_authority_reference",
        )
        engagement_authority_reference = object.__getattribute__(
            business_context,
            "engagement_authority_reference",
        )
        engagement_establishment_provenance_reference = object.__getattribute__(
            business_context,
            "engagement_establishment_provenance_reference",
        )
        participation_authority_reference = object.__getattribute__(
            business_context,
            "participation_authority_reference",
        )
        participation_provenance_reference = object.__getattribute__(
            business_context,
            "participation_provenance_reference",
        )
        business_entity_authority_reference = object.__getattribute__(
            business_context,
            "business_entity_authority_reference",
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(attempt_reference)
        or not _has_value(principal_id)
        or not _has_value(engagement_reference)
        or not _has_value(business_entity_id)
        or type(protected_operation) is not _NonProductionProtectedApplicationOperation
        or not _has_value(principal_authority_reference)
        or not _has_value(engagement_authority_reference)
        or not _has_value(engagement_establishment_provenance_reference)
        or not _has_value(participation_authority_reference)
        or not _has_value(participation_provenance_reference)
        or not _has_value(business_entity_authority_reference)
    ):
        return (_CapturedStatus.MALFORMED, None)
    return (
        _CapturedStatus.READY,
        _BusinessContextSnapshot(
            attempt_reference=attempt_reference,
            principal_id=principal_id,
            engagement_reference=engagement_reference,
            business_entity_id=business_entity_id,
            protected_operation=protected_operation,
            principal_authority_reference=principal_authority_reference,
            engagement_authority_reference=engagement_authority_reference,
            engagement_establishment_provenance_reference=(
                engagement_establishment_provenance_reference
            ),
            participation_authority_reference=participation_authority_reference,
            participation_provenance_reference=participation_provenance_reference,
            business_entity_authority_reference=business_entity_authority_reference,
        ),
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


def _allocation_output(
    allocation: NonProductionAssessmentSubmissionResourceAllocationEvidence,
) -> NonProductionAssessmentSubmissionResourceAllocationEvidence:
    return NonProductionAssessmentSubmissionResourceAllocationEvidence(
        resource_reference=allocation.resource_reference,
        resource_class=allocation.resource_class,
        allocation_authority_reference=allocation.allocation_authority_reference,
        allocation_provenance_reference=allocation.allocation_provenance_reference,
    )


def _binding_output(
    binding: NonProductionAssessmentSubmissionAttemptResourceBindingEvidence,
) -> NonProductionAssessmentSubmissionAttemptResourceBindingEvidence:
    return NonProductionAssessmentSubmissionAttemptResourceBindingEvidence(
        attempt_reference=binding.attempt_reference,
        resource_reference=binding.resource_reference,
        principal_id=binding.principal_id,
        engagement_reference=binding.engagement_reference,
        business_entity_id=binding.business_entity_id,
        protected_operation=binding.protected_operation,
        principal_authority_reference=binding.principal_authority_reference,
        engagement_authority_reference=binding.engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            binding.engagement_establishment_provenance_reference
        ),
        participation_authority_reference=binding.participation_authority_reference,
        participation_provenance_reference=binding.participation_provenance_reference,
        business_entity_authority_reference=(
            binding.business_entity_authority_reference
        ),
        allocation_authority_reference=binding.allocation_authority_reference,
        allocation_provenance_reference=binding.allocation_provenance_reference,
        binding_authority_reference=binding.binding_authority_reference,
        binding_provenance_reference=binding.binding_provenance_reference,
    )


def _result(
    status: NonProductionAssessmentSubmissionResourceAllocationBindingStatus,
) -> NonProductionAssessmentSubmissionResourceAllocationBindingResult:
    return NonProductionAssessmentSubmissionResourceAllocationBindingResult(
        status=status,
        allocation_evidence=None,
        binding_evidence=None,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value
