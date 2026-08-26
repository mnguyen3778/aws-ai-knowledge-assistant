from __future__ import annotations

import hashlib
import json
from typing import Protocol

from trusted_authorization.applicability import (
    APPLICABILITY_GOVERNANCE_VERSION,
    resolve_applicability,
)
from trusted_authorization.models import (
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationAuditEvidence,
    AuthorizationDecision,
    AuthorizationRequest,
    AuthorizationResult,
    BusinessEntity,
    Entitlement,
    GovernedResource,
    Membership,
    PrincipalMapping,
    ReasonCategory,
    RequestedAction,
    ResourceActionApplicability,
    ResourceClass,
    TrustedSubjectEvidence,
)


AUTHORIZATION_SEMANTICS_VERSION = (
    "deterministic-authorization-decision-semantics-v1"
)


class AuthorizationAuthoritySource(Protocol):
    def resolve_principal_mapping(
        self,
        subject_provider: str,
        subject: str,
    ) -> AuthorityLookupResult[PrincipalMapping]:
        ...

    def resolve_resource(
        self,
        resource_reference: str,
    ) -> AuthorityLookupResult[GovernedResource]:
        ...

    def resolve_business_entity(
        self,
        business_entity_id: str,
    ) -> AuthorityLookupResult[BusinessEntity]:
        ...

    def resolve_membership(
        self,
        principal_id: str,
        business_entity_id: str,
    ) -> AuthorityLookupResult[Membership]:
        ...

    def resolve_entitlement(
        self,
        principal_id: str,
        business_entity_id: str,
        resource_id: str,
        action: RequestedAction,
    ) -> AuthorityLookupResult[Entitlement]:
        ...


