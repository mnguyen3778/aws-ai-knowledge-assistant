from typing import Any

from assistant_contract.v1 import Message
from assistant_runtime.config import BedrockProviderConfig
from assistant_runtime.models import RuntimeRequestContext, RuntimeResponse


BEDROCK_PROVIDER_ERROR_MESSAGE = (
    "AI Knowledge Assistant provider request failed."
)


class BedrockRuntimeProvider:
    def __init__(
        self,
        client: Any,
        config: BedrockProviderConfig,
    ):
        self._client = client
        self._config = config

    def execute(self, context: RuntimeRequestContext) -> RuntimeResponse:
        try:
            response = self._client.converse(
                **_bedrock_request_from_context(context, self._config)
            )
            content = _assistant_text_from_bedrock_response(response)
        except Exception:
            content = BEDROCK_PROVIDER_ERROR_MESSAGE

        return RuntimeResponse(
            message=Message(
                role="assistant",
                content=content,
            )
        )


def _bedrock_request_from_context(
    context: RuntimeRequestContext,
    config: BedrockProviderConfig,
) -> dict[str, Any]:
    return {
        "modelId": config.model_id,
        "messages": [
            {
                "role": message.role,
                "content": [
                    {
                        "text": message.content,
                    }
                ],
            }
            for message in context.messages
        ],
    }


def _assistant_text_from_bedrock_response(response: Any) -> str:
    try:
        content = response["output"]["message"]["content"]
        first_entry = content[0]
        text = first_entry["text"]
    except (KeyError, IndexError, TypeError):
        return BEDROCK_PROVIDER_ERROR_MESSAGE

    if not isinstance(text, str) or not text.strip():
        return BEDROCK_PROVIDER_ERROR_MESSAGE

    return text
