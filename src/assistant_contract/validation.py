import json
import re
from typing import Any

from assistant_contract.models import (
    CONTRACT_VERSION,
    SERVICE_NAME,
    ContractValidationError,
    ConversationId,
    CorrelationId,
    ErrorDetail,
    ErrorResponse,
    KnowledgeAssistantRequest,
    KnowledgeAssistantResponse,
    Message,
    ServiceMetadata,
)


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")
_MAX_IDENTIFIER_LENGTH = 128
_MAX_MESSAGE_LENGTH = 8000
_MAX_REQUEST_MESSAGES = 20
_REQUEST_FIELDS = frozenset(
    {
        "contractVersion",
        "correlationId",
        "conversationId",
        "messages",
    }
)
_SUCCESS_RESPONSE_FIELDS = frozenset(
    {
        "contractVersion",
        "correlationId",
        "conversationId",
        "message",
        "service",
    }
)
_ERROR_RESPONSE_FIELDS = frozenset(
    {
        "contractVersion",
        "correlationId",
        "error",
        "service",
    }
)
_MESSAGE_FIELDS = frozenset(
    {
        "role",
        "content",
    }
)
_SERVICE_FIELDS = frozenset(
    {
        "name",
        "contractVersion",
    }
)
_ERROR_FIELDS = frozenset(
    {
        "code",
        "message",
        "details",
    }
)
_ERROR_DETAIL_FIELDS = frozenset(
    {
        "field",
        "message",
        "code",
    }
)


def parse_contract_json(raw_body: Any) -> tuple[Any, list[ContractValidationError]]:
    if raw_body is None:
        return None, [
            ContractValidationError(
                field="body",
                message="Request body is required.",
                code="REQUIRED",
            )
        ]

    if isinstance(raw_body, dict):
        return raw_body, []

    if not isinstance(raw_body, str):
        return None, [
            ContractValidationError(
                field="body",
                message="Body must be a JSON object string.",
            )
        ]

    try:
        return json.loads(raw_body, object_pairs_hook=_reject_duplicate_keys), []
    except DuplicateKeyError as exc:
        return None, [
            ContractValidationError(
                field=exc.field,
                message=f"Duplicate field '{exc.key}' is not allowed.",
                code="DUPLICATE_FIELD",
            )
        ]
    except json.JSONDecodeError:
        return None, [
            ContractValidationError(
                field="body",
                message="Body must be valid JSON.",
                code="INVALID_JSON",
            )
        ]


def validate_request(
    payload: Any,
) -> tuple[KnowledgeAssistantRequest | None, list[ContractValidationError]]:
    errors = _validate_object(payload, "body")
    if errors:
        return None, errors

    errors.extend(
        _validate_required_fields(
            payload,
            "body",
            frozenset(
                {
                    "contractVersion",
                    "correlationId",
                    "messages",
                }
            ),
        )
    )
    errors.extend(_validate_unknown_fields(payload, "body", _REQUEST_FIELDS))
    errors.extend(_validate_contract_version(payload))
    errors.extend(_validate_identifier(payload, "correlationId"))

    if "conversationId" in payload:
        errors.extend(_validate_identifier(payload, "conversationId"))

    messages: list[Message] = []
    if "messages" in payload:
        messages, message_errors = _validate_messages(
            payload["messages"],
            allowed_role="user",
            field="messages",
        )
        errors.extend(message_errors)

    if errors:
        return None, errors

    conversation_id = None
    if "conversationId" in payload:
        conversation_id = ConversationId(payload["conversationId"])

    return (
        KnowledgeAssistantRequest(
            contractVersion=payload["contractVersion"],
            correlationId=CorrelationId(payload["correlationId"]),
            conversationId=conversation_id,
            messages=messages,
        ),
        [],
    )


def validate_success_response(
    payload: Any,
) -> tuple[KnowledgeAssistantResponse | None, list[ContractValidationError]]:
    errors = _validate_object(payload, "body")
    if errors:
        return None, errors

    errors.extend(
        _validate_required_fields(
            payload,
            "body",
            _SUCCESS_RESPONSE_FIELDS,
        )
    )
    errors.extend(_validate_unknown_fields(payload, "body", _SUCCESS_RESPONSE_FIELDS))
    errors.extend(_validate_contract_version(payload))
    errors.extend(_validate_identifier(payload, "correlationId"))
    errors.extend(_validate_identifier(payload, "conversationId"))

    message = None
    if "message" in payload:
        messages, message_errors = _validate_messages(
            [payload["message"]],
            allowed_role="assistant",
            field="message",
        )
        errors.extend(message_errors)
        if messages:
            message = messages[0]

    service = None
    if "service" in payload:
        service, service_errors = _validate_service_metadata(payload["service"])
        errors.extend(service_errors)

    if errors:
        return None, errors

    return (
        KnowledgeAssistantResponse(
            contractVersion=payload["contractVersion"],
            correlationId=CorrelationId(payload["correlationId"]),
            conversationId=ConversationId(payload["conversationId"]),
            message=message,
            service=service,
        ),
        [],
    )


