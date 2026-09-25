from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import (
    AuthorityRecordState as _AuthorityRecordState,
    GovernedVersionContext as _GovernedVersionContext,
)


_SEMANTIC_OWNER_REFERENCE = "nguyen-ai-platform-governance-control-plane"
_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-governed-version-context-authority"
)
_SOURCE_REFERENCE = (
    "non-production-assessment-submission-governed-version-context-"
    "controlled-evidence-source"
)
_GOVERNANCE_REFERENCES = (
    "trusted-authorization-implementation-readiness-governance-v1",
    "trusted-authorization-corrective-implementation-governance-v1",
    "trusted-authorization-production-authority-source-ownership-governance-v1",
    "deterministic-authorization-decision-semantics-v1",
    "resource-action-applicability-governance-v1",
)
_SCOPE_REFERENCE = "bounded-non-production-assessment-submission-submit"
_AUTHORIZATION_SEMANTICS_VERSION = (
    "deterministic-authorization-decision-semantics-v1"
)
_APPLICABILITY_GOVERNANCE_VERSION = (
    "resource-action-applicability-governance-v1"
)
_EVALUATION_CONTEXT = "local-deterministic-fixture"


@_dataclass(frozen=True, slots=True)
class _ControlledGovernedVersionContextRecord:
    semantic_owner_reference: str
    authority_reference: str
    source_reference: str
    governance_references: tuple[str, ...]
    scope_reference: str
    state: _AuthorityRecordState
    compatible: bool
    authorization_semantics_version: str
    applicability_governance_version: str
    evaluation_context: str


