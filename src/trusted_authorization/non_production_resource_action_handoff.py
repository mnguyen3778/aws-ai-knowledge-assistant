from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.models import RequestedAction as _RequestedAction


class NonProductionApplicationOperation(_Enum):
    """Closed non-production application operation identities."""

    VIEW_RESOURCE = "VIEW_RESOURCE"
    DOWNLOAD_RESOURCE = "DOWNLOAD_RESOURCE"
    SUBMIT_ASSESSMENT = "SUBMIT_ASSESSMENT"


class NonProductionResourceActionHandoffStatus(_Enum):
    READY = "READY"
    INVALID = "INVALID"


@_dataclass(frozen=True, slots=True)
class NonProductionResourceActionHandoffResult:
    status: NonProductionResourceActionHandoffStatus
    resource_reference: str | None = None
    requested_action: _RequestedAction | None = None


def resolve_non_production_resource_action_handoff(
    *,
    resource_reference: object,
    operation: object,
) -> NonProductionResourceActionHandoffResult:
    if not _is_valid_resource_reference(resource_reference):
        return _invalid_handoff()

    if type(operation) is not NonProductionApplicationOperation:
        return _invalid_handoff()

    requested_action = _requested_action_for_operation(operation)
    if requested_action is None:
        return _invalid_handoff()

    return NonProductionResourceActionHandoffResult(
        status=NonProductionResourceActionHandoffStatus.READY,
        resource_reference=resource_reference,
        requested_action=requested_action,
    )


def _requested_action_for_operation(
    operation: NonProductionApplicationOperation,
) -> _RequestedAction | None:
    if operation is NonProductionApplicationOperation.VIEW_RESOURCE:
        return _RequestedAction.VIEW

    if operation is NonProductionApplicationOperation.DOWNLOAD_RESOURCE:
        return _RequestedAction.DOWNLOAD

    if operation is NonProductionApplicationOperation.SUBMIT_ASSESSMENT:
        return _RequestedAction.SUBMIT

    return None


def _is_valid_resource_reference(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.strip() == value
        and bool(value.strip())
    )


def _invalid_handoff() -> NonProductionResourceActionHandoffResult:
    return NonProductionResourceActionHandoffResult(
        status=NonProductionResourceActionHandoffStatus.INVALID,
        resource_reference=None,
        requested_action=None,
    )
