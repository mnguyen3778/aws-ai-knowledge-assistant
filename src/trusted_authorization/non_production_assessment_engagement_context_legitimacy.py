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
from trusted_authorization.non_production_assessment_submission_attempt_binding import (
    NonProductionAssessmentSubmissionAttemptBinding,
    NonProductionAssessmentSubmissionAttemptBindingResult,
    NonProductionAssessmentSubmissionAttemptBindingStatus,
)


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentEngagementContextLegitimacy:
    """Derived non-production engagement-context legitimacy for P/A/E."""

    attempt_reference: str
    principal_id: str
    engagement_reference: str
    protected_operation: NonProductionProtectedApplicationOperation
    principal_authority_reference: str
    engagement_authority_reference: str
    engagement_establishment_provenance_reference: str
    participation_authority_reference: str
    participation_provenance_reference: str


class NonProductionAssessmentEngagementContextLegitimacyStatus(Enum):
    READY = "READY"
    MALFORMED = "MALFORMED"
    PRINCIPAL_NOT_READY = "PRINCIPAL_NOT_READY"
    ENGAGEMENT_NOT_READY = "ENGAGEMENT_NOT_READY"
    PARTICIPATION_NOT_READY = "PARTICIPATION_NOT_READY"
    BINDING_NOT_READY = "BINDING_NOT_READY"
    MISMATCH = "MISMATCH"


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentEngagementContextLegitimacyResult:
    status: NonProductionAssessmentEngagementContextLegitimacyStatus
    context_legitimacy: (
        NonProductionAssessmentEngagementContextLegitimacy | None
    ) = None


