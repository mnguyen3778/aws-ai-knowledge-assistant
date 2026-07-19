import json
import boto3
from assessment.handler import handle_assessment

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-2"
)

def lambda_handler(event, context):
    if _is_assessment_request(event):
        return handle_assessment(event)

    response = bedrock.converse(
        modelId="amazon.nova-lite-v1:0",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": "Tell me one fact about AWS."
                    }
                ]
            }
        ]
    )

    ai_response = response["output"]["message"]["content"][0]["text"]

    return {
        "statusCode": 200,
        "body": json.dumps({
            "response": ai_response
        })
    }


def _is_assessment_request(event):
    method = event.get("httpMethod")
    path = event.get("path")

    if not method:
        http_context = event.get("requestContext", {}).get("http", {})
        method = http_context.get("method")
        path = event.get("rawPath")

    return method == "POST" and path == "/assessment"
