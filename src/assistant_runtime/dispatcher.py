from assistant_contract.v1 import (
    CONTRACT_VERSION,
    KnowledgeAssistantRequest,
    KnowledgeAssistantResponse,
    ServiceMetadata,
)
from assistant_runtime.models import RuntimeRequestContext
from assistant_runtime.provider import RuntimeProvider


class RuntimeDispatcher:
    def __init__(self, provider: RuntimeProvider):
        self._provider = provider

    def dispatch(
        self,
        request: KnowledgeAssistantRequest,
    ) -> KnowledgeAssistantResponse:
        context = RuntimeRequestContext(contract_request=request)
        runtime_response = self._provider.execute(context)

        return KnowledgeAssistantResponse(
            contractVersion=CONTRACT_VERSION,
            correlationId=context.correlation_id,
            conversationId=context.conversation_id,
            message=runtime_response.message,
            service=ServiceMetadata(),
        )


def create_default_runtime_dispatcher() -> RuntimeDispatcher:
    from assistant_runtime.composition import create_runtime_composition_root

    return create_runtime_composition_root().initialize()