def validate_error_response(
    payload: Any,
) -> tuple[ErrorResponse | None, list[ContractValidationError]]:
    errors = _validate_object(payload, "body")
    if errors:
        return None, errors

    errors.extend(
        _validate_required_fields(
            payload,
            "body",
            _ERROR_RESPONSE_FIELDS,
        )
    )
    errors.extend(_validate_unknown_fields(payload, "body", _ERROR_RESPONSE_FIELDS))
    errors.extend(_validate_contract_version(payload))
    errors.extend(_validate_identifier(payload, "correlationId"))

    error_details: list[ErrorDetail] = []
    error_code = ""
    error_message = ""
    if "error" in payload:
        error_payload = payload["error"]
        errors.extend(_validate_object(error_payload, "error"))
        if isinstance(error_payload, dict):
            errors.extend(
                _validate_required_fields(
                    error_payload,
                    "error",
                    _ERROR_FIELDS,
                )
            )
            errors.extend(_validate_unknown_fields(error_payload, "error", _ERROR_FIELDS))
            error_code = error_payload.get("code", "")
            error_message = error_payload.get("message", "")
            errors.extend(_validate_non_empty_string(error_payload, "error.code"))
            errors.extend(_validate_non_empty_string(error_payload, "error.message"))
            error_details, detail_errors = _validate_error_details(
                error_payload.get("details"),
            )
            errors.extend(detail_errors)

    service = None
    if "service" in payload:
        service, service_errors = _validate_service_metadata(payload["service"])
        errors.extend(service_errors)

    if errors:
        return None, errors

    return (
        ErrorResponse(
            contractVersion=payload["contractVersion"],
            correlationId=CorrelationId(payload["correlationId"]),
            code=error_code,
            message=error_message,
            details=error_details,
            service=service,
        ),
        [],
    )


def _validate_object(value: Any, field: str) -> list[ContractValidationError]:
    if isinstance(value, dict):
        return []

    return [
        ContractValidationError(
            field=field,
            message="Value must be an object.",
        )
    ]


def _validate_required_fields(
    payload: dict[str, Any],
    field_prefix: str,
    required_fields: frozenset[str],
) -> list[ContractValidationError]:
    errors: list[ContractValidationError] = []

    for field_name in sorted(required_fields - payload.keys()):
        errors.append(
            ContractValidationError(
                field=_field_path(field_prefix, field_name),
                message="Field is required.",
                code="REQUIRED",
            )
        )

    return errors


def _validate_unknown_fields(
    payload: dict[str, Any],
    field_prefix: str,
    allowed_fields: frozenset[str],
) -> list[ContractValidationError]:
    errors: list[ContractValidationError] = []

    for field_name in sorted(payload.keys() - allowed_fields):
        errors.append(
            ContractValidationError(
                field=_field_path(field_prefix, field_name),
                message="Unknown field is not allowed.",
                code="UNKNOWN_FIELD",
            )
        )

    return errors


def _validate_contract_version(
    payload: dict[str, Any],
) -> list[ContractValidationError]:
    if "contractVersion" not in payload:
        return []

    if payload["contractVersion"] != CONTRACT_VERSION:
        return [
            ContractValidationError(
                field="contractVersion",
                message="Unsupported contract version.",
                code="UNSUPPORTED_VERSION",
            )
        ]

    return []


def _validate_identifier(
    payload: dict[str, Any],
    field: str,
) -> list[ContractValidationError]:
    if field not in payload:
        return []

    value = payload[field]
    if (
        not isinstance(value, str)
        or not value
        or len(value) > _MAX_IDENTIFIER_LENGTH
        or not _IDENTIFIER_PATTERN.fullmatch(value)
    ):
        return [
            ContractValidationError(
                field=field,
                message=(
                    "Identifier must be 1-128 characters using letters, "
                    "numbers, period, underscore, colon, or hyphen."
                ),
            )
        ]

    return []


