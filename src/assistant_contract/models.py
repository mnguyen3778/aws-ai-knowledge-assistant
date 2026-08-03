from dataclasses import dataclass, field
from typing import Any


CONTRACT_VERSION = "ai-knowledge-assistant-v1"
SERVICE_NAME = "aws-ai-knowledge-assistant"


@dataclass(frozen=True)
class ContractValidationError:
    field: str
    message: str
    code: str = "INVALID_FIELD"

    def to_dict(self) -> dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
            "code": self.code,
        }


@dataclass(frozen=True)
class CorrelationId:
    value: str

    def to_dict(self) -> str:
        return self.value


@dataclass(frozen=True)
class ConversationId:
    value: str

    def to_dict(self) -> str:
        return self.value


@dataclass(frozen=True)
class Message:
    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "content": self.content,
        }


@dataclass(frozen=True)
class ServiceMetadata:
    name: str = SERVICE_NAME
    contractVersion: str = CONTRACT_VERSION

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "contractVersion": self.contractVersion,
        }


@dataclass(frozen=True)
class KnowledgeAssistantRequest:
    correlationId: CorrelationId
    messages: list[Message]
    contractVersion: str = CONTRACT_VERSION
    conversationId: ConversationId | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "contractVersion": self.contractVersion,
            "correlationId": self.correlationId.to_dict(),
            "messages": [
                message.to_dict()
                for message in self.messages
            ],
        }

        if self.conversationId is not None:
            payload["conversationId"] = self.conversationId.to_dict()

        return payload


@dataclass(frozen=True)
class KnowledgeAssistantResponse:
    correlationId: CorrelationId
    conversationId: ConversationId
    message: Message
    service: ServiceMetadata = field(default_factory=ServiceMetadata)
    contractVersion: str = CONTRACT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "contractVersion": self.contractVersion,
            "correlationId": self.correlationId.to_dict(),
            "conversationId": self.conversationId.to_dict(),
            "message": self.message.to_dict(),
            "service": self.service.to_dict(),
        }


@dataclass(frozen=True)
class ErrorDetail:
    field: str
    message: str
    code: str = "INVALID_FIELD"

    def to_dict(self) -> dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
            "code": self.code,
        }


@dataclass(frozen=True)
class ErrorResponse:
    correlationId: CorrelationId
    message: str
    details: list[ErrorDetail]
    code: str = "VALIDATION_ERROR"
    service: ServiceMetadata = field(default_factory=ServiceMetadata)
    contractVersion: str = CONTRACT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "contractVersion": self.contractVersion,
            "correlationId": self.correlationId.to_dict(),
            "error": {
                "code": self.code,
                "message": self.message,
                "details": [
                    detail.to_dict()
                    for detail in self.details
                ],
            },
            "service": self.service.to_dict(),
        }
