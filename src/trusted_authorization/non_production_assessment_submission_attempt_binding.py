from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from trusted_authorization.models import (
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    PrincipalMapping,
)
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_engagement_participation_source import (
    NonProductionAssessmentEngagementParticipationAuthorityEvidence,
    NonProductionAssessmentEngagementParticipationLifecycleState,
    NonProductionAssessmentEngagementParticipationLookupResult,
    NonProductionAssessmentEngagementParticipationLookupStatus,
)
from trusted_authorization.non_production_assessment_engagement_source import (
    NonProductionAssessmentEngagementAuthorityEvidence,
    NonProductionAssessmentEngagementLifecycleState,
    NonProductionAssessmentEngagementLookupResult,
    NonProductionAssessmentEngagementLookupStatus,
)


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionAttemptContext:
    """Bounded evaluation context; constructing it does not create authority."""

    attempt_reference: str
    principal_id: str
    candidate_engagement_reference: str
    protected_operation: NonProductionProtectedApplicationOperation


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionAttemptBinding:
    """Derived non-production Binding(A,E) for one bounded attempt."""

    attempt_reference: str
    principal_id: str
    candidate_engagement_reference: str
    engagement_reference: str
    protected_operation: NonProductionProtectedApplicationOperation
    principal_authority_reference: str
    engagement_authority_reference: str
    engagement_establishment_provenance_reference: str
    participation_authority_reference: str
    participation_provenance_reference: str


class NonProductionAssessmentSubmissionAttemptBindingStatus(Enum):
    READY = "READY"
    MALFORMED = "MALFORMED"
    ENGAGEMENT_NOT_READY = "ENGAGEMENT_NOT_READY"
    PARTICIPATION_NOT_READY = "PARTICIPATION_NOT_READY"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    MISMATCH = "MISMATCH"
    REPLAYED = "REPLAYED"
    REBINDING = "REBINDING"


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionAttemptBindingResult:
    status: NonProductionAssessmentSubmissionAttemptBindingStatus
    binding: NonProductionAssessmentSubmissionAttemptBinding | None = None


