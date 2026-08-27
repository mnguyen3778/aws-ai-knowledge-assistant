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
    GovernedVersionContext,
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
BOUNDED_EVALUATION_CONTEXT = "local-deterministic-fixture"
_MISSING = object()


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
                governed_version_context=None,
                correlation_id="malformed-request",
                evaluation_context=BOUNDED_EVALUATION_CONTEXT,
            )

        subject = _required_instance_field(request, "subject_evidence")
        subject_provider = _required_instance_field(subject, "provider")
        subject_identifier = _required_instance_field(subject, "subject")
        subject_verified = _required_instance_field(subject, "verified")
        if (
            not isinstance(subject, TrustedSubjectEvidence)
            or subject_verified is not True
            or not _has_value(subject_provider)
            or not _has_value(subject_identifier)
        ):
            return self._deny(
                request=request,
                reason=ReasonCategory.AUTHENTICATION_INVALID,
                requested_action=None,
                authority_inputs=("authentication_evidence:invalid",),
            )

        version_context = _required_instance_field(
            request,
            "governed_version_context",
        )
        evaluation_context = _required_instance_field(request, "evaluation_context")
        version_context_error = _governed_version_context_error(
            version_context,
            evaluation_context,
        )
        version_context_inputs = (
            ("authentication_evidence:verified",)
            + _governed_version_context_inputs(version_context)
        )
        if version_context_error is not None:
            return self._deny(
                request=request,
                reason=version_context_error,
                requested_action=None,
                authority_inputs=version_context_inputs,
            )

        action = _canonical_action(
            _required_instance_field(request, "requested_action")
        )
        if action is None:
            return self._deny(
                request=request,
                reason=ReasonCategory.ACTION_UNSUPPORTED,
                requested_action=None,
                authority_inputs=version_context_inputs,
            )

        principal_lookup = self._resolve_authority(
            "resolve_principal_mapping",
            subject_provider,
            subject_identifier,
        )
        consulted = (
            version_context_inputs
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

        principal_record = principal_lookup.records[0]
        principal_record_error, principal_mapping = _validated_principal_mapping(
            principal_record,
            subject_provider,
            subject_identifier,
        )
        if principal_record_error is not None:
            return self._deny(
                request=request,
                reason=principal_record_error,
                requested_action=action,
                principal_id=(
                    principal_mapping.principal_id
                    if principal_mapping is not None
                    else None
                ),
                authority_inputs=consulted,
            )

        resource_reference = _required_instance_field(
            request,
            "resource_reference",
        )
        if not _has_value(resource_reference):
            return self._deny(
                request=request,
                reason=ReasonCategory.RESOURCE_UNRESOLVED,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                authority_inputs=consulted,
            )

        resource_lookup = self._resolve_authority(
            "resolve_resource",
            resource_reference,
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

        resource_record = resource_lookup.records[0]
        resource_record_error, resource = _validated_resource(
            resource_record,
            resource_reference,
        )
        if resource_record_error is not None:
            return self._deny(
                request=request,
                reason=resource_record_error,
                requested_action=action,
                principal_id=principal_mapping.principal_id,
                business_entity_id=(
                    resource.business_entity_id
                    if resource is not None
                    else None
                ),
                resource=resource,
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

        business_entity_record = business_entity_lookup.records[0]
        business_entity_record_error, business_entity = _validated_business_entity(
            business_entity_record,
            resource.business_entity_id,
        )
        if business_entity_record_error is not None:
            safe_business_entity_id = (
                business_entity.business_entity_id
                if business_entity is not None
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

        membership_record = membership_lookup.records[0]
        membership_record_error, membership = _validated_membership(
            membership_record,
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

        entitlement_record = entitlement_lookup.records[0]
        entitlement_reason, entitlement = _validated_entitlement(
            entitlement_record,
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


def _governed_version_context_error(
    context: object,
    request_evaluation_context: object,
) -> ReasonCategory | None:
    if not isinstance(context, GovernedVersionContext):
        return ReasonCategory.UNKNOWN_STATE

    authorization_semantics_version = _required_instance_field(
        context,
        "authorization_semantics_version",
    )
    applicability_governance_version = _required_instance_field(
        context,
        "applicability_governance_version",
    )
    evaluation_context = _required_instance_field(context, "evaluation_context")
    if (
        not _has_value(authorization_semantics_version)
        or not _has_value(applicability_governance_version)
        or not _has_value(evaluation_context)
        or not _has_value(request_evaluation_context)
    ):
        return ReasonCategory.UNKNOWN_STATE

    if (
        authorization_semantics_version != AUTHORIZATION_SEMANTICS_VERSION
        or applicability_governance_version != APPLICABILITY_GOVERNANCE_VERSION
        or evaluation_context != BOUNDED_EVALUATION_CONTEXT
        or request_evaluation_context != BOUNDED_EVALUATION_CONTEXT
    ):
        return ReasonCategory.UNKNOWN_STATE

    return None


def _governed_version_context_inputs(
    context: object,
) -> tuple[str, ...]:
    if (
        _governed_version_context_error(
            context,
            _required_instance_field(context, "evaluation_context"),
        )
        is not None
    ):
        return ("governed_version_context:MALFORMED",)

    return (
        f"authorization_semantics:{AUTHORIZATION_SEMANTICS_VERSION}",
        f"resource_action_applicability:{APPLICABILITY_GOVERNANCE_VERSION}",
        f"evaluation_context:{BOUNDED_EVALUATION_CONTEXT}",
    )


def _lookup_error_reason(
    lookup: AuthorityLookupResult,
    default_reason: ReasonCategory,
) -> ReasonCategory | None:
    status = _required_instance_field(lookup, "status")
    records = _required_instance_field(lookup, "records")
    if not isinstance(status, AuthorityLookupStatus) or not isinstance(
        records,
        tuple,
    ):
        return ReasonCategory.UNKNOWN_STATE

    if status is AuthorityLookupStatus.FOUND:
        if len(records) == 1:
            return None
        return ReasonCategory.AUTHORIZATION_CONFLICT

    if status is AuthorityLookupStatus.UNAVAILABLE:
        return ReasonCategory.AUTHORITY_UNAVAILABLE

    if status is AuthorityLookupStatus.STALE:
        return ReasonCategory.STATE_STALE

    if status in (
        AuthorityLookupStatus.AMBIGUOUS,
        AuthorityLookupStatus.CONFLICTING,
    ):
        return ReasonCategory.AUTHORIZATION_CONFLICT

    if status in (
        AuthorityLookupStatus.MALFORMED,
        AuthorityLookupStatus.UNSUPPORTED,
    ):
        return ReasonCategory.UNKNOWN_STATE

    return default_reason


def _normalize_lookup_result(lookup: object) -> AuthorityLookupResult:
    if not isinstance(lookup, AuthorityLookupResult):
        return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

    status = _required_instance_field(lookup, "status")
    records = _required_instance_field(lookup, "records")
    if not isinstance(status, AuthorityLookupStatus):
        return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

    if not isinstance(records, tuple):
        return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

    return AuthorityLookupResult(status, records)


def _validated_principal_mapping(
    principal_mapping: object,
    subject_provider: str,
    subject: str,
) -> tuple[ReasonCategory | None, PrincipalMapping | None]:
    if not isinstance(principal_mapping, PrincipalMapping):
        return ReasonCategory.UNKNOWN_STATE, None

    authority_reference = _required_instance_field(
        principal_mapping,
        "authority_reference",
    )
    record_subject_provider = _required_instance_field(
        principal_mapping,
        "subject_provider",
    )
    record_subject = _required_instance_field(principal_mapping, "subject")
    principal_id = _required_instance_field(principal_mapping, "principal_id")

    if (
        not _has_value(authority_reference)
        or not _has_value(record_subject_provider)
        or not _has_value(record_subject)
        or not _has_value(principal_id)
    ):
        return ReasonCategory.UNKNOWN_STATE, None

    state = _authority_record_state(principal_mapping)
    if state is None:
        return ReasonCategory.UNKNOWN_STATE, None

    validated = PrincipalMapping(
        authority_reference=authority_reference,
        state=state,
        subject_provider=record_subject_provider,
        subject=record_subject,
        principal_id=principal_id,
    )

    if (
        validated.subject_provider != subject_provider
        or validated.subject != subject
    ):
        return ReasonCategory.PRINCIPAL_UNRESOLVED, validated

    if not _is_active(validated.state):
        return ReasonCategory.PRINCIPAL_UNRESOLVED, validated

    return None, validated


def _validated_resource(
    resource: object,
    resource_reference: str,
) -> tuple[ReasonCategory | None, GovernedResource | None]:
    if not isinstance(resource, GovernedResource):
        return ReasonCategory.UNKNOWN_STATE, None

    authority_reference = _required_instance_field(resource, "authority_reference")
    resource_id = _required_instance_field(resource, "resource_id")
    record_resource_reference = _required_instance_field(
        resource,
        "resource_reference",
    )
    business_entity_id = _required_instance_field(resource, "business_entity_id")
    resource_class = _required_instance_field(resource, "resource_class")

    if (
        not _has_value(authority_reference)
        or not _has_value(resource_id)
        or not _has_value(record_resource_reference)
        or not _has_value(business_entity_id)
        or not isinstance(resource_class, ResourceClass)
    ):
        return ReasonCategory.UNKNOWN_STATE, None

    state = _authority_record_state(resource)
    if state is None:
        return ReasonCategory.UNKNOWN_STATE, None

    validated = GovernedResource(
        authority_reference=authority_reference,
        state=state,
        resource_id=resource_id,
        resource_reference=record_resource_reference,
        resource_class=resource_class,
        business_entity_id=business_entity_id,
    )

    if validated.resource_reference != resource_reference:
        return ReasonCategory.RESOURCE_MISMATCH, validated

    if not _is_active(validated.state):
        return ReasonCategory.RESOURCE_UNRESOLVED, validated

    return None, validated


def _validated_business_entity(
    business_entity: object,
    business_entity_id: str,
) -> tuple[ReasonCategory | None, BusinessEntity | None]:
    if not isinstance(business_entity, BusinessEntity):
        return ReasonCategory.UNKNOWN_STATE, None

    authority_reference = _required_instance_field(
        business_entity,
        "authority_reference",
    )
    record_business_entity_id = _required_instance_field(
        business_entity,
        "business_entity_id",
    )

    if (
        not _has_value(authority_reference)
        or not _has_value(record_business_entity_id)
    ):
        return ReasonCategory.UNKNOWN_STATE, None

    state = _authority_record_state(business_entity)
    if state is None:
        return ReasonCategory.UNKNOWN_STATE, None

    validated = BusinessEntity(
        authority_reference=authority_reference,
        state=state,
        business_entity_id=record_business_entity_id,
    )

    if (
        validated.business_entity_id != business_entity_id
        or not _is_active(validated.state)
    ):
        return ReasonCategory.BUSINESS_ENTITY_INVALID, validated

    return None, validated


def _validated_membership(
    membership: object,
    principal_id: str,
    business_entity_id: str,
) -> tuple[ReasonCategory | None, Membership | None]:
    if not isinstance(membership, Membership):
        return ReasonCategory.UNKNOWN_STATE, None

    authority_reference = _required_instance_field(membership, "authority_reference")
    record_principal_id = _required_instance_field(membership, "principal_id")
    record_business_entity_id = _required_instance_field(
        membership,
        "business_entity_id",
    )

    if (
        not _has_value(authority_reference)
        or not _has_value(record_principal_id)
        or not _has_value(record_business_entity_id)
    ):
        return ReasonCategory.UNKNOWN_STATE, None

    state = _authority_record_state(membership)
    if state is None:
        return ReasonCategory.UNKNOWN_STATE, None

    validated = Membership(
        authority_reference=authority_reference,
        state=state,
        principal_id=record_principal_id,
        business_entity_id=record_business_entity_id,
    )

    if (
        not _is_active(validated.state)
        or validated.principal_id != principal_id
        or validated.business_entity_id != business_entity_id
    ):
        return ReasonCategory.MEMBERSHIP_INVALID, validated

    return None, validated


def _validated_entitlement(
    entitlement: object,
    principal_id: str,
    business_entity_id: str,
    resource_id: str,
    action: RequestedAction,
) -> tuple[ReasonCategory | None, Entitlement | None]:
    if not isinstance(entitlement, Entitlement):
        return ReasonCategory.UNKNOWN_STATE, None

    authority_reference = _required_instance_field(entitlement, "authority_reference")
    record_principal_id = _required_instance_field(entitlement, "principal_id")
    record_business_entity_id = _required_instance_field(
        entitlement,
        "business_entity_id",
    )
    record_resource_id = _required_instance_field(entitlement, "resource_id")
    record_action = _required_instance_field(entitlement, "action")

    if (
        not _has_value(authority_reference)
        or not _has_value(record_principal_id)
        or not _has_value(record_business_entity_id)
        or not _has_value(record_resource_id)
        or not isinstance(record_action, RequestedAction)
    ):
        return ReasonCategory.UNKNOWN_STATE, None

    state = _authority_record_state(entitlement)
    if state is None:
        return ReasonCategory.UNKNOWN_STATE, None

    validated = Entitlement(
        authority_reference=authority_reference,
        state=state,
        principal_id=record_principal_id,
        business_entity_id=record_business_entity_id,
        resource_id=record_resource_id,
        action=record_action,
    )

    if validated.principal_id != principal_id:
        return ReasonCategory.ENTITLEMENT_NOT_APPLICABLE, validated

    if validated.business_entity_id != business_entity_id:
        return ReasonCategory.BUSINESS_ENTITY_MISMATCH, validated

    if validated.resource_id != resource_id:
        return ReasonCategory.RESOURCE_MISMATCH, validated

    if validated.action is not action:
        return ReasonCategory.ENTITLEMENT_NOT_APPLICABLE, validated

    if not _is_active(validated.state):
        return ReasonCategory.ENTITLEMENT_REVOKED, validated

    return None, validated


def _is_active(state: AuthorityRecordState) -> bool:
    return state is AuthorityRecordState.ACTIVE


def _authority_record_state(record: object) -> AuthorityRecordState | None:
    state = _required_instance_field(record, "state")
    if isinstance(state, AuthorityRecordState):
        return state

    return None


def _has_value(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _required_instance_field(
    value: object,
    name: str,
    default: object = _MISSING,
) -> object:
    try:
        instance_fields = vars(value)
    except Exception:
        return default

    return instance_fields.get(name, default)


def _safe_evaluation_context(value: object) -> str:
    if value == BOUNDED_EVALUATION_CONTEXT:
        return BOUNDED_EVALUATION_CONTEXT

    return AuthorityLookupStatus.MALFORMED.value


def _safe_correlation_id(value: object) -> str:
    if _has_value(value):
        return value.strip()

    return "malformed-request"


def _safe_resource_class(resource: GovernedResource | None) -> ResourceClass | None:
    resource_class = _required_instance_field(resource, "resource_class")
    if isinstance(resource_class, ResourceClass):
        return resource_class

    return None


def _safe_resource_id(resource: GovernedResource | None) -> str | None:
    resource_id = _required_instance_field(resource, "resource_id")
    if _has_value(resource_id):
        return resource_id.strip()

    return None


def _authority_inputs(
    label: str,
    lookup: AuthorityLookupResult,
) -> tuple[str, ...]:
    status = _required_instance_field(lookup, "status")
    records = _required_instance_field(lookup, "records")
    if isinstance(records, tuple) and records:
        return tuple(
            f"{label}:{_authority_reference(record)}"
            for record in records
        )

    if isinstance(status, AuthorityLookupStatus):
        return (f"{label}:{status.value}",)

    return (f"{label}:{AuthorityLookupStatus.MALFORMED.value}",)


def _authority_reference(record: object) -> str:
    reference = _required_instance_field(record, "authority_reference")
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
        correlation_id=_safe_correlation_id(
            _required_instance_field(request, "correlation_id")
        ),
        evaluation_context=_safe_evaluation_context(
            _required_instance_field(request, "evaluation_context")
        ),
        principal_id=principal_id,
        business_entity_id=business_entity_id,
        resource_id=_safe_resource_id(resource) if resource else None,
        resource_class=_safe_resource_class(resource),
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
