from __future__ import annotations

from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import (
    AuthorityLookupResult as _AuthorityLookupResult,
    AuthorityLookupStatus as _AuthorityLookupStatus,
    AuthorityRecordState as _AuthorityRecordState,
    PrincipalMapping as _PrincipalMapping,
    RequestedAction as _RequestedAction,
    ResourceActionApplicability as _ResourceActionApplicability,
    ResourceClass as _ResourceClass,
    TrustedSubjectEvidence as _TrustedSubjectEvidence,
)
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation as _ProtectedOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (
    NonProductionAssessmentSubmissionBusinessContext as _BusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult as _BusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus as _BusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_entitlement_currentness_establishment import (
    NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority as _UpstreamAuthority,
    NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence as _UpstreamEvidence,
    NonProductionAssessmentSubmissionEntitlementCurrentnessFact as _UpstreamFact,
    NonProductionAssessmentSubmissionEntitlementCurrentnessResult as _UpstreamResult,
    NonProductionAssessmentSubmissionEntitlementCurrentnessStatus as _UpstreamStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (
    NonProductionAssessmentSubmissionLifecycleState as _LifecycleState,
)
from trusted_authorization.non_production_authenticated_subject_handoff import (
    NonProductionAuthenticatedSubjectHandoffResult as _HandoffResult,
    NonProductionAuthenticatedSubjectHandoffStatus as _HandoffStatus,
    NonProductionVerifiedAuthenticationFact as _VerifiedAuthenticationFact,
    resolve_non_production_authenticated_subject_handoff as _resolve_handoff,
)
from trusted_authorization.principal_mapping_source import (
    NonProductionPrincipalMappingAuthoritySource as _PrincipalMappingSource,
)


_BOUNDED_PROVIDER = "provider-alpha"
_BOUNDED_SUBJECT = "subject-alpha"
_BOUNDED_PRINCIPAL_ID = "principal-alpha"
_BOUNDED_BUSINESS_ENTITY_ID = "business-alpha"
_BOUNDED_RESOURCE_ID = "resource-alpha"
_PRINCIPAL_AUTHORITY_REFERENCE = "principal-authority"
_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-subject-currentness-authority"
)
_CURRENTNESS_PROVENANCE_PREFIX = (
    "non-production-assessment-submission-subject-currentness-"
    "establishment-provenance"
)
_AUTHENTICATION_GOVERNANCE_REFERENCE = (
    "trusted-authorization-authentication-trust-provenance-governance-v1"
)
_PRINCIPAL_MAPPING_GOVERNANCE_REFERENCE = (
    "principal-mapping-authority-source-governance-v1"
)
_TARGET_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-target-authority"
)
_TARGET_GOVERNANCE_REFERENCE = (
    "trusted-authorization-resource-reference-provenance-governance-v1"
)
_RESOURCE_IDENTITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-identity-authority"
)
_RESOURCE_IDENTITY_GOVERNANCE_REFERENCE = (
    "resource-identity-authority-source-governance-v1"
)
_APPLICABILITY_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-resource-action-applicability-authority"
)
_APPLICABILITY_GOVERNANCE_REFERENCE = (
    "resource-action-applicability-governance-v1"
)
_BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE = (
    "non-production-business-entity-authority"
)
_BUSINESS_ENTITY_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-business-entity-currentness-authority"
)
_BUSINESS_ENTITY_GOVERNANCE_REFERENCE = (
    "business-entity-authority-source-governance-v1"
)
_MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE = "non-production-membership-authority"
_MEMBERSHIP_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-membership-currentness-authority"
)
_MEMBERSHIP_GOVERNANCE_REFERENCE = "membership-authority-source-governance-v1"
_ENTITLEMENT_SOURCE_AUTHORITY_REFERENCE = "non-production-entitlement-authority"
_ENTITLEMENT_CURRENTNESS_AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-entitlement-currentness-authority"
)
_ENTITLEMENT_GOVERNANCE_REFERENCE = "entitlement-authority-source-governance-v1"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionSubjectCurrentnessFact:
    provider: str
    subject: str
    principal_id: str
    principal_mapping_state: _AuthorityRecordState


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionSubjectCurrentnessEvidence:
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
    requested_action: _RequestedAction
    applicability: _ResourceActionApplicability
    applicability_authority_reference: str
    applicability_provenance_reference: str
    applicability_governance_reference: str
    business_entity_state: _AuthorityRecordState
    business_entity_currentness_authority_reference: str
    business_entity_currentness_provenance_reference: str
    business_entity_governance_reference: str
    membership_state: _AuthorityRecordState
    membership_authority_reference: str
    membership_currentness_authority_reference: str
    membership_currentness_provenance_reference: str
    membership_governance_reference: str
    entitlement_state: _AuthorityRecordState
    entitlement_authority_reference: str
    entitlement_currentness_authority_reference: str
    entitlement_currentness_provenance_reference: str
    entitlement_governance_reference: str
    provider: str
    subject: str
    principal_mapping_state: _AuthorityRecordState
    subject_currentness_authority_reference: str
    subject_currentness_provenance_reference: str
    authentication_governance_reference: str
    principal_mapping_governance_reference: str


