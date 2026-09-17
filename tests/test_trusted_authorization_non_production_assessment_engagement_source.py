import ast
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_engagement_source as source_module  # noqa: E402
from trusted_authorization.models import AuthorityRecordState  # noqa: E402
from trusted_authorization.non_production_assessment_engagement_source import (  # noqa: E402
    NonProductionAssessmentEngagementAuthorityEvidence,
    NonProductionAssessmentEngagementAuthoritySource,
    NonProductionAssessmentEngagementLifecycleState,
    NonProductionAssessmentEngagementLookupStatus,
)


FOUND = NonProductionAssessmentEngagementLookupStatus.FOUND
NOT_FOUND = NonProductionAssessmentEngagementLookupStatus.NOT_FOUND
NON_CURRENT = NonProductionAssessmentEngagementLookupStatus.NON_CURRENT
STALE = NonProductionAssessmentEngagementLookupStatus.STALE
AMBIGUOUS = NonProductionAssessmentEngagementLookupStatus.AMBIGUOUS
CONFLICTING = NonProductionAssessmentEngagementLookupStatus.CONFLICTING
MALFORMED = NonProductionAssessmentEngagementLookupStatus.MALFORMED
CURRENT = NonProductionAssessmentEngagementLifecycleState.CURRENT
CANDIDATE = NonProductionAssessmentEngagementLifecycleState.CANDIDATE
NO_LONGER_CURRENT = NonProductionAssessmentEngagementLifecycleState.NON_CURRENT


def engagement(
    authority_reference="engagement-alpha-authority",
    state=AuthorityRecordState.ACTIVE,
    engagement_reference="engagement-alpha",
    business_entity_id="business-alpha",
    lifecycle_state=CURRENT,
    establishment_provenance_reference="establishment-alpha-provenance",
):
    return NonProductionAssessmentEngagementAuthorityEvidence(
        authority_reference=authority_reference,
        state=state,
        engagement_reference=engagement_reference,
        business_entity_id=business_entity_id,
        lifecycle_state=lifecycle_state,
        establishment_provenance_reference=establishment_provenance_reference,
    )


def source_with(*records):
    return NonProductionAssessmentEngagementAuthoritySource(records)


