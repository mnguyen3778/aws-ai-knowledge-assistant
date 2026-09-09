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


class NonProductionMembershipAuthoritySource:
    """Local read-only source for constructor-supplied memberships."""

    __slots__ = ("_has_malformed_evidence", "_memberships")

    def __init__(
        self,
        memberships: Iterable[Membership] = (),
    ):
        snapshots = []
        has_malformed_evidence = False
        for record in memberships:
            snapshot = _membership_snapshot(record)
            if snapshot is None:
                has_malformed_evidence = True
            else:
                snapshots.append(snapshot)

        self._memberships = tuple(snapshots)
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
        if not _has_value(principal_id) or not _has_value(business_entity_id):
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        if self._has_malformed_evidence:
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        applicable = tuple(
            record
            for record in self._memberships
            if record.principal_id == principal_id
            and record.business_entity_id == business_entity_id
        )
        if not applicable:
            return AuthorityLookupResult.missing()

        if len(applicable) > 1:
            identities = {
                (
                    record.authority_reference,
                    record.state,
                    record.principal_id,
                    record.business_entity_id,
                )
                for record in applicable
            }
            if len(identities) > 1:
                return AuthorityLookupResult.conflicting(_membership_outputs(applicable))
            return AuthorityLookupResult.ambiguous(_membership_outputs(applicable))

        record = applicable[0]
        state = record.state
        if state is AuthorityRecordState.ACTIVE:
            return AuthorityLookupResult.found(_membership_output(record))
        if state is AuthorityRecordState.STALE:
            return AuthorityLookupResult.stale()
        return AuthorityLookupResult.missing()

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


def _membership_outputs(
    records: tuple[Membership, ...],
) -> tuple[Membership, ...]:
    return tuple(_membership_output(record) for record in records)


def _membership_output(record: Membership) -> Membership:
    return Membership(
        authority_reference=record.authority_reference,
        state=record.state,
        principal_id=record.principal_id,
        business_entity_id=record.business_entity_id,
    )


def _membership_snapshot(record: object) -> Membership | None:
    if type(record) is not Membership:
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
        "principal_id",
        "business_entity_id",
    )
    if any(name not in instance_fields for name in required_fields):
        return None

    authority_reference = instance_fields["authority_reference"]
    state = instance_fields["state"]
    principal_id = instance_fields["principal_id"]
    business_entity_id = instance_fields["business_entity_id"]

    if (
        not _has_value(authority_reference)
        or not isinstance(state, AuthorityRecordState)
        or not _has_value(principal_id)
        or not _has_value(business_entity_id)
    ):
        return None

    return Membership(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        business_entity_id=business_entity_id,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value.strip())
