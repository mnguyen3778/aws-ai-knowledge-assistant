import re
from typing import Any

from assistant_contract.v1 import (
    CorrelationId,
    ErrorDetail,
    ErrorResponse,
    KnowledgeAssistantResponse,
    ServiceMetadata,
    dumps_contract_json,
    parse_contract_json,
    validate_request,
)
from assistant_runtime import RuntimeDispatcher, create_runtime_composition_root


PUBLIC_ASSISTANT_ENDPOINT_PATH = "/v1/assistant"
_PUBLIC_ENDPOINT_PATTERN = re.compile(r"^/v(?P<version>[0-9]+)/assistant$")
_FALLBACK_CORRELATION_ID = "unavailable"
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_DEFAULT_RUNTIME_DISPATCHER = create_runtime_composition_root().initialize()


def is_public_assistant_endpoint_request(event: dict[str, Any]) -> bool:
    _, path = _extract_method_and_path(event)
    return _PUBLIC_ENDPOINT_PATTERN.fullmatch(path or "") is not None


def handle_public_assistant_endpoint(
    event: dict[str, Any],
    runtime_dispatcher: RuntimeDispatcher = _DEFAULT_RUNTIME_DISPATCHER,
) -> dict[str, Any]:
    method, path = _extract_method_and_path(event)
    payload, parse_errors = parse_contract_json(event.get("body"))
    correlation_id = _correlation_id_from_payload(payload)

    route_match = _PUBLIC_ENDPOINT_PATTERN.fullmatch(path or "")
    if route_match is None:
        return _contract_error_response(
            404,
            correlation_id,
            "ENDPOINT_NOT_FOUND",
            "Endpoint is not supported.",
            [
                ErrorDetail(
                    field="path",
                    message="Endpoint path is not supported.",
                    code="ENDPOINT_NOT_FOUND",
                )
            ],
        )

    if route_match.group("version") != "1":
        return _contract_error_response(
            400,
            correlation_id,
            "UNSUPPORTED_ENDPOINT_VERSION",
            "Endpoint version is not supported.",
            [
                ErrorDetail(
                    field="path",
                    message="Only /v1/assistant is supported.",
                    code="UNSUPPORTED_ENDPOINT_VERSION",
                )
            ],
        )

    if method != "POST":
        return _contract_error_response(
            405,
            correlation_id,
            "METHOD_NOT_ALLOWED",
            "HTTP method is not supported for this endpoint.",
            [
                ErrorDetail(
                    field="method",
                    message="Only POST is supported.",
                    code="METHOD_NOT_ALLOWED",
                )
            ],
        )

    if parse_errors:
        return _contract_error_response(
            400,
            correlation_id,
            "VALIDATION_ERROR",
            "Request payload is invalid.",
            [
                ErrorDetail(
                    field=error.field,
                    message=error.message,
                    code=error.code,
                )
                for error in parse_errors
            ],
        )

    request, validation_errors = validate_request(payload)
    if validation_errors:
        return _contract_error_response(
            400,
            correlation_id,
            "VALIDATION_ERROR",
            "Request payload is invalid.",
            [
                ErrorDetail(
                    field=error.field,
                    message=error.message,
                    code=error.code,
                )
                for error in validation_errors
            ],
        )

    response = runtime_dispatcher.dispatch(request)
    return _json_response(200, response)


def _contract_error_response(
    status_code: int,
    correlation_id: CorrelationId,
    code: str,
    message: str,
    details: list[ErrorDetail],
) -> dict[str, Any]:
    return _json_response(
        status_code,
        ErrorResponse(
            correlationId=correlation_id,
            code=code,
            message=message,
            details=details,
            service=ServiceMetadata(),
        ),
    )


def _json_response(status_code: int, body: KnowledgeAssistantResponse | ErrorResponse):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": dumps_contract_json(body),
    }


def _extract_method_and_path(event: dict[str, Any]) -> tuple[str | None, str | None]:
    method = event.get("httpMethod")
    path = event.get("path")

    if not method:
        http_context = event.get("requestContext", {}).get("http", {})
        method = http_context.get("method")
        path = event.get("rawPath")

    return method, path


def _correlation_id_from_payload(payload: Any) -> CorrelationId:
    if not isinstance(payload, dict):
        return CorrelationId(_FALLBACK_CORRELATION_ID)

    correlation_id = payload.get("correlationId")
    if (
        isinstance(correlation_id, str)
        and _IDENTIFIER_PATTERN.fullmatch(correlation_id)
    ):
        return CorrelationId(correlation_id)

    return CorrelationId(_FALLBACK_CORRELATION_ID)
