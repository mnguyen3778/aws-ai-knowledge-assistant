from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import (
    AuthorityLookupResult as _AuthorityLookupResult,
    AuthorityLookupStatus as _AuthorityLookupStatus,
    AuthorityRecordState as _AuthorityRecordState,
    GovernedResource as _GovernedResource,
    ResourceClass as _ResourceClass,
)
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation as _ProtectedOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (
    NonProductionAssessmentSubmissionBusinessContext as _BusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult as _BusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus as _BusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)
from trusted_authorization.non_production_assessment_submission_target_establishment import (
    NonProductionAssessmentSubmissionTargetEstablishmentAuthority as _TargetAuthority,
    NonProductionAssessmentSubmissionTargetEstablishmentEvidence as _TargetEvidence,
    NonProductionAssessmentSubmissionTargetEstablishmentResult as _TargetResult,
    NonProductionAssessmentSubmissionTargetEstablishmentStatus as _TargetStatus,
    NonProductionAssessmentSubmissionTargetLegitimacyFact as _TargetFact,
)
from trusted_authorization.resource_identity_source import (
    NonProductionResourceIdentityAuthoritySource as _ResourceIdentitySource,
)


_RESOURCE_IDENTITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-identity-authority"
)
_RESOURCE_IDENTITY_GOVERNANCE_REFERENCE = (
    "resource-identity-authority-source-governance-v1"
)
_RESOURCE_IDENTITY_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-resource-identity-establishment-"
    "provenance"
)
_TARGET_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-target-authority"
)
_TARGET_GOVERNANCE_REFERENCE = (
    "trusted-authorization-resource-reference-provenance-governance-v1"
)


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceIdentityFact:
    """Minimal bounded fact for one resolved Assessment Submission identity."""

    resource_reference: str
    resource_id: str
    business_entity_id: str
    resource_class: _ResourceClass
    resource_lifecycle_state: _LifecycleState


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceIdentityEvidence:
    """Complete bounded lineage for one resource-identity event."""

    attempt_reference: str
    resource_reference: str
    resource_id: str
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
    resource_lifecycle_state: _LifecycleState
    lifecycle_authority_reference: str
    lifecycle_provenance_reference: str
    target_authority_reference: str
    target_provenance_reference: str
    target_governance_reference: str
    resource_identity_state: _AuthorityRecordState
    resource_identity_authority_reference: str
    resource_identity_provenance_reference: str
    resource_identity_governance_reference: str


class NonProductionAssessmentSubmissionResourceIdentityStatus(_Enum):
    ESTABLISHED = "ESTABLISHED"
    REUSED = "REUSED"
    MALFORMED = "MALFORMED"
    BUSINESS_CONTEXT_NOT_READY = "BUSINESS_CONTEXT_NOT_READY"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    MISMATCH = "MISMATCH"
    COLLISION = "COLLISION"
    ALLOCATION_UNAVAILABLE = "ALLOCATION_UNAVAILABLE"
    RESOURCE_IDENTITY_NOT_FOUND = "RESOURCE_IDENTITY_NOT_FOUND"
    RESOURCE_IDENTITY_AMBIGUOUS = "RESOURCE_IDENTITY_AMBIGUOUS"
    RESOURCE_IDENTITY_CONFLICTING = "RESOURCE_IDENTITY_CONFLICTING"
    RESOURCE_IDENTITY_STALE = "RESOURCE_IDENTITY_STALE"
    RESOURCE_IDENTITY_UNAVAILABLE = "RESOURCE_IDENTITY_UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionResourceIdentityResult:
    status: NonProductionAssessmentSubmissionResourceIdentityStatus
    resource_identity_fact: (
        NonProductionAssessmentSubmissionResourceIdentityFact | None
    ) = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionResourceIdentityEvidence | None
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
class _TargetSnapshot:
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
    resource_lifecycle_state: _LifecycleState
    lifecycle_authority_reference: str
    lifecycle_provenance_reference: str
    target_authority_reference: str
    target_provenance_reference: str
    target_governance_reference: str


