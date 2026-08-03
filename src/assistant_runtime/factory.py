from typing import Any

from assistant_runtime.bedrock_provider import BedrockRuntimeProvider
from assistant_runtime.config import BedrockProviderConfig


def create_bedrock_runtime_provider(
    config: BedrockProviderConfig,
    client: Any | None = None,
) -> BedrockRuntimeProvider:
    if client is None:
        import boto3

        client = boto3.client(
            "bedrock-runtime",
            region_name=config.region_name,
        )

    return BedrockRuntimeProvider(
        client=client,
        config=config,
    )
