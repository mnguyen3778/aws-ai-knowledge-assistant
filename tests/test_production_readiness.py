import sys
import unittest
from dataclasses import FrozenInstanceError
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
    ProviderIdentifier,
    ProviderSelectionConfig,
    RuntimeCompositionRoot,
    RuntimeConfiguration,
    RuntimeResponse,
)
from assistant_runtime.readiness import (  # noqa: E402
    RuntimeReadinessResult,
    RuntimeReadinessStatus,
    validate_runtime_provider_readiness,
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


class StaticConfigurationLoader:
    def __init__(self, configuration):
        self.configuration = configuration

    def load(self):
        return self.configuration


class RaisingProviderSelectionService:
    def select_provider(self, configuration):
        raise RuntimeError("provider unavailable")


class InvalidProviderSelectionService:
    def select_provider(self, configuration):
        return object()


class RecordingProviderSelectionService:
    def __init__(self, provider):
        self.provider = provider

    def select_provider(self, configuration):
        return self.provider


class ReadyProvider:
    def execute(self, context):
        return RuntimeResponse(
            message=Message(
                role="assistant",
                content=DETERMINISTIC_ASSISTANT_MESSAGE,
            )
        )


class ProductionReadinessTests(unittest.TestCase):
    def test_runtime_readiness_result_is_immutable(self):
        result = RuntimeReadinessResult(
            readiness_status=RuntimeReadinessStatus.READY,
            selected_provider=ProviderIdentifier.DETERMINISTIC,
            configuration_valid=True,
            provider_initialized=True,
            deterministic_fallback_applied=False,
            diagnostic_messages=["ready"],
        )

        self.assertEqual(result.diagnostic_messages, ("ready",))
        with self.assertRaises(FrozenInstanceError):
            result.readiness_status = RuntimeReadinessStatus.DEGRADED

    def test_ready_provider_passes_provider_readiness_validation(self):
        ready, diagnostic = validate_runtime_provider_readiness(ReadyProvider())

        self.assertTrue(ready)
        self.assertEqual(
            diagnostic,
            "Runtime provider readiness validation succeeded.",
        )

    def test_provider_without_execute_fails_provider_readiness_validation(self):
        ready, diagnostic = validate_runtime_provider_readiness(object())

        self.assertFalse(ready)
        self.assertEqual(
            diagnostic,
            "Runtime provider readiness validation failed.",
        )

    def test_default_startup_records_ready_deterministic_readiness(self):
        composition_root = RuntimeCompositionRoot(
            configuration_loader=StaticConfigurationLoader(RuntimeConfiguration()),
            provider_selection_service=RecordingProviderSelectionService(
                ReadyProvider(),
            ),
        )

        dispatcher = composition_root.initialize()
        response = dispatcher.dispatch(valid_contract_request())
        result = composition_root._readiness_result

        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)
        self.assertEqual(result.readiness_status, RuntimeReadinessStatus.READY)
        self.assertEqual(result.selected_provider, ProviderIdentifier.DETERMINISTIC)
        self.assertTrue(result.configuration_valid)
        self.assertTrue(result.provider_initialized)
        self.assertFalse(result.deterministic_fallback_applied)

    def test_provider_initialization_failure_fails_closed_to_deterministic(self):
        composition_root = RuntimeCompositionRoot(
            configuration_loader=StaticConfigurationLoader(
                RuntimeConfiguration(
                    provider_selection=ProviderSelectionConfig(
                        provider=ProviderIdentifier.BEDROCK,
                    )
                )
            ),
            provider_selection_service=RaisingProviderSelectionService(),
        )

        dispatcher = composition_root.initialize()
        response = dispatcher.dispatch(valid_contract_request())
        result = composition_root._readiness_result

        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)
        self.assertEqual(result.readiness_status, RuntimeReadinessStatus.DEGRADED)
        self.assertEqual(result.selected_provider, ProviderIdentifier.DETERMINISTIC)
        self.assertTrue(result.configuration_valid)
        self.assertFalse(result.provider_initialized)
        self.assertTrue(result.deterministic_fallback_applied)
        self.assertIn(
            (
                "Runtime provider initialization failed; "
                "deterministic fallback applied."
            ),
            result.diagnostic_messages,
        )

    def test_provider_readiness_failure_fails_closed_to_deterministic(self):
        composition_root = RuntimeCompositionRoot(
            configuration_loader=StaticConfigurationLoader(
                RuntimeConfiguration(
                    provider_selection=ProviderSelectionConfig(
                        provider=ProviderIdentifier.BEDROCK,
                    )
                )
            ),
            provider_selection_service=InvalidProviderSelectionService(),
        )

        dispatcher = composition_root.initialize()
        response = dispatcher.dispatch(valid_contract_request())
        result = composition_root._readiness_result

        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)
        self.assertEqual(result.readiness_status, RuntimeReadinessStatus.DEGRADED)
        self.assertEqual(result.selected_provider, ProviderIdentifier.DETERMINISTIC)
        self.assertFalse(result.provider_initialized)
        self.assertTrue(result.deterministic_fallback_applied)
        self.assertIn(
            "Runtime provider readiness validation failed.",
            result.diagnostic_messages,
        )

    def test_invalid_configuration_result_fails_closed_to_deterministic(self):
        composition_root = RuntimeCompositionRoot(
            configuration_loader=StaticConfigurationLoader(object()),
            provider_selection_service=RecordingProviderSelectionService(
                ReadyProvider(),
            ),
        )

        dispatcher = composition_root.initialize()
        response = dispatcher.dispatch(valid_contract_request())
        result = composition_root._readiness_result

        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)
        self.assertEqual(result.readiness_status, RuntimeReadinessStatus.DEGRADED)
        self.assertEqual(result.selected_provider, ProviderIdentifier.DETERMINISTIC)
        self.assertFalse(result.configuration_valid)
        self.assertTrue(result.provider_initialized)
        self.assertTrue(result.deterministic_fallback_applied)
        self.assertIn(
            "Runtime configuration validation failed.",
            result.diagnostic_messages,
        )
        self.assertIn(
            "Invalid runtime configuration; deterministic fallback applied.",
            result.diagnostic_messages,
        )


if __name__ == "__main__":
    unittest.main()
