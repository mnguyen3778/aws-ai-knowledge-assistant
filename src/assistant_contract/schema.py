from typing import Any

from assistant_contract.models import CONTRACT_VERSION, SERVICE_NAME


def contract_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://contracts.nguyen-ai.com/"
            "aws-ai-knowledge-assistant/"
            f"{CONTRACT_VERSION}.schema.json"
        ),
        "title": "AWS AI Knowledge Assistant Service Contract",
        "type": "object",
        "oneOf": [
            {
                "$ref": "#/$defs/KnowledgeAssistantRequest",
            },
            {
                "$ref": "#/$defs/KnowledgeAssistantResponse",
            },
            {
                "$ref": "#/$defs/ErrorResponse",
            },
        ],
        "$defs": {
            "Identifier": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128,
                "pattern": "^[A-Za-z0-9._:-]+$",
            },
            "ContractVersion": {
                "const": CONTRACT_VERSION,
            },
            "UserMessage": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "role",
                    "content",
                ],
                "properties": {
                    "role": {
                        "const": "user",
                    },
                    "content": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 8000,
                    },
                },
            },
            "AssistantMessage": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "role",
                    "content",
                ],
                "properties": {
                    "role": {
                        "const": "assistant",
                    },
                    "content": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 8000,
                    },
                },
            },
            "ServiceMetadata": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "name",
                    "contractVersion",
                ],
                "properties": {
                    "name": {
                        "const": SERVICE_NAME,
                    },
                    "contractVersion": {
                        "$ref": "#/$defs/ContractVersion",
                    },
                },
            },
            "ValidationDetail": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "field",
                    "message",
                    "code",
                ],
                "properties": {
                    "field": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "message": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "code": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
            },
            "KnowledgeAssistantRequest": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "contractVersion",
                    "correlationId",
                    "messages",
                ],
                "properties": {
                    "contractVersion": {
                        "$ref": "#/$defs/ContractVersion",
                    },
                    "correlationId": {
                        "$ref": "#/$defs/Identifier",
                    },
                    "conversationId": {
                        "$ref": "#/$defs/Identifier",
                    },
                    "messages": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 20,
                        "items": {
                            "$ref": "#/$defs/UserMessage",
                        },
                    },
                },
            },
            "KnowledgeAssistantResponse": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "contractVersion",
                    "correlationId",
                    "conversationId",
                    "message",
                    "service",
                ],
                "properties": {
                    "contractVersion": {
                        "$ref": "#/$defs/ContractVersion",
                    },
                    "correlationId": {
                        "$ref": "#/$defs/Identifier",
                    },
                    "conversationId": {
                        "$ref": "#/$defs/Identifier",
                    },
                    "message": {
                        "$ref": "#/$defs/AssistantMessage",
                    },
                    "service": {
                        "$ref": "#/$defs/ServiceMetadata",
                    },
                },
            },
            "ErrorResponse": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "contractVersion",
                    "correlationId",
                    "error",
                    "service",
                ],
                "properties": {
                    "contractVersion": {
                        "$ref": "#/$defs/ContractVersion",
                    },
                    "correlationId": {
                        "$ref": "#/$defs/Identifier",
                    },
                    "error": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "code",
                            "message",
                            "details",
                        ],
                        "properties": {
                            "code": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "message": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "details": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/$defs/ValidationDetail",
                                },
                            },
                        },
                    },
                    "service": {
                        "$ref": "#/$defs/ServiceMetadata",
                    },
                },
            },
        },
    }
