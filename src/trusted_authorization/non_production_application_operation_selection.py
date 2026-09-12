from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

from trusted_authorization.non_production_resource_action_handoff import (
    NonProductionApplicationOperation as _NonProductionApplicationOperation,
)


class NonProductionProtectedApplicationOperation(_Enum):
    """Closed non-production protected application operation identities."""

    PROTECTED_ASSESSMENT_SUBMISSION = "PROTECTED_ASSESSMENT_SUBMISSION"


class NonProductionApplicationOperationSelectionStatus(_Enum):
    READY = "READY"
    INVALID = "INVALID"


@_dataclass(frozen=True, slots=True)
class NonProductionApplicationOperationSelectionResult:
    status: NonProductionApplicationOperationSelectionStatus
    selected_application_operation: _NonProductionApplicationOperation | None = None


def resolve_non_production_application_operation_selection(
    *,
    protected_operation: object,
) -> NonProductionApplicationOperationSelectionResult:
    if type(protected_operation) is not NonProductionProtectedApplicationOperation:
        return _invalid_selection()

    if (
        protected_operation
        is NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
    ):
        return NonProductionApplicationOperationSelectionResult(
            status=NonProductionApplicationOperationSelectionStatus.READY,
            selected_application_operation=(
                _NonProductionApplicationOperation.SUBMIT_ASSESSMENT
            ),
        )

    return _invalid_selection()


def _invalid_selection() -> NonProductionApplicationOperationSelectionResult:
    return NonProductionApplicationOperationSelectionResult(
        status=NonProductionApplicationOperationSelectionStatus.INVALID,
        selected_application_operation=None,
    )
