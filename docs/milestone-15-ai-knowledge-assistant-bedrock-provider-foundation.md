# Milestone 15 - AI Knowledge Assistant Bedrock Provider Foundation

## Objective

Introduce an alternate Bedrock runtime provider behind the existing `RuntimeProvider` interface.

This milestone does not change the public contract, public endpoint, runtime dispatcher, deterministic provider, default runtime behavior, Website, Assessment Service, Executive Intelligence Platform, Cognito, API Gateway infrastructure, DynamoDB, RAG, vector search, prompt orchestration, monitoring, analytics, or logging.

## Provider Namespace

Bedrock provider code is isolated under:

```text
src/assistant_runtime/
  bedrock_provider.py
  config.py
  factory.py
```

## Provider Responsibilities

`BedrockRuntimeProvider` implements the existing runtime provider interface:

```python
execute(context: RuntimeRequestContext) -> RuntimeResponse
```

The provider owns:

- runtime request to Bedrock `converse` request mapping
- Bedrock response to runtime response mapping
- deterministic provider error handling
- provider configuration through `BedrockProviderConfig`

## Request Mapping

Runtime request messages map to Bedrock messages:

```json
{
  "modelId": "amazon.nova-lite-v1:0",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "What is Amazon Cognito?"
        }
      ]
    }
  ]
}
```

## Response Mapping

The provider reads:

```text
response["output"]["message"]["content"][0]["text"]
```

and returns a runtime response containing an assistant message.

## Deterministic Error Handling

Client exceptions, malformed Bedrock responses, missing response text, and blank response text map to:

```text
AI Knowledge Assistant provider request failed.
```

This keeps provider failure behavior deterministic.

## Configuration

Default provider configuration:

```python
BedrockProviderConfig(
    model_id="amazon.nova-lite-v1:0",
    region_name="us-east-2",
)
```

The provider is selectable only through explicit construction or factory use:

```python
create_bedrock_runtime_provider(config)
```

## Compatibility Notes

`DeterministicRuntimeProvider` remains unchanged and remains the default runtime provider.

`RuntimeDispatcher` continues to depend only on `RuntimeProvider`.

The endpoint continues to delegate only to `RuntimeDispatcher`.

The Bedrock provider is introduced but not activated by default.
