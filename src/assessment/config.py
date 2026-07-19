from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class PlaceholderScoreResult:
    overall_score: float
    readiness_level_id: str
    readiness_level_label: str
    readiness_level_description: str
    category_scores: tuple[Any, ...] = ()
    recommendations: tuple[Any, ...] = ()


@dataclass(frozen=True)
class AssessmentVersionConfig:
    version: str
    required_fields: frozenset[str]
    allowed_fields: frozenset[str]
    object_fields: frozenset[str]
    answer_entry_required_fields: frozenset[str]
    answer_entry_allowed_fields: frozenset[str]
    question_definitions: Mapping[str, Any] = field(default_factory=dict)
    category_definitions: Mapping[str, Any] = field(default_factory=dict)
    weights: Mapping[str, Any] = field(default_factory=dict)
    thresholds: Mapping[str, Any] = field(default_factory=dict)
    recommendation_mappings: Mapping[str, Any] = field(default_factory=dict)
    placeholder_result: PlaceholderScoreResult = field(
        default_factory=lambda: PlaceholderScoreResult(
            overall_score=0,
            readiness_level_id="pending-rubric",
            readiness_level_label="Pending Official Rubric",
            readiness_level_description=(
                "Deterministic scoring is not available until the official "
                "Nguyen-AI rubric is provided."
            ),
        )
    )

    def __post_init__(self) -> None:
        missing_allowed_fields = self.required_fields - self.allowed_fields
        if missing_allowed_fields:
            raise ValueError("Required fields must also be allowed fields.")

        missing_answer_fields = (
            self.answer_entry_required_fields
            - self.answer_entry_allowed_fields
        )
        if missing_answer_fields:
            raise ValueError("Required answer fields must also be allowed fields.")


NGUYEN_AI_READINESS_V1 = AssessmentVersionConfig(
    version="nguyen-ai-readiness-v1",
    required_fields=frozenset(
        {
            "assessmentVersion",
            "organization",
            "respondent",
            "answers",
        }
    ),
    allowed_fields=frozenset(
        {
            "assessmentVersion",
            "organization",
            "respondent",
            "answers",
        }
    ),
    object_fields=frozenset(
        {
            "organization",
            "respondent",
        }
    ),
    answer_entry_required_fields=frozenset(
        {
            "questionId",
            "value",
        }
    ),
    answer_entry_allowed_fields=frozenset(
        {
            "questionId",
            "value",
        }
    ),
    # TODO: Populate from the canonical Nguyen-AI Question Bank.
    question_definitions=MappingProxyType({}),
    # TODO: Populate with official Nguyen-AI category definitions.
    category_definitions=MappingProxyType({}),
    # TODO: Populate with official Nguyen-AI question/category weights.
    weights=MappingProxyType({}),
    # TODO: Populate with official Nguyen-AI readiness thresholds.
    thresholds=MappingProxyType({}),
    # TODO: Populate with official Nguyen-AI recommendation mappings.
    recommendation_mappings=MappingProxyType({}),
)


ASSESSMENT_CONFIGS: dict[str, AssessmentVersionConfig] = {
    NGUYEN_AI_READINESS_V1.version: NGUYEN_AI_READINESS_V1,
}


def get_assessment_config(version: str) -> AssessmentVersionConfig | None:
    return ASSESSMENT_CONFIGS.get(version)


def supported_assessment_versions() -> frozenset[str]:
    return frozenset(ASSESSMENT_CONFIGS)
