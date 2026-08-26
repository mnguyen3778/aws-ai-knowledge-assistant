from trusted_authorization.models import (
    RequestedAction,
    ResourceActionApplicability,
    ResourceClass,
)


APPLICABILITY_GOVERNANCE_VERSION = (
    "resource-action-applicability-governance-v1"
)


_APPLICABILITY_MATRIX: dict[
    ResourceClass,
    dict[RequestedAction, ResourceActionApplicability],
] = {
    ResourceClass.EXECUTIVE_DASHBOARD: {
        RequestedAction.VIEW: ResourceActionApplicability.APPLICABLE,
        RequestedAction.DOWNLOAD: ResourceActionApplicability.NOT_APPLICABLE,
        RequestedAction.SUBMIT: ResourceActionApplicability.NOT_APPLICABLE,
        RequestedAction.EXPLAIN: ResourceActionApplicability.APPLICABLE,
    },
    ResourceClass.REPORT: {
        RequestedAction.VIEW: ResourceActionApplicability.APPLICABLE,
        RequestedAction.DOWNLOAD: ResourceActionApplicability.APPLICABLE,
        RequestedAction.SUBMIT: ResourceActionApplicability.NOT_APPLICABLE,
        RequestedAction.EXPLAIN: ResourceActionApplicability.APPLICABLE,
    },
    ResourceClass.ASSESSMENT_SUBMISSION: {
        RequestedAction.VIEW: ResourceActionApplicability.NOT_APPLICABLE,
        RequestedAction.DOWNLOAD: ResourceActionApplicability.NOT_APPLICABLE,
        RequestedAction.SUBMIT: ResourceActionApplicability.APPLICABLE,
        RequestedAction.EXPLAIN: ResourceActionApplicability.NOT_APPLICABLE,
    },
}


def resolve_applicability(
    resource_class: ResourceClass,
    action: RequestedAction,
) -> ResourceActionApplicability:
    return _APPLICABILITY_MATRIX.get(resource_class, {}).get(
        action,
        ResourceActionApplicability.UNRESOLVED,
    )