@_dataclass(frozen=True, slots=True)
class _ResolvedResourceSnapshot:
    authority_reference: str
    state: _AuthorityRecordState
    resource_id: str
    resource_reference: str
    resource_class: _ResourceClass
    business_entity_id: str


@_dataclass(frozen=True, slots=True)
class _IdentitySnapshot:
    attempt_reference: str
    resource_reference: str
    resource_id: str
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
    resource_lifecycle_state: _LifecycleState
    lifecycle_authority_reference: str
    lifecycle_provenance_reference: str
    target_authority_reference: str
    target_provenance_reference: str
    target_governance_reference: str
    resource_identity_state: _AuthorityRecordState
    resource_identity_authority_reference: str
    resource_identity_provenance_reference: str
    resource_identity_governance_reference: str
    retry_identity: tuple[object, ...]


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class NonProductionAssessmentSubmissionResourceIdentityAuthority:
    """Sequential in-memory Assessment Submission resource-identity proof."""

    __slots__ = (
        "_target_establishment_authority",
        "_identities_by_attempt",
        "_identities_by_resource_reference",
        "_identities_by_resource_id",
        "_next_resource_identity_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._target_establishment_authority = _TargetAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._identities_by_attempt: dict[str, _IdentitySnapshot] = {}
        self._identities_by_resource_reference: dict[str, _IdentitySnapshot] = {}
        self._identities_by_resource_id: dict[str, _IdentitySnapshot] = {}
        self._next_resource_identity_provenance_index = 1

    def establish_assessment_submission_resource_identity(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionResourceIdentityResult:
        captured_status, business_context = _business_context_snapshot(
            business_context_result
        )
        if captured_status is _CapturedStatus.MALFORMED:
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
            )
        if captured_status is _CapturedStatus.NOT_READY or business_context is None:
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.
                BUSINESS_CONTEXT_NOT_READY
            )
        if (
            business_context.protected_operation
            is not _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.
                UNSUPPORTED_OPERATION
            )

        target_authority = self._target_establishment_authority
        if type(target_authority) is not _TargetAuthority:
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
            )
        try:
            target_result = _TargetAuthority.establish_assessment_submission_target(
                target_authority,
                business_context_result=business_context_result,
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
            )

        target_status, target = _target_snapshot(target_result, business_context)
        if target_status is not None:
            return _failure(target_status)
        if target is None:
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
            )

        projected_resource = _governed_resource_projection(target)
        lookup_status, resolved_resource = _resolve_projected_resource(
            projected_resource,
            target.resource_reference,
        )
        if lookup_status is not None:
            return _failure(lookup_status)
        if resolved_resource is None:
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
            )
        if not _resource_converges(target, resolved_resource):
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.MISMATCH
            )

        retry_identity = _retry_identity(target, resolved_resource)
        stored_for_attempt = self._identities_by_attempt.get(target.attempt_reference)
        if stored_for_attempt is not None:
            if stored_for_attempt.retry_identity != retry_identity:
                return _failure(
                    NonProductionAssessmentSubmissionResourceIdentityStatus.MISMATCH
                )
            stored_for_resource = self._identities_by_resource_reference.get(
                target.resource_reference
            )
            stored_for_resource_id = self._identities_by_resource_id.get(
                resolved_resource.resource_id
            )
            if (
                stored_for_resource is not stored_for_attempt
                or stored_for_resource_id is not stored_for_attempt
            ):
                return _failure(
                    NonProductionAssessmentSubmissionResourceIdentityStatus.MISMATCH
                )
            return _success_output(
                NonProductionAssessmentSubmissionResourceIdentityStatus.REUSED,
                stored_for_attempt,
            )

        if (
            target.resource_reference in self._identities_by_resource_reference
            or resolved_resource.resource_id in self._identities_by_resource_id
        ):
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.COLLISION
            )

        provenance_index = self._next_resource_identity_provenance_index
        provenance_reference = (
            f"{_RESOURCE_IDENTITY_PROVENANCE_PREFIX}-{provenance_index}"
        )
        try:
            fact = _identity_fact(target, resolved_resource)
            evidence = _identity_evidence(
                target,
                resolved_resource,
                provenance_reference,
            )
            snapshot = _identity_snapshot(evidence, retry_identity)
            if not _outputs_converge(fact, evidence, snapshot):
                return _failure(
                    NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
                )
            output = _success_output(
                NonProductionAssessmentSubmissionResourceIdentityStatus.ESTABLISHED,
                snapshot,
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
            )

        self._identities_by_attempt[target.attempt_reference] = snapshot
        self._identities_by_resource_reference[target.resource_reference] = snapshot
        self._identities_by_resource_id[resolved_resource.resource_id] = snapshot
        self._next_resource_identity_provenance_index = provenance_index + 1
        return output