class NonProductionAssessmentSubmissionSubjectCurrentnessStatus(_Enum):
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
    APPLICABILITY_NOT_APPLICABLE = "APPLICABILITY_NOT_APPLICABLE"
    APPLICABILITY_UNRESOLVED = "APPLICABILITY_UNRESOLVED"
    BUSINESS_ENTITY_NOT_FOUND = "BUSINESS_ENTITY_NOT_FOUND"
    BUSINESS_ENTITY_AMBIGUOUS = "BUSINESS_ENTITY_AMBIGUOUS"
    BUSINESS_ENTITY_CONFLICTING = "BUSINESS_ENTITY_CONFLICTING"
    BUSINESS_ENTITY_STALE = "BUSINESS_ENTITY_STALE"
    BUSINESS_ENTITY_UNAVAILABLE = "BUSINESS_ENTITY_UNAVAILABLE"
    MEMBERSHIP_NOT_FOUND = "MEMBERSHIP_NOT_FOUND"
    MEMBERSHIP_AMBIGUOUS = "MEMBERSHIP_AMBIGUOUS"
    MEMBERSHIP_CONFLICTING = "MEMBERSHIP_CONFLICTING"
    MEMBERSHIP_STALE = "MEMBERSHIP_STALE"
    MEMBERSHIP_UNAVAILABLE = "MEMBERSHIP_UNAVAILABLE"
    ENTITLEMENT_NOT_FOUND = "ENTITLEMENT_NOT_FOUND"
    ENTITLEMENT_AMBIGUOUS = "ENTITLEMENT_AMBIGUOUS"
    ENTITLEMENT_CONFLICTING = "ENTITLEMENT_CONFLICTING"
    ENTITLEMENT_STALE = "ENTITLEMENT_STALE"
    ENTITLEMENT_UNAVAILABLE = "ENTITLEMENT_UNAVAILABLE"
    AUTHENTICATION_NOT_CURRENT = "AUTHENTICATION_NOT_CURRENT"
    AUTHENTICATION_UNAVAILABLE = "AUTHENTICATION_UNAVAILABLE"
    PRINCIPAL_MAPPING_NOT_FOUND = "PRINCIPAL_MAPPING_NOT_FOUND"
    PRINCIPAL_MAPPING_AMBIGUOUS = "PRINCIPAL_MAPPING_AMBIGUOUS"
    PRINCIPAL_MAPPING_CONFLICTING = "PRINCIPAL_MAPPING_CONFLICTING"
    PRINCIPAL_MAPPING_STALE = "PRINCIPAL_MAPPING_STALE"
    PRINCIPAL_MAPPING_UNAVAILABLE = "PRINCIPAL_MAPPING_UNAVAILABLE"


@_dataclass(frozen=True, slots=True)
class NonProductionAssessmentSubmissionSubjectCurrentnessResult:
    status: NonProductionAssessmentSubmissionSubjectCurrentnessStatus
    subject_currentness_fact: (
        NonProductionAssessmentSubmissionSubjectCurrentnessFact | None
    ) = None
    establishment_evidence: (
        NonProductionAssessmentSubmissionSubjectCurrentnessEvidence | None
    ) = None


@_dataclass(frozen=True, slots=True)
class _Snapshot:
    values: tuple[object, ...]


@_dataclass(frozen=True, slots=True)
class _CurrentnessSnapshot:
    evidence_values: tuple[object, ...]
    retry_identity: tuple[object, ...]