class TrustedAuthorizationEvaluator:
    def __init__(self, authority_source: AuthorizationAuthoritySource):
        self._authority_source = authority_source

    def evaluate(self, request: AuthorizationRequest) -> AuthorizationResult:
        if not isinstance(request, AuthorizationRequest):
            request = AuthorizationRequest(
                subject_evidence=None,
                resource_reference=None,
                requested_action=None,
                correlation_id="malformed-request",
                evaluation_context="trusted-authorization",
            )

        subject = request.subject_evidence
        if (
            not isinstance(subject, TrustedSubjectEvidence)
            or subject.verified is not True
            or not _has_value(subject.provider)
            or not _has_value(subject.subject)
        ):
            return self._deny(
                request=request,
                reason=ReasonCategory.AUTHENTICATION_INVALID,
                requested_action=None,
                authority_inputs=("authentication_evidence:invalid",),
            )

        action = _canonical_action(request.requested_action)
        if action is None:
            return self._deny(
                request=request,
                reason=ReasonCategory.ACTION_UNSUPPORTED,
                requested_action=None,
                authority_inputs=("authentication_evidence:verified",),
            )

        principal_lookup = self._resolve_authority(
            "resolve_principal_mapping",
            subject.provider,
            subject.subject,
        )
        consulted = (
            ("authentication_evidence:verified",)
            + _authority_inputs("principal_mapping", principal_lookup)
        )
        principal_error = _lookup_error_reason(
            principal_lookup,
            default_reason=ReasonCategory.PRINCIPAL_UNRESOLVED,
        )
        if principal_error is not None:
            return self._deny(
                request=request,
                reason=principal_error,
                requested_action=action,
                authority_inputs=consulted,
            )

        principal_mapping = principal_lookup.records[0]
        principal_record_error = _principal_mapping_record_error(
            principal_mapping,
            subject.provider,
            subject.subject,
        )
        if principal_record_error is not None:
            return self._deny(
                request=request,
                reason=principal_record_error,
                requested_action=action,
                principal_id=(
                    principal_mapping.principal_id
                    if isinstance(principal_mapping, PrincipalMapping)
                    else None
                ),
                authority_inputs=consulted,
            )

        if not _has_value(request.resource_reference):
            return self._deny(
                request=request,
                reason=ReasonCategory.RESOURCE_UNRESOLVED,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                authority_inputs=consulted,
            )

        resource_lookup = self._resolve_authority(
            "resolve_resource",
            request.resource_reference or "",
        )
        resource_error = _lookup_error_reason(
            resource_lookup,
            default_reason=ReasonCategory.RESOURCE_UNRESOLVED,
        )
        consulted = consulted + _authority_inputs(
            "resource_identity",
            resource_lookup,
        )
        if resource_error is not None:
            return self._deny(
                request=request,
                reason=resource_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                authority_inputs=consulted,
            )

        resource = resource_lookup.records[0]
        resource_record_error = _resource_record_error(
            resource,
            request.resource_reference or "",
        )
        if resource_record_error is not None:
            return self._deny(
                request=request,
                reason=resource_record_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=(
                    resource.business_entity_id
                    if isinstance(resource, GovernedResource)
                    else None
                ),
                resource=resource if isinstance(resource, GovernedResource) else None,
                authority_inputs=consulted,
            )

        applicability = resolve_applicability(resource.resource_class, action)
        consulted = consulted + (
            f"resource_action_applicability:{APPLICABILITY_GOVERNANCE_VERSION}",
        )
        if applicability is not ResourceActionApplicability.APPLICABLE:
            return self._deny(
                request=request,
                reason=ReasonCategory.ACTION_NOT_APPLICABLE,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=resource.business_entity_id,
                resource=resource,
                applicability=applicability,
                authority_inputs=consulted,
            )

        business_entity_lookup = self._resolve_authority(
            "resolve_business_entity",
            resource.business_entity_id,
        )
        consulted = consulted + _authority_inputs(
            "business_entity",
            business_entity_lookup,
        )
        business_entity_error = _lookup_error_reason(
            business_entity_lookup,
            default_reason=ReasonCategory.BUSINESS_ENTITY_INVALID,
        )
        if business_entity_error is not None:
            return self._deny(
                request=request,
                reason=business_entity_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=resource.business_entity_id,
                resource=resource,
                applicability=applicability,
                authority_inputs=consulted,
            )

        business_entity = business_entity_lookup.records[0]
        business_entity_record_error = _business_entity_record_error(
            business_entity,
            resource.business_entity_id,
        )
        if business_entity_record_error is not None:
            safe_business_entity_id = (
                business_entity.business_entity_id
                if isinstance(business_entity, BusinessEntity)
                and _has_value(business_entity.business_entity_id)
                else resource.business_entity_id
            )
            return self._deny(
                request=request,
                reason=business_entity_record_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=safe_business_entity_id,
                resource=resource,
                applicability=applicability,
                authority_inputs=consulted,
            )

        membership_lookup = self._resolve_authority(
            "resolve_membership",
            principal_mapping.principal_id,
            resource.business_entity_id,
        )
        consulted = consulted + _authority_inputs("membership", membership_lookup)
        membership_error = _lookup_error_reason(
            membership_lookup,
            default_reason=ReasonCategory.MEMBERSHIP_INVALID,
        )
        if membership_error is not None:
            return self._deny(
                request=request,
                reason=membership_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=resource.business_entity_id,
                resource=resource,
                applicability=applicability,
                authority_inputs=consulted,
            )

        membership = membership_lookup.records[0]
        membership_record_error = _membership_record_error(
            membership,
            principal_mapping.principal_id,
            resource.business_entity_id,
        )
        if membership_record_error is not None:
            return self._deny(
                request=request,
                reason=membership_record_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=resource.business_entity_id,
                resource=resource,
                applicability=applicability,
                authority_inputs=consulted,
            )

        entitlement_lookup = self._resolve_authority(
            "resolve_entitlement",
            principal_mapping.principal_id,
            resource.business_entity_id,
            resource.resource_id,
            action,
        )
        consulted = consulted + _authority_inputs(
            "entitlement",
            entitlement_lookup,
        )
        entitlement_error = _lookup_error_reason(
            entitlement_lookup,
            default_reason=ReasonCategory.ENTITLEMENT_MISSING,
        )
        if entitlement_error is not None:
            return self._deny(
                request=request,
                reason=entitlement_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=resource.business_entity_id,
                resource=resource,
                applicability=applicability,
                authority_inputs=consulted,
            )

        entitlement = entitlement_lookup.records[0]
        entitlement_reason = _entitlement_record_error(
            entitlement,
            principal_mapping.principal_id,
            resource.business_entity_id,
            resource.resource_id,
            action,
        )
        if entitlement_reason is not None:
            return self._deny(
                request=request,
                reason=entitlement_reason,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=resource.business_entity_id,
                resource=resource,
                applicability=applicability,
                authority_inputs=consulted,
            )

        return self._allow(
            request=request,
            requested_action=action,
            principal_id=principal_mapping.principal_id,
            business_entity_id=resource.business_entity_id,
            resource=resource,
            applicability=applicability,
            authority_inputs=consulted,
        )

    def _allow(
        self,
        request: AuthorizationRequest,
        requested_action: RequestedAction,
        principal_id: str,
        business_entity_id: str,
        resource: GovernedResource,
        applicability: ResourceActionApplicability,
        authority_inputs: tuple[str, ...],
    ) -> AuthorizationResult:
        evidence = _audit_evidence(
            request=request,
            decision=AuthorizationDecision.ALLOW,
            reason=None,
            requested_action=requested_action,
            principal_id=principal_id,
            business_entity_id=business_entity_id,
            resource=resource,
            applicability=applicability,
            authority_inputs=authority_inputs,
        )
        return AuthorizationResult(
            decision=AuthorizationDecision.ALLOW,
            reason=None,
            audit_evidence=evidence,
        )

    def _resolve_authority(
        self,
        method_name: str,
        *args: object,
    ) -> AuthorityLookupResult:
        try:
            resolver = getattr(self._authority_source, method_name)
            lookup = resolver(*args)
        except Exception:
            return AuthorityLookupResult.unavailable()

        return _normalize_lookup_result(lookup)

    def _deny(
        self,
        request: AuthorizationRequest,
        reason: ReasonCategory,
        requested_action: RequestedAction | None = None,
        principal_id: str | None = None,
        business_entity_id: str | None = None,
        resource: GovernedResource | None = None,
        applicability: ResourceActionApplicability
        = ResourceActionApplicability.UNRESOLVED,
        authority_inputs: tuple[str, ...] = (),
    ) -> AuthorizationResult:
        evidence = _audit_evidence(
            request=request,
            decision=AuthorizationDecision.DENY,
            reason=reason,
            requested_action=requested_action,
            principal_id=principal_id,
            business_entity_id=business_entity_id,
            resource=resource,
            applicability=applicability,
            authority_inputs=authority_inputs,
        )
        return AuthorizationResult(
            decision=AuthorizationDecision.DENY,
            reason=reason,
            audit_evidence=evidence,
        )