def _business_context_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _BusinessContextSnapshot | None]:
    if type(result) is not _BusinessContextResult:
        return (_CapturedStatus.MALFORMED, None)
    try:
        status = object.__getattribute__(result, "status")
        context = object.__getattribute__(result, "business_context")
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if type(status) is not _BusinessContextStatus:
        return (_CapturedStatus.MALFORMED, None)
    if status is not _BusinessContextStatus.READY:
        if context is not None:
            return (_CapturedStatus.MALFORMED, None)
        return (_CapturedStatus.NOT_READY, None)
    if type(context) is not _BusinessContext:
        return (_CapturedStatus.MALFORMED, None)
    try:
        snapshot = _BusinessContextSnapshot(
            attempt_reference=object.__getattribute__(context, "attempt_reference"),
            principal_id=object.__getattribute__(context, "principal_id"),
            engagement_reference=object.__getattribute__(
                context, "engagement_reference"
            ),
            business_entity_id=object.__getattribute__(context, "business_entity_id"),
            protected_operation=object.__getattribute__(context, "protected_operation"),
            principal_authority_reference=object.__getattribute__(
                context, "principal_authority_reference"
            ),
            engagement_authority_reference=object.__getattribute__(
                context, "engagement_authority_reference"
            ),
            engagement_establishment_provenance_reference=object.__getattribute__(
                context, "engagement_establishment_provenance_reference"
            ),
            participation_authority_reference=object.__getattribute__(
                context, "participation_authority_reference"
            ),
            participation_provenance_reference=object.__getattribute__(
                context, "participation_provenance_reference"
            ),
            business_entity_authority_reference=object.__getattribute__(
                context, "business_entity_authority_reference"
            ),
        )
    except Exception:
        return (_CapturedStatus.MALFORMED, None)
    if not _valid_business_context(snapshot):
        return (_CapturedStatus.MALFORMED, None)
    return (_CapturedStatus.READY, snapshot)


def _valid_business_context(snapshot: _BusinessContextSnapshot) -> bool:
    return (
        _has_value(snapshot.attempt_reference)
        and _has_value(snapshot.principal_id)
        and _has_value(snapshot.engagement_reference)
        and _has_value(snapshot.business_entity_id)
        and type(snapshot.protected_operation) is _ProtectedOperation
        and _has_value(snapshot.principal_authority_reference)
        and _has_value(snapshot.engagement_authority_reference)
        and _has_value(snapshot.engagement_establishment_provenance_reference)
        and _has_value(snapshot.participation_authority_reference)
        and _has_value(snapshot.participation_provenance_reference)
        and _has_value(snapshot.business_entity_authority_reference)
    )


