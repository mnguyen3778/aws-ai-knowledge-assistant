import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assessment.config import (  # noqa: E402
    ASSESSMENT_CONFIGS,
    NGUYEN_AI_READINESS_V1,
    get_assessment_config,
    supported_assessment_versions,
)


class AssessmentConfigTests(unittest.TestCase):
    def test_config_loads_supported_version(self):
        config = get_assessment_config("nguyen-ai-readiness-v1")

        self.assertIs(config, NGUYEN_AI_READINESS_V1)
        self.assertIn("nguyen-ai-readiness-v1", supported_assessment_versions())

    def test_config_is_single_source_for_placeholder_rubric_data(self):
        config = ASSESSMENT_CONFIGS["nguyen-ai-readiness-v1"]

        self.assertEqual(config.question_definitions, {})
        self.assertEqual(config.category_definitions, {})
        self.assertEqual(config.weights, {})
        self.assertEqual(config.thresholds, {})
        self.assertEqual(config.recommendation_mappings, {})
        self.assertEqual(config.placeholder_result.overall_score, 0)
        self.assertEqual(
            config.placeholder_result.readiness_level_id,
            "pending-rubric",
        )


if __name__ == "__main__":
    unittest.main()