class NonProductionAssessmentSubmissionAttemptBindingDeriver:
    """Derives attempt-scoped Binding from captured governed facts only.

    Replay/rebinding tracking is local to this non-production deriver instance.
    It is not persistent, distributed, runtime replay protection, or production
    authority.
    """

    __slots__ = ("_bound_attempts",)

    def __init__(self) -> None:
        self._bound_attempts: dict[str, tuple[object, ...]] = {}

    def derive_assessment_submission_attempt_binding(
        self,
        *,
        attempt_context: object,
        principal_mapping_result: object,
        engagement_result: object,
        participation_result: object,
    ) -> NonProductionAssessmentSubmissionAttemptBindingResult:
        attempt = _attempt_snapshot(attempt_context)
        principal = _principal_snapshot(principal_mapping_result)
        engagement_status, engagement = _engagement_snapshot(engagement_result)
        participation_status, participation = _participation_snapshot(
            participation_result
        )

        if (
            attempt is None
            or principal is None
            or engagement_status is _CapturedStatus.MALFORMED
            or participation_status is _CapturedStatus.MALFORMED
        ):
            return _result(
                NonProductionAssessmentSubmissionAttemptBindingStatus.MALFORMED
            )

        if (
            attempt.protected_operation
            is not NonProductionProtectedApplicationOperation.
            PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _result(
                NonProductionAssessmentSubmissionAttemptBindingStatus.
                UNSUPPORTED_OPERATION
            )

        if engagement_status is not _CapturedStatus.READY or engagement is None:
            return _result(
                NonProductionAssessmentSubmissionAttemptBindingStatus.
                ENGAGEMENT_NOT_READY
            )

        if participation_status is not _CapturedStatus.READY or participation is None:
            return _result(
                NonProductionAssessmentSubmissionAttemptBindingStatus.
                PARTICIPATION_NOT_READY
            )

        if (
            attempt.principal_id != principal.principal_id
            or attempt.principal_id != participation.principal_id
            or attempt.candidate_engagement_reference != engagement.engagement_reference
            or attempt.candidate_engagement_reference
            != participation.engagement_reference
            or engagement.engagement_reference != participation.engagement_reference
        ):
            return _result(
                NonProductionAssessmentSubmissionAttemptBindingStatus.MISMATCH
            )

        binding = NonProductionAssessmentSubmissionAttemptBinding(
            attempt_reference=attempt.attempt_reference,
            principal_id=attempt.principal_id,
            candidate_engagement_reference=attempt.candidate_engagement_reference,
            engagement_reference=engagement.engagement_reference,
            protected_operation=attempt.protected_operation,
            principal_authority_reference=principal.authority_reference,
            engagement_authority_reference=engagement.authority_reference,
            engagement_establishment_provenance_reference=(
                engagement.establishment_provenance_reference
            ),
            participation_authority_reference=participation.authority_reference,
            participation_provenance_reference=(
                participation.participation_provenance_reference
            ),
        )
        identity = _binding_identity(binding)
        stored_identity = self._bound_attempts.get(attempt.attempt_reference)

        if stored_identity is not None:
            if stored_identity == identity:
                return _result(
                    NonProductionAssessmentSubmissionAttemptBindingStatus.REPLAYED
                )
            return _result(
                NonProductionAssessmentSubmissionAttemptBindingStatus.REBINDING
            )

        self._bound_attempts[attempt.attempt_reference] = identity
        return NonProductionAssessmentSubmissionAttemptBindingResult(
            status=NonProductionAssessmentSubmissionAttemptBindingStatus.READY,
            binding=_binding_output(binding),
        )


class _CapturedStatus(Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


@dataclass(frozen=True, slots=True)
class _AttemptSnapshot:
    attempt_reference: str
    principal_id: str
    candidate_engagement_reference: str
    protected_operation: NonProductionProtectedApplicationOperation


@dataclass(frozen=True, slots=True)
class _PrincipalSnapshot:
    authority_reference: str
    principal_id: str


@dataclass(frozen=True, slots=True)
class _EngagementSnapshot:
    authority_reference: str
    engagement_reference: str
    establishment_provenance_reference: str


@dataclass(frozen=True, slots=True)
class _ParticipationSnapshot:
    authority_reference: str
    principal_id: str
    engagement_reference: str
    participation_provenance_reference: str


def _attempt_snapshot(record: object) -> _AttemptSnapshot | None:
    if type(record) is not NonProductionAssessmentSubmissionAttemptContext:
        return None
    try:
        attempt_reference = object.__getattribute__(record, "attempt_reference")
        principal_id = object.__getattribute__(record, "principal_id")
        candidate_engagement_reference = object.__getattribute__(
            record,
            "candidate_engagement_reference",
        )
        protected_operation = object.__getattribute__(record, "protected_operation")
    except Exception:
        return None
    if (
        not _has_value(attempt_reference)
        or not _has_value(principal_id)
        or not _has_value(candidate_engagement_reference)
        or type(protected_operation) is not NonProductionProtectedApplicationOperation
    ):
        return None
    return _AttemptSnapshot(
        attempt_reference=attempt_reference,
        principal_id=principal_id,
        candidate_engagement_reference=candidate_engagement_reference,
        protected_operation=protected_operation,
    )


def _principal_snapshot(record: object) -> _PrincipalSnapshot | None:
    if type(record) is not AuthorityLookupResult:
        return None
    try:
        status = object.__getattribute__(record, "status")
        records = object.__getattribute__(record, "records")
    except Exception:
        return None
    if status is not AuthorityLookupStatus.FOUND or type(records) is not tuple:
        return None
    if len(records) != 1:
        return None
    principal = records[0]
    if type(principal) is not PrincipalMapping:
        return None
    try:
        authority_reference = object.__getattribute__(principal, "authority_reference")
        state = object.__getattribute__(principal, "state")
        principal_id = object.__getattribute__(principal, "principal_id")
    except Exception:
        return None
    if (
        not _has_value(authority_reference)
        or state is not AuthorityRecordState.ACTIVE
        or not _has_value(principal_id)
    ):
        return None
    return _PrincipalSnapshot(
        authority_reference=authority_reference,
        principal_id=principal_id,
    )


def _engagement_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _EngagementSnapshot | None]:
    if type(result) is not NonProductionAssessmentEngagementLookupResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        records = object.__getattribute__(result, "records")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not NonProductionAssessmentEngagementLookupStatus:
        return (_CapturedStatus.MALFORMED, None)
    if type(records) is not tuple:
        return (_CapturedStatus.MALFORMED, None)
    if status is not NonProductionAssessmentEngagementLookupStatus.FOUND:
        return (_CapturedStatus.NOT_READY, None)
    if len(records) != 1:
        return (_CapturedStatus.MALFORMED, None)
    engagement = records[0]
    if type(engagement) is not NonProductionAssessmentEngagementAuthorityEvidence:
        return (_CapturedStatus.MALFORMED, None)
    try:
        authority_reference = object.__getattribute__(engagement, "authority_reference")
        state = object.__getattribute__(engagement, "state")
        engagement_reference = object.__getattribute__(
            engagement,
            "engagement_reference",
        )
        lifecycle_state = object.__getattribute__(engagement, "lifecycle_state")
        establishment_provenance_reference = object.__getattribute__(
            engagement,
            "establishment_provenance_reference",
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(authority_reference)
        or state is not AuthorityRecordState.ACTIVE
        or not _has_value(engagement_reference)
        or lifecycle_state is not NonProductionAssessmentEngagementLifecycleState.CURRENT
        or not _has_value(establishment_provenance_reference)
    ):
        return (_CapturedStatus.MALFORMED, None)
    return (
        _CapturedStatus.READY,
        _EngagementSnapshot(
            authority_reference=authority_reference,
            engagement_reference=engagement_reference,
            establishment_provenance_reference=establishment_provenance_reference,
        ),
    )


def _participation_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _ParticipationSnapshot | None]:
    if (
        type(result)
        is not NonProductionAssessmentEngagementParticipationLookupResult
    ):
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        records = object.__getattribute__(result, "records")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not NonProductionAssessmentEngagementParticipationLookupStatus:
        return (_CapturedStatus.MALFORMED, None)
    if type(records) is not tuple:
        return (_CapturedStatus.MALFORMED, None)
    if (
        status
        is not NonProductionAssessmentEngagementParticipationLookupStatus.FOUND
    ):
        return (_CapturedStatus.NOT_READY, None)
    if len(records) != 1:
        return (_CapturedStatus.MALFORMED, None)
    participation = records[0]
    if (
        type(participation)
        is not NonProductionAssessmentEngagementParticipationAuthorityEvidence
    ):
        return (_CapturedStatus.MALFORMED, None)
    try:
        authority_reference = object.__getattribute__(
            participation,
            "authority_reference",
        )
        state = object.__getattribute__(participation, "state")
        principal_id = object.__getattribute__(participation, "principal_id")
        engagement_reference = object.__getattribute__(
            participation,
            "engagement_reference",
        )
        lifecycle_state = object.__getattribute__(participation, "lifecycle_state")
        participation_provenance_reference = object.__getattribute__(
            participation,
            "participation_provenance_reference",
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(authority_reference)
        or state is not AuthorityRecordState.ACTIVE
        or not _has_value(principal_id)
        or not _has_value(engagement_reference)
        or lifecycle_state
        is not NonProductionAssessmentEngagementParticipationLifecycleState.CURRENT
        or not _has_value(participation_provenance_reference)
    ):
        return (_CapturedStatus.MALFORMED, None)
    return (
        _CapturedStatus.READY,
        _ParticipationSnapshot(
            authority_reference=authority_reference,
            principal_id=principal_id,
            engagement_reference=engagement_reference,
            participation_provenance_reference=participation_provenance_reference,
        ),
    )