class _CapturedStatus(Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


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


@dataclass(frozen=True, slots=True)
class _BindingSnapshot:
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


def resolve_non_production_assessment_engagement_context_legitimacy(
    *,
    principal_mapping_result: object,
    engagement_result: object,
    participation_result: object,
    attempt_binding_result: object,
) -> NonProductionAssessmentEngagementContextLegitimacyResult:
    principal_status, principal = _principal_snapshot(principal_mapping_result)
    engagement_status, engagement = _engagement_snapshot(engagement_result)
    participation_status, participation = _participation_snapshot(
        participation_result
    )
    binding_status, binding = _binding_snapshot(attempt_binding_result)

    if (
        principal_status is _CapturedStatus.MALFORMED
        or engagement_status is _CapturedStatus.MALFORMED
        or participation_status is _CapturedStatus.MALFORMED
        or binding_status is _CapturedStatus.MALFORMED
    ):
        return _result(
            NonProductionAssessmentEngagementContextLegitimacyStatus.MALFORMED
        )

    if principal_status is not _CapturedStatus.READY or principal is None:
        return _result(
            NonProductionAssessmentEngagementContextLegitimacyStatus.
            PRINCIPAL_NOT_READY
        )

    if engagement_status is not _CapturedStatus.READY or engagement is None:
        return _result(
            NonProductionAssessmentEngagementContextLegitimacyStatus.
            ENGAGEMENT_NOT_READY
        )

    if participation_status is not _CapturedStatus.READY or participation is None:
        return _result(
            NonProductionAssessmentEngagementContextLegitimacyStatus.
            PARTICIPATION_NOT_READY
        )

    if binding_status is not _CapturedStatus.READY or binding is None:
        return _result(
            NonProductionAssessmentEngagementContextLegitimacyStatus.
            BINDING_NOT_READY
        )

    if (
        principal.principal_id != participation.principal_id
        or principal.principal_id != binding.principal_id
        or engagement.engagement_reference != participation.engagement_reference
        or engagement.engagement_reference != binding.engagement_reference
        or engagement.engagement_reference
        != binding.candidate_engagement_reference
        or binding.protected_operation
        is not NonProductionProtectedApplicationOperation.
        PROTECTED_ASSESSMENT_SUBMISSION
        or principal.authority_reference != binding.principal_authority_reference
        or engagement.authority_reference != binding.engagement_authority_reference
        or engagement.establishment_provenance_reference
        != binding.engagement_establishment_provenance_reference
        or participation.authority_reference
        != binding.participation_authority_reference
        or participation.participation_provenance_reference
        != binding.participation_provenance_reference
    ):
        return _result(
            NonProductionAssessmentEngagementContextLegitimacyStatus.MISMATCH
        )

    return NonProductionAssessmentEngagementContextLegitimacyResult(
        status=NonProductionAssessmentEngagementContextLegitimacyStatus.READY,
        context_legitimacy=(
            NonProductionAssessmentEngagementContextLegitimacy(
                attempt_reference=binding.attempt_reference,
                principal_id=principal.principal_id,
                engagement_reference=engagement.engagement_reference,
                protected_operation=binding.protected_operation,
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
        ),
    )


def _principal_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _PrincipalSnapshot | None]:
    if type(result) is not AuthorityLookupResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        records = object.__getattribute__(result, "records")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not AuthorityLookupStatus:
        return (_CapturedStatus.MALFORMED, None)
    if type(records) is not tuple:
        return (_CapturedStatus.MALFORMED, None)
    if status is not AuthorityLookupStatus.FOUND:
        return (_CapturedStatus.NOT_READY, None)
    if len(records) != 1:
        return (_CapturedStatus.MALFORMED, None)
    principal = records[0]
    if type(principal) is not PrincipalMapping:
        return (_CapturedStatus.MALFORMED, None)
    try:
        authority_reference = object.__getattribute__(principal, "authority_reference")
        state = object.__getattribute__(principal, "state")
        principal_id = object.__getattribute__(principal, "principal_id")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(authority_reference)
        or state is not AuthorityRecordState.ACTIVE
        or not _has_value(principal_id)
    ):
        return (_CapturedStatus.MALFORMED, None)
    return (
        _CapturedStatus.READY,
        _PrincipalSnapshot(
            authority_reference=authority_reference,
            principal_id=principal_id,
        ),
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
        business_entity_id = object.__getattribute__(engagement, "business_entity_id")
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
        or not _has_value(business_entity_id)
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


def _binding_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _BindingSnapshot | None]:
    if type(result) is not NonProductionAssessmentSubmissionAttemptBindingResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        binding = object.__getattribute__(result, "binding")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not NonProductionAssessmentSubmissionAttemptBindingStatus:
        return (_CapturedStatus.MALFORMED, None)
    if status is not NonProductionAssessmentSubmissionAttemptBindingStatus.READY:
        if binding is not None:
            return (_CapturedStatus.MALFORMED, None)
        return (_CapturedStatus.NOT_READY, None)
    if type(binding) is not NonProductionAssessmentSubmissionAttemptBinding:
        return (_CapturedStatus.MALFORMED, None)
    try:
        attempt_reference = object.__getattribute__(binding, "attempt_reference")
        principal_id = object.__getattribute__(binding, "principal_id")
        candidate_engagement_reference = object.__getattribute__(
            binding,
            "candidate_engagement_reference",
        )
        engagement_reference = object.__getattribute__(
            binding,
            "engagement_reference",
        )
        protected_operation = object.__getattribute__(binding, "protected_operation")
        principal_authority_reference = object.__getattribute__(
            binding,
            "principal_authority_reference",
        )
        engagement_authority_reference = object.__getattribute__(
            binding,
            "engagement_authority_reference",
        )
        engagement_establishment_provenance_reference = object.__getattribute__(
            binding,
            "engagement_establishment_provenance_reference",
        )
        participation_authority_reference = object.__getattribute__(
            binding,
            "participation_authority_reference",
        )
        participation_provenance_reference = object.__getattribute__(
            binding,
            "participation_provenance_reference",
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(attempt_reference)
        or not _has_value(principal_id)
        or not _has_value(candidate_engagement_reference)
        or not _has_value(engagement_reference)
        or type(protected_operation) is not NonProductionProtectedApplicationOperation
        or not _has_value(principal_authority_reference)
        or not _has_value(engagement_authority_reference)
        or not _has_value(engagement_establishment_provenance_reference)
        or not _has_value(participation_authority_reference)
        or not _has_value(participation_provenance_reference)
    ):
        return (_CapturedStatus.MALFORMED, None)
    return (
        _CapturedStatus.READY,
        _BindingSnapshot(
            attempt_reference=attempt_reference,
            principal_id=principal_id,
            candidate_engagement_reference=candidate_engagement_reference,
            engagement_reference=engagement_reference,
            protected_operation=protected_operation,
            principal_authority_reference=principal_authority_reference,
            engagement_authority_reference=engagement_authority_reference,
            engagement_establishment_provenance_reference=(
                engagement_establishment_provenance_reference
            ),
            participation_authority_reference=participation_authority_reference,
            participation_provenance_reference=participation_provenance_reference,
        ),
    )


def _result(
    status: NonProductionAssessmentEngagementContextLegitimacyStatus,
) -> NonProductionAssessmentEngagementContextLegitimacyResult:
    return NonProductionAssessmentEngagementContextLegitimacyResult(
        status=status,
        context_legitimacy=None,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value