def _canonical_action(
    value: RequestedAction | str | None,
) -> RequestedAction | None:
    if isinstance(value, RequestedAction):
        return value

    if not isinstance(value, str):
        return None

    try:
        return RequestedAction(value)
    except ValueError:
        return None


def _lookup_error_reason(
    lookup: AuthorityLookupResult,
    default_reason: ReasonCategory,
) -> ReasonCategory | None:
    if lookup.status is AuthorityLookupStatus.FOUND:
        if len(lookup.records) == 1:
            return None
        return ReasonCategory.AUTHORIZATION_CONFLICT

    if lookup.status is AuthorityLookupStatus.UNAVAILABLE:
        return ReasonCategory.AUTHORITY_UNAVAILABLE

    if lookup.status is AuthorityLookupStatus.STALE:
        return ReasonCategory.STATE_STALE

    if lookup.status in (
        AuthorityLookupStatus.AMBIGUOUS,
        AuthorityLookupStatus.CONFLICTING,
    ):
        return ReasonCategory.AUTHORIZATION_CONFLICT

    if lookup.status in (
        AuthorityLookupStatus.MALFORMED,
        AuthorityLookupStatus.UNSUPPORTED,
    ):
        return ReasonCategory.UNKNOWN_STATE

    return default_reason


def _normalize_lookup_result(lookup: object) -> AuthorityLookupResult:
    if not isinstance(lookup, AuthorityLookupResult):
        return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

    if not isinstance(lookup.status, AuthorityLookupStatus):
        return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

    if not isinstance(lookup.records, tuple):
        return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

    return lookup


def _principal_mapping_record_error(
    principal_mapping: object,
    subject_provider: str,
    subject: str,
) -> ReasonCategory | None:
    if not isinstance(principal_mapping, PrincipalMapping):
        return ReasonCategory.UNKNOWN_STATE

    if (
        not _has_value(principal_mapping.authority_reference)
        or not _has_value(principal_mapping.subject_provider)
        or not _has_value(principal_mapping.subject)
        or not _has_value(principal_mapping.principal_id)
    ):
        return ReasonCategory.UNKNOWN_STATE

    if (
        principal_mapping.subject_provider != subject_provider
        or principal_mapping.subject != subject
    ):
        return ReasonCategory.PRINCIPAL_UNRESOLVED

    if not _is_active(principal_mapping.state):
        return ReasonCategory.PRINCIPAL_UNRESOLVED

    return None


def _resource_record_error(
    resource: object,
    resource_reference: str,
) -> ReasonCategory | None:
    if not isinstance(resource, GovernedResource):
        return ReasonCategory.UNKNOWN_STATE

    if (
        not _has_value(resource.authority_reference)
        or not _has_value(resource.resource_id)
        or not _has_value(resource.resource_reference)
        or not _has_value(resource.business_entity_id)
        or not isinstance(resource.resource_class, ResourceClass)
    ):
        return ReasonCategory.UNKNOWN_STATE

    if resource.resource_reference != resource_reference:
        return ReasonCategory.RESOURCE_MISMATCH

    if not _is_active(resource.state):
        return ReasonCategory.RESOURCE_UNRESOLVED

    return None


