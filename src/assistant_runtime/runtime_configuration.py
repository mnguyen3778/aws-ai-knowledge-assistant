import os
from dataclasses import dataclass, field
from typing import Mapping

from assistant_runtime.config import BedrockProviderConfig
from assistant_runtime.provider_selection import (
    ProviderIdentifier,
    ProviderSelectionConfig,
    resolve_provider_selection_config,
)


RUNTIME_PROVIDER_ENV = "AI_KNOWLEDGE_ASSISTANT_RUNTIME_PROVIDER"
BEDROCK_MODEL_ID_ENV = "AI_KNOWLEDGE_ASSISTANT_BEDROCK_MODEL_ID"
BEDROCK_REGION_ENV = "AI_KNOWLEDGE_ASSISTANT_BEDROCK_REGION"


@dataclass(frozen=True)
class RuntimeConfiguration:
    provider_selection: ProviderSelectionConfig = field(
        default_factory=ProviderSelectionConfig,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provider_selection",
            resolve_provider_selection_config(self.provider_selection),
        )


class RuntimeConfigurationLoader:
    def __init__(self, environment: Mapping[str, str] | None = None):
        self._environment = environment
        self._configuration: RuntimeConfiguration | None = None

    def load(self) -> RuntimeConfiguration:
        if self._configuration is None:
            self._configuration = _runtime_configuration_from_environment(
                os.environ if self._environment is None else self._environment,
            )

        return self._configuration


def load_runtime_configuration(
    environment: Mapping[str, str] | None = None,
) -> RuntimeConfiguration:
    return RuntimeConfigurationLoader(environment=environment).load()


def validate_runtime_configuration(value: object) -> RuntimeConfiguration:
    if isinstance(value, RuntimeConfiguration):
        return value

    return RuntimeConfiguration()


def _runtime_configuration_from_environment(
    environment: Mapping[str, str],
) -> RuntimeConfiguration:
    provider = environment.get(RUNTIME_PROVIDER_ENV)
    if provider is None:
        return RuntimeConfiguration()

    raw_config: dict[str, object] = {
        "provider": provider,
    }

    if ProviderIdentifier.from_value(provider) is ProviderIdentifier.BEDROCK:
        raw_config[ProviderIdentifier.BEDROCK.value] = {
            "model_id": environment.get(
                BEDROCK_MODEL_ID_ENV,
                BedrockProviderConfig().model_id,
            ),
            "region_name": environment.get(
                BEDROCK_REGION_ENV,
                BedrockProviderConfig().region_name,
            ),
        }

    return RuntimeConfiguration(
        provider_selection=resolve_provider_selection_config(raw_config),
    )
