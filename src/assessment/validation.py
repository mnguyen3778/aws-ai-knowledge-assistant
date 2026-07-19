import json
from typing import Any

from assessment.models import (
    AssessmentRequest,
    SUPPORTED_ASSESSMENT_VERSIONS,
    ValidationError,
    ValidationResult,
)
from assessment.schema import (
    ANSWER_ENTRY_ALLOWED_FIELDS,
    ANSWER_ENTRY_REQUIRED_FIELDS,
    REQUEST_ALLOWED_FIELDS,
    REQUEST_REQUIRED_FIELDS,
)


def validate_assessment_request(raw_body: Any) -> ValidationResult:
    payload, errors = _parse_json(raw_body)
    if errors:
        return ValidationResult(request=None, errors=errors)

    errors.extend(_validate_top_level_payload(payload))
    if errors:
        return ValidationResult(request=None, errors=errors)

    answers, answer_errors = _normalize_answers(payload["answers"])
    errors.extend(answer_errors)
    if errors:
        return ValidationResult(request=None, errors=errors)

    normalized_payload = {
        **payload,
        "answers": answers,
    }
    return ValidationResult(
        request=AssessmentRequest.from_payload(normalized_payload),
        errors=[],
    )


def _parse_json(raw_body: Any) -> tuple[Any, list[ValidationError]]:
    if raw_body is None:
        return None, [
            ValidationError(
                field="body",
                message="Request body is required.",
                code="REQUIRED",
            )
        ]

    if isinstance(raw_body, dict):
        return raw_body, []

    if not isinstance(raw_body, str):
        return None, [
            ValidationError(
                field="body",
                message="Request body must be a JSON object string.",
            )
        ]

    try:
        return json.loads(raw_body, object_pairs_hook=_reject_duplicate_keys), []
    except DuplicateKeyError as exc:
        return None, [
            ValidationError(
                field=exc.field,
                message=f"Duplicate field '{exc.key}' is not allowed.",
                code="DUPLICATE_FIELD",
            )
        ]
    except json.JSONDecodeError:
        return None, [
            ValidationError(
                field="body",
                message="Request body must be valid JSON.",
                code="INVALID_JSON",
            )
        ]


def _validate_top_level_payload(payload: Any) -> list[ValidationError]:
    errors: list[ValidationError] = []

    if not isinstance(payload, dict):
        return [
            ValidationError(
                field="body",
                message="Request body must be a JSON object.",
            )
        ]

    for field_name in sorted(REQUEST_REQUIRED_FIELDS - payload.keys()):
        errors.append(
            ValidationError(
                field=field_name,
                message="Field is required.",
                code="REQUIRED",
            )
        )

    for field_name in sorted(payload.keys() - REQUEST_ALLOWED_FIELDS):
        errors.append(
            ValidationError(
                field=field_name,
                message="Unknown field is not allowed.",
                code="UNKNOWN_FIELD",
            )
        )

    assessment_version = payload.get("assessmentVersion")
    if (
        "assessmentVersion" in payload
        and assessment_version not in SUPPORTED_ASSESSMENT_VERSIONS
    ):
        errors.append(
            ValidationError(
                field="assessmentVersion",
                message="Unsupported assessment version.",
                code="UNSUPPORTED_VERSION",
            )
        )

    if "organization" in payload and not isinstance(payload["organization"], dict):
        errors.append(
            ValidationError(
                field="organization",
                message="Organization must be an object.",
            )
        )

    if "respondent" in payload and not isinstance(payload["respondent"], dict):
        errors.append(
            ValidationError(
                field="respondent",
                message="Respondent must be an object.",
            )
        )

    if "answers" in payload and not payload["answers"]:
        errors.append(
            ValidationError(
                field="answers",
                message="At least one answer is required.",
                code="REQUIRED",
            )
        )

    return errors


def _normalize_answers(raw_answers: Any) -> tuple[dict[str, float | int], list[ValidationError]]:
    if isinstance(raw_answers, dict):
        return _normalize_answer_map(raw_answers)

    if isinstance(raw_answers, list):
        return _normalize_answer_entries(raw_answers)

    return {}, [
        ValidationError(
            field="answers",
            message="Answers must be an object or a list of answer entries.",
        )
    ]


def _normalize_answer_map(
    raw_answers: dict[str, Any],
) -> tuple[dict[str, float | int], list[ValidationError]]:
    errors: list[ValidationError] = []
    answers: dict[str, float | int] = {}

    for question_id, value in raw_answers.items():
        field_path = f"answers.{question_id}"
        if not isinstance(question_id, str) or not question_id.strip():
            errors.append(
                ValidationError(
                    field="answers",
                    message="Question IDs must be non-empty strings.",
                )
            )
            continue

        if not _is_numeric_answer(value):
            errors.append(
                ValidationError(
                    field=field_path,
                    message="Answer value must be numeric.",
                )
            )
            continue

        answers[question_id] = value

    return answers, errors


def _normalize_answer_entries(
    raw_answers: list[Any],
) -> tuple[dict[str, float | int], list[ValidationError]]:
    errors: list[ValidationError] = []
    answers: dict[str, float | int] = {}
    seen_question_ids: set[str] = set()

    for index, entry in enumerate(raw_answers):
        entry_errors: list[ValidationError] = []
        field_prefix = f"answers[{index}]"
        if not isinstance(entry, dict):
            errors.append(
                ValidationError(
                    field=field_prefix,
                    message="Answer entry must be an object.",
                )
            )
            continue

        for field_name in sorted(ANSWER_ENTRY_REQUIRED_FIELDS - entry.keys()):
            entry_errors.append(
                ValidationError(
                    field=f"{field_prefix}.{field_name}",
                    message="Field is required.",
                    code="REQUIRED",
                )
            )

        for field_name in sorted(entry.keys() - ANSWER_ENTRY_ALLOWED_FIELDS):
            entry_errors.append(
                ValidationError(
                    field=f"{field_prefix}.{field_name}",
                    message="Unknown field is not allowed.",
                    code="UNKNOWN_FIELD",
                )
            )

        question_id = entry.get("questionId")
        value = entry.get("value")

        if "questionId" in entry and (
            not isinstance(question_id, str) or not question_id.strip()
        ):
            entry_errors.append(
                ValidationError(
                    field=f"{field_prefix}.questionId",
                    message="Question ID must be a non-empty string.",
                )
            )

        if isinstance(question_id, str) and question_id in seen_question_ids:
            entry_errors.append(
                ValidationError(
                    field=f"{field_prefix}.questionId",
                    message="Duplicate question ID is not allowed.",
                    code="DUPLICATE_QUESTION_ID",
                )
            )

        if "value" in entry and not _is_numeric_answer(value):
            entry_errors.append(
                ValidationError(
                    field=f"{field_prefix}.value",
                    message="Answer value must be numeric.",
                )
            )

        if entry_errors:
            errors.extend(entry_errors)
            continue

        seen_question_ids.add(question_id)
        answers[question_id] = value

    return answers, errors


def _is_numeric_answer(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


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