def _business_entity_record_error(
    business_entity: object,
    business_entity_id: str,
) -> ReasonCategory | None:
    if not isinstance(business_entity, BusinessEntity):
        return ReasonCategory.UNKNOWN_STATE

    if (
        not _has_value(business_entity.authority_reference)
        or not _has_value(business_entity.business_entity_id)
    ):
        return ReasonCategory.UNKNOWN_STATE

    if (
        business_entity.business_entity_id != business_entity_id
        or not _is_active(business_entity.state)
    ):
        return ReasonCategory.BUSINESS_ENTITY_INVALID

    return None


def _membership_record_error(
    membership: object,
    principal_id: str,
    business_entity_id: str,
) -> ReasonCategory | None:
    if not isinstance(membership, Membership):
        return ReasonCategory.UNKNOWN_STATE

    if (
        not _has_value(membership.authority_reference)
        or not _has_value(membership.principal_id)
        or not _has_value(membership.business_entity_id)
    ):
        return ReasonCategory.UNKNOWN_STATE

    if (
        not _is_active(membership.state)
        or membership.principal_id != principal_id
        or membership.business_entity_id != business_entity_id
    ):
        return ReasonCategory.MEMBERSHIP_INVALID

    return None


def _entitlement_record_error(
    entitlement: object,
    principal_id: str,
    business_entity_id: str,
    resource_id: str,
    action: RequestedAction,
) -> ReasonCategory | None:
    if not isinstance(entitlement, Entitlement):
        return ReasonCategory.UNKNOWN_STATE

    if (
        not _has_value(entitlement.authority_reference)
        or not _has_value(entitlement.principal_id)
        or not _has_value(entitlement.business_entity_id)
        or not _has_value(entitlement.resource_id)
        or not isinstance(entitlement.action, RequestedAction)
    ):
        return ReasonCategory.UNKNOWN_STATE

    if entitlement.principal_id != principal_id:
        return ReasonCategory.ENTITLEMENT_NOT_APPLICABLE

    if entitlement.business_entity_id != business_entity_id:
        return ReasonCategory.BUSINESS_ENTITY_MISMATCH

    if entitlement.resource_id != resource_id:
        return ReasonCategory.RESOURCE_MISMATCH

    if entitlement.action is not action:
        return ReasonCategory.ENTITLEMENT_NOT_APPLICABLE

    if not _is_active(entitlement.state):
        return ReasonCategory.ENTITLEMENT_REVOKED

    return None


def _is_active(state: AuthorityRecordState) -> bool:
    return state is AuthorityRecordState.ACTIVE


def _has_value(value: str | None) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _authority_inputs(
    label: str,
    lookup: AuthorityLookupResult,
) -> tuple[str, ...]:
    if lookup.records:
        return tuple(
            f"{label}:{_authority_reference(record)}"
            for record in lookup.records
        )

    return (f"{label}:{lookup.status.value}",)


def _authority_reference(record: object) -> str:
    reference = getattr(record, "authority_reference", None)
    if _has_value(reference):
        return reference.strip()

    return AuthorityLookupStatus.MALFORMED.value


def _audit_evidence(
    request: AuthorizationRequest,
    decision: AuthorizationDecision,
    reason: ReasonCategory | None,
    requested_action: RequestedAction | None,
    principal_id: str | None,
    business_entity_id: str | None,
    resource: GovernedResource | None,
    applicability: ResourceActionApplicability,
    authority_inputs: tuple[str, ...],
) -> AuthorizationAuditEvidence:
    evidence = AuthorizationAuditEvidence(
        decision_id="pending",
        correlation_id=request.correlation_id,
        evaluation_context=request.evaluation_context,
        principal_id=principal_id,
        business_entity_id=business_entity_id,
        resource_id=resource.resource_id if resource else None,
        resource_class=resource.resource_class if resource else None,
        requested_action=requested_action,
        applicability=applicability,
        authority_inputs=authority_inputs,
        decision=decision,
        reason=reason,
        semantics_version=AUTHORIZATION_SEMANTICS_VERSION,
        applicability_version=APPLICABILITY_GOVERNANCE_VERSION,
    )
    return evidence.with_decision_id(_decision_id(evidence))


def _decision_id(evidence: AuthorizationAuditEvidence) -> str:
    payload = evidence.to_dict()
    payload.pop("decisionId")
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
