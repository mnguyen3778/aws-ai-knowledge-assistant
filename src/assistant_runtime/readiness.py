from dataclasses import dataclass, field
from enum import Enum

from assistant_runtime.provider_selection import ProviderIdentifier


class RuntimeReadinessStatus(Enum):
    READY = "ready"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class RuntimeReadinessResult:
    readiness_status: RuntimeReadinessStatus
    selected_provider: ProviderIdentifier
    configuration_valid: bool
    provider_initialized: bool
    deterministic_fallback_applied: bool
    diagnostic_messages: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "diagnostic_messages",
            tuple(self.diagnostic_messages),
        )


def validate_runtime_provider_readiness(provider: object) -> tuple[bool, str]:
    if callable(getattr(provider, "execute", None)):
        return True, "Runtime provider readiness validation succeeded."

    return False, "Runtime provider readiness validation failed."
