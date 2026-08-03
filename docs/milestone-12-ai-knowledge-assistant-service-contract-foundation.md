# Milestone 12 - AI Knowledge Assistant Service Contract Foundation

## Objective

Define the public, versioned service contract for the AWS AI Knowledge Assistant so future Website integration can consume a repository-owned backend interface.

This milestone defines interface shape only. It does not change Lambda routing, invoke Bedrock, implement prompt orchestration, persist conversations, integrate Cognito, modify API Gateway, or connect the Website.

## Contract Namespace

The contract is isolated under:

```text
src/assistant_contract/
  __init__.py
  models.py
  schema.py
  serialization.py
  validation.py
  v1/
    __init__.py
```

The external JSON Schema artifact is:

```text
docs/contracts/ai-knowledge-assistant-v1.schema.json
```

## Version

Current contract version:

```text
ai-knowledge-assistant-v1
```

The version is exported as `CONTRACT_VERSION` from `assistant_contract.models`.

The stable v1 namespace is:

```python
assistant_contract.v1
```

## Request Contract

Request payload:

```json
{
  "contractVersion": "ai-knowledge-assistant-v1",
  "correlationId": "web-req-001",
  "conversationId": "conversation-001",
  "messages": [
    {
      "role": "user",
      "content": "What AWS service should I use for managed identity?"
    }
  ]
}
```

Required fields:

- `contractVersion`
- `correlationId`
- `messages`

Optional fields:

- `conversationId`

Request messages are user-authored only. Assistant output belongs in the response contract.

## Success Response Contract

Success response payload:

```json
{
  "contractVersion": "ai-knowledge-assistant-v1",
  "correlationId": "web-req-001",
  "conversationId": "conversation-001",
  "message": {
    "role": "assistant",
    "content": "Amazon Cognito provides managed user authentication and identity services."
  },
  "service": {
    "name": "aws-ai-knowledge-assistant",
    "contractVersion": "ai-knowledge-assistant-v1"
  }
}
```

## Error Response Contract

Error response payload:

```json
{
  "contractVersion": "ai-knowledge-assistant-v1",
  "correlationId": "web-req-001",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request payload is invalid.",
    "details": [
      {
        "field": "messages",
        "message": "At least one message is required.",
        "code": "REQUIRED"
      }
    ]
  },
  "service": {
    "name": "aws-ai-knowledge-assistant",
    "contractVersion": "ai-knowledge-assistant-v1"
  }
}
```

## Validation Rules

Validation fails closed:

1. Payloads must be JSON objects.
2. Duplicate JSON object keys are rejected.
3. Unknown fields are rejected.
4. `contractVersion` must exactly equal `ai-knowledge-assistant-v1`.
5. `correlationId` is required.
6. `conversationId` is optional on requests and required on success responses.
7. Identifiers must be 1-128 characters and use only letters, numbers, period, underscore, colon, or hyphen.
8. Request `messages` must contain 1-20 entries.
9. Request message role must be `user`.
10. Success response message role must be `assistant`.
11. Message content must be 1-8000 characters.
12. Service metadata must identify `aws-ai-knowledge-assistant` and the active contract version.

## Deterministic Serialization

Contract serialization uses sorted JSON keys, compact separators, and ASCII output through:

```python
dumps_contract_json(value)
```

This keeps contract examples stable for tests and downstream consumers.

## Compatibility Policy

Contract `v1` is immutable after publication.

Backward-compatible changes may be introduced only by adding a new contract version and preserving this one. Breaking changes include removing fields, renaming fields, changing required fields, changing accepted identifier formats, changing message role rules, changing response envelope shape, or changing error envelope shape.

Consumers should send `contractVersion` explicitly. Producers should reject unsupported versions instead of silently coercing them.

## Boundary Notes

This contract is owned by the AWS AI Knowledge Assistant repository.

The Website must consume this contract as a presentation-only client and must not define backend request or response semantics.

The Assessment Service remains separate and unchanged.
