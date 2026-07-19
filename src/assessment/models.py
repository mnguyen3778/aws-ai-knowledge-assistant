from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationError:
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
class AssessmentRequest:
    assessment_version: str
    organization: dict[str, Any]
    respondent: dict[str, Any]
    answers: dict[str, float | int]
    source_payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AssessmentRequest":
        return cls(
            assessment_version=payload["assessmentVersion"],
            organization=payload.get("organization", {}),
            respondent=payload.get("respondent", {}),
            answers=payload["answers"],
            source_payload=payload,
        )


@dataclass(frozen=True)
class ReadinessLevel:
    id: str
    label: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
        }


@dataclass(frozen=True)
class CategoryScore:
    categoryId: str
    label: str
    score: float
    maxScore: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "categoryId": self.categoryId,
            "label": self.label,
            "score": self.score,
            "maxScore": self.maxScore,
        }


@dataclass(frozen=True)
class Recommendation:
    priority: int
    categoryId: str | None
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "priority": self.priority,
            "categoryId": self.categoryId,
            "summary": self.summary,
        }


@dataclass(frozen=True)
class AssessmentResponse:
    requestId: str
    assessmentVersion: str
    overallScore: float
    readinessLevel: ReadinessLevel
    categoryScores: list[CategoryScore] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    modelInvoked: bool = False
    persisted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "requestId": self.requestId,
            "assessmentVersion": self.assessmentVersion,
            "overallScore": self.overallScore,
            "readinessLevel": self.readinessLevel.to_dict(),
            "categoryScores": [
                category_score.to_dict()
                for category_score in self.categoryScores
            ],
            "recommendations": [
                recommendation.to_dict()
                for recommendation in self.recommendations
            ],
            "modelInvoked": self.modelInvoked,
            "persisted": self.persisted,
        }


@dataclass(frozen=True)
class ValidationResult:
    request: AssessmentRequest | None
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors and self.request is not None
