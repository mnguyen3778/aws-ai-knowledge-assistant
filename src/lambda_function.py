import json
import boto3

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-east-2"
)

def lambda_handler(event, context):

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
