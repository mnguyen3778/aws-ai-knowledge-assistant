# Milestone 14 - AI Knowledge Assistant Runtime Dispatch Foundation

## Objective

Introduce an internal runtime dispatch layer behind the existing public AI Knowledge Assistant endpoint.

This milestone does not change the public endpoint, public contract, deterministic response content, endpoint error behavior, Bedrock behavior, persistence, Website integration, API Gateway infrastructure, Cognito, Assessment Service integration, or Executive Intelligence Platform integration.

## Runtime Namespace

Runtime code is isolated under:

```text
src/assistant_runtime/
  __init__.py
  dispatcher.py
  models.py
  provider.py
```

## Runtime Responsibilities

The runtime layer owns deterministic assistant response construction.

Module responsibilities:

- `dispatcher.py`: runtime dispatcher, dependency injection boundary, runtime lifecycle factory, and contract response construction.
- `models.py`: runtime request context and runtime response abstraction.
- `provider.py`: runtime provider interface and deterministic default provider.

## Endpoint Boundary

The public endpoint remains responsible for:

- request deserialization
- validation
- contract enforcement
- response serialization
- error serialization

After a request is deserialized and validated, the endpoint delegates execution to the runtime dispatcher.

## Runtime Lifecycle

The endpoint uses a default runtime dispatcher created by:

```python
create_default_runtime_dispatcher()
```

The default dispatcher uses `DeterministicRuntimeProvider`, which performs no external calls and returns the existing deterministic assistant message:

```text
AI Knowledge Assistant v1 contract request accepted.
```

## Provider Boundary

The runtime provider interface is:

```python
execute(context: RuntimeRequestContext) -> RuntimeResponse
```

The provider receives a runtime request context derived from a validated `KnowledgeAssistantRequest`.

The provider does not own endpoint parsing, validation, serialization, or error handling.

## Compatibility Notes

The public contract remains `ai-knowledge-assistant-v1`.

The public endpoint remains:

```text
POST /v1/assistant
```

Valid endpoint responses and deterministic endpoint errors remain unchanged.

No AI reasoning, Bedrock orchestration, prompt engineering, RAG, vector search, DynamoDB persistence, or cross-service integration is introduced.
