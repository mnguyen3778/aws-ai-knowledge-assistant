from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from trusted_authorization.business_entity_source import (
    NonProductionBusinessEntityAuthoritySource,
)
from trusted_authorization.entitlement_source import (
    NonProductionEntitlementAuthoritySource,
)
from trusted_authorization.membership_source import (
    NonProductionMembershipAuthoritySource,
)
from trusted_authorization.models import (
    AuthorityLookupResult,
    BusinessEntity,
    Entitlement,
    GovernedResource,
    Membership,
    PrincipalMapping,
    RequestedAction,
)
from trusted_authorization.principal_mapping_source import (
    NonProductionPrincipalMappingAuthoritySource,
)
from trusted_authorization.resource_identity_source import (
    NonProductionResourceIdentityAuthoritySource,
)


@dataclass(frozen=True, init=False, slots=True)
class NonProductionTrustedAuthorizationRuntimeComposition:
    """Explicit non-production composition of accepted read-side sources."""

    _principal_mapping_source: NonProductionPrincipalMappingAuthoritySource = field(
        init=False,
        repr=False,
    )
    _resource_identity_source: NonProductionResourceIdentityAuthoritySource = field(
        init=False,
        repr=False,
    )
    _business_entity_source: NonProductionBusinessEntityAuthoritySource = field(
        init=False,
        repr=False,
    )
    _membership_source: NonProductionMembershipAuthoritySource = field(
        init=False,
        repr=False,
    )
    _entitlement_source: NonProductionEntitlementAuthoritySource = field(
        init=False,
        repr=False,
    )

    def __init__(
        self,
        *,
        principal_mappings: Iterable[PrincipalMapping] = (),
        resources: Iterable[GovernedResource] = (),
        business_entities: Iterable[BusinessEntity] = (),
        memberships: Iterable[Membership] = (),
        entitlements: Iterable[Entitlement] = (),
    ) -> None:
        object.__setattr__(
            self,
            "_principal_mapping_source",
            NonProductionPrincipalMappingAuthoritySource(principal_mappings),
        )
        object.__setattr__(
            self,
            "_resource_identity_source",
            NonProductionResourceIdentityAuthoritySource(resources),
        )
        object.__setattr__(
            self,
            "_business_entity_source",
            NonProductionBusinessEntityAuthoritySource(business_entities),
        )
        object.__setattr__(
            self,
            "_membership_source",
            NonProductionMembershipAuthoritySource(memberships),
        )
        object.__setattr__(
            self,
            "_entitlement_source",
            NonProductionEntitlementAuthoritySource(entitlements),
        )

    def resolve_principal_mapping(
        self,
        subject_provider: str,
        subject: str,
    ) -> AuthorityLookupResult[PrincipalMapping]:
        return self._principal_mapping_source.resolve_principal_mapping(
            subject_provider,
            subject,
        )

    def resolve_resource(
        self,
        resource_reference: str,
    ) -> AuthorityLookupResult[GovernedResource]:
        return self._resource_identity_source.resolve_resource(resource_reference)

    def resolve_business_entity(
        self,
        business_entity_id: str,
    ) -> AuthorityLookupResult[BusinessEntity]:
        return self._business_entity_source.resolve_business_entity(
            business_entity_id,
        )

    def resolve_membership(
        self,
        principal_id: str,
        business_entity_id: str,
    ) -> AuthorityLookupResult[Membership]:
        return self._membership_source.resolve_membership(
            principal_id,
            business_entity_id,
        )

    def resolve_entitlement(
        self,
        principal_id: str,
        business_entity_id: str,
        resource_id: str,
        action: RequestedAction,
    ) -> AuthorityLookupResult[Entitlement]:
        return self._entitlement_source.resolve_entitlement(
            principal_id,
            business_entity_id,
            resource_id,
            action,
        )