class _ControlledGovernedVersionContextAdapterStatus(_Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class _ControlledGovernedVersionContextAdapterResult:
    status: _ControlledGovernedVersionContextAdapterStatus
    records: tuple[_ControlledGovernedVersionContextRecord, ...]


class _ControlledGovernedVersionContextAdapter:
    __slots__ = ("_records",)

    def __init__(self) -> None:
        self._records = (
            _ControlledGovernedVersionContextRecord(
                semantic_owner_reference=_SEMANTIC_OWNER_REFERENCE,
                authority_reference=_AUTHORITY_REFERENCE,
                source_reference=_SOURCE_REFERENCE,
                governance_references=_GOVERNANCE_REFERENCES,
                scope_reference=_SCOPE_REFERENCE,
                state=_AuthorityRecordState.ACTIVE,
                compatible=True,
                authorization_semantics_version=(
                    _AUTHORIZATION_SEMANTICS_VERSION
                ),
                applicability_governance_version=(
                    _APPLICABILITY_GOVERNANCE_VERSION
                ),
                evaluation_context=_EVALUATION_CONTEXT,
            ),
        )

    def resolve_current_governed_version_context(
        self,
    ) -> _ControlledGovernedVersionContextAdapterResult:
        return _ControlledGovernedVersionContextAdapterResult(
            status=_ControlledGovernedVersionContextAdapterStatus.AVAILABLE,
            records=tuple(self._records),
        )


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionGovernedVersionContextFact:
    governed_version_context: _GovernedVersionContext


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionGovernedVersionContextEvidence:
    semantic_owner_reference: str
    governed_version_context_authority_reference: str
    governed_version_context_source_reference: str
    governance_references: tuple[str, ...]
    scope_reference: str
    source_state: _AuthorityRecordState
    source_record_count: int
    compatible: bool
    authorization_semantics_version: str
    applicability_governance_version: str
    evaluation_context: str


class NonProductionAssessmentSubmissionGovernedVersionContextStatus(_Enum):
    ESTABLISHED = "ESTABLISHED"
    MALFORMED = "MALFORMED"
    NOT_CURRENT = "NOT_CURRENT"
    UNAVAILABLE = "UNAVAILABLE"
    AMBIGUOUS = "AMBIGUOUS"
    CONFLICTING = "CONFLICTING"
    STALE = "STALE"
    UNSUPPORTED = "UNSUPPORTED"
    INCOMPATIBLE = "INCOMPATIBLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionGovernedVersionContextResult:
    status: NonProductionAssessmentSubmissionGovernedVersionContextStatus
    governed_version_context_fact: (
        NonProductionAssessmentSubmissionGovernedVersionContextFact | None
    )
    establishment_evidence: (
        NonProductionAssessmentSubmissionGovernedVersionContextEvidence | None
    )


class NonProductionAssessmentSubmissionGovernedVersionContextAuthority:
    __slots__ = ("_governed_version_context_adapter",)

    def __init__(self) -> None:
        self._governed_version_context_adapter = (
            _ControlledGovernedVersionContextAdapter()
        )

    def establish_assessment_submission_governed_version_context(
        self,
    ) -> NonProductionAssessmentSubmissionGovernedVersionContextResult:
        try:
            adapter_result = (
                self._governed_version_context_adapter
                .resolve_current_governed_version_context()
            )
        except Exception:
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.UNAVAILABLE
            )

        if type(adapter_result) is not _ControlledGovernedVersionContextAdapterResult:
            return self._malformed()

        try:
            adapter_status = adapter_result.status
            records = adapter_result.records
        except Exception:
            return self._malformed()

        if type(adapter_status) is not _ControlledGovernedVersionContextAdapterStatus:
            return self._malformed()
        if type(records) is not tuple:
            return self._malformed()

        if adapter_status is _ControlledGovernedVersionContextAdapterStatus.UNAVAILABLE:
            if records:
                return self._malformed()
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.UNAVAILABLE
            )
        if adapter_status is not _ControlledGovernedVersionContextAdapterStatus.AVAILABLE:
            return self._malformed()

        snapshots = []
        for record in records:
            snapshot = self._snapshot_record(record)
            if snapshot is None:
                return self._malformed()
            snapshots.append(snapshot)

        record_count = len(snapshots)
        if record_count == 0:
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.NOT_CURRENT
            )
        if record_count > 1:
            first_snapshot = snapshots[0]
            if all(snapshot == first_snapshot for snapshot in snapshots[1:]):
                return self._failure(
                    NonProductionAssessmentSubmissionGovernedVersionContextStatus.AMBIGUOUS
                )
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.CONFLICTING
            )

        snapshot = snapshots[0]
        state = snapshot[5]
        if state is _AuthorityRecordState.STALE:
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.STALE
            )
        if state is not _AuthorityRecordState.ACTIVE:
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.NOT_CURRENT
            )

        authorization_semantics_version = snapshot[7]
        applicability_governance_version = snapshot[8]
        evaluation_context = snapshot[9]
        if (
            authorization_semantics_version != _AUTHORIZATION_SEMANTICS_VERSION
            or applicability_governance_version
            != _APPLICABILITY_GOVERNANCE_VERSION
            or evaluation_context != _EVALUATION_CONTEXT
        ):
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.UNSUPPORTED
            )

        compatible = snapshot[6]
        if compatible is not True:
            return self._failure(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.INCOMPATIBLE
            )

        governed_version_context = _GovernedVersionContext(
            authorization_semantics_version=authorization_semantics_version,
            applicability_governance_version=applicability_governance_version,
            evaluation_context=evaluation_context,
        )
        fact = NonProductionAssessmentSubmissionGovernedVersionContextFact(
            governed_version_context=governed_version_context,
        )
        evidence = NonProductionAssessmentSubmissionGovernedVersionContextEvidence(
            semantic_owner_reference=snapshot[0],
            governed_version_context_authority_reference=snapshot[1],
            governed_version_context_source_reference=snapshot[2],
            governance_references=tuple(snapshot[3]),
            scope_reference=snapshot[4],
            source_state=state,
            source_record_count=record_count,
            compatible=compatible,
            authorization_semantics_version=authorization_semantics_version,
            applicability_governance_version=applicability_governance_version,
            evaluation_context=evaluation_context,
        )
        return NonProductionAssessmentSubmissionGovernedVersionContextResult(
            status=(
                NonProductionAssessmentSubmissionGovernedVersionContextStatus.ESTABLISHED
            ),
            governed_version_context_fact=fact,
            establishment_evidence=evidence,
        )

    @staticmethod
    def _snapshot_record(record: object) -> tuple[object, ...] | None:
        if type(record) is not _ControlledGovernedVersionContextRecord:
            return None
        try:
            snapshot = (
                record.semantic_owner_reference,
                record.authority_reference,
                record.source_reference,
                record.governance_references,
                record.scope_reference,
                record.state,
                record.compatible,
                record.authorization_semantics_version,
                record.applicability_governance_version,
                record.evaluation_context,
            )
        except Exception:
            return None

        string_indexes = (0, 1, 2, 4, 7, 8, 9)
        for index in string_indexes:
            value = snapshot[index]
            if not NonProductionAssessmentSubmissionGovernedVersionContextAuthority._canonical_string(
                value
            ):
                return None

        governance_references = snapshot[3]
        if type(governance_references) is not tuple:
            return None
        for reference in governance_references:
            if not NonProductionAssessmentSubmissionGovernedVersionContextAuthority._canonical_string(
                reference
            ):
                return None

        if type(snapshot[5]) is not _AuthorityRecordState:
            return None
        if type(snapshot[6]) is not bool:
            return None
        if snapshot[0] != _SEMANTIC_OWNER_REFERENCE:
            return None
        if snapshot[1] != _AUTHORITY_REFERENCE:
            return None
        if snapshot[2] != _SOURCE_REFERENCE:
            return None
        if governance_references != _GOVERNANCE_REFERENCES:
            return None
        if snapshot[4] != _SCOPE_REFERENCE:
            return None
        return snapshot

    @staticmethod
    def _canonical_string(value: object) -> bool:
        return (
            type(value) is str
            and bool(value)
            and bool(value.strip())
            and value == value.strip()
        )

    @staticmethod
    def _malformed(
    ) -> NonProductionAssessmentSubmissionGovernedVersionContextResult:
        return NonProductionAssessmentSubmissionGovernedVersionContextAuthority._failure(
            NonProductionAssessmentSubmissionGovernedVersionContextStatus.MALFORMED
        )

    @staticmethod
    def _failure(
        status: NonProductionAssessmentSubmissionGovernedVersionContextStatus,
    ) -> NonProductionAssessmentSubmissionGovernedVersionContextResult:
        return NonProductionAssessmentSubmissionGovernedVersionContextResult(
            status=status,
            governed_version_context_fact=None,
            establishment_evidence=None,
        )
