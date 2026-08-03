# Milestone 13 - AI Knowledge Assistant Public Service Endpoint Foundation

## Objective

Expose the immutable AI Knowledge Assistant v1 contract through a bounded public endpoint foundation owned by this repository.

This milestone does not change the v1 contract, invoke Bedrock, implement prompt orchestration, add persistence, integrate the Assessment Service, integrate the Executive Intelligence Platform, modify the Website, change Cognito, or change API Gateway infrastructure.

## Endpoint

Versioned public endpoint:

```text
POST /v1/assistant
```

Unsupported versioned assistant endpoint paths, such as `/v2/assistant`, fail closed with a deterministic v1 error envelope.

The endpoint supports both API Gateway REST API events and HTTP API v2 event shapes.

## Adapter Architecture

Endpoint code is isolated under:

```text
src/assistant_endpoint/
  __init__.py
  handler.py
```

Module responsibilities:

- `assistant_endpoint.handler`: route recognition, request body deserialization, v1 contract validation, compatibility enforcement, deterministic success serialization, and deterministic error serialization.
- `lambda_function.py`: routes versioned assistant endpoint requests to the endpoint adapter before preserving existing assessment and legacy routes.

## Request Lifecycle

```text
POST /v1/assistant
-> lambda_function.lambda_handler
-> assistant_endpoint.handler.handle_public_assistant_endpoint
-> assistant_contract.v1.parse_contract_json
-> assistant_contract.v1.validate_request
-> deterministic v1 response or v1 error response
```

## Success Response

Valid requests return HTTP `200` and a serialized `KnowledgeAssistantResponse` using the existing v1 contract.

The endpoint foundation returns a deterministic contract acknowledgement:

```json
{
  "contractVersion": "ai-knowledge-assistant-v1",
  "correlationId": "web-req-001",
  "conversationId": "conversation-001",
  "message": {
    "role": "assistant",
    "content": "AI Knowledge Assistant v1 contract request accepted."
  },
  "service": {
    "name": "aws-ai-knowledge-assistant",
    "contractVersion": "ai-knowledge-assistant-v1"
  }
}
```

This response is not AI reasoning output. It exists only to expose and verify the public service contract surface.

If the request omits `conversationId`, the response uses the valid `correlationId` as the deterministic conversation identifier. This preserves the v1 request contract, where `conversationId` is optional, while satisfying the v1 success response contract, where `conversationId` is required.

## Error Responses

All endpoint errors use the existing v1 `ErrorResponse` envelope and deterministic JSON serialization.

Failure cases include:

- unsupported endpoint version
- unsupported HTTP method
- invalid JSON
- duplicate JSON object keys
- unsupported contract version
- unknown fields
- validation failures

When the request does not contain a valid usable `correlationId`, the endpoint returns:

```text
unavailable
```

as a deterministic fallback correlation identifier.

## Boundary Notes

The endpoint exposes the existing v1 contract exactly.

The contract remains immutable.

The Website remains a presentation-only consumer.

The Assessment Service remains separate and unchanged.