def _target_snapshot(
    result: object,
    business_context: _BusinessContextSnapshot,
) -> tuple[
    NonProductionAssessmentSubmissionResourceIdentityStatus | None,
    _TargetSnapshot | None,
]:
    malformed = NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
    if type(result) is not _TargetResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        fact = object.__getattribute__(result, "target_fact")
        evidence = object.__getattribute__(result, "establishment_evidence")
    except Exception:
        return (malformed, None)
    if type(status) is not _TargetStatus:
        return (malformed, None)

    mapped_failure = _mapped_target_failure(status)
    if mapped_failure is not None:
        if fact is not None or evidence is not None:
            return (malformed, None)
        return (mapped_failure, None)
    if status not in (_TargetStatus.ESTABLISHED, _TargetStatus.REUSED):
        return (malformed, None)
    if type(fact) is not _TargetFact or type(evidence) is not _TargetEvidence:
        return (malformed, None)

    try:
        fact_values = (
            object.__getattribute__(fact, "attempt_reference"),
            object.__getattribute__(fact, "engagement_reference"),
            object.__getattribute__(fact, "business_entity_id"),
            object.__getattribute__(fact, "resource_reference"),
            object.__getattribute__(fact, "resource_class"),
            object.__getattribute__(fact, "protected_operation"),
        )
        target = _TargetSnapshot(
            attempt_reference=object.__getattribute__(evidence, "attempt_reference"),
            resource_reference=object.__getattribute__(
                evidence, "resource_reference"
            ),
            principal_id=object.__getattribute__(evidence, "principal_id"),
            engagement_reference=object.__getattribute__(
                evidence, "engagement_reference"
            ),
            business_entity_id=object.__getattribute__(
                evidence, "business_entity_id"
            ),
            protected_operation=object.__getattribute__(
                evidence, "protected_operation"
            ),
            principal_authority_reference=object.__getattribute__(
                evidence, "principal_authority_reference"
            ),
            engagement_authority_reference=object.__getattribute__(
                evidence, "engagement_authority_reference"
            ),
            engagement_establishment_provenance_reference=object.__getattribute__(
                evidence, "engagement_establishment_provenance_reference"
            ),
            participation_authority_reference=object.__getattribute__(
                evidence, "participation_authority_reference"
            ),
            participation_provenance_reference=object.__getattribute__(
                evidence, "participation_provenance_reference"
            ),
            business_entity_authority_reference=object.__getattribute__(
                evidence, "business_entity_authority_reference"
            ),
            allocation_authority_reference=object.__getattribute__(
                evidence, "allocation_authority_reference"
            ),
            allocation_provenance_reference=object.__getattribute__(
                evidence, "allocation_provenance_reference"
            ),
            binding_authority_reference=object.__getattribute__(
                evidence, "binding_authority_reference"
            ),
            binding_provenance_reference=object.__getattribute__(
                evidence, "binding_provenance_reference"
            ),
            resource_class=object.__getattribute__(evidence, "resource_class"),
            resource_lifecycle_state=object.__getattribute__(
                evidence, "resource_lifecycle_state"
            ),
            lifecycle_authority_reference=object.__getattribute__(
                evidence, "lifecycle_authority_reference"
            ),
            lifecycle_provenance_reference=object.__getattribute__(
                evidence, "lifecycle_provenance_reference"
            ),
            target_authority_reference=object.__getattribute__(
                evidence, "target_authority_reference"
            ),
            target_provenance_reference=object.__getattribute__(
                evidence, "target_provenance_reference"
            ),
            target_governance_reference=object.__getattribute__(
                evidence, "target_governance_reference"
            ),
        )
    except Exception:
        return (malformed, None)

    if (
        not _valid_target(target)
        or fact_values
        != (
            target.attempt_reference,
            target.engagement_reference,
            target.business_entity_id,
            target.resource_reference,
            target.resource_class,
            target.protected_operation,
        )
        or _business_context_identity_from_target(target)
        != _business_context_identity(business_context)
    ):
        return (malformed, None)
    return (None, target)


