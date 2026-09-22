from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import ResourceClass as _ResourceClass
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation as _ProtectedOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (
    NonProductionAssessmentSubmissionBusinessContext as _BusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult as _BusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus as _BusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_provisional_resource_establishment import (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority as _ProvisionalAuthority,
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence as _ProvisionalEvidence,
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult as _ProvisionalResult,
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus as _ProvisionalStatus,
    NonProductionAssessmentSubmissionProvisionalResourceFact as _ProvisionalResourceFact,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)


_TARGET_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-target-authority"
)
_TARGET_GOVERNANCE_REFERENCE = (
    "trusted-authorization-resource-reference-provenance-governance-v1"
)
_TARGET_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-target-establishment-provenance"
)


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionTargetLegitimacyFact:
    """Minimal fact identifying one legitimate Assessment Submission target."""

    attempt_reference: str
    engagement_reference: str
    business_entity_id: str
    resource_reference: str
    resource_class: _ResourceClass
    protected_operation: _ProtectedOperation


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionTargetEstablishmentEvidence:
    """Complete bounded lineage for one target-establishment event."""

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


class NonProductionAssessmentSubmissionTargetEstablishmentStatus(_Enum):
    ESTABLISHED = "ESTABLISHED"
    REUSED = "REUSED"
    MALFORMED = "MALFORMED"
    BUSINESS_CONTEXT_NOT_READY = "BUSINESS_CONTEXT_NOT_READY"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"
    MISMATCH = "MISMATCH"
    COLLISION = "COLLISION"
    ALLOCATION_UNAVAILABLE = "ALLOCATION_UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionTargetEstablishmentResult:
    status: NonProductionAssessmentSubmissionTargetEstablishmentStatus
    target_fact: NonProductionAssessmentSubmissionTargetLegitimacyFact | None = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionTargetEstablishmentEvidence | None
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
class _UpstreamSnapshot:
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
    retry_identity: tuple[object, ...]


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class NonProductionAssessmentSubmissionTargetEstablishmentAuthority:
    """Sequential in-memory non-production target-legitimacy proof."""

    __slots__ = (
        "_provisional_establishment_authority",
        "_targets_by_attempt",
        "_targets_by_resource_reference",
        "_next_target_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._provisional_establishment_authority = _ProvisionalAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._targets_by_attempt: dict[str, _TargetSnapshot] = {}
        self._targets_by_resource_reference: dict[str, _TargetSnapshot] = {}
        self._next_target_provenance_index = 1

    def establish_assessment_submission_target(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionTargetEstablishmentResult:
        captured_status, business_context = _business_context_snapshot(
            business_context_result
        )
        if captured_status is _CapturedStatus.MALFORMED:
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
            )
        if captured_status is _CapturedStatus.NOT_READY or business_context is None:
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.
                BUSINESS_CONTEXT_NOT_READY
            )
        if (
            business_context.protected_operation
            is not _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.
                UNSUPPORTED_OPERATION
            )

        provisional_authority = self._provisional_establishment_authority
        if type(provisional_authority) is not _ProvisionalAuthority:
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
            )
        try:
            provisional_result = (
                _ProvisionalAuthority.
                establish_assessment_submission_provisional_resource(
                    provisional_authority,
                    business_context_result=business_context_result,
                )
            )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
            )

        upstream_status, upstream = _upstream_snapshot(
            provisional_result,
            business_context,
        )
        if upstream_status is not None:
            return _failure(upstream_status)
        if upstream is None:
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
            )

        retry_identity = _retry_identity(upstream)
        stored_for_attempt = self._targets_by_attempt.get(upstream.attempt_reference)
        if stored_for_attempt is not None:
            if stored_for_attempt.retry_identity != retry_identity:
                return _failure(
                    NonProductionAssessmentSubmissionTargetEstablishmentStatus.MISMATCH
                )
            stored_for_resource = self._targets_by_resource_reference.get(
                upstream.resource_reference
            )
            if stored_for_resource is not stored_for_attempt:
                return _failure(
                    NonProductionAssessmentSubmissionTargetEstablishmentStatus.MISMATCH
                )
            return _success_output(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.REUSED,
                stored_for_attempt,
            )

        if upstream.resource_reference in self._targets_by_resource_reference:
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.COLLISION
            )

        provenance_index = self._next_target_provenance_index
        target_provenance_reference = (
            f"{_TARGET_PROVENANCE_PREFIX}-{provenance_index}"
        )
        try:
            target_fact = _target_fact(upstream)
            evidence = _target_evidence(upstream, target_provenance_reference)
            snapshot = _target_snapshot(evidence, retry_identity)
            if not _outputs_converge(target_fact, evidence, snapshot):
                return _failure(
                    NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
                )
        except Exception:
            return _failure(
                NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
            )

        self._targets_by_attempt[upstream.attempt_reference] = snapshot
        self._targets_by_resource_reference[upstream.resource_reference] = snapshot
        self._next_target_provenance_index = provenance_index + 1

        return _success_output(
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.ESTABLISHED,
            snapshot,
        )


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


