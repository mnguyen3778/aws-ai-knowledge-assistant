import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assistant_contract.v1 import (  # noqa: E402
    CONTRACT_VERSION,
    CorrelationId,
    KnowledgeAssistantRequest,
    Message,
)
from assistant_runtime import (  # noqa: E402
    DETERMINISTIC_ASSISTANT_MESSAGE,
    BedrockProviderConfig,
    DeterministicRuntimeProvider,
    ProviderIdentifier,
    ProviderSelectionConfig,
    RuntimeCompositionRoot,
    RuntimeConfiguration,
    RuntimeResponse,
    create_default_runtime_dispatcher,
    create_runtime_composition_root,
)


def valid_contract_request():
    return KnowledgeAssistantRequest(
        contractVersion=CONTRACT_VERSION,
        correlationId=CorrelationId("web-req-001"),
        messages=[
            Message(
                role="user",
                content="What is Amazon Cognito?",
            )
        ],
    )


class RecordingConfigurationLoader:
    def __init__(self, configuration):
        self.configuration = configuration
        self.load_count = 0

    def load(self):
        self.load_count += 1
        return self.configuration


class RecordingProviderSelectionService:
    def __init__(self, provider):
        self.provider = provider
        self.configurations = []

    def select_provider(self, configuration):
        self.configurations.append(configuration)
        return self.provider


class RecordingProvider:
    def __init__(self):
        self.contexts = []

    def execute(self, context):
        self.contexts.append(context)
        return RuntimeResponse(
            message=Message(
                role="assistant",
                content=DETERMINISTIC_ASSISTANT_MESSAGE,
            )
        )


class RuntimeActivationTests(unittest.TestCase):
    def test_composition_root_initializes_runtime_once(self):
        provider = RecordingProvider()
        configuration = RuntimeConfiguration()
        configuration_loader = RecordingConfigurationLoader(configuration)
        provider_selection_service = RecordingProviderSelectionService(provider)
        composition_root = RuntimeCompositionRoot(
            configuration_loader=configuration_loader,
            provider_selection_service=provider_selection_service,
        )

        first_dispatcher = composition_root.initialize()
        second_dispatcher = composition_root.initialize()

        self.assertIs(first_dispatcher, second_dispatcher)
        self.assertEqual(configuration_loader.load_count, 1)
        self.assertEqual(provider_selection_service.configurations, [configuration])

    def test_composition_root_wires_selected_provider_into_dispatcher(self):
        provider = RecordingProvider()
        composition_root = RuntimeCompositionRoot(
            configuration_loader=RecordingConfigurationLoader(RuntimeConfiguration()),
            provider_selection_service=RecordingProviderSelectionService(provider),
        )

        dispatcher = composition_root.initialize()
        response = dispatcher.dispatch(valid_contract_request())

        self.assertEqual(len(provider.contexts), 1)
        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)

    def test_invalid_runtime_configuration_fails_closed_to_deterministic(self):
        configuration_loader = RecordingConfigurationLoader(
            RuntimeConfiguration(
                provider_selection=ProviderSelectionConfig(
                    provider="bedrock",
                    bedrock=BedrockProviderConfig(model_id="test-model"),
                )
            )
        )
        composition_root = create_runtime_composition_root(
            configuration_loader=configuration_loader,
        )

        dispatcher = composition_root.initialize()
        response = dispatcher.dispatch(valid_contract_request())

        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)

    def test_default_runtime_dispatcher_still_uses_deterministic_provider(self):
        dispatcher = create_default_runtime_dispatcher()

        response = dispatcher.dispatch(valid_contract_request())

        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)

    def test_composition_root_factory_accepts_constructor_injection(self):
        provider = DeterministicRuntimeProvider()
        composition_root = create_runtime_composition_root(
            configuration_loader=RecordingConfigurationLoader(
                RuntimeConfiguration(
                    provider_selection=ProviderSelectionConfig(
                        provider=ProviderIdentifier.DETERMINISTIC,
                    )
                )
            ),
            provider_selection_service=RecordingProviderSelectionService(provider),
        )

        dispatcher = composition_root.initialize()
        response = dispatcher.dispatch(valid_contract_request())

        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)


if __name__ == "__main__":
    unittest.main()