def _valid_target(target: _TargetSnapshot) -> bool:
    return (
        _has_value(target.attempt_reference)
        and _has_value(target.resource_reference)
        and _has_value(target.principal_id)
        and _has_value(target.engagement_reference)
        and _has_value(target.business_entity_id)
        and type(target.protected_operation) is _ProtectedOperation
        and target.protected_operation
        is _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        and _has_value(target.principal_authority_reference)
        and _has_value(target.engagement_authority_reference)
        and _has_value(target.engagement_establishment_provenance_reference)
        and _has_value(target.participation_authority_reference)
        and _has_value(target.participation_provenance_reference)
        and _has_value(target.business_entity_authority_reference)
        and _has_value(target.allocation_authority_reference)
        and _has_value(target.allocation_provenance_reference)
        and _has_value(target.binding_authority_reference)
        and _has_value(target.binding_provenance_reference)
        and type(target.resource_class) is _ResourceClass
        and target.resource_class is _ResourceClass.ASSESSMENT_SUBMISSION
        and type(target.resource_lifecycle_state) is _LifecycleState
        and target.resource_lifecycle_state is _LifecycleState.PROVISIONAL
        and _has_value(target.lifecycle_authority_reference)
        and _has_value(target.lifecycle_provenance_reference)
        and target.target_authority_reference == _TARGET_AUTHORITY_REFERENCE
        and _has_value(target.target_provenance_reference)
        and target.target_governance_reference == _TARGET_GOVERNANCE_REFERENCE
    )


def _mapped_target_failure(
    status: _TargetStatus,
) -> NonProductionAssessmentSubmissionResourceIdentityStatus | None:
    mapping = {
        _TargetStatus.MALFORMED: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
        ),
        _TargetStatus.BUSINESS_CONTEXT_NOT_READY: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            BUSINESS_CONTEXT_NOT_READY
        ),
        _TargetStatus.UNSUPPORTED_OPERATION: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            UNSUPPORTED_OPERATION
        ),
        _TargetStatus.MISMATCH: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.MISMATCH
        ),
        _TargetStatus.COLLISION: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.COLLISION
        ),
        _TargetStatus.ALLOCATION_UNAVAILABLE: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            ALLOCATION_UNAVAILABLE
        ),
    }
    return mapping.get(status)


def _governed_resource_projection(target: _TargetSnapshot) -> _GovernedResource:
    return _GovernedResource(
        authority_reference=_RESOURCE_IDENTITY_AUTHORITY_REFERENCE,
        state=_AuthorityRecordState.ACTIVE,
        resource_id=target.resource_reference,
        resource_reference=target.resource_reference,
        resource_class=_ResourceClass.ASSESSMENT_SUBMISSION,
        business_entity_id=target.business_entity_id,
    )


def _resolve_projected_resource(
    projected_resource: _GovernedResource,
    resource_reference: str,
) -> tuple[
    NonProductionAssessmentSubmissionResourceIdentityStatus | None,
    _ResolvedResourceSnapshot | None,
]:
    malformed = NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
    try:
        source = _ResourceIdentitySource((projected_resource,))
        if type(source) is not _ResourceIdentitySource:
            return (malformed, None)
        result = _ResourceIdentitySource.resolve_resource(source, resource_reference)
    except Exception:
        return (malformed, None)
    if type(result) is not _AuthorityLookupResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        records = object.__getattribute__(result, "records")
    except Exception:
        return (malformed, None)
    if type(status) is not _AuthorityLookupStatus or type(records) is not tuple:
        return (malformed, None)

    mapped_failure = _mapped_lookup_failure(status)
    if mapped_failure is not None:
        return (mapped_failure, None)
    if status is not _AuthorityLookupStatus.FOUND or len(records) != 1:
        return (malformed, None)
    record = records[0]
    if type(record) is not _GovernedResource:
        return (malformed, None)
    try:
        snapshot = _ResolvedResourceSnapshot(
            authority_reference=object.__getattribute__(
                record, "authority_reference"
            ),
            state=object.__getattribute__(record, "state"),
            resource_id=object.__getattribute__(record, "resource_id"),
            resource_reference=object.__getattribute__(
                record, "resource_reference"
            ),
            resource_class=object.__getattribute__(record, "resource_class"),
            business_entity_id=object.__getattribute__(
                record, "business_entity_id"
            ),
        )
    except Exception:
        return (malformed, None)
    if not _valid_resolved_resource(snapshot):
        return (malformed, None)
    return (None, snapshot)