def _upstream_snapshot(
    result: object,
    business_context: _BusinessContextSnapshot,
) -> tuple[
    NonProductionAssessmentSubmissionTargetEstablishmentStatus | None,
    _UpstreamSnapshot | None,
]:
    malformed = NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
    if type(result) is not _ProvisionalResult:
        return (malformed, None)
    try:
        status = object.__getattribute__(result, "status")
        resource = object.__getattribute__(result, "provisional_resource")
        evidence = object.__getattribute__(result, "establishment_evidence")
    except Exception:
        return (malformed, None)
    if type(status) is not _ProvisionalStatus:
        return (malformed, None)

    mapped_failure = _mapped_upstream_failure(status)
    if mapped_failure is not None:
        if resource is not None or evidence is not None:
            return (malformed, None)
        return (mapped_failure, None)
    if status not in (_ProvisionalStatus.ESTABLISHED, _ProvisionalStatus.REUSED):
        return (malformed, None)
    if type(resource) is not _ProvisionalResourceFact:
        return (malformed, None)
    if type(evidence) is not _ProvisionalEvidence:
        return (malformed, None)

    try:
        resource_reference = object.__getattribute__(resource, "resource_reference")
        resource_business_entity_id = object.__getattribute__(
            resource, "business_entity_id"
        )
        resource_class = object.__getattribute__(resource, "resource_class")
        resource_lifecycle_state = object.__getattribute__(
            resource, "lifecycle_state"
        )
        upstream = _UpstreamSnapshot(
            attempt_reference=object.__getattribute__(evidence, "attempt_reference"),
            resource_reference=object.__getattribute__(evidence, "resource_reference"),
            principal_id=object.__getattribute__(evidence, "principal_id"),
            engagement_reference=object.__getattribute__(
                evidence, "engagement_reference"
            ),
            business_entity_id=object.__getattribute__(evidence, "business_entity_id"),
            protected_operation=object.__getattribute__(evidence, "protected_operation"),
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
                evidence, "lifecycle_state"
            ),
            lifecycle_authority_reference=object.__getattribute__(
                evidence, "lifecycle_authority_reference"
            ),
            lifecycle_provenance_reference=object.__getattribute__(
                evidence, "lifecycle_provenance_reference"
            ),
        )
    except Exception:
        return (malformed, None)

    if (
        not _valid_upstream(upstream)
        or resource_reference != upstream.resource_reference
        or resource_business_entity_id != upstream.business_entity_id
        or resource_class is not upstream.resource_class
        or resource_lifecycle_state is not upstream.resource_lifecycle_state
        or _business_context_identity_from_upstream(upstream)
        != _business_context_identity(business_context)
    ):
        return (malformed, None)
    return (None, upstream)


def _mapped_upstream_failure(
    status: _ProvisionalStatus,
) -> NonProductionAssessmentSubmissionTargetEstablishmentStatus | None:
    mapping = {
        _ProvisionalStatus.MALFORMED: (
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
        ),
        _ProvisionalStatus.BUSINESS_CONTEXT_NOT_READY: (
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.
            BUSINESS_CONTEXT_NOT_READY
        ),
        _ProvisionalStatus.UNSUPPORTED_OPERATION: (
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.
            UNSUPPORTED_OPERATION
        ),
        _ProvisionalStatus.MISMATCH: (
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.MISMATCH
        ),
        _ProvisionalStatus.COLLISION: (
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.COLLISION
        ),
        _ProvisionalStatus.ALLOCATION_UNAVAILABLE: (
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.
            ALLOCATION_UNAVAILABLE
        ),
    }
    return mapping.get(status)


