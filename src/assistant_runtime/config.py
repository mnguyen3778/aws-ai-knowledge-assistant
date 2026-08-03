from dataclasses import dataclass


@dataclass(frozen=True)
class BedrockProviderConfig:
    model_id: str = "amazon.nova-lite-v1:0"
    region_name: str = "us-east-2"
