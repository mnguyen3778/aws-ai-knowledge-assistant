import importlib
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assessment.handler import handle_assessment  # noqa: E402


def valid_event():
    return {
        "httpMethod": "POST",
        "path": "/assessment",
        "body": json.dumps(
            {
                "assessmentVersion": "nguyen-ai-readiness-v1",
                "organization": {
                    "name": "Nguyen AI",
                },
                "respondent": {
                    "role": "Founder",
                },
                "answers": {
                    "future.question.1": 3,
                },
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
                            "text": "existing chat response",
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


class AssessmentHandlerTests(unittest.TestCase):
    def test_invalid_requests_return_400(self):
        response = handle_assessment(
            {
                "body": "{",
            }
        )
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(body["error"]["code"], "VALIDATION_ERROR")
        self.assertFalse(body["modelInvoked"])
        self.assertFalse(body["persisted"])

    def test_valid_requests_return_200(self):
        response = handle_assessment(valid_event())
        body = json.loads(response["body"])

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(body["assessmentVersion"], "nguyen-ai-readiness-v1")
        self.assertEqual(body["overallScore"], 0)
        self.assertEqual(body["readinessLevel"]["id"], "pending-rubric")
        self.assertEqual(body["categoryScores"], [])
        self.assertEqual(body["recommendations"], [])
        self.assertFalse(body["modelInvoked"])
        self.assertFalse(body["persisted"])

    def test_assessment_route_does_not_invoke_bedrock_or_dynamodb(self):
        fake_boto3 = FakeBoto3()

        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            sys.modules.pop("lambda_function", None)
            lambda_function = importlib.import_module("lambda_function")

            response = lambda_function.lambda_handler(valid_event(), None)

        self.assertEqual(response["statusCode"], 200)
        self.assertFalse(fake_boto3.bedrock_client.converse_called)
        self.assertNotIn("dynamodb", fake_boto3.clients)

    def test_http_api_v2_assessment_route_is_isolated(self):
        fake_boto3 = FakeBoto3()
        event = valid_event()
        event.pop("httpMethod")
        event.pop("path")
        event["rawPath"] = "/assessment"
        event["requestContext"] = {
            "http": {
                "method": "POST",
            }
        }

        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            sys.modules.pop("lambda_function", None)
            lambda_function = importlib.import_module("lambda_function")

            response = lambda_function.lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 200)
        self.assertFalse(fake_boto3.bedrock_client.converse_called)
        self.assertNotIn("dynamodb", fake_boto3.clients)

    def test_non_assessment_route_preserves_existing_chat_behavior(self):
        fake_boto3 = FakeBoto3()

        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            sys.modules.pop("lambda_function", None)
            lambda_function = importlib.import_module("lambda_function")

            response = lambda_function.lambda_handler(
                {
                    "httpMethod": "GET",
                    "path": "/chat",
                },
                None,
            )

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(
            json.loads(response["body"]),
            {
                "response": "existing chat response",
            },
        )
        self.assertTrue(fake_boto3.bedrock_client.converse_called)
        self.assertNotIn("dynamodb", fake_boto3.clients)


if __name__ == "__main__":
    unittest.main()
