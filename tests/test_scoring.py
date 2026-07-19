import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assessment.config import (  # noqa: E402
    AssessmentVersionConfig,
    PlaceholderScoreResult,
)
from assessment.models import AssessmentRequest  # noqa: E402
from assessment.scoring import score_assessment  # noqa: E402


class AssessmentScoringTests(unittest.TestCase):
    def test_score_assessment_returns_deterministic_placeholder(self):
        request = AssessmentRequest(
            assessment_version="nguyen-ai-readiness-v1",
            organization={},
            respondent={},
            answers={
                "future.question.1": 3,
            },
        )

        first_response = score_assessment(request)
        second_response = score_assessment(request)

        self.assertEqual(first_response, second_response)
        self.assertEqual(first_response.requestId, "")
        self.assertEqual(first_response.assessmentVersion, "nguyen-ai-readiness-v1")
        self.assertEqual(first_response.overallScore, 0)
        self.assertEqual(first_response.readinessLevel.id, "pending-rubric")
        self.assertEqual(first_response.categoryScores, [])
        self.assertEqual(first_response.recommendations, [])
        self.assertFalse(first_response.modelInvoked)
        self.assertFalse(first_response.persisted)

    def test_score_assessment_consumes_version_configuration(self):
        future_config = AssessmentVersionConfig(
            version="future-readiness-v2",
            required_fields=frozenset(),
            allowed_fields=frozenset(),
            object_fields=frozenset(),
            answer_entry_required_fields=frozenset(),
            answer_entry_allowed_fields=frozenset(),
            placeholder_result=PlaceholderScoreResult(
                overall_score=0,
                readiness_level_id="future-pending-rubric",
                readiness_level_label="Future Pending Official Rubric",
                readiness_level_description="Future rubric placeholder.",
            ),
        )
        request = AssessmentRequest(
            assessment_version="future-readiness-v2",
            organization={},
            respondent={},
            answers={
                "future.question.1": 3,
            },
        )

        with patch.dict(
            "assessment.config.ASSESSMENT_CONFIGS",
            {
                "future-readiness-v2": future_config,
            },
        ):
            response = score_assessment(request)

        self.assertEqual(response.assessmentVersion, "future-readiness-v2")
        self.assertEqual(response.readinessLevel.id, "future-pending-rubric")


if __name__ == "__main__":
    unittest.main()
