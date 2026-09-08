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


class NonProductionPrincipalMappingAuthoritySource:
    """Local read-only source for constructor-supplied principal mappings."""

    __slots__ = ("_has_malformed_evidence", "_principal_mappings")

    def __init__(
        self,
        principal_mappings: Iterable[PrincipalMapping] = (),
    ):
        snapshots = []
        has_malformed_evidence = False
        for record in principal_mappings:
            snapshot = _principal_mapping_snapshot(record)
            if snapshot is None:
                has_malformed_evidence = True
            else:
                snapshots.append(snapshot)

        self._principal_mappings = tuple(snapshots)
        self._has_malformed_evidence = has_malformed_evidence

    def resolve_principal_mapping(
        self,
        subject_provider: str,
        subject: str,
    ) -> AuthorityLookupResult[PrincipalMapping]:
        if not _has_value(subject_provider) or not _has_value(subject):
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        if self._has_malformed_evidence:
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)

        applicable = tuple(
            record
            for record in self._principal_mappings
            if record.subject_provider == subject_provider
            and record.subject == subject
        )
        if not applicable:
            return AuthorityLookupResult.missing()

        if len(applicable) > 1:
            identities = {
                (
                    record.authority_reference,
                    record.state,
                    record.subject_provider,
                    record.subject,
                    record.principal_id,
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


def _principal_mapping_snapshot(record: object) -> PrincipalMapping | None:
    if type(record) is not PrincipalMapping:
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
        "subject_provider",
        "subject",
        "principal_id",
    )
    if any(name not in instance_fields for name in required_fields):
        return None

    authority_reference = instance_fields["authority_reference"]
    state = instance_fields["state"]
    subject_provider = instance_fields["subject_provider"]
    subject = instance_fields["subject"]
    principal_id = instance_fields["principal_id"]

    if (
        not _has_value(authority_reference)
        or not isinstance(state, AuthorityRecordState)
        or not _has_value(subject_provider)
        or not _has_value(subject)
        or not _has_value(principal_id)
    ):
        return None

    return PrincipalMapping(
        authority_reference=authority_reference,
        state=state,
        subject_provider=subject_provider,
        subject=subject,
        principal_id=principal_id,
    )


def _has_value(value: object) -> bool:
    return type(value) is str and bool(value.strip())
