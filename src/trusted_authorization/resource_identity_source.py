from __future__ import annotations

from collections.abc import Iterable

from trusted_authorization.models import (
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    BusinessEntity,
    Entitlement,
    GovernedResource,
    Membership,
    PrincipalMapping,
    RequestedAction,
    ResourceClass,
)


class NonProductionResourceIdentityAuthoritySource:
    """Local read-only source for constructor-supplied resource identities."""

    __slots__ = ("_has_malformed_evidence", "_resources")

    def __init__(
        self,
        resources: Iterable[GovernedResource] = (),
    ):
        snapshots = []
        has_malformed_evidence = False
        for record in resources:
            snapshot = _resource_snapshot(record)
            if snapshot is None:
                has_malformed_evidence = True
            else:
                snapshots.append(snapshot)

        self._resources = tuple(snapshots)
        self._has_malformed_evidence = has_malformed_evidence

    def resolve_principal_mapping(
        self,
        subject_provider: str,
        subject: str,
    ) -> AuthorityLookupResult[PrincipalMapping]:
        return _unsupported()

    def resolve_resource(
        self,
        resource_reference: str,
    ) -> AuthorityLookupResult[GovernedResource]:
        if not _has_value(resource_reference):
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        if self._has_malformed_evidence:
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        applicable = tuple(
            record
            for record in self._resources
            if record.resource_reference == resource_reference
        )
        if not applicable:
            return AuthorityLookupResult.missing()

        if len(applicable) > 1:
            identities = {
                (
                    record.authority_reference,
                    record.state,
                    record.resource_id,
                    record.business_entity_id,
                    record.resource_class,
                )
                for record in applicable
            }
            if len(identities) > 1:
                return AuthorityLookupResult.conflicting(applicable)
            return AuthorityLookupResult.ambiguous(applicable)

        record = applicable[0]
        state = record.state
        if state is AuthorityRecordState.ACTIVE:
            return AuthorityLookupResult.found(record)
        if state is AuthorityRecordState.STALE:
            return AuthorityLookupResult.stale()
        return AuthorityLookupResult.missing()

    def resolve_business_entity(
        self,
        business_entity_id: str,
    ) -> AuthorityLookupResult[BusinessEntity]:
        return _unsupported()

    def resolve_membership(
        self,
        principal_id: str,
        business_entity_id: str,
    ) -> AuthorityLookupResult[Membership]:
        return _unsupported()

    def resolve_entitlement(
        self,
        principal_id: str,
        business_entity_id: str,
        resource_id: str,
        action: RequestedAction,
    ) -> AuthorityLookupResult[Entitlement]:
        return _unsupported()


def _unsupported() -> AuthorityLookupResult:
    return AuthorityLookupResult(AuthorityLookupStatus.UNSUPPORTED)


def _resource_snapshot(record: object) -> GovernedResource | None:
    if type(record) is not GovernedResource:
        return None

    try:
        instance_fields = object.__getattribute__(record, "__dict__")
    except Exception:
        return None

    if type(instance_fields) is not dict:
        return None

    required_fields = (
        "authority_reference",
        "state",
        "resource_id",
        "resource_reference",
        "resource_class",
        "business_entity_id",
    )
    if any(name not in instance_fields for name in required_fields):
        return None

    authority_reference = instance_fields["authority_reference"]
    state = instance_fields["state"]
    resource_id = instance_fields["resource_id"]
    resource_reference = instance_fields["resource_reference"]
    resource_class = instance_fields["resource_class"]
    business_entity_id = instance_fields["business_entity_id"]

    if (
        not _has_value(authority_reference)
        or not isinstance(state, AuthorityRecordState)
        or not _has_value(resource_id)
        or not _has_value(resource_reference)
        or not isinstance(resource_class, ResourceClass)
        or not _has_value(business_entity_id)
    ):
        return None

    return GovernedResource(
        authority_reference=authority_reference,
        state=state,
        resource_id=resource_id,
        resource_reference=resource_reference,
        resource_class=resource_class,
        business_entity_id=business_entity_id,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value.strip())