class _CapturedStatus(_Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    MALFORMED = "MALFORMED"


class _ControlledAuthenticationAdapter:
    __slots__ = ()

    def current_verified_authentication(self) -> _VerifiedAuthenticationFact:
        return _VerifiedAuthenticationFact(
            provider=_BOUNDED_PROVIDER,
            subject=_BOUNDED_SUBJECT,
        )


class NonProductionAssessmentSubmissionSubjectCurrentnessAuthority:
    """Sequential bounded proof of current authenticated subject mapping."""

    __slots__ = (
        "_authentication_adapter",
        "_principal_mapping_source",
        "_entitlement_currentness_authority",
        "_subject_currentness_by_attempt",
        "_next_subject_currentness_provenance_index",
    )

    def __init__(
        self,
        *,
        candidate_resource_references: tuple[str, ...] | None = None,
    ) -> None:
        self._authentication_adapter = _ControlledAuthenticationAdapter()
        self._principal_mapping_source = _PrincipalMappingSource(
            (
                _PrincipalMapping(
                    authority_reference=_PRINCIPAL_AUTHORITY_REFERENCE,
                    state=_AuthorityRecordState.ACTIVE,
                    subject_provider=_BOUNDED_PROVIDER,
                    subject=_BOUNDED_SUBJECT,
                    principal_id=_BOUNDED_PRINCIPAL_ID,
                ),
            )
        )
        self._entitlement_currentness_authority = _UpstreamAuthority(
            candidate_resource_references=candidate_resource_references,
        )
        self._subject_currentness_by_attempt: dict[str, _CurrentnessSnapshot] = {}
        self._next_subject_currentness_provenance_index = 1

    def establish_assessment_submission_subject_currentness(
        self,
        *,
        business_context_result: object,
    ) -> NonProductionAssessmentSubmissionSubjectCurrentnessResult:
        output = NonProductionAssessmentSubmissionSubjectCurrentnessStatus
        context_status, context = _business_context_snapshot(business_context_result)
        if context_status is _CapturedStatus.MALFORMED:
            return _failure(output.MALFORMED)
        if context_status is _CapturedStatus.NOT_READY or context is None:
            return _failure(output.BUSINESS_CONTEXT_NOT_READY)
        if _value(context, _BUSINESS_CONTEXT_FIELDS, "protected_operation") is not (
            _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        ):
            return _failure(output.UNSUPPORTED_OPERATION)

        adapter = self._authentication_adapter
        if type(adapter) is not _ControlledAuthenticationAdapter:
            return _failure(output.MALFORMED)
        try:
            authentication = (
                _ControlledAuthenticationAdapter.current_verified_authentication(adapter)
            )
        except Exception:
            return _failure(output.AUTHENTICATION_UNAVAILABLE)
        if authentication is None:
            return _failure(output.AUTHENTICATION_NOT_CURRENT)
        authentication_status, authentication_snapshot = _authentication_snapshot(
            authentication
        )
        if authentication_status is not None:
            return _failure(authentication_status)
        if authentication_snapshot is None:
            return _failure(output.MALFORMED)
        provider = _value(authentication_snapshot, _AUTHENTICATION_FIELDS, "provider")
        subject = _value(authentication_snapshot, _AUTHENTICATION_FIELDS, "subject")
        if provider != _BOUNDED_PROVIDER or subject != _BOUNDED_SUBJECT:
            return _failure(output.MISMATCH)

        try:
            handoff_result = _resolve_handoff(
                verified_authentication_fact=authentication,
            )
        except Exception:
            return _failure(output.MALFORMED)
        handoff_status, handoff = _handoff_snapshot(handoff_result)
        if handoff_status is not None:
            return _failure(handoff_status)
        if handoff is None:
            return _failure(output.MALFORMED)
        if (
            _value(handoff, _HANDOFF_EVIDENCE_FIELDS, "provider") != provider
            or _value(handoff, _HANDOFF_EVIDENCE_FIELDS, "subject") != subject
        ):
            return _failure(output.MISMATCH)

        source = self._principal_mapping_source
        if type(source) is not _PrincipalMappingSource:
            return _failure(output.MALFORMED)
        try:
            mapping_result = _PrincipalMappingSource.resolve_principal_mapping(
                source,
                provider,
                subject,
            )
        except Exception:
            return _failure(output.PRINCIPAL_MAPPING_UNAVAILABLE)
        mapping_status, mapping = _principal_mapping_snapshot(
            mapping_result,
            provider,
            subject,
        )
        if mapping_status is not None:
            return _failure(mapping_status)
        if mapping is None:
            return _failure(output.MALFORMED)
        if not _mapping_matches_bounded_identity(mapping, provider, subject):
            return _failure(output.MISMATCH)

        upstream_authority = self._entitlement_currentness_authority
        if type(upstream_authority) is not _UpstreamAuthority:
            return _failure(output.MALFORMED)
        try:
            upstream_result = (
                _UpstreamAuthority.establish_assessment_submission_entitlement_currentness(
                    upstream_authority,
                    business_context_result=business_context_result,
                )
            )
        except Exception:
            return _failure(output.MALFORMED)
        upstream_status, upstream = _upstream_snapshot(upstream_result, context)
        if upstream_status is not None:
            return _failure(upstream_status)
        if upstream is None:
            return _failure(output.MALFORMED)
        if not _lineage_converges(upstream, mapping, provider, subject):
            return _failure(output.MISMATCH)

        mapping_state = _value(mapping, _PRINCIPAL_MAPPING_FIELDS, "state")
        retry_identity = upstream.values + (
            provider,
            subject,
            mapping_state,
            _CURRENTNESS_AUTHORITY_REFERENCE,
            _AUTHENTICATION_GOVERNANCE_REFERENCE,
            _PRINCIPAL_MAPPING_GOVERNANCE_REFERENCE,
        )
        attempt_reference = _value(
            upstream,
            _UPSTREAM_EVIDENCE_FIELDS,
            "attempt_reference",
        )
        stored = self._subject_currentness_by_attempt.get(attempt_reference)
        if stored is not None:
            if stored.retry_identity != retry_identity:
                return _failure(output.MISMATCH)
            return _success_output(output.REUSED, stored)

        provenance_index = self._next_subject_currentness_provenance_index
        provenance_reference = f"{_CURRENTNESS_PROVENANCE_PREFIX}-{provenance_index}"
        try:
            evidence_values = upstream.values + (
                provider,
                subject,
                mapping_state,
                _CURRENTNESS_AUTHORITY_REFERENCE,
                provenance_reference,
                _AUTHENTICATION_GOVERNANCE_REFERENCE,
                _PRINCIPAL_MAPPING_GOVERNANCE_REFERENCE,
            )
            snapshot = _CurrentnessSnapshot(evidence_values, retry_identity)
            result = _success_output(output.ESTABLISHED, snapshot)
            if not _output_converges(result):
                return _failure(output.MALFORMED)
        except Exception:
            return _failure(output.MALFORMED)

        self._subject_currentness_by_attempt[attempt_reference] = snapshot
        self._next_subject_currentness_provenance_index = provenance_index + 1
        return result


def _business_context_snapshot(
    result: object,
) -> tuple[_CapturedStatus, _Snapshot | None]:
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
        if context is None:
            return (_CapturedStatus.NOT_READY, None)
        return (_CapturedStatus.MALFORMED, None)
    if type(context) is not _BusinessContext:
        return (_CapturedStatus.MALFORMED, None)
    values = _capture(context, _BUSINESS_CONTEXT_FIELDS)
    if values is None:
        return (_CapturedStatus.MALFORMED, None)
    snapshot = _Snapshot(values)
    strings = values[:4] + values[5:]
    if not all(_has_value(value) for value in strings):
        return (_CapturedStatus.MALFORMED, None)
    if type(values[4]) is not _ProtectedOperation:
        return (_CapturedStatus.MALFORMED, None)
    return (_CapturedStatus.READY, snapshot)


def _authentication_snapshot(
    fact: object,
) -> tuple[
    NonProductionAssessmentSubmissionSubjectCurrentnessStatus | None,
    _Snapshot | None,
]:
    malformed = NonProductionAssessmentSubmissionSubjectCurrentnessStatus.MALFORMED
    if type(fact) is not _VerifiedAuthenticationFact:
        return (malformed, None)
    values = _capture(fact, _AUTHENTICATION_FIELDS)
    if values is None or not all(_has_value(value) for value in values):
        return (malformed, None)
    return (None, _Snapshot(values))


def _handoff_snapshot(
    result: object,
) -> tuple[
    NonProductionAssessmentSubmissionSubjectCurrentnessStatus | None,
    _Snapshot | None,
]:
    malformed = NonProductionAssessmentSubmissionSubjectCurrentnessStatus.MALFORMED
    if type(result) is not _HandoffResult:
        return (malformed, None)
    values = _capture(result, _HANDOFF_RESULT_FIELDS)
    if values is None:
        return (malformed, None)
    status, evidence = values
    if type(status) is not _HandoffStatus:
        return (malformed, None)
    if status is not _HandoffStatus.READY:
        return (malformed, None)
    if type(evidence) is not _TrustedSubjectEvidence:
        return (malformed, None)
    evidence_values = _capture(evidence, _HANDOFF_EVIDENCE_FIELDS)
    if evidence_values is None:
        return (malformed, None)
    provider, subject, verified = evidence_values
    if not _has_value(provider) or not _has_value(subject):
        return (malformed, None)
    if type(verified) is not bool or verified is not True:
        return (malformed, None)
    return (None, _Snapshot(evidence_values))


def _principal_mapping_snapshot(
    result: object,
    provider: object,
    subject: object,
) -> tuple[
    NonProductionAssessmentSubmissionSubjectCurrentnessStatus | None,
    _Snapshot | None,
]:
    output = NonProductionAssessmentSubmissionSubjectCurrentnessStatus
    if type(result) is not _AuthorityLookupResult:
        return (output.MALFORMED, None)
    values = _capture(result, _LOOKUP_RESULT_FIELDS)
    if values is None:
        return (output.MALFORMED, None)
    status, records = values
    if type(status) is not _AuthorityLookupStatus or type(records) is not tuple:
        return (output.MALFORMED, None)
    mapped = {
        _AuthorityLookupStatus.NOT_FOUND: output.PRINCIPAL_MAPPING_NOT_FOUND,
        _AuthorityLookupStatus.AMBIGUOUS: output.PRINCIPAL_MAPPING_AMBIGUOUS,
        _AuthorityLookupStatus.CONFLICTING: output.PRINCIPAL_MAPPING_CONFLICTING,
        _AuthorityLookupStatus.STALE: output.PRINCIPAL_MAPPING_STALE,
        _AuthorityLookupStatus.UNAVAILABLE: output.PRINCIPAL_MAPPING_UNAVAILABLE,
        _AuthorityLookupStatus.MALFORMED: output.MALFORMED,
        _AuthorityLookupStatus.UNSUPPORTED: output.MALFORMED,
    }
    if status in (_AuthorityLookupStatus.AMBIGUOUS, _AuthorityLookupStatus.CONFLICTING):
        if len(records) < 2:
            return (output.MALFORMED, None)
        snapshots = []
        for record in records:
            snapshot = _principal_mapping_record_snapshot(record)
            if snapshot is None:
                return (output.MALFORMED, None)
            snapshots.append(snapshot)
        identities = {snapshot.values for snapshot in snapshots}
        keys = {
            (
                _value(snapshot, _PRINCIPAL_MAPPING_FIELDS, "subject_provider"),
                _value(snapshot, _PRINCIPAL_MAPPING_FIELDS, "subject"),
            )
            for snapshot in snapshots
        }
        if keys != {(provider, subject)}:
            return (output.MALFORMED, None)
        if (status is _AuthorityLookupStatus.AMBIGUOUS) != (len(identities) == 1):
            return (output.MALFORMED, None)
        return (mapped[status], None)
    if status is not _AuthorityLookupStatus.FOUND:
        if records:
            return (output.MALFORMED, None)
        return (mapped.get(status, output.MALFORMED), None)
    if len(records) != 1:
        return (output.MALFORMED, None)
    snapshot = _principal_mapping_record_snapshot(records[0])
    if snapshot is None:
        return (output.MALFORMED, None)
    return (None, snapshot)


def _principal_mapping_record_snapshot(record: object) -> _Snapshot | None:
    if type(record) is not _PrincipalMapping:
        return None
    values = _capture(record, _PRINCIPAL_MAPPING_FIELDS)
    if values is None:
        return None
    authority_reference, state, provider, subject, principal_id = values
    if (
        not _has_value(authority_reference)
        or type(state) is not _AuthorityRecordState
        or not _has_value(provider)
        or not _has_value(subject)
        or not _has_value(principal_id)
    ):
        return None
    return _Snapshot(values)


def _mapping_matches_bounded_identity(
    mapping: _Snapshot,
    provider: object,
    subject: object,
) -> bool:
    return (
        _value(mapping, _PRINCIPAL_MAPPING_FIELDS, "authority_reference")
        == _PRINCIPAL_AUTHORITY_REFERENCE
        and _value(mapping, _PRINCIPAL_MAPPING_FIELDS, "state")
        is _AuthorityRecordState.ACTIVE
        and _value(mapping, _PRINCIPAL_MAPPING_FIELDS, "subject_provider")
        == provider
        and _value(mapping, _PRINCIPAL_MAPPING_FIELDS, "subject") == subject
        and _value(mapping, _PRINCIPAL_MAPPING_FIELDS, "principal_id")
        == _BOUNDED_PRINCIPAL_ID
    )


def _upstream_snapshot(
    result: object,
    context: _Snapshot,
) -> tuple[
    NonProductionAssessmentSubmissionSubjectCurrentnessStatus | None,
    _Snapshot | None,
]:
    output = NonProductionAssessmentSubmissionSubjectCurrentnessStatus
    if type(result) is not _UpstreamResult:
        return (output.MALFORMED, None)
    values = _capture(result, _UPSTREAM_RESULT_FIELDS)
    if values is None:
        return (output.MALFORMED, None)
    status, fact, evidence = values
    if type(status) is not _UpstreamStatus:
        return (output.MALFORMED, None)
    if status not in (_UpstreamStatus.ESTABLISHED, _UpstreamStatus.REUSED):
        if fact is not None or evidence is not None:
            return (output.MALFORMED, None)
        return (_mapped_upstream_failure(status) or output.MALFORMED, None)
    if type(fact) is not _UpstreamFact or type(evidence) is not _UpstreamEvidence:
        return (output.MALFORMED, None)
    fact_values = _capture(fact, _UPSTREAM_FACT_FIELDS)
    evidence_values = _capture(evidence, _UPSTREAM_EVIDENCE_FIELDS)
    if fact_values is None or evidence_values is None:
        return (output.MALFORMED, None)
    snapshot = _Snapshot(evidence_values)
    if not _valid_upstream(snapshot):
        return (output.MALFORMED, None)
    if fact_values != (
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "principal_id"),
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "business_entity_id"),
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "resource_id"),
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "requested_action"),
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, "entitlement_state"),
    ):
        return (output.MISMATCH, None)
    upstream_context = tuple(
        _value(snapshot, _UPSTREAM_EVIDENCE_FIELDS, name)
        for name in _BUSINESS_CONTEXT_FIELDS
    )
    if context.values != upstream_context:
        return (output.MISMATCH, None)
    return (None, snapshot)


