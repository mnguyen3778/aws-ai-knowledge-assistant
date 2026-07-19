from assessment.models import (
    AssessmentRequest,
    AssessmentResponse,
    ReadinessLevel,
)


# TODO: Replace these placeholders with the canonical Nguyen-AI Question Bank.
QUESTION_MAPPINGS: dict[str, str] = {}

# TODO: Map canonical question IDs to official Nguyen-AI categories.
CATEGORY_MAPPINGS: dict[str, str] = {}

# TODO: Add official Nguyen-AI question/category weights.
WEIGHTS: dict[str, float] = {}

# TODO: Add official Nguyen-AI readiness-level thresholds.
THRESHOLDS: dict[str, tuple[float, float]] = {}

# TODO: Add official Nguyen-AI recommendation mappings.
RECOMMENDATION_MAPPINGS: dict[str, str] = {}


def score_assessment(request: AssessmentRequest) -> AssessmentResponse:
    """Return a deterministic placeholder until the official rubric is supplied."""
    # TODO: Calculate normalized score from canonical mappings, weights, and thresholds.
    # TODO: Populate categoryScores from official Nguyen-AI categories.
    # TODO: Populate recommendations from official recommendation mappings.
    return AssessmentResponse(
        requestId="",
        assessmentVersion=request.assessment_version,
        overallScore=0,
        readinessLevel=ReadinessLevel(
            id="pending-rubric",
            label="Pending Official Rubric",
            description=(
                "Deterministic scoring is not available until the official "
                "Nguyen-AI rubric is provided."
            ),
        ),
        categoryScores=[],
        recommendations=[],
        modelInvoked=False,
        persisted=False,
    )
