from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from trusted_authorization.models import (
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    BusinessEntity,
)
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_engagement_context_legitimacy import (
    NonProductionAssessmentEngagementContextLegitimacy,
    NonProductionAssessmentEngagementContextLegitimacyResult,
    NonProductionAssessmentEngagementContextLegitimacyStatus,
)
from trusted_authorization.non_production_assessment_engagement_source import (
    NonProductionAssessmentEngagementAuthorityEvidence,
    NonProductionAssessmentEngagementLifecycleState,
    NonProductionAssessmentEngagementLookupResult,
    NonProductionAssessmentEngagementLookupStatus,
)


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionBusinessContext:
    """Derived non-production Assessment Submission business context."""

    attempt_reference: str
    principal_id: str
    engagement_reference: str
    business_entity_id: str
    protected_operation: NonProductionProtectedApplicationOperation
    principal_authority_reference: str
    engagement_authority_reference: str
    engagement_establishment_provenance_reference: str
    participation_authority_reference: str
    participation_provenance_reference: str
    business_entity_authority_reference: str


class NonProductionAssessmentSubmissionBusinessContextStatus(Enum):
    READY = "READY"
    MALFORMED = "MALFORMED"
    ENGAGEMENT_NOT_READY = "ENGAGEMENT_NOT_READY"
    BUSINESS_ENTITY_NOT_READY = "BUSINESS_ENTITY_NOT_READY"
    E_CONTEXT_NOT_READY = "E_CONTEXT_NOT_READY"
    MISMATCH = "MISMATCH"


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionBusinessContextResult:
    status: NonProductionAssessmentSubmissionBusinessContextStatus
    business_context: NonProductionAssessmentSubmissionBusinessContext | None = None


class _CapturedStatus(Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


@dataclass(frozen=True, slots=True)
class _EngagementSnapshot:
    authority_reference: str
    engagement_reference: str
    business_entity_id: str
    establishment_provenance_reference: str


@dataclass(frozen=True, slots=True)
class _BusinessEntitySnapshot:
    authority_reference: str
    business_entity_id: str


@dataclass(frozen=True, slots=True)
class _ContextLegitimacySnapshot:
    attempt_reference: str
    principal_id: str
    engagement_reference: str
    protected_operation: NonProductionProtectedApplicationOperation
    principal_authority_reference: str
    engagement_authority_reference: str
    engagement_establishment_provenance_reference: str
    participation_authority_reference: str
    participation_provenance_reference: str


def resolve_non_production_assessment_submission_business_context(
    *,
    engagement_result: object,
    business_entity_result: object,
    engagement_context_legitimacy_result: object,
) -> NonProductionAssessmentSubmissionBusinessContextResult:
    engagement_status, engagement = _engagement_snapshot(engagement_result)
    business_entity_status, business_entity = _business_entity_snapshot(
        business_entity_result
    )
    context_status, context_legitimacy = _context_legitimacy_snapshot(
        engagement_context_legitimacy_result
    )

    if (
        engagement_status is _CapturedStatus.MALFORMED
        or business_entity_status is _CapturedStatus.MALFORMED
        or context_status is _CapturedStatus.MALFORMED
    ):
        return _result(NonProductionAssessmentSubmissionBusinessContextStatus.MALFORMED)

    if engagement_status is not _CapturedStatus.READY or engagement is None:
        return _result(
            NonProductionAssessmentSubmissionBusinessContextStatus.
            ENGAGEMENT_NOT_READY
        )

    if (
        business_entity_status is not _CapturedStatus.READY
        or business_entity is None
    ):
        return _result(
            NonProductionAssessmentSubmissionBusinessContextStatus.
            BUSINESS_ENTITY_NOT_READY
        )

    if (
        context_status is not _CapturedStatus.READY
        or context_legitimacy is None
    ):
        return _result(
            NonProductionAssessmentSubmissionBusinessContextStatus.
            E_CONTEXT_NOT_READY
        )

    if (
        engagement.engagement_reference
        != context_legitimacy.engagement_reference
        or engagement.business_entity_id != business_entity.business_entity_id
        or context_legitimacy.protected_operation
        is not NonProductionProtectedApplicationOperation.
        PROTECTED_ASSESSMENT_SUBMISSION
        or context_legitimacy.engagement_authority_reference
        != engagement.authority_reference
        or context_legitimacy.engagement_establishment_provenance_reference
        != engagement.establishment_provenance_reference
    ):
        return _result(NonProductionAssessmentSubmissionBusinessContextStatus.MISMATCH)

    return NonProductionAssessmentSubmissionBusinessContextResult(
        status=NonProductionAssessmentSubmissionBusinessContextStatus.READY,
        business_context=NonProductionAssessmentSubmissionBusinessContext(
            attempt_reference=context_legitimacy.attempt_reference,
            principal_id=context_legitimacy.principal_id,
            engagement_reference=engagement.engagement_reference,
            business_entity_id=business_entity.business_entity_id,
            protected_operation=context_legitimacy.protected_operation,
            principal_authority_reference=(
                context_legitimacy.principal_authority_reference
            ),
            engagement_authority_reference=engagement.authority_reference,
            engagement_establishment_provenance_reference=(
                engagement.establishment_provenance_reference
            ),
            participation_authority_reference=(
                context_legitimacy.participation_authority_reference
            ),
            participation_provenance_reference=(
                context_legitimacy.participation_provenance_reference
            ),
            business_entity_authority_reference=business_entity.authority_reference,
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
            business_entity_id=business_entity_id,
            establishment_provenance_reference=establishment_provenance_reference,
        ),
    )


def _business_entity_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _BusinessEntitySnapshot | None]:
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

    business_entity = records[0]
    if type(business_entity) is not BusinessEntity:
        return (_CapturedStatus.MALFORMED, None)
    try:
        authority_reference = object.__getattribute__(
            business_entity,
            "authority_reference",
        )
        state = object.__getattribute__(business_entity, "state")
        business_entity_id = object.__getattribute__(
            business_entity,
            "business_entity_id",
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(authority_reference)
        or state is not AuthorityRecordState.ACTIVE
        or not _has_value(business_entity_id)
    ):
        return (_CapturedStatus.MALFORMED, None)
    return (
        _CapturedStatus.READY,
        _BusinessEntitySnapshot(
            authority_reference=authority_reference,
            business_entity_id=business_entity_id,
        ),
    )


