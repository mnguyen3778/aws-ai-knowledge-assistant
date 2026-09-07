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
)


_MISSING = object()


class NonProductionPrincipalMappingAuthoritySource:
    """Local read-only source for constructor-supplied principal mappings."""

    __slots__ = ("_principal_mappings",)

    def __init__(
        self,
        principal_mappings: Iterable[PrincipalMapping] = (),
    ):
        self._principal_mappings = tuple(principal_mappings)

    def resolve_principal_mapping(
        self,
        subject_provider: str,
        subject: str,
    ) -> AuthorityLookupResult[PrincipalMapping]:
        if not _has_value(subject_provider) or not _has_value(subject):
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        records = self._principal_mappings
        if any(not _valid_mapping_shape(record) for record in records):
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        applicable = tuple(
            record
            for record in records
            if _instance_value(record, "subject_provider") == subject_provider
            and _instance_value(record, "subject") == subject
        )
        if not applicable:
            return AuthorityLookupResult.missing()

        if len(applicable) > 1:
            principal_ids = {
                _instance_value(record, "principal_id") for record in applicable
            }
            states = {_instance_value(record, "state") for record in applicable}
            if len(principal_ids) > 1 or len(states) > 1:
                return AuthorityLookupResult.conflicting(applicable)
            return AuthorityLookupResult.ambiguous(applicable)

        record = applicable[0]
        state = _instance_value(record, "state")
        if state is AuthorityRecordState.ACTIVE:
            return AuthorityLookupResult.found(record)
        if state is AuthorityRecordState.STALE:
            return AuthorityLookupResult.stale()
        return AuthorityLookupResult.missing()

    def resolve_resource(
        self,
        resource_reference: str,
    ) -> AuthorityLookupResult[GovernedResource]:
        return _unsupported()

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


def _valid_mapping_shape(record: object) -> bool:
    if not isinstance(record, PrincipalMapping):
        return False

    return (
        _has_value(_instance_value(record, "authority_reference"))
        and isinstance(_instance_value(record, "state"), AuthorityRecordState)
        and _has_value(_instance_value(record, "subject_provider"))
        and _has_value(_instance_value(record, "subject"))
        and _has_value(_instance_value(record, "principal_id"))
    )


def _instance_value(value: object, name: str) -> object:
    try:
        return vars(value).get(name, _MISSING)
    except Exception:
        return _MISSING


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value.strip())
