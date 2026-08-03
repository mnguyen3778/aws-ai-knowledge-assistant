from assistant_runtime.dispatcher import RuntimeDispatcher
from assistant_runtime.provider import DeterministicRuntimeProvider
from assistant_runtime.provider_selection import (
    ProviderIdentifier,
    ProviderSelectionService,
)
from assistant_runtime.readiness import (
    RuntimeReadinessResult,
    RuntimeReadinessStatus,
    validate_runtime_provider_readiness,
)
from assistant_runtime.runtime_configuration import (
    RuntimeConfiguration,
    RuntimeConfigurationLoader,
    validate_runtime_configuration,
)


class RuntimeCompositionRoot:
    def __init__(
        self,
        configuration_loader: RuntimeConfigurationLoader,
        provider_selection_service: ProviderSelectionService,
    ):
        self._configuration_loader = configuration_loader
        self._provider_selection_service = provider_selection_service
        self._runtime_dispatcher: RuntimeDispatcher | None = None
        self._readiness_result: RuntimeReadinessResult | None = None

    def initialize(self) -> RuntimeDispatcher:
        if self._runtime_dispatcher is None:
            loaded_configuration = self._configuration_loader.load()
            configuration_valid = isinstance(
                loaded_configuration,
                RuntimeConfiguration,
            )
            configuration = validate_runtime_configuration(loaded_configuration)
            requested_provider = configuration.provider_selection.provider
            diagnostics = [
                (
                    "Runtime configuration validation succeeded."
                    if configuration_valid
                    else "Runtime configuration validation failed."
                )
            ]

            provider_initialized = True
            deterministic_fallback_applied = False

            try:
                provider = self._provider_selection_service.select_provider(
                    configuration,
                )
            except Exception:
                provider = DeterministicRuntimeProvider()
                provider_initialized = False
                deterministic_fallback_applied = True
                diagnostics.append(
                    "Runtime provider initialization failed; "
                    "deterministic fallback applied."
                )

            provider_ready, provider_diagnostic = validate_runtime_provider_readiness(
                provider,
            )
            diagnostics.append(provider_diagnostic)

            if not configuration_valid:
                provider = DeterministicRuntimeProvider()
                deterministic_fallback_applied = True
                diagnostics.append(
                    "Invalid runtime configuration; "
                    "deterministic fallback applied."
                )
            elif not provider_ready:
                provider = DeterministicRuntimeProvider()
                provider_initialized = False
                deterministic_fallback_applied = True
                diagnostics.append(
                    "Runtime provider readiness failed; "
                    "deterministic fallback applied."
                )

            if (
                requested_provider is not ProviderIdentifier.DETERMINISTIC
                and isinstance(provider, DeterministicRuntimeProvider)
            ):
                deterministic_fallback_applied = True

            selected_provider = (
                ProviderIdentifier.DETERMINISTIC
                if deterministic_fallback_applied
                else requested_provider
            )
            readiness_status = (
                RuntimeReadinessStatus.DEGRADED
                if (
                    deterministic_fallback_applied
                    or not configuration_valid
                    or not provider_initialized
                )
                else RuntimeReadinessStatus.READY
            )
            self._readiness_result = RuntimeReadinessResult(
                readiness_status=readiness_status,
                selected_provider=selected_provider,
                configuration_valid=configuration_valid,
                provider_initialized=provider_initialized,
                deterministic_fallback_applied=deterministic_fallback_applied,
                diagnostic_messages=tuple(diagnostics),
            )
            self._runtime_dispatcher = RuntimeDispatcher(provider=provider)

        return self._runtime_dispatcher


def create_runtime_composition_root(
    configuration_loader: RuntimeConfigurationLoader | None = None,
    provider_selection_service: ProviderSelectionService | None = None,
) -> RuntimeCompositionRoot:
    return RuntimeCompositionRoot(
        configuration_loader=configuration_loader or RuntimeConfigurationLoader(),
        provider_selection_service=(
            provider_selection_service or ProviderSelectionService()
        ),
    )
