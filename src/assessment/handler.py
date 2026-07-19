from dataclasses import replace
import json
from typing import Any
from uuid import uuid4

from assessment.scoring import score_assessment
from assessment.validation import validate_assessment_request


def handle_assessment(event: dict[str, Any]) -> dict[str, Any]:
    request_id = str(uuid4())
    validation_result = validate_assessment_request(event.get("body"))

    if not validation_result.is_valid:
        return _json_response(
            400,
            {
                "requestId": request_id,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Assessment request is invalid.",
                    "details": [
                        error.to_dict()
                        for error in validation_result.errors
                    ],
                },
                "modelInvoked": False,
                "persisted": False,
            },
        )

    assessment_response = replace(
        score_assessment(validation_result.request),
        requestId=request_id,
    )
    return _json_response(200, assessment_response.to_dict())


def _json_response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body),
    }