class NonProductionAssessmentEngagementAuthoritySourceTests(unittest.TestCase):
    def test_01_valid_current_e_to_b_resolution_returns_found(self):
        result = source_with(engagement()).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, FOUND)
        self.assertEqual(len(result.records), 1)

    def test_02_found_output_contains_correct_engagement_reference(self):
        result = source_with(engagement()).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.records[0].engagement_reference, "engagement-alpha")

    def test_03_found_output_contains_authoritative_business_entity(self):
        result = source_with(engagement()).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.records[0].business_entity_id, "business-alpha")

    def test_04_found_output_preserves_establishment_provenance(self):
        result = source_with(engagement()).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(
            result.records[0].establishment_provenance_reference,
            "establishment-alpha-provenance",
        )

    def test_05_authority_record_state_and_lifecycle_are_distinct(self):
        stale_authority = source_with(
            engagement(state=AuthorityRecordState.STALE, lifecycle_state=CURRENT)
        )
        candidate_lifecycle = source_with(
            engagement(state=AuthorityRecordState.ACTIVE, lifecycle_state=CANDIDATE)
        )

        stale = stale_authority.resolve_assessment_engagement("engagement-alpha")
        candidate = candidate_lifecycle.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(stale.status, STALE)
        self.assertEqual(candidate.status, NON_CURRENT)

    def test_06_unknown_e_returns_not_found(self):
        result = source_with(engagement()).resolve_assessment_engagement("engagement-missing")

        self.assertEqual(result.status, NOT_FOUND)
        self.assertEqual(result.records, ())

    def test_07_empty_e_returns_malformed(self):
        result = source_with(engagement()).resolve_assessment_engagement("")

        self.assertEqual(result.status, MALFORMED)

    def test_08_blank_e_returns_malformed(self):
        result = source_with(engagement()).resolve_assessment_engagement("   ")

        self.assertEqual(result.status, MALFORMED)

    def test_09_leading_whitespace_e_returns_malformed(self):
        result = source_with(engagement()).resolve_assessment_engagement(" engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_10_trailing_whitespace_e_returns_malformed(self):
        result = source_with(engagement()).resolve_assessment_engagement("engagement-alpha ")

        self.assertEqual(result.status, MALFORMED)

    def test_11_str_subclass_query_returns_malformed_without_behavior(self):
        class HostileStr(str):
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        result = source_with(engagement()).resolve_assessment_engagement(
            HostileStr("engagement-alpha")
        )

        self.assertEqual(result.status, MALFORMED)
        self.assertEqual(HostileStr.comparisons, 0)

    def test_12_bytes_query_returns_malformed(self):
        result = source_with(engagement()).resolve_assessment_engagement(b"engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_13_none_query_returns_malformed(self):
        result = source_with(engagement()).resolve_assessment_engagement(None)

        self.assertEqual(result.status, MALFORMED)

    def test_14_custom_str_query_rejected_without_string_conversion(self):
        class Hostile:
            conversions = 0

            def __str__(self):
                type(self).conversions += 1
                return "engagement-alpha"

        result = source_with(engagement()).resolve_assessment_engagement(Hostile())

        self.assertEqual(result.status, MALFORMED)
        self.assertEqual(Hostile.conversions, 0)

    def test_15_foreign_query_type_returns_malformed(self):
        class ForeignEngagement(Enum):
            ALPHA = "engagement-alpha"

        result = source_with(engagement()).resolve_assessment_engagement(ForeignEngagement.ALPHA)

        self.assertEqual(result.status, MALFORMED)

    def test_16_current_engagement_lifecycle_required_for_found(self):
        current = source_with(engagement(lifecycle_state=CURRENT))

        result = current.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, FOUND)

    def test_17_candidate_lifecycle_returns_non_current(self):
        result = source_with(
            engagement(lifecycle_state=CANDIDATE)
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, NON_CURRENT)
        self.assertEqual(result.records, ())

    def test_18_non_current_lifecycle_returns_non_current(self):
        result = source_with(
            engagement(lifecycle_state=NO_LONGER_CURRENT)
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, NON_CURRENT)
        self.assertEqual(result.records, ())

    def test_19_stale_or_non_current_authority_evidence_returns_stale(self):
        non_current_states = (
            AuthorityRecordState.INACTIVE,
            AuthorityRecordState.DISABLED,
            AuthorityRecordState.REVOKED,
            AuthorityRecordState.EXPIRED,
            AuthorityRecordState.TERMINATED,
            AuthorityRecordState.STALE,
            AuthorityRecordState.UNKNOWN,
        )
        for state in non_current_states:
            with self.subTest(state=state):
                result = source_with(
                    engagement(state=state, lifecycle_state=CURRENT)
                ).resolve_assessment_engagement("engagement-alpha")

                self.assertEqual(result.status, STALE)
                self.assertNotEqual(result.status, FOUND)

    def test_20_one_business_entity_may_have_multiple_engagements(self):
        source = source_with(
            engagement(engagement_reference="engagement-alpha"),
            engagement(
                authority_reference="engagement-beta-authority",
                engagement_reference="engagement-beta",
                business_entity_id="business-alpha",
                establishment_provenance_reference="establishment-beta-provenance",
            ),
        )

        alpha = source.resolve_assessment_engagement("engagement-alpha")
        beta = source.resolve_assessment_engagement("engagement-beta")

        self.assertEqual(alpha.status, FOUND)
        self.assertEqual(beta.status, FOUND)
        self.assertEqual(alpha.records[0].business_entity_id, "business-alpha")
        self.assertEqual(beta.records[0].business_entity_id, "business-alpha")

    def test_21_same_b_engagements_remain_distinct(self):
        source = source_with(
            engagement(engagement_reference="engagement-alpha"),
            engagement(
                authority_reference="engagement-beta-authority",
                engagement_reference="engagement-beta",
                business_entity_id="business-alpha",
                establishment_provenance_reference="establishment-beta-provenance",
            ),
        )

        alpha = source.resolve_assessment_engagement("engagement-alpha")
        beta = source.resolve_assessment_engagement("engagement-beta")

        self.assertNotEqual(alpha.records[0].engagement_reference, beta.records[0].engagement_reference)
        self.assertEqual(alpha.records[0].business_entity_id, beta.records[0].business_entity_id)

    def test_22_same_b_resolution_does_not_claim_context_legitimacy(self):
        result = source_with(engagement()).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, FOUND)
        self.assertFalse(hasattr(result.records[0], "context_legitimate"))
        self.assertFalse(hasattr(result.records[0], "valid_for_request"))

    def test_23_cross_b_resolution_preserves_authoritative_b(self):
        source = source_with(
            engagement(engagement_reference="engagement-alpha", business_entity_id="business-alpha"),
            engagement(
                authority_reference="engagement-beta-authority",
                engagement_reference="engagement-beta",
                business_entity_id="business-beta",
                establishment_provenance_reference="establishment-beta-provenance",
            ),
        )

        result = source.resolve_assessment_engagement("engagement-beta")

        self.assertEqual(result.status, FOUND)
        self.assertEqual(result.records[0].business_entity_id, "business-beta")

    def test_24_e_to_multiple_b_returns_conflicting(self):
        result = source_with(
            engagement(),
            engagement(business_entity_id="business-beta"),
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, CONFLICTING)
        self.assertEqual(result.records, ())

    def test_25_rebinding_b1_to_b2_returns_conflicting(self):
        result = source_with(
            engagement(business_entity_id="business-original"),
            engagement(business_entity_id="business-correction"),
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, CONFLICTING)

    def test_26_conflicting_lifecycle_returns_conflicting(self):
        result = source_with(
            engagement(lifecycle_state=CURRENT),
            engagement(lifecycle_state=NO_LONGER_CURRENT),
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, CONFLICTING)

    def test_27_conflicting_provenance_returns_conflicting(self):
        result = source_with(
            engagement(establishment_provenance_reference="establishment-alpha-provenance"),
            engagement(establishment_provenance_reference="establishment-beta-provenance"),
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, CONFLICTING)

    def test_28_conflicting_authority_reference_returns_conflicting(self):
        result = source_with(
            engagement(authority_reference="engagement-alpha-authority"),
            engagement(authority_reference="engagement-beta-authority"),
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, CONFLICTING)

    def test_29_identical_duplicate_evidence_returns_ambiguous(self):
        result = source_with(engagement(), engagement()).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, AMBIGUOUS)
        self.assertEqual(result.records, ())

    def test_30_duplicate_evidence_is_not_first_or_last_selected(self):
        source = source_with(engagement(), engagement())

        first = source.resolve_assessment_engagement("engagement-alpha")
        second = source.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(first.status, AMBIGUOUS)
        self.assertEqual(second.status, AMBIGUOUS)
        self.assertNotEqual(first.status, FOUND)

    def test_31_malformed_authority_reference_poisons_source(self):
        result = source_with(
            engagement(authority_reference=" bad-authority")
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_32_malformed_engagement_reference_poisons_source(self):
        result = source_with(
            engagement(engagement_reference="engagement-alpha ")
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_33_malformed_business_entity_id_poisons_source(self):
        result = source_with(
            engagement(business_entity_id="")
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_34_malformed_establishment_provenance_poisons_source(self):
        result = source_with(
            engagement(establishment_provenance_reference="\t")
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_35_malformed_lifecycle_poisons_source(self):
        result = source_with(
            engagement(lifecycle_state="CURRENT")
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_36_malformed_authority_state_poisons_source(self):
        result = source_with(
            engagement(state="ACTIVE")
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_37_record_subclass_rejected_and_poisons_source(self):
        class EvidenceSubclass(NonProductionAssessmentEngagementAuthorityEvidence):
            pass

        record = EvidenceSubclass(
            "engagement-alpha-authority",
            AuthorityRecordState.ACTIVE,
            "engagement-alpha",
            "business-alpha",
            CURRENT,
            "establishment-alpha-provenance",
        )
        result = source_with(record).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_38_foreign_record_rejected_and_poisons_source(self):
        result = source_with(object()).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_39_collection_hostile_subclass_defense(self):
        class HostileList(list):
            iter_calls = 0

            def __iter__(self):
                type(self).iter_calls += 1
                return super().__iter__()

        records = HostileList([engagement()])
        source = NonProductionAssessmentEngagementAuthoritySource(records)
        records.append(engagement(engagement_reference="engagement-beta"))

        alpha = source.resolve_assessment_engagement("engagement-alpha")
        beta = source.resolve_assessment_engagement("engagement-beta")

        self.assertEqual(HostileList.iter_calls, 1)
        self.assertEqual(alpha.status, FOUND)
        self.assertEqual(beta.status, NOT_FOUND)

    def test_40_constructor_consumes_generator_once(self):
        calls = {"count": 0}

        def records():
            calls["count"] += 1
            yield engagement()

        source = NonProductionAssessmentEngagementAuthoritySource(records())
        first = source.resolve_assessment_engagement("engagement-alpha")
        second = source.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(calls["count"], 1)
        self.assertEqual(first.status, FOUND)
        self.assertEqual(second.status, FOUND)

    def test_41_caller_collection_mutation_cannot_change_result(self):
        records = [engagement()]
        source = NonProductionAssessmentEngagementAuthoritySource(records)
        records.clear()
        records.append(engagement(engagement_reference="engagement-beta"))

        self.assertEqual(source.resolve_assessment_engagement("engagement-alpha").status, FOUND)
        self.assertEqual(source.resolve_assessment_engagement("engagement-beta").status, NOT_FOUND)

    def test_42_caller_record_mutation_attack_cannot_change_result(self):
        record = engagement()
        source = source_with(record)
        object.__setattr__(record, "business_entity_id", "business-forged")
        object.__setattr__(record, "lifecycle_state", NO_LONGER_CURRENT)

        result = source.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, FOUND)
        self.assertEqual(result.records[0].business_entity_id, "business-alpha")
        self.assertEqual(result.records[0].lifecycle_state, CURRENT)

    def test_43_stored_string_subclass_spoof_attack_rejected(self):
        class HostileStr(str):
            pass

        result = source_with(
            engagement(business_entity_id=HostileStr("business-alpha"))
        ).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)

    def test_44_forged_dict_or_field_spoof_subclass_rejected(self):
        class SpoofedEvidence(NonProductionAssessmentEngagementAuthorityEvidence):
            field_reads = 0

            def __getattribute__(self, name):
                if name == "business_entity_id":
                    type(self).field_reads += 1
                    return "business-alpha"
                return object.__getattribute__(self, name)

        record = SpoofedEvidence(
            "engagement-alpha-authority",
            AuthorityRecordState.ACTIVE,
            "engagement-alpha",
            "business-spoofed",
            CURRENT,
            "establishment-alpha-provenance",
        )
        result = source_with(record).resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(result.status, MALFORMED)
        self.assertEqual(SpoofedEvidence.field_reads, 0)

    def test_45_found_output_is_fresh_each_lookup(self):
        source = source_with(engagement())

        first = source.resolve_assessment_engagement("engagement-alpha")
        second = source.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(first.status, FOUND)
        self.assertEqual(second.status, FOUND)
        self.assertIsNot(first.records[0], second.records[0])
        self.assertIsNot(first.records[0], source._records[0])
        self.assertIsNot(second.records[0], source._records[0])

    def test_46_output_mutation_attack_cannot_alter_future_result(self):
        source = source_with(engagement())
        first = source.resolve_assessment_engagement("engagement-alpha")
        object.__setattr__(first.records[0], "business_entity_id", "business-forged")

        second = source.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(second.status, FOUND)
        self.assertEqual(second.records[0].business_entity_id, "business-alpha")

    def test_47_repeated_lookup_is_deterministic(self):
        source = source_with(engagement())

        first = source.resolve_assessment_engagement("engagement-alpha")
        second = source.resolve_assessment_engagement("engagement-alpha")

        self.assertEqual(first, second)
        self.assertEqual(first.status, FOUND)

    def test_48_source_has_no_forbidden_authority_dependencies(self):
        tree = ast.parse(Path(source_module.__file__).read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
                imported.update(alias.name for alias in node.names)

        forbidden = (
            "membership",
            "entitlement",
            "principal",
            "resource_identity",
            "evaluator",
            "applicability",
            "runtime",
            "authenticated",
            "target",
            "business_context",
            "aws",
            "cognito",
            "bedrock",
            "model_provider",
        )
        lowered = "\n".join(imported).lower()
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, lowered)

    def test_49_source_exposes_no_management_or_mutation_api_surface(self):
        forbidden = (
            "create",
            "establish",
            "approve",
            "activate",
            "close",
            "revoke",
            "restore",
            "update",
            "delete",
            "assign",
            "authorize",
            "permit",
            "submit",
        )
        public_callables = {
            name
            for name, value in inspect.getmembers(
                NonProductionAssessmentEngagementAuthoritySource,
                predicate=callable,
            )
            if not name.startswith("_")
        }

        self.assertEqual(public_callables, {"resolve_assessment_engagement"})
        for token in forbidden:
            with self.subTest(token=token):
                self.assertFalse(any(token in name.lower() for name in public_callables))

    def test_50_no_permission_context_business_target_or_runtime_semantic_surface(self):
        public_names = [
            name
            for name in dir(source_module)
            if not name.startswith("_")
        ]
        public_names.extend(status.name for status in NonProductionAssessmentEngagementLookupStatus)
        public_names.extend(status.value for status in NonProductionAssessmentEngagementLookupStatus)
        surface = "\n".join(public_names).lower()
        forbidden = (
            "allow",
            "deny",
            "authorized",
            "permitted",
            "valid_for_request",
            "context_ready",
            "business_context_ready",
            "target_legitimacy",
            "runtime",
        )

        self.assertFalse(hasattr(NonProductionAssessmentEngagementAuthoritySource, "context_legitimate"))
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, surface)


if __name__ == "__main__":
    unittest.main()
