import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assistant_contract.v1 import (  # noqa: E402
    CONTRACT_VERSION,
    ConversationId,
    CorrelationId,
    KnowledgeAssistantRequest,
    Message,
    validate_success_response,
)
from assistant_runtime import (  # noqa: E402
    DETERMINISTIC_ASSISTANT_MESSAGE,
    RuntimeDispatcher,
    RuntimeResponse,
    create_default_runtime_dispatcher,
)


def valid_contract_request(conversation_id=None):
    return KnowledgeAssistantRequest(
        contractVersion=CONTRACT_VERSION,
        correlationId=CorrelationId("web-req-001"),
        conversationId=conversation_id,
        messages=[
            Message(
                role="user",
                content="What is Amazon Cognito?",
            )
        ],
    )


class RecordingRuntimeProvider:
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


class AssistantRuntimeTests(unittest.TestCase):
    def test_default_runtime_dispatcher_returns_contract_response(self):
        dispatcher = create_default_runtime_dispatcher()

        response = dispatcher.dispatch(valid_contract_request())
        contract_response, errors = validate_success_response(response.to_dict())

        self.assertEqual(errors, [])
        self.assertEqual(contract_response.contractVersion, CONTRACT_VERSION)
        self.assertEqual(contract_response.correlationId.value, "web-req-001")
        self.assertEqual(contract_response.conversationId.value, "web-req-001")
        self.assertEqual(contract_response.message.role, "assistant")
        self.assertEqual(
            contract_response.message.content,
            DETERMINISTIC_ASSISTANT_MESSAGE,
        )

    def test_runtime_dispatcher_preserves_explicit_conversation_id(self):
        dispatcher = create_default_runtime_dispatcher()
        request = valid_contract_request(
            conversation_id=ConversationId("conversation-001"),
        )

        response = dispatcher.dispatch(request)

        self.assertEqual(response.conversationId.value, "conversation-001")

    def test_runtime_dispatcher_injects_provider_boundary(self):
        provider = RecordingRuntimeProvider()
        dispatcher = RuntimeDispatcher(provider=provider)
        request = valid_contract_request()

        response = dispatcher.dispatch(request)

        self.assertEqual(len(provider.contexts), 1)
        self.assertIs(provider.contexts[0].contract_request, request)
        self.assertEqual(provider.contexts[0].correlation_id.value, "web-req-001")
        self.assertEqual(provider.contexts[0].conversation_id.value, "web-req-001")
        self.assertEqual(response.message.content, DETERMINISTIC_ASSISTANT_MESSAGE)

    def test_runtime_dispatcher_is_deterministic(self):
        dispatcher = create_default_runtime_dispatcher()
        request = valid_contract_request()

        first_response = dispatcher.dispatch(request)
        second_response = dispatcher.dispatch(request)

        self.assertEqual(first_response, second_response)


if __name__ == "__main__":
    unittest.main()