def _validate_messages(
    raw_messages: Any,
    allowed_role: str,
    field: str,
) -> tuple[list[Message], list[ContractValidationError]]:
    if not isinstance(raw_messages, list):
        return [], [
            ContractValidationError(
                field=field,
                message="Messages must be a list.",
            )
        ]

    if not raw_messages:
        return [], [
            ContractValidationError(
                field=field,
                message="At least one message is required.",
                code="REQUIRED",
            )
        ]

    if len(raw_messages) > _MAX_REQUEST_MESSAGES:
        return [], [
            ContractValidationError(
                field=field,
                message="Messages must not contain more than 20 entries.",
            )
        ]

    errors: list[ContractValidationError] = []
    messages: list[Message] = []

    for index, raw_message in enumerate(raw_messages):
        field_prefix = f"{field}[{index}]"
        if not isinstance(raw_message, dict):
            errors.append(
                ContractValidationError(
                    field=field_prefix,
                    message="Message must be an object.",
                )
            )
            continue

        errors.extend(
            _validate_required_fields(
                raw_message,
                field_prefix,
                _MESSAGE_FIELDS,
            )
        )
        errors.extend(_validate_unknown_fields(raw_message, field_prefix, _MESSAGE_FIELDS))

        role = raw_message.get("role")
        content = raw_message.get("content")

        if role != allowed_role:
            errors.append(
                ContractValidationError(
                    field=f"{field_prefix}.role",
                    message=f"Message role must be '{allowed_role}'.",
                )
            )

        if (
            not isinstance(content, str)
            or not content.strip()
            or len(content) > _MAX_MESSAGE_LENGTH
        ):
            errors.append(
                ContractValidationError(
                    field=f"{field_prefix}.content",
                    message="Message content must be 1-8000 characters.",
                )
            )

        if not errors:
            messages.append(Message(role=role, content=content))

    if errors:
        return [], errors

    return messages, []


def _validate_service_metadata(
    payload: Any,
) -> tuple[ServiceMetadata | None, list[ContractValidationError]]:
    errors = _validate_object(payload, "service")
    if errors:
        return None, errors

    errors.extend(_validate_required_fields(payload, "service", _SERVICE_FIELDS))
    errors.extend(_validate_unknown_fields(payload, "service", _SERVICE_FIELDS))

    if payload.get("name") != SERVICE_NAME:
        errors.append(
            ContractValidationError(
                field="service.name",
                message="Service name is unsupported.",
                code="UNSUPPORTED_SERVICE",
            )
        )

    if payload.get("contractVersion") != CONTRACT_VERSION:
        errors.append(
            ContractValidationError(
                field="service.contractVersion",
                message="Unsupported contract version.",
                code="UNSUPPORTED_VERSION",
            )
        )

    if errors:
        return None, errors

    return (
        ServiceMetadata(
            name=payload["name"],
            contractVersion=payload["contractVersion"],
        ),
        [],
    )


def _validate_error_details(
    payload: Any,
) -> tuple[list[ErrorDetail], list[ContractValidationError]]:
    if not isinstance(payload, list):
        return [], [
            ContractValidationError(
                field="error.details",
                message="Error details must be a list.",
            )
        ]

    errors: list[ContractValidationError] = []
    details: list[ErrorDetail] = []

    for index, detail in enumerate(payload):
        field_prefix = f"error.details[{index}]"
        if not isinstance(detail, dict):
            errors.append(
                ContractValidationError(
                    field=field_prefix,
                    message="Error detail must be an object.",
                )
            )
            continue

        errors.extend(
            _validate_required_fields(
                detail,
                field_prefix,
                _ERROR_DETAIL_FIELDS,
            )
        )
        errors.extend(
            _validate_unknown_fields(
                detail,
                field_prefix,
                _ERROR_DETAIL_FIELDS,
            )
        )
        errors.extend(_validate_non_empty_string(detail, f"{field_prefix}.field"))
        errors.extend(_validate_non_empty_string(detail, f"{field_prefix}.message"))
        errors.extend(_validate_non_empty_string(detail, f"{field_prefix}.code"))

        if not errors:
            details.append(
                ErrorDetail(
                    field=detail["field"],
                    message=detail["message"],
                    code=detail["code"],
                )
            )

    if errors:
        return [], errors

    return details, []


def _validate_non_empty_string(
    payload: dict[str, Any],
    field: str,
) -> list[ContractValidationError]:
    field_name = field.rsplit(".", 1)[-1]
    if field_name not in payload:
        return []

    value = payload[field_name]
    if not isinstance(value, str) or not value.strip():
        return [
            ContractValidationError(
                field=field,
                message="Value must be a non-empty string.",
            )
        ]

    return []


def _field_path(prefix: str, field: str) -> str:
    if prefix == "body":
        return field

    return f"{prefix}.{field}"


class DuplicateKeyError(ValueError):
    def __init__(self, key: str):
        super().__init__(key)
        self.key = key
        self.field = key


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}

    for key, value in pairs:
        if key in parsed:
            raise DuplicateKeyError(key)
        parsed[key] = value

    return parsed