def _binding_identity(
    binding: NonProductionAssessmentSubmissionAttemptBinding,
) -> tuple[object, ...]:
    return (
        binding.attempt_reference,
        binding.principal_id,
        binding.engagement_reference,
        binding.protected_operation,
    )


def _binding_output(
    binding: NonProductionAssessmentSubmissionAttemptBinding,
) -> NonProductionAssessmentSubmissionAttemptBinding:
    return NonProductionAssessmentSubmissionAttemptBinding(
        attempt_reference=binding.attempt_reference,
        principal_id=binding.principal_id,
        candidate_engagement_reference=binding.candidate_engagement_reference,
        engagement_reference=binding.engagement_reference,
        protected_operation=binding.protected_operation,
        principal_authority_reference=binding.principal_authority_reference,
        engagement_authority_reference=binding.engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            binding.engagement_establishment_provenance_reference
        ),
        participation_authority_reference=binding.participation_authority_reference,
        participation_provenance_reference=(
            binding.participation_provenance_reference
        ),
    )


def _result(
    status: NonProductionAssessmentSubmissionAttemptBindingStatus,
) -> NonProductionAssessmentSubmissionAttemptBindingResult:
    return NonProductionAssessmentSubmissionAttemptBindingResult(
        status=status,
        binding=None,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value