def _mapped_lookup_failure(
    status: _AuthorityLookupStatus,
) -> NonProductionAssessmentSubmissionResourceIdentityStatus | None:
    mapping = {
        _AuthorityLookupStatus.NOT_FOUND: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_NOT_FOUND
        ),
        _AuthorityLookupStatus.AMBIGUOUS: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_AMBIGUOUS
        ),
        _AuthorityLookupStatus.CONFLICTING: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_CONFLICTING
        ),
        _AuthorityLookupStatus.STALE: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_STALE
        ),
        _AuthorityLookupStatus.UNAVAILABLE: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_UNAVAILABLE
        ),
        _AuthorityLookupStatus.MALFORMED: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
        ),
        _AuthorityLookupStatus.UNSUPPORTED: (
            NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
        ),
    }
    return mapping.get(status)


def _valid_resolved_resource(resource: _ResolvedResourceSnapshot) -> bool:
    return (
        resource.authority_reference == _RESOURCE_IDENTITY_AUTHORITY_REFERENCE
        and type(resource.state) is _AuthorityRecordState
        and resource.state is _AuthorityRecordState.ACTIVE
        and _has_value(resource.resource_id)
        and _has_value(resource.resource_reference)
        and type(resource.resource_class) is _ResourceClass
        and resource.resource_class is _ResourceClass.ASSESSMENT_SUBMISSION
        and _has_value(resource.business_entity_id)
    )


def _resource_converges(
    target: _TargetSnapshot,
    resource: _ResolvedResourceSnapshot,
) -> bool:
    return (
        resource.resource_reference == target.resource_reference
        and resource.resource_id == target.resource_reference
        and resource.business_entity_id == target.business_entity_id
        and resource.resource_class is target.resource_class
        and target.resource_lifecycle_state is _LifecycleState.PROVISIONAL
    )


def _identity_fact(
    target: _TargetSnapshot,
    resource: _ResolvedResourceSnapshot,
) -> NonProductionAssessmentSubmissionResourceIdentityFact:
    return NonProductionAssessmentSubmissionResourceIdentityFact(
        resource_reference=resource.resource_reference,
        resource_id=resource.resource_id,
        business_entity_id=resource.business_entity_id,
        resource_class=resource.resource_class,
        resource_lifecycle_state=target.resource_lifecycle_state,
    )


def _identity_evidence(
    target: _TargetSnapshot,
    resource: _ResolvedResourceSnapshot,
    provenance_reference: str,
) -> NonProductionAssessmentSubmissionResourceIdentityEvidence:
    return NonProductionAssessmentSubmissionResourceIdentityEvidence(
        attempt_reference=target.attempt_reference,
        resource_reference=resource.resource_reference,
        resource_id=resource.resource_id,
        principal_id=target.principal_id,
        engagement_reference=target.engagement_reference,
        business_entity_id=resource.business_entity_id,
        protected_operation=target.protected_operation,
        principal_authority_reference=target.principal_authority_reference,
        engagement_authority_reference=target.engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            target.engagement_establishment_provenance_reference
        ),
        participation_authority_reference=(
            target.participation_authority_reference
        ),
        participation_provenance_reference=(
            target.participation_provenance_reference
        ),
        business_entity_authority_reference=(
            target.business_entity_authority_reference
        ),
        allocation_authority_reference=target.allocation_authority_reference,
        allocation_provenance_reference=target.allocation_provenance_reference,
        binding_authority_reference=target.binding_authority_reference,
        binding_provenance_reference=target.binding_provenance_reference,
        resource_class=resource.resource_class,
        resource_lifecycle_state=target.resource_lifecycle_state,
        lifecycle_authority_reference=target.lifecycle_authority_reference,
        lifecycle_provenance_reference=target.lifecycle_provenance_reference,
        target_authority_reference=target.target_authority_reference,
        target_provenance_reference=target.target_provenance_reference,
        target_governance_reference=target.target_governance_reference,
        resource_identity_state=resource.state,
        resource_identity_authority_reference=(
            resource.authority_reference
        ),
        resource_identity_provenance_reference=provenance_reference,
        resource_identity_governance_reference=(
            _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE
        ),
    )


