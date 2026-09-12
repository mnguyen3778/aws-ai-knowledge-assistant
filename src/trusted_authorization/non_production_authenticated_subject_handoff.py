from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import (
    TrustedSubjectEvidence as _TrustedSubjectEvidence,
)


@_dataclass(frozen=True, slots=True)
class NonProductionVerifiedAuthenticationFact:
    """Bounded representation of an already-verified authentication result.

    Constructing this Python object does not perform authentication and does
    not prove real-world authentication provenance. It represents, for this
    non-production proof only, a successful/current verification result already
    established upstream by the governed Authentication Verification Owner.
    """

    provider: str
    subject: str


class NonProductionAuthenticatedSubjectHandoffStatus(_Enum):
    READY = "READY"
    INVALID = "INVALID"


@_dataclass(frozen=True, slots=True)
class NonProductionAuthenticatedSubjectHandoffResult:
    status: NonProductionAuthenticatedSubjectHandoffStatus
    trusted_subject_evidence: _TrustedSubjectEvidence | None = None


def resolve_non_production_authenticated_subject_handoff(
    *,
    verified_authentication_fact: object,
) -> NonProductionAuthenticatedSubjectHandoffResult:
    if type(verified_authentication_fact) is not NonProductionVerifiedAuthenticationFact:
        return _invalid_handoff()

    provider = verified_authentication_fact.provider
    subject = verified_authentication_fact.subject

    if not _is_valid_subject_component(provider):
        return _invalid_handoff()

    if not _is_valid_subject_component(subject):
        return _invalid_handoff()

    return NonProductionAuthenticatedSubjectHandoffResult(
        status=NonProductionAuthenticatedSubjectHandoffStatus.READY,
        trusted_subject_evidence=_TrustedSubjectEvidence(
            provider=provider,
            subject=subject,
            verified=True,
        ),
    )


def _is_valid_subject_component(value: object) -> bool:
    return type(value) is str and bool(value.strip())


def _invalid_handoff() -> NonProductionAuthenticatedSubjectHandoffResult:
    return NonProductionAuthenticatedSubjectHandoffResult(
        status=NonProductionAuthenticatedSubjectHandoffStatus.INVALID,
        trusted_subject_evidence=None,
    )