def _valid_upstream(upstream: _Snapshot) -> bool:
    value = lambda name: _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, name)
    return (
        all(_has_value(value(name)) for name in _UPSTREAM_STRING_FIELDS)
        and value("resource_reference") == value("resource_id")
        and type(value("protected_operation")) is _ProtectedOperation
        and value("protected_operation")
        is _ProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION
        and type(value("resource_class")) is _ResourceClass
        and value("resource_class") is _ResourceClass.ASSESSMENT_SUBMISSION
        and type(value("resource_lifecycle_state")) is _LifecycleState
        and value("resource_lifecycle_state") is _LifecycleState.PROVISIONAL
        and type(value("resource_identity_state")) is _AuthorityRecordState
        and value("resource_identity_state") is _AuthorityRecordState.ACTIVE
        and type(value("requested_action")) is _RequestedAction
        and type(value("applicability")) is _ResourceActionApplicability
        and value("applicability") is _ResourceActionApplicability.APPLICABLE
        and type(value("business_entity_state")) is _AuthorityRecordState
        and value("business_entity_state") is _AuthorityRecordState.ACTIVE
        and type(value("membership_state")) is _AuthorityRecordState
        and value("membership_state") is _AuthorityRecordState.ACTIVE
        and type(value("entitlement_state")) is _AuthorityRecordState
        and value("entitlement_state") is _AuthorityRecordState.ACTIVE
        and value("business_entity_authority_reference")
        == _BUSINESS_ENTITY_SOURCE_AUTHORITY_REFERENCE
        and value("target_authority_reference") == _TARGET_AUTHORITY_REFERENCE
        and value("target_governance_reference") == _TARGET_GOVERNANCE_REFERENCE
        and value("resource_identity_authority_reference")
        == _RESOURCE_IDENTITY_AUTHORITY_REFERENCE
        and value("resource_identity_governance_reference")
        == _RESOURCE_IDENTITY_GOVERNANCE_REFERENCE
        and value("applicability_authority_reference")
        == _APPLICABILITY_AUTHORITY_REFERENCE
        and value("applicability_governance_reference")
        == _APPLICABILITY_GOVERNANCE_REFERENCE
        and value("business_entity_currentness_authority_reference")
        == _BUSINESS_ENTITY_CURRENTNESS_AUTHORITY_REFERENCE
        and value("business_entity_governance_reference")
        == _BUSINESS_ENTITY_GOVERNANCE_REFERENCE
        and value("membership_authority_reference")
        == _MEMBERSHIP_SOURCE_AUTHORITY_REFERENCE
        and value("membership_currentness_authority_reference")
        == _MEMBERSHIP_CURRENTNESS_AUTHORITY_REFERENCE
        and value("membership_governance_reference")
        == _MEMBERSHIP_GOVERNANCE_REFERENCE
        and value("entitlement_authority_reference")
        == _ENTITLEMENT_SOURCE_AUTHORITY_REFERENCE
        and value("entitlement_currentness_authority_reference")
        == _ENTITLEMENT_CURRENTNESS_AUTHORITY_REFERENCE
        and value("entitlement_governance_reference")
        == _ENTITLEMENT_GOVERNANCE_REFERENCE
    )


