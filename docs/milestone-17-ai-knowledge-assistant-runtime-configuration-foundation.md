# Milestone 17 - AI Knowledge Assistant Runtime Configuration Foundation

## Objective

Introduce an internal runtime configuration foundation that governs provider selection while preserving the immutable public contract, public endpoint, runtime dispatcher, runtime provider interface, provider selection behavior, and default deterministic provider.

This milestone does not activate Bedrock by default.

## Configuration Namespace

Runtime configuration is isolated under:

```text
src/assistant_runtime/runtime_configuration.py
```

This module is the only runtime layer that reads environment variables.

## Runtime Configuration Model

`RuntimeConfiguration` is immutable and validates its provider selection during initialization.

Future runtime settings must be added through `RuntimeConfiguration` rather than direct environment access.

## Environment Variables

Runtime configuration recognizes:

```text
AI_KNOWLEDGE_ASSISTANT_RUNTIME_PROVIDER
AI_KNOWLEDGE_ASSISTANT_BEDROCK_MODEL_ID
AI_KNOWLEDGE_ASSISTANT_BEDROCK_REGION
```

Provider values are governed by `ProviderIdentifier`.

Valid provider identifiers:

```text
deterministic
bedrock
```

## Defaults

Missing configuration resolves to:

```text
ProviderIdentifier.DETERMINISTIC
```

`DeterministicRuntimeProvider` remains the default provider.

`BedrockRuntimeProvider` is not activated by default.

## Fail-Closed Behavior

Invalid provider names, invalid provider configuration, invalid runtime configuration input, blank Bedrock model IDs, and blank Bedrock regions resolve to deterministic provider selection.

## Startup Loading

`RuntimeConfigurationLoader` loads configuration once and returns the same immutable `RuntimeConfiguration` object on subsequent calls.

Use:

```python
configuration = RuntimeConfigurationLoader().load()
```

or:

```python
configuration = load_runtime_configuration()
```

## Provider Selection Integration

`ProviderSelectionService` consumes `RuntimeConfiguration` by reading its validated `provider_selection` value.

Downstream runtime components consume validated configuration objects and do not read environment variables directly.

## Compatibility Notes

The public contract remains unchanged.

The public endpoint remains unchanged.

The runtime dispatcher remains unchanged.

The runtime provider interface remains unchanged.

Existing deterministic runtime behavior remains unchanged.
