from typing import Protocol

from assistant_contract.v1 import Message
from assistant_runtime.models import RuntimeRequestContext, RuntimeResponse


DETERMINISTIC_ASSISTANT_MESSAGE = (
    "AI Knowledge Assistant v1 contract request accepted."
)


class RuntimeProvider(Protocol):
    def execute(self, context: RuntimeRequestContext) -> RuntimeResponse:
        ...


class DeterministicRuntimeProvider:
    def execute(self, context: RuntimeRequestContext) -> RuntimeResponse:
        return RuntimeResponse(
            message=Message(
                role="assistant",
                content=DETERMINISTIC_ASSISTANT_MESSAGE,
            )
        )