def _mapped_upstream_failure(
    status: _UpstreamStatus,
) -> NonProductionAssessmentSubmissionSubjectCurrentnessStatus | None:
    output = NonProductionAssessmentSubmissionSubjectCurrentnessStatus
    return {
        _UpstreamStatus.MALFORMED: output.MALFORMED,
        _UpstreamStatus.BUSINESS_CONTEXT_NOT_READY: output.BUSINESS_CONTEXT_NOT_READY,
        _UpstreamStatus.UNSUPPORTED_OPERATION: output.UNSUPPORTED_OPERATION,
        _UpstreamStatus.MISMATCH: output.MISMATCH,
        _UpstreamStatus.COLLISION: output.COLLISION,
        _UpstreamStatus.ALLOCATION_UNAVAILABLE: output.ALLOCATION_UNAVAILABLE,
        _UpstreamStatus.RESOURCE_IDENTITY_NOT_FOUND: output.RESOURCE_IDENTITY_NOT_FOUND,
        _UpstreamStatus.RESOURCE_IDENTITY_AMBIGUOUS: output.RESOURCE_IDENTITY_AMBIGUOUS,
        _UpstreamStatus.RESOURCE_IDENTITY_CONFLICTING: output.RESOURCE_IDENTITY_CONFLICTING,
        _UpstreamStatus.RESOURCE_IDENTITY_STALE: output.RESOURCE_IDENTITY_STALE,
        _UpstreamStatus.RESOURCE_IDENTITY_UNAVAILABLE: output.RESOURCE_IDENTITY_UNAVAILABLE,
        _UpstreamStatus.APPLICABILITY_NOT_APPLICABLE: output.APPLICABILITY_NOT_APPLICABLE,
        _UpstreamStatus.APPLICABILITY_UNRESOLVED: output.APPLICABILITY_UNRESOLVED,
        _UpstreamStatus.BUSINESS_ENTITY_NOT_FOUND: output.BUSINESS_ENTITY_NOT_FOUND,
        _UpstreamStatus.BUSINESS_ENTITY_AMBIGUOUS: output.BUSINESS_ENTITY_AMBIGUOUS,
        _UpstreamStatus.BUSINESS_ENTITY_CONFLICTING: output.BUSINESS_ENTITY_CONFLICTING,
        _UpstreamStatus.BUSINESS_ENTITY_STALE: output.BUSINESS_ENTITY_STALE,
        _UpstreamStatus.BUSINESS_ENTITY_UNAVAILABLE: output.BUSINESS_ENTITY_UNAVAILABLE,
        _UpstreamStatus.MEMBERSHIP_NOT_FOUND: output.MEMBERSHIP_NOT_FOUND,
        _UpstreamStatus.MEMBERSHIP_AMBIGUOUS: output.MEMBERSHIP_AMBIGUOUS,
        _UpstreamStatus.MEMBERSHIP_CONFLICTING: output.MEMBERSHIP_CONFLICTING,
        _UpstreamStatus.MEMBERSHIP_STALE: output.MEMBERSHIP_STALE,
        _UpstreamStatus.MEMBERSHIP_UNAVAILABLE: output.MEMBERSHIP_UNAVAILABLE,
        _UpstreamStatus.ENTITLEMENT_NOT_FOUND: output.ENTITLEMENT_NOT_FOUND,
        _UpstreamStatus.ENTITLEMENT_AMBIGUOUS: output.ENTITLEMENT_AMBIGUOUS,
        _UpstreamStatus.ENTITLEMENT_CONFLICTING: output.ENTITLEMENT_CONFLICTING,
        _UpstreamStatus.ENTITLEMENT_STALE: output.ENTITLEMENT_STALE,
        _UpstreamStatus.ENTITLEMENT_UNAVAILABLE: output.ENTITLEMENT_UNAVAILABLE,
    }.get(status)


