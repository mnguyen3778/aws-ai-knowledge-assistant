import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assistant_runtime import (  # noqa: E402
    BedrockProviderConfig,
    BedrockRuntimeProvider,
    DeterministicRuntimeProvider,
    ProviderIdentifier,
    ProviderRegistry,
    ProviderSelectionConfig,
    ProviderSelectionService,
    RuntimeResponse,
    create_default_provider_registry,
    create_default_runtime_dispatcher,
    resolve_provider_selection_config,
)
from assistant_contract.v1 import (  # noqa: E402
    CONTRACT_VERSION,
    CorrelationId,
    KnowledgeAssistantRequest,
    Message,
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


class FakeProvider:
    def execute(self, context):
        return RuntimeResponse(
            message=Message(
                role="assistant",
                content="fake response",
            )
        )


class ProviderSelectionTests(unittest.TestCase):
    def test_provider_identifiers_are_centralized(self):
        self.assertEqual(ProviderIdentifier.DETERMINISTIC.value, "deterministic")
        self.assertEqual(ProviderIdentifier.BEDROCK.value, "bedrock")
        self.assertIs(
            ProviderIdentifier.from_value("deterministic"),
            ProviderIdentifier.DETERMINISTIC,
        )
        self.assertIs(
            ProviderIdentifier.from_value("bedrock"),
            ProviderIdentifier.BEDROCK,
        )

    def test_provider_selection_defaults_to_deterministic_provider(self):
        service = ProviderSelectionService()

        provider = service.select_provider()

        self.assertIsInstance(provider, DeterministicRuntimeProvider)

    def test_default_runtime_dispatcher_remains_deterministic(self):
        dispatcher = create_default_runtime_dispatcher()
        request = KnowledgeAssistantRequest(
            contractVersion=CONTRACT_VERSION,
            correlationId=CorrelationId("web-req-001"),
            messages=[
                Message(
                    role="user",
                    content="What is Amazon Cognito?",
                )
            ],
        )

        response = dispatcher.dispatch(request)

        self.assertEqual(
            response.message.content,
            "AI Knowledge Assistant v1 contract request accepted.",
        )

    def test_resolves_explicit_bedrock_selection_config(self):
        config = resolve_provider_selection_config(
            {
                "provider": ProviderIdentifier.BEDROCK.value,
                ProviderIdentifier.BEDROCK.value: {
                    "model_id": "test-model",
                    "region_name": "us-west-2",
                },
            }
        )

        self.assertEqual(config.provider, ProviderIdentifier.BEDROCK)
        self.assertEqual(config.bedrock.model_id, "test-model")
        self.assertEqual(config.bedrock.region_name, "us-west-2")

    def test_bedrock_selection_uses_registered_factory(self):
        registry = ProviderRegistry()
        registry.register(
            ProviderIdentifier.BEDROCK,
            lambda config: BedrockRuntimeProvider(
                client=FakeBedrockClient(),
                config=config.bedrock,
            ),
        )
        service = ProviderSelectionService(registry=registry)

        provider = service.select_provider(
            ProviderSelectionConfig(
                provider=ProviderIdentifier.BEDROCK,
                bedrock=BedrockProviderConfig(model_id="test-model"),
            )
        )

        self.assertIsInstance(provider, BedrockRuntimeProvider)

    def test_invalid_provider_identifier_falls_back_to_deterministic(self):
        service = ProviderSelectionService()

        provider = service.select_provider(
            {
                "provider": "unknown",
            }
        )

        self.assertIsInstance(provider, DeterministicRuntimeProvider)

    def test_invalid_bedrock_configuration_falls_back_to_deterministic(self):
        service = ProviderSelectionService()

        provider = service.select_provider(
            {
                "provider": ProviderIdentifier.BEDROCK.value,
                ProviderIdentifier.BEDROCK.value: {
                    "model_id": "",
                    "region_name": "us-east-2",
                },
            }
        )

        self.assertIsInstance(provider, DeterministicRuntimeProvider)

    def test_unregistered_provider_falls_back_to_deterministic(self):
        service = ProviderSelectionService(registry=ProviderRegistry())

        provider = service.select_provider(
            ProviderSelectionConfig(
                provider=ProviderIdentifier.BEDROCK,
                bedrock=BedrockProviderConfig(),
            )
        )

        self.assertIsInstance(provider, DeterministicRuntimeProvider)

    def test_default_registry_registers_known_provider_identifiers(self):
        registry = create_default_provider_registry()

        self.assertIn(ProviderIdentifier.DETERMINISTIC, registry.providers)
        self.assertIn(ProviderIdentifier.BEDROCK, registry.providers)


if __name__ == "__main__":
    unittest.main()
