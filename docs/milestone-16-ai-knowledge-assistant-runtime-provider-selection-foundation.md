# Milestone 16 - AI Knowledge Assistant Runtime Provider Selection Foundation

## Objective

Introduce an internal runtime provider selection foundation while preserving the existing public endpoint, immutable v1 contract, runtime dispatcher, runtime provider interface, and default deterministic behavior.

This milestone does not activate Bedrock by default.

## Selection Namespace

Provider selection code is isolated under:

```text
src/assistant_runtime/provider_selection.py
```

## Provider Identifier Governance

Provider identifiers are centralized in `ProviderIdentifier`:

```python
ProviderIdentifier.DETERMINISTIC
ProviderIdentifier.BEDROCK
```

Provider lookup, registration, configuration resolution, and factory selection use these identifiers.

## Selection Components

The selection foundation contains:

- `ProviderIdentifier`: centralized provider identifier enumeration.
- `ProviderSelectionConfig`: resolved provider selection configuration.
- `ProviderRegistry`: provider identifier to provider factory registration.
- `ProviderSelectionService`: single abstraction for selecting runtime providers.
- `resolve_provider_selection_config`: fail-closed configuration resolver.
- `create_default_provider_registry`: default registry for deterministic and Bedrock factories.

## Default Behavior

When selection input is missing, malformed, unsupported, unregistered, or invalid, provider selection returns `DeterministicRuntimeProvider`.

`DeterministicRuntimeProvider` remains the default provider.

`BedrockRuntimeProvider` is selectable only through explicit configuration.

## Configuration Shape

Deterministic selection:

```python
{
    "provider": ProviderIdentifier.DETERMINISTIC.value
}
```

Bedrock selection:

```python
{
    "provider": ProviderIdentifier.BEDROCK.value,
    ProviderIdentifier.BEDROCK.value: {
        "model_id": "amazon.nova-lite-v1:0",
        "region_name": "us-east-2",
    },
}
```

## Compatibility Notes

The runtime dispatcher remains unaware of concrete provider implementations.

The runtime dispatcher continues to depend only on `RuntimeProvider`.

The public endpoint remains unchanged.

The public contract remains unchanged.

No Website, Assessment Service, Executive Intelligence Platform, DynamoDB, Cognito, API Gateway, monitoring, analytics, RAG, vector search, or persistence behavior is introduced.