def _lineage_converges(
    upstream: _Snapshot,
    mapping: _Snapshot,
    provider: object,
    subject: object,
) -> bool:
    upstream_value = lambda name: _value(upstream, _UPSTREAM_EVIDENCE_FIELDS, name)
    mapping_value = lambda name: _value(mapping, _PRINCIPAL_MAPPING_FIELDS, name)
    return (
        provider == _BOUNDED_PROVIDER
        and subject == _BOUNDED_SUBJECT
        and mapping_value("subject_provider") == provider
        and mapping_value("subject") == subject
        and mapping_value("principal_id") == upstream_value("principal_id")
        and mapping_value("principal_id") == _BOUNDED_PRINCIPAL_ID
        and mapping_value("authority_reference")
        == upstream_value("principal_authority_reference")
        and mapping_value("authority_reference") == _PRINCIPAL_AUTHORITY_REFERENCE
        and mapping_value("state") is _AuthorityRecordState.ACTIVE
        and upstream_value("business_entity_id") == _BOUNDED_BUSINESS_ENTITY_ID
        and upstream_value("resource_id") == _BOUNDED_RESOURCE_ID
        and upstream_value("requested_action") is _RequestedAction.SUBMIT
    )


def _success_output(
    status: NonProductionAssessmentSubmissionSubjectCurrentnessStatus,
    snapshot: _CurrentnessSnapshot,
) -> NonProductionAssessmentSubmissionSubjectCurrentnessResult:
    values = dict(zip(_CURRENTNESS_EVIDENCE_FIELDS, snapshot.evidence_values, strict=True))
    fact = NonProductionAssessmentSubmissionSubjectCurrentnessFact(
        provider=values["provider"],
        subject=values["subject"],
        principal_id=values["principal_id"],
        principal_mapping_state=values["principal_mapping_state"],
    )
    evidence = NonProductionAssessmentSubmissionSubjectCurrentnessEvidence(**values)
    return NonProductionAssessmentSubmissionSubjectCurrentnessResult(
        status=status,
        subject_currentness_fact=fact,
        establishment_evidence=evidence,
    )