def _valid_upstream(upstream: _UpstreamSnapshot) -> bool:
    return (
        _has_value(upstream.attempt_reference)
        and _has_value(upstream.resource_reference)
        and _has_value(upstream.principal_id)
        and _has_value(upstream.engagement_reference)
        and _has_value(upstream.business_entity_id)
        and type(upstream.protected_operation) is _ProtectedOperation
        and upstream.protected_operation
        is _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        and _has_value(upstream.principal_authority_reference)
        and _has_value(upstream.engagement_authority_reference)
        and _has_value(upstream.engagement_establishment_provenance_reference)
        and _has_value(upstream.participation_authority_reference)
        and _has_value(upstream.participation_provenance_reference)
        and _has_value(upstream.business_entity_authority_reference)
        and _has_value(upstream.allocation_authority_reference)
        and _has_value(upstream.allocation_provenance_reference)
        and _has_value(upstream.binding_authority_reference)
        and _has_value(upstream.binding_provenance_reference)
        and type(upstream.resource_class) is _ResourceClass
        and upstream.resource_class is _ResourceClass.ASSESSMENT_SUBMISSION
        and type(upstream.resource_lifecycle_state) is _LifecycleState
        and upstream.resource_lifecycle_state is _LifecycleState.PROVISIONAL
        and _has_value(upstream.lifecycle_authority_reference)
        and _has_value(upstream.lifecycle_provenance_reference)
    )


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


def _business_context_identity_from_upstream(
    upstream: _UpstreamSnapshot,
) -> tuple[object, ...]:
    return (
        upstream.attempt_reference,
        upstream.principal_id,
        upstream.engagement_reference,
        upstream.business_entity_id,
        upstream.protected_operation,
        upstream.principal_authority_reference,
        upstream.engagement_authority_reference,
        upstream.engagement_establishment_provenance_reference,
        upstream.participation_authority_reference,
        upstream.participation_provenance_reference,
        upstream.business_entity_authority_reference,
    )


def _retry_identity(upstream: _UpstreamSnapshot) -> tuple[object, ...]:
    return (
        *_business_context_identity_from_upstream(upstream),
        upstream.resource_reference,
        upstream.allocation_authority_reference,
        upstream.allocation_provenance_reference,
        upstream.binding_authority_reference,
        upstream.binding_provenance_reference,
        upstream.resource_class,
        upstream.resource_lifecycle_state,
        upstream.lifecycle_authority_reference,
        upstream.lifecycle_provenance_reference,
        _TARGET_GOVERNANCE_REFERENCE,
    )


def _target_fact(
    upstream: _UpstreamSnapshot,
) -> NonProductionAssessmentSubmissionTargetLegitimacyFact:
    return NonProductionAssessmentSubmissionTargetLegitimacyFact(
        attempt_reference=upstream.attempt_reference,
        engagement_reference=upstream.engagement_reference,
        business_entity_id=upstream.business_entity_id,
        resource_reference=upstream.resource_reference,
        resource_class=upstream.resource_class,
        protected_operation=upstream.protected_operation,
    )


def _target_evidence(
    upstream: _UpstreamSnapshot,
    target_provenance_reference: str,
) -> NonProductionAssessmentSubmissionTargetEstablishmentEvidence:
    return NonProductionAssessmentSubmissionTargetEstablishmentEvidence(
        attempt_reference=upstream.attempt_reference,
        resource_reference=upstream.resource_reference,
        principal_id=upstream.principal_id,
        engagement_reference=upstream.engagement_reference,
        business_entity_id=upstream.business_entity_id,
        protected_operation=upstream.protected_operation,
        principal_authority_reference=upstream.principal_authority_reference,
        engagement_authority_reference=upstream.engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            upstream.engagement_establishment_provenance_reference
        ),
        participation_authority_reference=(
            upstream.participation_authority_reference
        ),
        participation_provenance_reference=(
            upstream.participation_provenance_reference
        ),
        business_entity_authority_reference=(
            upstream.business_entity_authority_reference
        ),
        allocation_authority_reference=upstream.allocation_authority_reference,
        allocation_provenance_reference=upstream.allocation_provenance_reference,
        binding_authority_reference=upstream.binding_authority_reference,
        binding_provenance_reference=upstream.binding_provenance_reference,
        resource_class=upstream.resource_class,
        resource_lifecycle_state=upstream.resource_lifecycle_state,
        lifecycle_authority_reference=upstream.lifecycle_authority_reference,
        lifecycle_provenance_reference=upstream.lifecycle_provenance_reference,
        target_authority_reference=_TARGET_AUTHORITY_REFERENCE,
        target_provenance_reference=target_provenance_reference,
        target_governance_reference=_TARGET_GOVERNANCE_REFERENCE,
    )