def _identity_snapshot(
    evidence: NonProductionAssessmentSubmissionResourceIdentityEvidence,
    retry_identity: tuple[object, ...],
) -> _IdentitySnapshot:
    return _IdentitySnapshot(
        **{
            name: object.__getattribute__(evidence, name)
            for name in (
                "attempt_reference",
                "resource_reference",
                "resource_id",
                "principal_id",
                "engagement_reference",
                "business_entity_id",
                "protected_operation",
                "principal_authority_reference",
                "engagement_authority_reference",
                "engagement_establishment_provenance_reference",
                "participation_authority_reference",
                "participation_provenance_reference",
                "business_entity_authority_reference",
                "allocation_authority_reference",
                "allocation_provenance_reference",
                "binding_authority_reference",
                "binding_provenance_reference",
                "resource_class",
                "resource_lifecycle_state",
                "lifecycle_authority_reference",
                "lifecycle_provenance_reference",
                "target_authority_reference",
                "target_provenance_reference",
                "target_governance_reference",
                "resource_identity_state",
                "resource_identity_authority_reference",
                "resource_identity_provenance_reference",
                "resource_identity_governance_reference",
            )
        },
        retry_identity=retry_identity,
    )


def _retry_identity(
    target: _TargetSnapshot,
    resource: _ResolvedResourceSnapshot,
) -> tuple[object, ...]:
    return (
        target.attempt_reference,
        target.resource_reference,
        resource.resource_id,
        target.principal_id,
        target.engagement_reference,
        target.business_entity_id,
        target.protected_operation,
        target.principal_authority_reference,
        target.engagement_authority_reference,
        target.engagement_establishment_provenance_reference,
        target.participation_authority_reference,
        target.participation_provenance_reference,
        target.business_entity_authority_reference,
        target.allocation_authority_reference,
        target.allocation_provenance_reference,
        target.binding_authority_reference,
        target.binding_provenance_reference,
        target.resource_class,
        target.resource_lifecycle_state,
        target.lifecycle_authority_reference,
        target.lifecycle_provenance_reference,
        target.target_authority_reference,
        target.target_provenance_reference,
        target.target_governance_reference,
        resource.state,
        resource.authority_reference,
        _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE,
    )


def _outputs_converge(
    fact: NonProductionAssessmentSubmissionResourceIdentityFact,
    evidence: NonProductionAssessmentSubmissionResourceIdentityEvidence,
    snapshot: _IdentitySnapshot,
) -> bool:
    return (
        type(fact) is NonProductionAssessmentSubmissionResourceIdentityFact
        and type(evidence)
        is NonProductionAssessmentSubmissionResourceIdentityEvidence
        and fact.resource_reference == snapshot.resource_reference
        and fact.resource_id == snapshot.resource_id
        and fact.business_entity_id == snapshot.business_entity_id
        and fact.resource_class is snapshot.resource_class
        and fact.resource_lifecycle_state is snapshot.resource_lifecycle_state
        and evidence.attempt_reference == snapshot.attempt_reference
        and evidence.resource_reference == snapshot.resource_reference
        and evidence.resource_id == snapshot.resource_id
        and evidence.resource_identity_authority_reference
        == _RESOURCE_IDENTITY_AUTHORITY_REFERENCE
        and evidence.resource_identity_governance_reference
        == _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE
        and _has_value(evidence.resource_identity_provenance_reference)
    )


