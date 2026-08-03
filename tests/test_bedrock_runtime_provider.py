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
    BEDROCK_PROVIDER_ERROR_MESSAGE,
    BedrockProviderConfig,
    BedrockRuntimeProvider,
    RuntimeRequestContext,
    create_bedrock_runtime_provider,
)


def runtime_context():
    return RuntimeRequestContext(
        contract_request=KnowledgeAssistantRequest(
            contractVersion=CONTRACT_VERSION,
            correlationId=CorrelationId("web-req-001"),
            messages=[
                Message(
                    role="user",
                    content="What is Amazon Cognito?",
                )
            ],
        )
    )


class FakeBedrockClient:
    def __init__(self, response=None, error=None):
        self.calls = []
        self.response = response or {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": "Amazon Cognito manages user identity.",
                        }
                    ]
                }
            }
        }
        self.error = error

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error

        return self.response


class BedrockRuntimeProviderTests(unittest.TestCase):
    def test_provider_maps_runtime_request_to_bedrock_converse_request(self):
        client = FakeBedrockClient()
        provider = BedrockRuntimeProvider(
            client=client,
            config=BedrockProviderConfig(model_id="test-model"),
        )

        response = provider.execute(runtime_context())

        self.assertEqual(
            client.calls,
            [
                {
                    "modelId": "test-model",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": "What is Amazon Cognito?",
                                }
                            ],
                        }
                    ],
                }
            ],
        )
        self.assertEqual(response.message.role, "assistant")
        self.assertEqual(
            response.message.content,
            "Amazon Cognito manages user identity.",
        )

    def test_factory_registers_bedrock_provider_with_injected_client(self):
        client = FakeBedrockClient()

        provider = create_bedrock_runtime_provider(
            config=BedrockProviderConfig(model_id="test-model"),
            client=client,
        )
        response = provider.execute(runtime_context())

        self.assertIsInstance(provider, BedrockRuntimeProvider)
        self.assertEqual(client.calls[0]["modelId"], "test-model")
        self.assertEqual(
            response.message.content,
            "Amazon Cognito manages user identity.",
        )

    def test_provider_maps_malformed_bedrock_response_to_deterministic_error(self):
        client = FakeBedrockClient(response={"output": {"message": {"content": []}}})
        provider = BedrockRuntimeProvider(
            client=client,
            config=BedrockProviderConfig(),
        )

        response = provider.execute(runtime_context())

        self.assertEqual(response.message.role, "assistant")
        self.assertEqual(response.message.content, BEDROCK_PROVIDER_ERROR_MESSAGE)

    def test_provider_maps_blank_bedrock_text_to_deterministic_error(self):
        client = FakeBedrockClient(
            response={
                "output": {
                    "message": {
                        "content": [
                            {
                                "text": "   ",
                            }
                        ]
                    }
                }
            }
        )
        provider = BedrockRuntimeProvider(
            client=client,
            config=BedrockProviderConfig(),
        )

        response = provider.execute(runtime_context())

        self.assertEqual(response.message.content, BEDROCK_PROVIDER_ERROR_MESSAGE)

    def test_provider_maps_client_exception_to_deterministic_error(self):
        client = FakeBedrockClient(error=RuntimeError("bedrock unavailable"))
        provider = BedrockRuntimeProvider(
            client=client,
            config=BedrockProviderConfig(),
        )

        first_response = provider.execute(runtime_context())
        second_response = provider.execute(runtime_context())

        self.assertEqual(first_response, second_response)
        self.assertEqual(
            first_response.message.content,
            BEDROCK_PROVIDER_ERROR_MESSAGE,
        )

    def test_provider_config_defaults_are_explicit(self):
        config = BedrockProviderConfig()

        self.assertEqual(config.model_id, "amazon.nova-lite-v1:0")
        self.assertEqual(config.region_name, "us-east-2")


if __name__ == "__main__":
    unittest.main()
