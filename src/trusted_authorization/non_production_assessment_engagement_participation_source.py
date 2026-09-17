from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from trusted_authorization.models import AuthorityRecordState


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentEngagementParticipationAuthorityEvidence:
    """Represented already-authoritative Participation evidence.

    This non-production source models a deterministic read-side authority-source
    contract. Constructing evidence for tests does not create Participation,
    select a production producer, select persistence, or authorize runtime use.
    """

    authority_reference: str
    state: AuthorityRecordState
    principal_id: str
    engagement_reference: str
    lifecycle_state: "NonProductionAssessmentEngagementParticipationLifecycleState"
    participation_provenance_reference: str


class NonProductionAssessmentEngagementParticipationLifecycleState(Enum):
    CURRENT = "CURRENT"
    NON_CURRENT = "NON_CURRENT"


class NonProductionAssessmentEngagementParticipationLookupStatus(Enum):
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    NON_CURRENT = "NON_CURRENT"
    STALE = "STALE"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTING = "CONFLICTING"
    MALFORMED = "MALFORMED"


@dataclass(frozen=True, slots=True)
class NonProductionAssessmentEngagementParticipationLookupResult:
    status: NonProductionAssessmentEngagementParticipationLookupStatus
    records: tuple[
        NonProductionAssessmentEngagementParticipationAuthorityEvidence,
        ...,
    ] = ()


class NonProductionAssessmentEngagementParticipationAuthoritySource:
    """Non-production read-side source for represented Participation evidence.

    It resolves a bounded constructor snapshot only. It does not create,
    approve, persist, revoke, or produce real Participation authority.
    """

    __slots__ = ("_has_malformed_evidence", "_records")

    def __init__(
        self,
        participations: Iterable[
            NonProductionAssessmentEngagementParticipationAuthorityEvidence
        ] = (),
    ):
        snapshots = []
        has_malformed_evidence = False
        try:
            iterator = iter(participations)
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

    def resolve_assessment_engagement_participation(
        self,
        principal_id: str,
        engagement_reference: str,
    ) -> NonProductionAssessmentEngagementParticipationLookupResult:
        if not _has_value(principal_id) or not _has_value(engagement_reference):
            return _result(
                NonProductionAssessmentEngagementParticipationLookupStatus.MALFORMED
            )

        if self._has_malformed_evidence:
            return _result(
                NonProductionAssessmentEngagementParticipationLookupStatus.MALFORMED
            )

        applicable = tuple(
            record
            for record in self._records
            if record.principal_id == principal_id
            and record.engagement_reference == engagement_reference
        )
        if not applicable:
            return _result(
                NonProductionAssessmentEngagementParticipationLookupStatus.NOT_FOUND
            )

        if len(applicable) > 1:
            identities = {_identity(record) for record in applicable}
            if len(identities) > 1:
                return _result(
                    NonProductionAssessmentEngagementParticipationLookupStatus.CONFLICTING
                )
            return _result(
                NonProductionAssessmentEngagementParticipationLookupStatus.AMBIGUOUS
            )

        record = applicable[0]
        if record.state is not AuthorityRecordState.ACTIVE:
            return _result(
                NonProductionAssessmentEngagementParticipationLookupStatus.STALE
            )
        if (
            record.lifecycle_state
            is not NonProductionAssessmentEngagementParticipationLifecycleState.CURRENT
        ):
            return _result(
                NonProductionAssessmentEngagementParticipationLookupStatus.NON_CURRENT
            )

        return NonProductionAssessmentEngagementParticipationLookupResult(
            status=NonProductionAssessmentEngagementParticipationLookupStatus.FOUND,
            records=(_evidence_output(record),),
        )


def _identity(
    record: NonProductionAssessmentEngagementParticipationAuthorityEvidence,
) -> tuple[object, ...]:
    return (
        record.authority_reference,
        record.state,
        record.principal_id,
        record.engagement_reference,
        record.lifecycle_state,
        record.participation_provenance_reference,
    )


def _evidence_output(
    record: NonProductionAssessmentEngagementParticipationAuthorityEvidence,
) -> NonProductionAssessmentEngagementParticipationAuthorityEvidence:
    return NonProductionAssessmentEngagementParticipationAuthorityEvidence(
        authority_reference=record.authority_reference,
        state=record.state,
        principal_id=record.principal_id,
        engagement_reference=record.engagement_reference,
        lifecycle_state=record.lifecycle_state,
        participation_provenance_reference=record.participation_provenance_reference,
    )


def _evidence_snapshot(
    record: object,
) -> NonProductionAssessmentEngagementParticipationAuthorityEvidence | None:
    if type(record) is not NonProductionAssessmentEngagementParticipationAuthorityEvidence:
        return None

    try:
        authority_reference = object.__getattribute__(record, "authority_reference")
        state = object.__getattribute__(record, "state")
        principal_id = object.__getattribute__(record, "principal_id")
        engagement_reference = object.__getattribute__(record, "engagement_reference")
        lifecycle_state = object.__getattribute__(record, "lifecycle_state")
        participation_provenance_reference = object.__getattribute__(
            record,
            "participation_provenance_reference",
        )
    except Exception:
        return None

    if (
        not _has_value(authority_reference)
        or type(state) is not AuthorityRecordState
        or not _has_value(principal_id)
        or not _has_value(engagement_reference)
        or type(lifecycle_state)
        is not NonProductionAssessmentEngagementParticipationLifecycleState
        or not _has_value(participation_provenance_reference)
    ):
        return None

    return NonProductionAssessmentEngagementParticipationAuthorityEvidence(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        engagement_reference=engagement_reference,
        lifecycle_state=lifecycle_state,
        participation_provenance_reference=participation_provenance_reference,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value


def _result(
    status: NonProductionAssessmentEngagementParticipationLookupStatus,
) -> NonProductionAssessmentEngagementParticipationLookupResult:
    return NonProductionAssessmentEngagementParticipationLookupResult(
        status=status,
        records=(),
    )