def _target_snapshot(
    evidence: NonProductionAssessmentSubmissionTargetEstablishmentEvidence,
    retry_identity: tuple[object, ...],
) -> _TargetSnapshot:
    return _TargetSnapshot(
        attempt_reference=evidence.attempt_reference,
        resource_reference=evidence.resource_reference,
        principal_id=evidence.principal_id,
        engagement_reference=evidence.engagement_reference,
        business_entity_id=evidence.business_entity_id,
        protected_operation=evidence.protected_operation,
        principal_authority_reference=evidence.principal_authority_reference,
        engagement_authority_reference=evidence.engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            evidence.engagement_establishment_provenance_reference
        ),
        participation_authority_reference=evidence.participation_authority_reference,
        participation_provenance_reference=(
            evidence.participation_provenance_reference
        ),
        business_entity_authority_reference=(
            evidence.business_entity_authority_reference
        ),
        allocation_authority_reference=evidence.allocation_authority_reference,
        allocation_provenance_reference=evidence.allocation_provenance_reference,
        binding_authority_reference=evidence.binding_authority_reference,
        binding_provenance_reference=evidence.binding_provenance_reference,
        resource_class=evidence.resource_class,
        resource_lifecycle_state=evidence.resource_lifecycle_state,
        lifecycle_authority_reference=evidence.lifecycle_authority_reference,
        lifecycle_provenance_reference=evidence.lifecycle_provenance_reference,
        target_authority_reference=evidence.target_authority_reference,
        target_provenance_reference=evidence.target_provenance_reference,
        target_governance_reference=evidence.target_governance_reference,
        retry_identity=retry_identity,
    )


def _outputs_converge(
    fact: NonProductionAssessmentSubmissionTargetLegitimacyFact,
    evidence: NonProductionAssessmentSubmissionTargetEstablishmentEvidence,
    snapshot: _TargetSnapshot,
) -> bool:
    return (
        fact.attempt_reference == evidence.attempt_reference == snapshot.attempt_reference
        and fact.engagement_reference
        == evidence.engagement_reference
        == snapshot.engagement_reference
        and fact.business_entity_id
        == evidence.business_entity_id
        == snapshot.business_entity_id
        and fact.resource_reference
        == evidence.resource_reference
        == snapshot.resource_reference
        and fact.resource_class is evidence.resource_class is snapshot.resource_class
        and fact.protected_operation
        is evidence.protected_operation
        is snapshot.protected_operation
        and evidence.target_authority_reference == _TARGET_AUTHORITY_REFERENCE
        and evidence.target_governance_reference == _TARGET_GOVERNANCE_REFERENCE
        and _has_value(evidence.target_provenance_reference)
    )


def _success_output(
    status: NonProductionAssessmentSubmissionTargetEstablishmentStatus,
    snapshot: _TargetSnapshot,
) -> NonProductionAssessmentSubmissionTargetEstablishmentResult:
    return NonProductionAssessmentSubmissionTargetEstablishmentResult(
        status=status,
        target_fact=NonProductionAssessmentSubmissionTargetLegitimacyFact(
            attempt_reference=snapshot.attempt_reference,
            engagement_reference=snapshot.engagement_reference,
            business_entity_id=snapshot.business_entity_id,
            resource_reference=snapshot.resource_reference,
            resource_class=snapshot.resource_class,
            protected_operation=snapshot.protected_operation,
        ),
        establishment_evidence=(
            NonProductionAssessmentSubmissionTargetEstablishmentEvidence(
                attempt_reference=snapshot.attempt_reference,
                resource_reference=snapshot.resource_reference,
                principal_id=snapshot.principal_id,
                engagement_reference=snapshot.engagement_reference,
                business_entity_id=snapshot.business_entity_id,
                protected_operation=snapshot.protected_operation,
                principal_authority_reference=(
                    snapshot.principal_authority_reference
                ),
                engagement_authority_reference=(
                    snapshot.engagement_authority_reference
                ),
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
                allocation_authority_reference=(
                    snapshot.allocation_authority_reference
                ),
                allocation_provenance_reference=(
                    snapshot.allocation_provenance_reference
                ),
                binding_authority_reference=snapshot.binding_authority_reference,
                binding_provenance_reference=(
                    snapshot.binding_provenance_reference
                ),
                resource_class=snapshot.resource_class,
                resource_lifecycle_state=snapshot.resource_lifecycle_state,
                lifecycle_authority_reference=(
                    snapshot.lifecycle_authority_reference
                ),
                lifecycle_provenance_reference=(
                    snapshot.lifecycle_provenance_reference
                ),
                target_authority_reference=snapshot.target_authority_reference,
                target_provenance_reference=snapshot.target_provenance_reference,
                target_governance_reference=snapshot.target_governance_reference,
            )
        ),
    )


def _failure(
    status: NonProductionAssessmentSubmissionTargetEstablishmentStatus,
) -> NonProductionAssessmentSubmissionTargetEstablishmentResult:
    return NonProductionAssessmentSubmissionTargetEstablishmentResult(
        status=status,
        target_fact=None,
        establishment_evidence=None,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value) and value.strip() == value
