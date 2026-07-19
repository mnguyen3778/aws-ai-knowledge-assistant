from dataclasses import dataclass
from typing import Any

from assessment.models import (
    AssessmentRequest,
    AssessmentResponse,
    CategoryScore,
    ReadinessLevel,
    Recommendation,
)


@dataclass(frozen=True)
class AnswerEntry:
    questionId: str
    value: float | int

    def to_dict(self) -> dict[str, Any]:
        return {
            "questionId": self.questionId,
            "value": self.value,
        }


REQUEST_REQUIRED_FIELDS = {
    "assessmentVersion",
    "organization",
    "respondent",
    "answers",
}

REQUEST_ALLOWED_FIELDS = REQUEST_REQUIRED_FIELDS

ANSWER_ENTRY_REQUIRED_FIELDS = {
    "questionId",
    "value",
}

ANSWER_ENTRY_ALLOWED_FIELDS = ANSWER_ENTRY_REQUIRED_FIELDS


__all__ = [
    "ANSWER_ENTRY_ALLOWED_FIELDS",
    "ANSWER_ENTRY_REQUIRED_FIELDS",
    "AnswerEntry",
    "AssessmentRequest",
    "AssessmentResponse",
    "CategoryScore",
    "ReadinessLevel",
    "Recommendation",
    "REQUEST_ALLOWED_FIELDS",
    "REQUEST_REQUIRED_FIELDS",
]

