import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assistant_runtime import (  # noqa: E402
    BEDROCK_MODEL_ID_ENV,
    BEDROCK_REGION_ENV,
    RUNTIME_PROVIDER_ENV,
    BedrockProviderConfig,
    BedrockRuntimeProvider,
    DeterministicRuntimeProvider,
    ProviderIdentifier,
    ProviderRegistry,
    ProviderSelectionConfig,
    ProviderSelectionService,
    RuntimeConfiguration,
    RuntimeConfigurationLoader,
    load_runtime_configuration,
    validate_runtime_configuration,
)


class FakeBedrockClient:
    def converse(self, **kwargs):
        return {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": "bedrock response",
                        }
                    ]
                }
            }
        }


class RuntimeConfigurationTests(unittest.TestCase):
    def test_runtime_configuration_is_immutable(self):
        configuration = RuntimeConfiguration()

        with self.assertRaises(FrozenInstanceError):
            configuration.provider_selection = ProviderSelectionConfig(
                provider=ProviderIdentifier.BEDROCK,
            )

    def test_missing_environment_defaults_to_deterministic_provider(self):
        configuration = load_runtime_configuration(environment={})

        self.assertEqual(
            configuration.provider_selection.provider,
            ProviderIdentifier.DETERMINISTIC,
        )

    def test_invalid_provider_environment_fails_closed_to_deterministic(self):
        configuration = load_runtime_configuration(
            environment={
                RUNTIME_PROVIDER_ENV: "unknown-provider",
            }
        )

        self.assertEqual(
            configuration.provider_selection.provider,
            ProviderIdentifier.DETERMINISTIC,
        )

    def test_valid_bedrock_environment_resolves_provider_configuration(self):
        configuration = load_runtime_configuration(
            environment={
                RUNTIME_PROVIDER_ENV: ProviderIdentifier.BEDROCK.value,
                BEDROCK_MODEL_ID_ENV: "test-model",
                BEDROCK_REGION_ENV: "us-west-2",
            }
        )

        self.assertEqual(
            configuration.provider_selection.provider,
            ProviderIdentifier.BEDROCK,
        )
        self.assertEqual(configuration.provider_selection.bedrock.model_id, "test-model")
        self.assertEqual(
            configuration.provider_selection.bedrock.region_name,
            "us-west-2",
        )

    def test_invalid_bedrock_environment_fails_closed_to_deterministic(self):
        configuration = load_runtime_configuration(
            environment={
                RUNTIME_PROVIDER_ENV: ProviderIdentifier.BEDROCK.value,
                BEDROCK_MODEL_ID_ENV: "",
                BEDROCK_REGION_ENV: "us-east-2",
            }
        )

        self.assertEqual(
            configuration.provider_selection.provider,
            ProviderIdentifier.DETERMINISTIC,
        )

    def test_runtime_configuration_loader_reads_environment_once(self):
        environment = {
            RUNTIME_PROVIDER_ENV: ProviderIdentifier.DETERMINISTIC.value,
        }
        loader = RuntimeConfigurationLoader(environment=environment)

        first_configuration = loader.load()
        environment[RUNTIME_PROVIDER_ENV] = ProviderIdentifier.BEDROCK.value
        second_configuration = loader.load()

        self.assertIs(first_configuration, second_configuration)
        self.assertEqual(
            second_configuration.provider_selection.provider,
            ProviderIdentifier.DETERMINISTIC,
        )

    def test_provider_selection_service_consumes_runtime_configuration(self):
        registry = ProviderRegistry()
        registry.register(
            ProviderIdentifier.BEDROCK,
            lambda config: BedrockRuntimeProvider(
                client=FakeBedrockClient(),
                config=config.bedrock,
            ),
        )
        service = ProviderSelectionService(registry=registry)
        configuration = RuntimeConfiguration(
            provider_selection=ProviderSelectionConfig(
                provider=ProviderIdentifier.BEDROCK,
                bedrock=BedrockProviderConfig(model_id="test-model"),
            )
        )

        provider = service.select_provider(configuration)

        self.assertIsInstance(provider, BedrockRuntimeProvider)

    def test_invalid_runtime_configuration_input_validates_to_default(self):
        configuration = validate_runtime_configuration(object())

        self.assertEqual(
            configuration.provider_selection.provider,
            ProviderIdentifier.DETERMINISTIC,
        )

    def test_invalid_runtime_configuration_model_fails_closed(self):
        configuration = RuntimeConfiguration(
            provider_selection=ProviderSelectionConfig(
                provider="bedrock",
                bedrock=BedrockProviderConfig(model_id="test-model"),
            )
        )
        service = ProviderSelectionService()

        provider = service.select_provider(configuration)

        self.assertIsInstance(provider, DeterministicRuntimeProvider)


if __name__ == "__main__":
    unittest.main()
