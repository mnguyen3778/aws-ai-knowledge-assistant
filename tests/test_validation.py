import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assessment.config import AssessmentVersionConfig  # noqa: E402
from assessment.validation import validate_assessment_request  # noqa: E402


def valid_payload():
    return {
        "assessmentVersion": "nguyen-ai-readiness-v1",
        "organization": {
            "name": "Nguyen AI",
        },
        "respondent": {
            "role": "Founder",
        },
        "answers": {
            "future.question.1": 3,
        },
    }


class AssessmentValidationTests(unittest.TestCase):
    def test_valid_mapping_request_passes(self):
        payload = json.dumps(valid_payload())
        result = validate_assessment_request(payload)
        second_result = validate_assessment_request(payload)

        self.assertTrue(result.is_valid)
        self.assertEqual(result, second_result)
        self.assertEqual(result.request.answers, {"future.question.1": 3})

    def test_valid_list_request_passes_and_normalizes_answers(self):
        payload = valid_payload()
        payload["answers"] = [
            {
                "questionId": "future.question.1",
                "value": 3,
            }
        ]

        result = validate_assessment_request(json.dumps(payload))

        self.assertTrue(result.is_valid)
        self.assertEqual(result.request.answers, {"future.question.1": 3})

    def test_invalid_json_returns_structured_error(self):
        result = validate_assessment_request("{")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "INVALID_JSON")

    def test_missing_required_field_returns_structured_error(self):
        payload = valid_payload()
        del payload["answers"]

        result = validate_assessment_request(json.dumps(payload))

        self.assertFalse(result.is_valid)
        self.assertIn("answers", [error.field for error in result.errors])

    def test_unsupported_version_returns_structured_error(self):
        payload = valid_payload()
        payload["assessmentVersion"] = "unknown"

        result = validate_assessment_request(json.dumps(payload))

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "UNSUPPORTED_VERSION")

    def test_answer_values_must_be_numeric(self):
        payload = valid_payload()
        payload["answers"] = {
            "future.question.1": "high",
        }

        result = validate_assessment_request(json.dumps(payload))

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].field, "answers.future.question.1")

    def test_duplicate_question_ids_are_rejected_for_list_answers(self):
        payload = valid_payload()
        payload["answers"] = [
            {
                "questionId": "future.question.1",
                "value": 1,
            },
            {
                "questionId": "future.question.1",
                "value": 2,
            },
        ]

        result = validate_assessment_request(json.dumps(payload))

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "DUPLICATE_QUESTION_ID")

    def test_duplicate_question_ids_are_rejected_for_mapping_answers(self):
        raw_payload = """
        {
            "assessmentVersion": "nguyen-ai-readiness-v1",
            "organization": {},
            "respondent": {},
            "answers": {
                "future.question.1": 1,
                "future.question.1": 2
            }
        }
        """

        result = validate_assessment_request(raw_payload)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "DUPLICATE_FIELD")

    def test_unknown_top_level_field_is_rejected(self):
        payload = valid_payload()
        payload["unexpected"] = True

        result = validate_assessment_request(json.dumps(payload))

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "UNKNOWN_FIELD")

    def test_future_version_can_be_enabled_by_configuration(self):
        future_config = AssessmentVersionConfig(
            version="future-readiness-v2",
            required_fields=frozenset(
                {
                    "assessmentVersion",
                    "answers",
                }
            ),
            allowed_fields=frozenset(
                {
                    "assessmentVersion",
                    "answers",
                    "metadata",
                }
            ),
            object_fields=frozenset(
                {
                    "metadata",
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
        )
        payload = {
            "assessmentVersion": "future-readiness-v2",
            "metadata": {},
            "answers": {
                "future.question.1": 1,
            },
        }

        with patch.dict(
            "assessment.config.ASSESSMENT_CONFIGS",
            {
                "future-readiness-v2": future_config,
            },
        ):
            result = validate_assessment_request(json.dumps(payload))

        self.assertTrue(result.is_valid)
        self.assertEqual(result.request.assessment_version, "future-readiness-v2")


if __name__ == "__main__":
    unittest.main()
