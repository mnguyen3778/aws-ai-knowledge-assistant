from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionTargetFact:
    """Bounded representation of an already-legitimate target fact.

    Constructing this Python object does not prove real-world resource-target provenance.
    It represents, for this non-production proof only, an
    Assessment Submission target fact already established upstream by the
    Governed Assessment Submission Resource-Target Authority.
    """

    resource_reference: str


class NonProductionAssessmentSubmissionTargetHandoffStatus(_Enum):
    READY = "READY"
    INVALID = "INVALID"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionTargetHandoffResult:
    status: NonProductionAssessmentSubmissionTargetHandoffStatus
    resource_reference: str | None = None


def resolve_non_production_assessment_submission_target_handoff(
    *,
    assessment_submission_target_fact: object,
) -> NonProductionAssessmentSubmissionTargetHandoffResult:
    if (
        type(assessment_submission_target_fact)
        is not NonProductionAssessmentSubmissionTargetFact
    ):
        return _invalid_handoff()

    resource_reference = assessment_submission_target_fact.resource_reference
    if not _is_valid_resource_reference(resource_reference):
        return _invalid_handoff()

    return NonProductionAssessmentSubmissionTargetHandoffResult(
        status=NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        resource_reference=resource_reference,
    )


def _is_valid_resource_reference(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and bool(value.strip())
    )


def _invalid_handoff() -> NonProductionAssessmentSubmissionTargetHandoffResult:
    return NonProductionAssessmentSubmissionTargetHandoffResult(
        status=NonProductionAssessmentSubmissionTargetHandoffStatus.INVALID,
        resource_reference=None,
    )
