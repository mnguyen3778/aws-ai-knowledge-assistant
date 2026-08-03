from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from assistant_runtime.config import BedrockProviderConfig
from assistant_runtime.factory import create_bedrock_runtime_provider
from assistant_runtime.provider import (
    DeterministicRuntimeProvider,
    RuntimeProvider,
)


class ProviderIdentifier(Enum):
    DETERMINISTIC = "deterministic"
    BEDROCK = "bedrock"

    @classmethod
    def from_value(cls, value: Any) -> "ProviderIdentifier | None":
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            return None

        for identifier in cls:
            if value == identifier.value:
                return identifier

        return None


@dataclass(frozen=True)
class ProviderSelectionConfig:
    provider: ProviderIdentifier = ProviderIdentifier.DETERMINISTIC
    bedrock: BedrockProviderConfig = field(default_factory=BedrockProviderConfig)


ProviderFactory = Callable[[ProviderSelectionConfig], RuntimeProvider]


class ProviderRegistry:
    def __init__(
        self,
        factories: Mapping[ProviderIdentifier, ProviderFactory] | None = None,
    ):
        self._factories = dict(factories or {})

    def register(
        self,
        provider: ProviderIdentifier,
        factory: ProviderFactory,
    ) -> None:
        self._factories[provider] = factory

    def create(
        self,
        config: ProviderSelectionConfig,
    ) -> RuntimeProvider | None:
        factory = self._factories.get(config.provider)
        if factory is None:
            return None

        return factory(config)

    @property
    def providers(self) -> Mapping[ProviderIdentifier, ProviderFactory]:
        return MappingProxyType(self._factories)


class ProviderSelectionService:
    def __init__(
        self,
        registry: ProviderRegistry | None = None,
    ):
        self._registry = registry or create_default_provider_registry()

    def select_provider(
        self,
        raw_config: Any = None,
    ) -> RuntimeProvider:
        config = resolve_provider_selection_config(raw_config)
        provider = self._registry.create(config)

        if provider is None:
            return DeterministicRuntimeProvider()

        return provider


def create_default_provider_registry() -> ProviderRegistry:
    return ProviderRegistry(
        {
            ProviderIdentifier.DETERMINISTIC: (
                lambda config: DeterministicRuntimeProvider()
            ),
            ProviderIdentifier.BEDROCK: (
                lambda config: create_bedrock_runtime_provider(config.bedrock)
            ),
        }
    )


def resolve_provider_selection_config(
    raw_config: Any,
) -> ProviderSelectionConfig:
    if raw_config is None:
        return ProviderSelectionConfig()

    runtime_provider_selection = getattr(raw_config, "provider_selection", None)
    if isinstance(runtime_provider_selection, ProviderSelectionConfig):
        return resolve_provider_selection_config(runtime_provider_selection)

    if isinstance(raw_config, ProviderSelectionConfig):
        if _is_valid_provider_selection_config(raw_config):
            return raw_config

        return ProviderSelectionConfig()

    if not isinstance(raw_config, Mapping):
        return ProviderSelectionConfig()

    provider = ProviderIdentifier.from_value(raw_config.get("provider"))
    if provider is None:
        return ProviderSelectionConfig()

    bedrock_config = BedrockProviderConfig()
    if provider is ProviderIdentifier.BEDROCK:
        raw_bedrock_config = raw_config.get(ProviderIdentifier.BEDROCK.value, {})
        bedrock_config = _resolve_bedrock_config(raw_bedrock_config)
        if bedrock_config is None:
            return ProviderSelectionConfig()

    return ProviderSelectionConfig(
        provider=provider,
        bedrock=bedrock_config,
    )


def _resolve_bedrock_config(raw_config: Any) -> BedrockProviderConfig | None:
    if raw_config is None:
        return BedrockProviderConfig()

    if isinstance(raw_config, BedrockProviderConfig):
        if _is_valid_bedrock_config(raw_config):
            return raw_config

        return None

    if not isinstance(raw_config, Mapping):
        return None

    default_bedrock_config = BedrockProviderConfig()
    config = BedrockProviderConfig(
        model_id=raw_config.get("model_id", default_bedrock_config.model_id),
        region_name=raw_config.get(
            "region_name",
            default_bedrock_config.region_name,
        ),
    )
    if not _is_valid_bedrock_config(config):
        return None

    return config


def _is_valid_provider_selection_config(config: ProviderSelectionConfig) -> bool:
    if not isinstance(config.provider, ProviderIdentifier):
        return False

    if config.provider is ProviderIdentifier.BEDROCK:
        return _is_valid_bedrock_config(config.bedrock)

    return config.provider is ProviderIdentifier.DETERMINISTIC


def _is_valid_bedrock_config(config: BedrockProviderConfig) -> bool:
    return (
        isinstance(config.model_id, str)
        and bool(config.model_id.strip())
        and isinstance(config.region_name, str)
        and bool(config.region_name.strip())
    )
