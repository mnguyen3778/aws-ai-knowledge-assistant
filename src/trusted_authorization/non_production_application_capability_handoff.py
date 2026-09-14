from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.non_production_application_operation_selection import (
    NonProductionProtectedApplicationOperation as _NonProductionProtectedApplicationOperation,
)


class NonProductionApplicationCapability(_Enum):
    """Closed non-production application capability identities.

    This enum represents an already-legitimate application capability fact for
    this bounded proof. Selecting or constructing the enum does not prove that a
    real runtime request originated from the governed application capability.
    Capability legitimacy is established upstream by governed application
    capability architecture / the product application contract owner.
    """

    ASSESSMENT_SUBMISSION = "ASSESSMENT_SUBMISSION"


class NonProductionApplicationCapabilityHandoffStatus(_Enum):
    READY = "READY"
    INVALID = "INVALID"


@_dataclass(frozen=True, slots=True)
class NonProductionApplicationCapabilityHandoffResult:
    status: NonProductionApplicationCapabilityHandoffStatus
    protected_operation: _NonProductionProtectedApplicationOperation | None = None


def resolve_non_production_application_capability_handoff(
    *,
    application_capability: object,
) -> NonProductionApplicationCapabilityHandoffResult:
    if type(application_capability) is not NonProductionApplicationCapability:
        return _invalid_handoff()

    if application_capability is NonProductionApplicationCapability.ASSESSMENT_SUBMISSION:
        return NonProductionApplicationCapabilityHandoffResult(
            status=NonProductionApplicationCapabilityHandoffStatus.READY,
            protected_operation=(
                _NonProductionProtectedApplicationOperation.
                PROTECTED_ASSESSMENT_SUBMISSION
            ),
        )

    return _invalid_handoff()


def _invalid_handoff() -> NonProductionApplicationCapabilityHandoffResult:
    return NonProductionApplicationCapabilityHandoffResult(
        status=NonProductionApplicationCapabilityHandoffStatus.INVALID,
        protected_operation=None,
    )
