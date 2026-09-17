from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from trusted_authorization.models import AuthorityRecordState


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentEngagementAuthorityEvidence:
    """Represented already-authoritative Assessment Engagement evidence."""

    authority_reference: str
    state: AuthorityRecordState
    engagement_reference: str
    business_entity_id: str
    lifecycle_state: "NonProductionAssessmentEngagementLifecycleState"
    establishment_provenance_reference: str


class NonProductionAssessmentEngagementLifecycleState(Enum):
    CANDIDATE = "CANDIDATE"
    CURRENT = "CURRENT"
    NON_CURRENT = "NON_CURRENT"


class NonProductionAssessmentEngagementLookupStatus(Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    NON_CURRENT = "NON_CURRENT"
    STALE = "STALE"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTING = "CONFLICTING"
    MALFORMED = "MALFORMED"


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentEngagementLookupResult:
    status: NonProductionAssessmentEngagementLookupStatus
    records: tuple[NonProductionAssessmentEngagementAuthorityEvidence, ...] = ()


class NonProductionAssessmentEngagementAuthoritySource:
    """Local read-only source for constructor-supplied engagement evidence."""

    __slots__ = ("_has_malformed_evidence", "_records")

    def __init__(
        self,
        assessment_engagements: Iterable[
            NonProductionAssessmentEngagementAuthorityEvidence
        ] = (),
    ):
        snapshots = []
        has_malformed_evidence = False
        try:
            iterator = iter(assessment_engagements)
            for record in iterator:
                snapshot = _evidence_snapshot(record)
                if snapshot is None:
                    has_malformed_evidence = True
                else:
                    snapshots.append(snapshot)
        except Exception:
            has_malformed_evidence = True

        self._records = tuple(snapshots)
        self._has_malformed_evidence = has_malformed_evidence

    def resolve_assessment_engagement(
        self,
        engagement_reference: str,
    ) -> NonProductionAssessmentEngagementLookupResult:
        if not _has_value(engagement_reference):
            return _result(NonProductionAssessmentEngagementLookupStatus.MALFORMED)

        if self._has_malformed_evidence:
            return _result(NonProductionAssessmentEngagementLookupStatus.MALFORMED)

        applicable = tuple(
            record
            for record in self._records
            if record.engagement_reference == engagement_reference
        )
        if not applicable:
            return _result(NonProductionAssessmentEngagementLookupStatus.NOT_FOUND)

        if len(applicable) > 1:
            identities = {_identity(record) for record in applicable}
            if len(identities) > 1:
                return _result(NonProductionAssessmentEngagementLookupStatus.CONFLICTING)
            return _result(NonProductionAssessmentEngagementLookupStatus.AMBIGUOUS)

        record = applicable[0]
        if record.state is not AuthorityRecordState.ACTIVE:
            return _result(NonProductionAssessmentEngagementLookupStatus.STALE)
        if record.lifecycle_state is not NonProductionAssessmentEngagementLifecycleState.CURRENT:
            return _result(NonProductionAssessmentEngagementLookupStatus.NON_CURRENT)

        return NonProductionAssessmentEngagementLookupResult(
            status=NonProductionAssessmentEngagementLookupStatus.FOUND,
            records=(_evidence_output(record),),
        )


def _identity(
    record: NonProductionAssessmentEngagementAuthorityEvidence,
) -> tuple[object, ...]:
    return (
        record.authority_reference,
        record.state,
        record.engagement_reference,
        record.business_entity_id,
        record.lifecycle_state,
        record.establishment_provenance_reference,
    )


def _evidence_output(
    record: NonProductionAssessmentEngagementAuthorityEvidence,
) -> NonProductionAssessmentEngagementAuthorityEvidence:
    return NonProductionAssessmentEngagementAuthorityEvidence(
        authority_reference=record.authority_reference,
        state=record.state,
        engagement_reference=record.engagement_reference,
        business_entity_id=record.business_entity_id,
        lifecycle_state=record.lifecycle_state,
        establishment_provenance_reference=record.establishment_provenance_reference,
    )


def _evidence_snapshot(record: object) -> NonProductionAssessmentEngagementAuthorityEvidence | None:
    if type(record) is not NonProductionAssessmentEngagementAuthorityEvidence:
        return None

    try:
        authority_reference = object.__getattribute__(record, "authority_reference")
        state = object.__getattribute__(record, "state")
        engagement_reference = object.__getattribute__(record, "engagement_reference")
        business_entity_id = object.__getattribute__(record, "business_entity_id")
        lifecycle_state = object.__getattribute__(record, "lifecycle_state")
        establishment_provenance_reference = object.__getattribute__(
            record,
            "establishment_provenance_reference",
        )
    except Exception:
        return None

    if (
        not _has_value(authority_reference)
        or type(state) is not AuthorityRecordState
        or not _has_value(engagement_reference)
        or not _has_value(business_entity_id)
        or type(lifecycle_state) is not NonProductionAssessmentEngagementLifecycleState
        or not _has_value(establishment_provenance_reference)
    ):
        return None

    return NonProductionAssessmentEngagementAuthorityEvidence(
        authority_reference=authority_reference,
        state=state,
        engagement_reference=engagement_reference,
        business_entity_id=business_entity_id,
        lifecycle_state=lifecycle_state,
        establishment_provenance_reference=establishment_provenance_reference,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value


def _result(
    status: NonProductionAssessmentEngagementLookupStatus,
) -> NonProductionAssessmentEngagementLookupResult:
    return NonProductionAssessmentEngagementLookupResult(status=status, records=())
