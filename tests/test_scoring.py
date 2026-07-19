import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assessment.models import AssessmentRequest  # noqa: E402
from assessment.scoring import (  # noqa: E402
    CATEGORY_MAPPINGS,
    QUESTION_MAPPINGS,
    RECOMMENDATION_MAPPINGS,
    THRESHOLDS,
    WEIGHTS,
    score_assessment,
)


class AssessmentScoringTests(unittest.TestCase):
    def test_scoring_placeholders_are_empty_until_official_rubric_exists(self):
        self.assertEqual(QUESTION_MAPPINGS, {})
        self.assertEqual(CATEGORY_MAPPINGS, {})
        self.assertEqual(WEIGHTS, {})
        self.assertEqual(THRESHOLDS, {})
        self.assertEqual(RECOMMENDATION_MAPPINGS, {})

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


if __name__ == "__main__":
    unittest.main()
