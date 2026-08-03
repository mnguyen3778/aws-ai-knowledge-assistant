import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assistant_contract import (  # noqa: E402
    CONTRACT_VERSION,
    SERVICE_NAME,
    ConversationId,
    CorrelationId,
    ErrorDetail,
    ErrorResponse,
    KnowledgeAssistantRequest,
    KnowledgeAssistantResponse,
    Message,
    ServiceMetadata,
    contract_schema,
    dumps_contract_json,
    parse_contract_json,
    validate_error_response,
    validate_request,
    validate_success_response,
)
from assistant_contract.v1 import CONTRACT_VERSION as V1_CONTRACT_VERSION  # noqa: E402


def valid_request_payload():
    return {
        "contractVersion": CONTRACT_VERSION,
        "correlationId": "web-req-001",
        "conversationId": "conversation-001",
        "messages": [
            {
                "role": "user",
                "content": "What is Amazon Cognito?",
            }
        ],
    }


def valid_success_payload():
    return {
        "contractVersion": CONTRACT_VERSION,
        "correlationId": "web-req-001",
        "conversationId": "conversation-001",
        "message": {
            "role": "assistant",
            "content": "Amazon Cognito provides managed identity services.",
        },
        "service": {
            "name": SERVICE_NAME,
            "contractVersion": CONTRACT_VERSION,
        },
    }


def valid_error_payload():
    return {
        "contractVersion": CONTRACT_VERSION,
        "correlationId": "web-req-001",
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Request payload is invalid.",
            "details": [
                {
                    "field": "messages",
                    "message": "At least one message is required.",
                    "code": "REQUIRED",
                }
            ],
        },
        "service": {
            "name": SERVICE_NAME,
            "contractVersion": CONTRACT_VERSION,
        },
    }


class AssistantContractTests(unittest.TestCase):
    def test_valid_request_payload_creates_typed_model(self):
        request, errors = validate_request(valid_request_payload())

        self.assertEqual(errors, [])
        self.assertEqual(request.contractVersion, CONTRACT_VERSION)
        self.assertEqual(request.correlationId.value, "web-req-001")
        self.assertEqual(request.conversationId.value, "conversation-001")
        self.assertEqual(request.messages[0].role, "user")
        self.assertEqual(V1_CONTRACT_VERSION, CONTRACT_VERSION)

    def test_request_rejects_unknown_fields(self):
        payload = valid_request_payload()
        payload["prompt"] = "Do not infer alternate request shapes."

        request, errors = validate_request(payload)

        self.assertIsNone(request)
        self.assertEqual(errors[0].code, "UNKNOWN_FIELD")
        self.assertEqual(errors[0].field, "prompt")

    def test_request_rejects_unsupported_contract_version(self):
        payload = valid_request_payload()
        payload["contractVersion"] = "ai-knowledge-assistant-v2"

        request, errors = validate_request(payload)

        self.assertIsNone(request)
        self.assertEqual(errors[0].code, "UNSUPPORTED_VERSION")

    def test_request_rejects_non_user_messages(self):
        payload = valid_request_payload()
        payload["messages"][0]["role"] = "assistant"

        request, errors = validate_request(payload)

        self.assertIsNone(request)
        self.assertEqual(errors[0].field, "messages[0].role")

    def test_request_rejects_invalid_identifier(self):
        payload = valid_request_payload()
        payload["correlationId"] = "bad id with spaces"

        request, errors = validate_request(payload)

        self.assertIsNone(request)
        self.assertEqual(errors[0].field, "correlationId")

    def test_duplicate_json_fields_are_rejected(self):
        payload, errors = parse_contract_json(
            """
            {
              "contractVersion": "ai-knowledge-assistant-v1",
              "contractVersion": "ai-knowledge-assistant-v1"
            }
            """
        )

        self.assertIsNone(payload)
        self.assertEqual(errors[0].code, "DUPLICATE_FIELD")

    def test_valid_success_response_payload_creates_typed_model(self):
        response, errors = validate_success_response(valid_success_payload())

        self.assertEqual(errors, [])
        self.assertEqual(response.message.role, "assistant")
        self.assertEqual(response.service.name, SERVICE_NAME)

    def test_success_response_requires_service_metadata(self):
        payload = valid_success_payload()
        del payload["service"]

        response, errors = validate_success_response(payload)

        self.assertIsNone(response)
        self.assertEqual(errors[0].code, "REQUIRED")
        self.assertEqual(errors[0].field, "service")

    def test_valid_error_response_payload_creates_typed_model(self):
        response, errors = validate_error_response(valid_error_payload())

        self.assertEqual(errors, [])
        self.assertEqual(response.code, "VALIDATION_ERROR")
        self.assertEqual(response.details[0].field, "messages")

    def test_models_serialize_to_stable_wire_format(self):
        request = KnowledgeAssistantRequest(
            contractVersion=CONTRACT_VERSION,
            correlationId=CorrelationId("web-req-001"),
            conversationId=ConversationId("conversation-001"),
            messages=[
                Message(
                    role="user",
                    content="What is Amazon Cognito?",
                )
            ],
        )
        response = KnowledgeAssistantResponse(
            contractVersion=CONTRACT_VERSION,
            correlationId=CorrelationId("web-req-001"),
            conversationId=ConversationId("conversation-001"),
            message=Message(
                role="assistant",
                content="Amazon Cognito provides managed identity services.",
            ),
            service=ServiceMetadata(),
        )
        error = ErrorResponse(
            contractVersion=CONTRACT_VERSION,
            correlationId=CorrelationId("web-req-001"),
            message="Request payload is invalid.",
            details=[
                ErrorDetail(
                    field="messages",
                    message="At least one message is required.",
                    code="REQUIRED",
                )
            ],
            service=ServiceMetadata(),
        )

        self.assertEqual(request.to_dict(), valid_request_payload())
        self.assertEqual(response.to_dict(), valid_success_payload())
        self.assertEqual(error.to_dict(), valid_error_payload())

    def test_json_serialization_is_deterministic(self):
        payload = KnowledgeAssistantRequest(
            contractVersion=CONTRACT_VERSION,
            correlationId=CorrelationId("web-req-001"),
            messages=[
                Message(
                    role="user",
                    content="What is Amazon Cognito?",
                )
            ],
        )

        self.assertEqual(
            dumps_contract_json(payload),
            (
                '{"contractVersion":"ai-knowledge-assistant-v1",'
                '"correlationId":"web-req-001",'
                '"messages":[{"content":"What is Amazon Cognito?",'
                '"role":"user"}]}'
            ),
        )

    def test_schema_artifact_matches_exported_contract_schema(self):
        schema_path = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "contracts"
            / "ai-knowledge-assistant-v1.schema.json"
        )
        artifact = json.loads(schema_path.read_text())

        self.assertEqual(artifact, contract_schema())
        self.assertEqual(
            artifact["$defs"]["ContractVersion"]["const"],
            CONTRACT_VERSION,
        )
        self.assertEqual(
            artifact["$defs"]["ServiceMetadata"]["properties"]["name"]["const"],
            SERVICE_NAME,
        )


if __name__ == "__main__":
    unittest.main()
