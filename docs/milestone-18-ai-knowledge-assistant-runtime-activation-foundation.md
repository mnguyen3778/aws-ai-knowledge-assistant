# Milestone 18 - AI Knowledge Assistant Runtime Activation Foundation

## Objective

Introduce a single internal runtime composition root that initializes the AI Knowledge Assistant runtime through validated configuration and provider selection.

This milestone does not change the public service contract, public endpoint behavior, response serialization, runtime dispatcher public interface, runtime provider interface, provider selection interface, runtime configuration model, Website, Assessment Service, Executive Intelligence Platform, DynamoDB, Cognito, API Gateway, IAM, monitoring, analytics, RAG, vector search, or persistence.

## Composition Root

Runtime activation is isolated under:

```text
src/assistant_runtime/composition.py
```

The composition root is:

```python
RuntimeCompositionRoot
```

## Responsibilities

`RuntimeCompositionRoot` is the only component that assembles runtime dependencies.

It performs:

1. Load `RuntimeConfiguration`.
2. Validate `RuntimeConfiguration`.
3. Resolve `ProviderSelectionService`.
4. Instantiate the selected `RuntimeProvider` through provider selection.
5. Construct `RuntimeDispatcher`.
6. Return the initialized `RuntimeDispatcher`.

## Startup Lifecycle

Runtime initialization is idempotent. A composition root loads configuration once, selects a provider once, constructs a dispatcher once, and returns the same dispatcher for subsequent initialization calls.

The compatibility factory:

```python
create_default_runtime_dispatcher()
```

delegates to the composition root instead of assembling providers directly.

## Dependency Injection

`RuntimeCompositionRoot` uses constructor injection for:

- `RuntimeConfigurationLoader`
- `ProviderSelectionService`

The factory:

```python
create_runtime_composition_root()
```

provides default dependencies for normal startup while still allowing tests to inject controlled dependencies.

## Fail-Closed Behavior

Missing or invalid runtime configuration continues to initialize `DeterministicRuntimeProvider`.

`BedrockRuntimeProvider` is not activated by default.

## Compatibility Notes

The public endpoint continues to consume an initialized `RuntimeDispatcher`.

`RuntimeDispatcher` remains unaware of concrete provider implementations.

The public contract remains unchanged.

The public endpoint response body remains unchanged.
