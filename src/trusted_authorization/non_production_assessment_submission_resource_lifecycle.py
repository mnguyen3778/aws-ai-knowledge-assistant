from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import (
    AuthorityRecordState as _AuthorityRecordState,
    GovernedResource as _GovernedResource,
    ResourceClass as _ResourceClass,
)


_AUTHORITY_REFERENCE = "assessment-submission-resource-lifecycle-authority"


@_dataclass(frozen=True, slots=True)
class NonProductionGovernedAssessmentSubmissionBusinessContext:
    """Representation of already-authoritative business context.

    Constructing this Python object does not establish real business-context
    authority. It represents, for this non-production proof only, a Business
    Entity binding context already established upstream.
    """

    business_entity_id: str


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceReferenceAllocation:
    """Representation of an already-authoritative resource reference allocation.

    Constructing this Python object does not establish resource authority.
    Allocation is distinct from governed resource existence.
    """

    resource_reference: str


class NonProductionAssessmentSubmissionLifecycleState(_Enum):
    PROVISIONAL = "PROVISIONAL"


class NonProductionAssessmentSubmissionResourceEstablishmentStatus(_Enum):
    READY = "READY"
    INVALID = "INVALID"


@_dataclass(frozen=True, slots=True)
class NonProductionProvisionalAssessmentSubmissionResourceFact:
    resource_reference: str
    business_entity_id: str
    resource_class: _ResourceClass
    lifecycle_state: NonProductionAssessmentSubmissionLifecycleState


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceEstablishmentResult:
    status: NonProductionAssessmentSubmissionResourceEstablishmentStatus
    provisional_resource: NonProductionProvisionalAssessmentSubmissionResourceFact | None
    resource_identity_record: _GovernedResource | None


def establish_non_production_provisional_assessment_submission_resource(
    *,
    business_context: object,
    resource_reference_allocation: object,
) -> NonProductionAssessmentSubmissionResourceEstablishmentResult:
    if (
        type(business_context)
        is not NonProductionGovernedAssessmentSubmissionBusinessContext
    ):
        return _invalid_establishment()

    if (
        type(resource_reference_allocation)
        is not NonProductionAssessmentSubmissionResourceReferenceAllocation
    ):
        return _invalid_establishment()

    business_entity_id = business_context.business_entity_id
    resource_reference = resource_reference_allocation.resource_reference

    if not _is_valid_identifier(business_entity_id):
        return _invalid_establishment()

    if not _is_valid_identifier(resource_reference):
        return _invalid_establishment()

    provisional_resource = NonProductionProvisionalAssessmentSubmissionResourceFact(
        resource_reference=resource_reference,
        business_entity_id=business_entity_id,
        resource_class=_ResourceClass.ASSESSMENT_SUBMISSION,
        lifecycle_state=(
            NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL
        ),
    )
    resource_identity_record = _GovernedResource(
        authority_reference=_AUTHORITY_REFERENCE,
        state=_AuthorityRecordState.ACTIVE,
        resource_id=resource_reference,
        resource_reference=resource_reference,
        resource_class=_ResourceClass.ASSESSMENT_SUBMISSION,
        business_entity_id=business_entity_id,
    )

    return NonProductionAssessmentSubmissionResourceEstablishmentResult(
        status=NonProductionAssessmentSubmissionResourceEstablishmentStatus.READY,
        provisional_resource=provisional_resource,
        resource_identity_record=resource_identity_record,
    )


def _is_valid_identifier(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and bool(value.strip())
    )


def _invalid_establishment() -> (
    NonProductionAssessmentSubmissionResourceEstablishmentResult
):
    return NonProductionAssessmentSubmissionResourceEstablishmentResult(
        status=NonProductionAssessmentSubmissionResourceEstablishmentStatus.INVALID,
        provisional_resource=None,
        resource_identity_record=None,
    )
