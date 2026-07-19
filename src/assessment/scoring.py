from assessment.config import AssessmentVersionConfig, get_assessment_config
from assessment.models import AssessmentRequest, AssessmentResponse, ReadinessLevel


def score_assessment(request: AssessmentRequest) -> AssessmentResponse:
    """Return a deterministic placeholder until the official rubric is supplied."""
    config = get_assessment_config(request.assessment_version)
    if config is None:
        config = _unsupported_version_config(request.assessment_version)

    # TODO: Calculate normalized score from canonical mappings, weights, and thresholds.
    # TODO: Populate categoryScores from official Nguyen-AI categories.
    # TODO: Populate recommendations from official recommendation mappings.
    placeholder = config.placeholder_result
    return AssessmentResponse(
        requestId="",
        assessmentVersion=request.assessment_version,
        overallScore=placeholder.overall_score,
        readinessLevel=ReadinessLevel(
            id=placeholder.readiness_level_id,
            label=placeholder.readiness_level_label,
            description=placeholder.readiness_level_description,
        ),
        categoryScores=list(placeholder.category_scores),
        recommendations=list(placeholder.recommendations),
        modelInvoked=False,
        persisted=False,
    )


def _unsupported_version_config(version: str) -> AssessmentVersionConfig:
    # This path is defensive. Normal request handling rejects unsupported
    # versions during validation before scoring is called.
    return AssessmentVersionConfig(
        version=version,
        required_fields=frozenset(),
        allowed_fields=frozenset(),
        object_fields=frozenset(),
        answer_entry_required_fields=frozenset(),
        answer_entry_allowed_fields=frozenset(),
    )
