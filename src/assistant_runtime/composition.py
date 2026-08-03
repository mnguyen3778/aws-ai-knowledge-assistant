from assistant_runtime.dispatcher import RuntimeDispatcher
from assistant_runtime.provider_selection import ProviderSelectionService
from assistant_runtime.runtime_configuration import (
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

    def initialize(self) -> RuntimeDispatcher:
        if self._runtime_dispatcher is None:
            configuration = validate_runtime_configuration(
                self._configuration_loader.load(),
            )
            provider = self._provider_selection_service.select_provider(
                configuration,
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