def _success_output(
    status: NonProductionAssessmentSubmissionResourceIdentityStatus,
    snapshot: _IdentitySnapshot,
) -> NonProductionAssessmentSubmissionResourceIdentityResult:
    fact = NonProductionAssessmentSubmissionResourceIdentityFact(
        resource_reference=snapshot.resource_reference,
        resource_id=snapshot.resource_id,
        business_entity_id=snapshot.business_entity_id,
        resource_class=snapshot.resource_class,
        resource_lifecycle_state=snapshot.resource_lifecycle_state,
    )
    evidence = NonProductionAssessmentSubmissionResourceIdentityEvidence(
        attempt_reference=snapshot.attempt_reference,
        resource_reference=snapshot.resource_reference,
        resource_id=snapshot.resource_id,
        principal_id=snapshot.principal_id,
        engagement_reference=snapshot.engagement_reference,
        business_entity_id=snapshot.business_entity_id,
        protected_operation=snapshot.protected_operation,
        principal_authority_reference=snapshot.principal_authority_reference,
        engagement_authority_reference=snapshot.engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            snapshot.engagement_establishment_provenance_reference
        ),
        participation_authority_reference=(
            snapshot.participation_authority_reference
        ),
        participation_provenance_reference=(
            snapshot.participation_provenance_reference
        ),
        business_entity_authority_reference=(
            snapshot.business_entity_authority_reference
        ),
        allocation_authority_reference=snapshot.allocation_authority_reference,
        allocation_provenance_reference=snapshot.allocation_provenance_reference,
        binding_authority_reference=snapshot.binding_authority_reference,
        binding_provenance_reference=snapshot.binding_provenance_reference,
        resource_class=snapshot.resource_class,
        resource_lifecycle_state=snapshot.resource_lifecycle_state,
        lifecycle_authority_reference=snapshot.lifecycle_authority_reference,
        lifecycle_provenance_reference=snapshot.lifecycle_provenance_reference,
        target_authority_reference=snapshot.target_authority_reference,
        target_provenance_reference=snapshot.target_provenance_reference,
        target_governance_reference=snapshot.target_governance_reference,
        resource_identity_state=snapshot.resource_identity_state,
        resource_identity_authority_reference=(
            snapshot.resource_identity_authority_reference
        ),
        resource_identity_provenance_reference=(
            snapshot.resource_identity_provenance_reference
        ),
        resource_identity_governance_reference=(
            snapshot.resource_identity_governance_reference
        ),
    )
    return NonProductionAssessmentSubmissionResourceIdentityResult(
        status=status,
        resource_identity_fact=fact,
        establishment_evidence=evidence,
    )


def _failure(
    status: NonProductionAssessmentSubmissionResourceIdentityStatus,
) -> NonProductionAssessmentSubmissionResourceIdentityResult:
    return NonProductionAssessmentSubmissionResourceIdentityResult(status=status)


def _business_context_identity(
    context: _BusinessContextSnapshot,
) -> tuple[object, ...]:
    return (
        context.attempt_reference,
        context.principal_id,
        context.engagement_reference,
        context.business_entity_id,
        context.protected_operation,
        context.principal_authority_reference,
        context.engagement_authority_reference,
        context.engagement_establishment_provenance_reference,
        context.participation_authority_reference,
        context.participation_provenance_reference,
        context.business_entity_authority_reference,
    )


def _business_context_identity_from_target(
    target: _TargetSnapshot,
) -> tuple[object, ...]:
    return (
        target.attempt_reference,
        target.principal_id,
        target.engagement_reference,
        target.business_entity_id,
        target.protected_operation,
        target.principal_authority_reference,
        target.engagement_authority_reference,
        target.engagement_establishment_provenance_reference,
        target.participation_authority_reference,
        target.participation_provenance_reference,
        target.business_entity_authority_reference,
    )


def _has_value(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and bool(value.strip())
    )