def _context_legitimacy_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _ContextLegitimacySnapshot | None]:
    if type(result) is not NonProductionAssessmentEngagementContextLegitimacyResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        context_legitimacy = object.__getattribute__(result, "context_legitimacy")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not NonProductionAssessmentEngagementContextLegitimacyStatus:
        return (_CapturedStatus.MALFORMED, None)
    if status is not NonProductionAssessmentEngagementContextLegitimacyStatus.READY:
        if context_legitimacy is not None:
            return (_CapturedStatus.MALFORMED, None)
        return (_CapturedStatus.NOT_READY, None)
    if type(context_legitimacy) is not NonProductionAssessmentEngagementContextLegitimacy:
        return (_CapturedStatus.MALFORMED, None)
    try:
        attempt_reference = object.__getattribute__(
            context_legitimacy,
            "attempt_reference",
        )
        principal_id = object.__getattribute__(context_legitimacy, "principal_id")
        engagement_reference = object.__getattribute__(
            context_legitimacy,
            "engagement_reference",
        )
        protected_operation = object.__getattribute__(
            context_legitimacy,
            "protected_operation",
        )
        principal_authority_reference = object.__getattribute__(
            context_legitimacy,
            "principal_authority_reference",
        )
        engagement_authority_reference = object.__getattribute__(
            context_legitimacy,
            "engagement_authority_reference",
        )
        engagement_establishment_provenance_reference = object.__getattribute__(
            context_legitimacy,
            "engagement_establishment_provenance_reference",
        )
        participation_authority_reference = object.__getattribute__(
            context_legitimacy,
            "participation_authority_reference",
        )
        participation_provenance_reference = object.__getattribute__(
            context_legitimacy,
            "participation_provenance_reference",
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if (
        not _has_value(attempt_reference)
        or not _has_value(principal_id)
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
        _ContextLegitimacySnapshot(
            attempt_reference=attempt_reference,
            principal_id=principal_id,
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
    status: NonProductionAssessmentSubmissionBusinessContextStatus,
) -> NonProductionAssessmentSubmissionBusinessContextResult:
    return NonProductionAssessmentSubmissionBusinessContextResult(
        status=status,
        business_context=None,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value
