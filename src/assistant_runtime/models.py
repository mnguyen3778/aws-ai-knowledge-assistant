from dataclasses import dataclass

from assistant_contract.v1 import (
    ConversationId,
    CorrelationId,
    KnowledgeAssistantRequest,
    Message,
)


@dataclass(frozen=True)
class RuntimeRequestContext:
    contract_request: KnowledgeAssistantRequest

    @property
    def correlation_id(self) -> CorrelationId:
        return self.contract_request.correlationId

    @property
    def conversation_id(self) -> ConversationId:
        if self.contract_request.conversationId is not None:
            return self.contract_request.conversationId

        return ConversationId(self.contract_request.correlationId.value)

    @property
    def messages(self) -> list[Message]:
        return self.contract_request.messages


@dataclass(frozen=True)
class RuntimeResponse:
    message: Message