def _output_converges(
    result: NonProductionAssessmentSubmissionSubjectCurrentnessResult,
) -> bool:
    fact = result.subject_currentness_fact
    evidence = result.establishment_evidence
    return (
        type(fact) is NonProductionAssessmentSubmissionSubjectCurrentnessFact
        and type(evidence) is NonProductionAssessmentSubmissionSubjectCurrentnessEvidence
        and fact.provider == evidence.provider == _BOUNDED_PROVIDER
        and fact.subject == evidence.subject == _BOUNDED_SUBJECT
        and fact.principal_id == evidence.principal_id == _BOUNDED_PRINCIPAL_ID
        and fact.principal_mapping_state is evidence.principal_mapping_state
        and fact.principal_mapping_state is _AuthorityRecordState.ACTIVE
        and evidence.principal_authority_reference == _PRINCIPAL_AUTHORITY_REFERENCE
        and evidence.subject_currentness_authority_reference
        == _CURRENTNESS_AUTHORITY_REFERENCE
        and _has_value(evidence.subject_currentness_provenance_reference)
        and evidence.authentication_governance_reference
        == _AUTHENTICATION_GOVERNANCE_REFERENCE
        and evidence.principal_mapping_governance_reference
        == _PRINCIPAL_MAPPING_GOVERNANCE_REFERENCE
    )


