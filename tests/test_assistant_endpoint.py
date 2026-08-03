import importlib
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assistant_contract.v1 import (  # noqa: E402
    CONTRACT_VERSION,
    SERVICE_NAME,
    validate_error_response,
    validate_success_response,
)
from assistant_endpoint import handle_public_assistant_endpoint  # noqa: E402


def valid_endpoint_event():
    return {
        "httpMethod": "POST",
        "path": "/v1/assistant",
        "body": json.dumps(
            {
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
        ),
    }


class FakeBedrockClient:
    def __init__(self):
        self.converse_called = False

    def converse(self, **kwargs):
        self.converse_called = True
        return {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": "legacy response",
                        }
                    ]
                }
            }
        }


class FakeBoto3(types.SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.clients = []
        self.bedrock_client = FakeBedrockClient()

    def client(self, service_name, region_name=None):
        self.clients.append(service_name)
        if service_name == "bedrock-runtime":
            return self.bedrock_client
        raise AssertionError(f"Unexpected boto3 client: {service_name}")


class AssistantEndpointTests(unittest.TestCase):
    def test_valid_v1_endpoint_request_returns_contract_response(self):
        response = handle_public_assistant_endpoint(valid_endpoint_event())
        body = json.loads(response["body"])
        contract_response, errors = validate_success_response(body)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["headers"]["Content-Type"], "application/json")
        self.assertEqual(errors, [])
        self.assertEqual(contract_response.contractVersion, CONTRACT_VERSION)
        self.assertEqual(contract_response.correlationId.value, "web-req-001")
        self.assertEqual(contract_response.conversationId.value, "conversation-001")
        self.assertEqual(contract_response.message.role, "assistant")
        self.assertEqual(contract_response.service.name, SERVICE_NAME)

    def test_valid_request_without_conversation_id_is_deterministic(self):
        event = valid_endpoint_event()
        payload = json.loads(event["body"])
        del payload["conversationId"]
        event["body"] = json.dumps(payload)

        first_response = handle_public_assistant_endpoint(event)
        second_response = handle_public_assistant_endpoint(event)
        body = json.loads(first_response["body"])

        self.assertEqual(first_response, second_response)
        self.assertEqual(body["conversationId"], "web-req-001")

    def test_endpoint_rejects_unknown_fields(self):
        event = valid_endpoint_event()
        payload = json.loads(event["body"])
        payload["prompt"] = "Do not accept alternate request shapes."
        event["body"] = json.dumps(payload)

        response = handle_public_assistant_endpoint(event)
        body = json.loads(response["body"])
        error_response, errors = validate_error_response(body)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(errors, [])
        self.assertEqual(error_response.code, "VALIDATION_ERROR")
        self.assertEqual(error_response.details[0].code, "UNKNOWN_FIELD")

    def test_endpoint_rejects_unsupported_contract_version(self):
        event = valid_endpoint_event()
        payload = json.loads(event["body"])
        payload["contractVersion"] = "ai-knowledge-assistant-v2"
        event["body"] = json.dumps(payload)

        response = handle_public_assistant_endpoint(event)
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["error"]["details"][0]["code"], "UNSUPPORTED_VERSION")

    def test_endpoint_rejects_invalid_json_with_fallback_correlation_id(self):
        event = valid_endpoint_event()
        event["body"] = "{"

        response = handle_public_assistant_endpoint(event)
        body = json.loads(response["body"])
        error_response, errors = validate_error_response(body)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(errors, [])
        self.assertEqual(error_response.correlationId.value, "unavailable")
        self.assertEqual(error_response.details[0].code, "INVALID_JSON")

    def test_endpoint_rejects_unsupported_endpoint_version(self):
        event = valid_endpoint_event()
        event["path"] = "/v2/assistant"

        response = handle_public_assistant_endpoint(event)
        body = json.loads(response["body"])
        error_response, errors = validate_error_response(body)

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(errors, [])
        self.assertEqual(error_response.code, "UNSUPPORTED_ENDPOINT_VERSION")

    def test_endpoint_rejects_wrong_method(self):
        event = valid_endpoint_event()
        event["httpMethod"] = "GET"

        response = handle_public_assistant_endpoint(event)
        body = json.loads(response["body"])
        error_response, errors = validate_error_response(body)

        self.assertEqual(response["statusCode"], 405)
        self.assertEqual(errors, [])
        self.assertEqual(error_response.code, "METHOD_NOT_ALLOWED")

    def test_http_api_v2_endpoint_event_is_supported(self):
        event = valid_endpoint_event()
        event.pop("httpMethod")
        event.pop("path")
        event["rawPath"] = "/v1/assistant"
        event["requestContext"] = {
            "http": {
                "method": "POST",
            }
        }

        response = handle_public_assistant_endpoint(event)
        body = json.loads(response["body"])
        contract_response, errors = validate_success_response(body)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(errors, [])
        self.assertEqual(contract_response.correlationId.value, "web-req-001")

    def test_lambda_routes_v1_endpoint_without_invoking_bedrock(self):
        fake_boto3 = FakeBoto3()

        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            sys.modules.pop("lambda_function", None)
            lambda_function = importlib.import_module("lambda_function")

            response = lambda_function.lambda_handler(valid_endpoint_event(), None)

        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["contractVersion"], CONTRACT_VERSION)
        self.assertFalse(fake_boto3.bedrock_client.converse_called)

    def test_lambda_fails_closed_for_unsupported_endpoint_version(self):
        fake_boto3 = FakeBoto3()
        event = valid_endpoint_event()
        event["path"] = "/v2/assistant"

        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            sys.modules.pop("lambda_function", None)
            lambda_function = importlib.import_module("lambda_function")

            response = lambda_function.lambda_handler(event, None)

        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["error"]["code"], "UNSUPPORTED_ENDPOINT_VERSION")
        self.assertFalse(fake_boto3.bedrock_client.converse_called)


if __name__ == "__main__":
    unittest.main()
