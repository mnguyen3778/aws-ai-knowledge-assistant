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


ASSESSMENT_VERSION_FIELD = "assessmentVersion"
ANSWERS_FIELD = "answers"
ANSWER_ENTRY_QUESTION_ID_FIELD = "questionId"
ANSWER_ENTRY_VALUE_FIELD = "value"


__all__ = [
    "AnswerEntry",
    "AssessmentRequest",
    "AssessmentResponse",
    "ASSESSMENT_VERSION_FIELD",
    "ANSWER_ENTRY_QUESTION_ID_FIELD",
    "ANSWER_ENTRY_VALUE_FIELD",
    "ANSWERS_FIELD",
    "CategoryScore",
    "ReadinessLevel",
    "Recommendation",
]