def _failure(
    status: NonProductionAssessmentSubmissionSubjectCurrentnessStatus,
) -> NonProductionAssessmentSubmissionSubjectCurrentnessResult:
    return NonProductionAssessmentSubmissionSubjectCurrentnessResult(status=status)


def _capture(value: object, fields: tuple[str, ...]) -> tuple[object, ...] | None:
    try:
        return tuple(object.__getattribute__(value, name) for name in fields)
    except Exception:
        return None


def _value(snapshot: _Snapshot, fields: tuple[str, ...], name: str) -> object:
    return snapshot.values[fields.index(name)]


def _has_value(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and bool(value.strip())
    )


_BUSINESS_CONTEXT_FIELDS = (
    "attempt_reference",
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
)
_AUTHENTICATION_FIELDS = ("provider", "subject")
_HANDOFF_RESULT_FIELDS = ("status", "trusted_subject_evidence")
_HANDOFF_EVIDENCE_FIELDS = ("provider", "subject", "verified")
_LOOKUP_RESULT_FIELDS = ("status", "records")
_PRINCIPAL_MAPPING_FIELDS = (
    "authority_reference",
    "state",
    "subject_provider",
    "subject",
    "principal_id",
)
_UPSTREAM_RESULT_FIELDS = (
    "status",
    "entitlement_currentness_fact",
    "establishment_evidence",
)
_UPSTREAM_FACT_FIELDS = (
    "principal_id",
    "business_entity_id",
    "resource_id",
    "requested_action",
    "entitlement_state",
)
_UPSTREAM_EVIDENCE_FIELDS = (
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
    "requested_action",
    "applicability",
    "applicability_authority_reference",
    "applicability_provenance_reference",
    "applicability_governance_reference",
    "business_entity_state",
    "business_entity_currentness_authority_reference",
    "business_entity_currentness_provenance_reference",
    "business_entity_governance_reference",
    "membership_state",
    "membership_authority_reference",
    "membership_currentness_authority_reference",
    "membership_currentness_provenance_reference",
    "membership_governance_reference",
    "entitlement_state",
    "entitlement_authority_reference",
    "entitlement_currentness_authority_reference",
    "entitlement_currentness_provenance_reference",
    "entitlement_governance_reference",
)
_CURRENTNESS_EVIDENCE_FIELDS = _UPSTREAM_EVIDENCE_FIELDS + (
    "provider",
    "subject",
    "principal_mapping_state",
    "subject_currentness_authority_reference",
    "subject_currentness_provenance_reference",
    "authentication_governance_reference",
    "principal_mapping_governance_reference",
)
_UPSTREAM_STRING_FIELDS = tuple(
    name
    for name in _UPSTREAM_EVIDENCE_FIELDS
    if name
    not in {
        "protected_operation",
        "resource_class",
        "resource_lifecycle_state",
        "resource_identity_state",
        "requested_action",
        "applicability",
        "business_entity_state",
        "membership_state",
        "entitlement_state",
    }
)
