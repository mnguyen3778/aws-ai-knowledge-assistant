import ast
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization as trusted_authorization_package  # noqa: E402
import trusted_authorization.non_production_assessment_engagement_participation_source as source_module  # noqa: E402
from trusted_authorization.models import AuthorityRecordState  # noqa: E402
from trusted_authorization.non_production_assessment_engagement_participation_source import (  # noqa: E402
    NonProductionAssessmentEngagementParticipationAuthorityEvidence,
    NonProductionAssessmentEngagementParticipationAuthoritySource,
    NonProductionAssessmentEngagementParticipationLifecycleState,
    NonProductionAssessmentEngagementParticipationLookupStatus,
)


FOUND = NonProductionAssessmentEngagementParticipationLookupStatus.FOUND
NOT_FOUND = NonProductionAssessmentEngagementParticipationLookupStatus.NOT_FOUND
NON_CURRENT = NonProductionAssessmentEngagementParticipationLookupStatus.NON_CURRENT
STALE = NonProductionAssessmentEngagementParticipationLookupStatus.STALE
AMBIGUOUS = NonProductionAssessmentEngagementParticipationLookupStatus.AMBIGUOUS
CONFLICTING = NonProductionAssessmentEngagementParticipationLookupStatus.CONFLICTING
MALFORMED = NonProductionAssessmentEngagementParticipationLookupStatus.MALFORMED
CURRENT = NonProductionAssessmentEngagementParticipationLifecycleState.CURRENT
NO_LONGER_CURRENT = (
    NonProductionAssessmentEngagementParticipationLifecycleState.NON_CURRENT
)


def participation(
    authority_reference="participation-alpha-authority",
    state=AuthorityRecordState.ACTIVE,
    principal_id="principal-alpha",
    engagement_reference="engagement-alpha",
    lifecycle_state=CURRENT,
    participation_provenance_reference="participation-alpha-provenance",
):
    return NonProductionAssessmentEngagementParticipationAuthorityEvidence(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        engagement_reference=engagement_reference,
        lifecycle_state=lifecycle_state,
        participation_provenance_reference=participation_provenance_reference,
    )


def source_with(*records):
    return NonProductionAssessmentEngagementParticipationAuthoritySource(records)


def mutate_to_forged_participation(record):
    object.__setattr__(record, "authority_reference", "attacker-authority")
    object.__setattr__(record, "state", AuthorityRecordState.REVOKED)
    object.__setattr__(record, "principal_id", "principal-admin")
    object.__setattr__(record, "engagement_reference", "engagement-admin")
    object.__setattr__(record, "lifecycle_state", NO_LONGER_CURRENT)
    object.__setattr__(
        record,
        "participation_provenance_reference",
        "attacker-provenance",
    )


class NonProductionAssessmentEngagementParticipationAuthoritySourceTests(
    unittest.TestCase
):
    def test_01_empty_source_returns_not_found(self):
        result = source_with().resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, NOT_FOUND)
        self.assertEqual(result.records, ())

    def test_02_active_current_exact_pair_returns_found(self):
        expected = participation()
        result = source_with(expected).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, FOUND)
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0], expected)
        self.assertIs(
            type(result.records[0]),
            NonProductionAssessmentEngagementParticipationAuthorityEvidence,
        )
        self.assertIsNot(result.records[0], expected)

    def test_03_found_preserves_required_provenance(self):
        result = source_with(participation()).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        record = result.records[0]

        self.assertEqual(record.authority_reference, "participation-alpha-authority")
        self.assertEqual(record.state, AuthorityRecordState.ACTIVE)
        self.assertEqual(record.principal_id, "principal-alpha")
        self.assertEqual(record.engagement_reference, "engagement-alpha")
        self.assertIs(record.lifecycle_state, CURRENT)
        self.assertEqual(
            record.participation_provenance_reference,
            "participation-alpha-provenance",
        )

    def test_04_different_principal_returns_not_found(self):
        result = source_with(participation()).resolve_assessment_engagement_participation(
            "principal-beta",
            "engagement-alpha",
        )

        self.assertEqual(result.status, NOT_FOUND)
        self.assertEqual(result.records, ())

    def test_05_different_engagement_returns_not_found(self):
        result = source_with(participation()).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-beta",
        )

        self.assertEqual(result.status, NOT_FOUND)
        self.assertEqual(result.records, ())

    def test_06_same_principal_multiple_engagements_use_exact_e(self):
        source = source_with(
            participation(engagement_reference="engagement-alpha"),
            participation(
                authority_reference="participation-beta-authority",
                engagement_reference="engagement-beta",
                participation_provenance_reference="participation-beta-provenance",
            ),
        )

        alpha = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        beta = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-beta",
        )

        self.assertEqual(alpha.status, FOUND)
        self.assertEqual(beta.status, FOUND)
        self.assertEqual(alpha.records[0].engagement_reference, "engagement-alpha")
        self.assertEqual(beta.records[0].engagement_reference, "engagement-beta")

    def test_07_same_engagement_multiple_principals_use_exact_p(self):
        source = source_with(
            participation(principal_id="principal-alpha"),
            participation(
                authority_reference="participation-beta-authority",
                principal_id="principal-beta",
                participation_provenance_reference="participation-beta-provenance",
            ),
        )

        alpha = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        beta = source.resolve_assessment_engagement_participation(
            "principal-beta",
            "engagement-alpha",
        )

        self.assertEqual(alpha.status, FOUND)
        self.assertEqual(beta.status, FOUND)
        self.assertEqual(alpha.records[0].principal_id, "principal-alpha")
        self.assertEqual(beta.records[0].principal_id, "principal-beta")

    def test_08_same_b_different_e_substitution_returns_not_found(self):
        source = source_with(participation(engagement_reference="engagement-one"))

        result = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-two",
        )

        self.assertEqual(result.status, NOT_FOUND)
        self.assertEqual(result.records, ())

    def test_09_cross_b_has_no_rewrite_semantics(self):
        source = source_with(
            participation(engagement_reference="engagement-business-one")
        )

        result = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-business-two",
        )

        self.assertEqual(result.status, NOT_FOUND)
        self.assertFalse(hasattr(result, "business_entity_id"))

    def test_10_active_non_current_lifecycle_returns_non_current(self):
        result = source_with(
            participation(lifecycle_state=NO_LONGER_CURRENT)
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, NON_CURRENT)
        self.assertEqual(result.records, ())

    def test_11_non_active_authority_states_return_stale(self):
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
                    participation(state=state)
                ).resolve_assessment_engagement_participation(
                    "principal-alpha",
                    "engagement-alpha",
                )

                self.assertEqual(result.status, STALE)
                self.assertEqual(result.records, ())

    def test_12_revoked_authority_state_returns_stale(self):
        result = source_with(
            participation(state=AuthorityRecordState.REVOKED)
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, STALE)
        self.assertEqual(result.records, ())

    def test_13_identical_duplicate_exact_pair_returns_ambiguous(self):
        result = source_with(
            participation(),
            participation(),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, AMBIGUOUS)
        self.assertEqual(result.records, ())

    def test_14_duplicate_evidence_is_not_selected_by_record_order(self):
        source = source_with(participation(), participation())

        first = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        second = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(first.status, AMBIGUOUS)
        self.assertEqual(second.status, AMBIGUOUS)
        self.assertNotEqual(first.status, FOUND)

    def test_15_different_authority_reference_returns_conflicting(self):
        result = source_with(
            participation(),
            participation(authority_reference="participation-beta-authority"),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)
        self.assertEqual(result.records, ())

    def test_16_different_state_returns_conflicting(self):
        result = source_with(
            participation(),
            participation(state=AuthorityRecordState.STALE),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)
        self.assertEqual(result.records, ())

    def test_17_different_lifecycle_returns_conflicting(self):
        result = source_with(
            participation(),
            participation(lifecycle_state=NO_LONGER_CURRENT),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)
        self.assertEqual(result.records, ())

    def test_18_different_provenance_returns_conflicting(self):
        result = source_with(
            participation(),
            participation(
                participation_provenance_reference="participation-beta-provenance"
            ),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)
        self.assertEqual(result.records, ())

    def test_19_current_plus_stale_returns_conflicting(self):
        result = source_with(
            participation(),
            participation(state=AuthorityRecordState.STALE),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)

    def test_20_current_plus_non_current_returns_conflicting(self):
        result = source_with(
            participation(),
            participation(lifecycle_state=NO_LONGER_CURRENT),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)

    def test_21_stale_plus_non_current_returns_conflicting(self):
        result = source_with(
            participation(state=AuthorityRecordState.STALE),
            participation(
                state=AuthorityRecordState.STALE,
                lifecycle_state=NO_LONGER_CURRENT,
            ),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)

    def test_22_current_plus_revoked_returns_conflicting(self):
        result = source_with(
            participation(),
            participation(state=AuthorityRecordState.REVOKED),
        ).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, CONFLICTING)

    def test_23_invalid_principal_lookup_returns_malformed(self):
        for lookup in _malformed_identifiers():
            with self.subTest(lookup=repr(lookup)):
                result = source_with(
                    participation()
                ).resolve_assessment_engagement_participation(
                    lookup,
                    "engagement-alpha",
                )

                self.assertEqual(result.status, MALFORMED)
                self.assertEqual(result.records, ())

    def test_24_invalid_engagement_lookup_returns_malformed(self):
        for lookup in _malformed_identifiers():
            with self.subTest(lookup=repr(lookup)):
                result = source_with(
                    participation()
                ).resolve_assessment_engagement_participation(
                    "principal-alpha",
                    lookup,
                )

                self.assertEqual(result.status, MALFORMED)
                self.assertEqual(result.records, ())

    def test_25_str_subclass_lookup_fails_without_behavior_invocation(self):
        class HostileStr(str):
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        source = source_with(participation())
        for principal_id, engagement_reference in (
            (HostileStr("principal-alpha"), "engagement-alpha"),
            ("principal-alpha", HostileStr("engagement-alpha")),
        ):
            with self.subTest(principal_id=principal_id, engagement_reference=engagement_reference):
                HostileStr.comparisons = 0

                result = source.resolve_assessment_engagement_participation(
                    principal_id,
                    engagement_reference,
                )

                self.assertEqual(result.status, MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(HostileStr.comparisons, 0)

    def test_26_malformed_evidence_wrong_type_poisons_source(self):
        result = source_with(object()).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, MALFORMED)
        self.assertEqual(result.records, ())

    def test_27_evidence_subclass_rejected_without_field_reads(self):
        class EvidenceSubclass(
            NonProductionAssessmentEngagementParticipationAuthorityEvidence
        ):
            field_reads = 0

            def __getattribute__(self, name):
                if name == "principal_id":
                    type(self).field_reads += 1
                    return "principal-alpha"
                return object.__getattribute__(self, name)

        record = EvidenceSubclass(
            "participation-alpha-authority",
            AuthorityRecordState.ACTIVE,
            "principal-alpha",
            "engagement-alpha",
            CURRENT,
            "participation-alpha-provenance",
        )
        result = source_with(record).resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(EvidenceSubclass.field_reads, 0)

    def test_28_malformed_evidence_fields_poison_source(self):
        class OtherState(Enum):
            ACTIVE = "ACTIVE"

        class OtherLifecycle(Enum):
            CURRENT = "CURRENT"

        cases = (
            ("authority_reference", None),
            ("authority_reference", ""),
            ("authority_reference", " authority"),
            ("authority_reference", "authority "),
            ("state", None),
            ("state", "ACTIVE"),
            ("state", OtherState.ACTIVE),
            ("principal_id", None),
            ("principal_id", ""),
            ("principal_id", " principal-alpha"),
            ("principal_id", "principal-alpha "),
            ("engagement_reference", None),
            ("engagement_reference", ""),
            ("engagement_reference", " engagement-alpha"),
            ("engagement_reference", "engagement-alpha "),
            ("lifecycle_state", None),
            ("lifecycle_state", "CURRENT"),
            ("lifecycle_state", OtherLifecycle.CURRENT),
            ("participation_provenance_reference", None),
            ("participation_provenance_reference", ""),
            ("participation_provenance_reference", " provenance"),
            ("participation_provenance_reference", "provenance "),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                result = source_with(
                    replace(participation(), **{field: value})
                ).resolve_assessment_engagement_participation(
                    "principal-alpha",
                    "engagement-alpha",
                )

                self.assertEqual(result.status, MALFORMED)
                self.assertEqual(result.records, ())

    def test_29_stored_string_subclass_poisons_source(self):
        class HostileStr(str):
            pass

        for field in (
            "authority_reference",
            "principal_id",
            "engagement_reference",
            "participation_provenance_reference",
        ):
            with self.subTest(field=field):
                result = source_with(
                    replace(participation(), **{field: HostileStr("value")})
                ).resolve_assessment_engagement_participation(
                    "principal-alpha",
                    "engagement-alpha",
                )

                self.assertEqual(result.status, MALFORMED)
                self.assertEqual(result.records, ())

    def test_30_malformed_matching_record_poisons_source(self):
        malformed = object.__new__(
            NonProductionAssessmentEngagementParticipationAuthorityEvidence
        )
        object.__setattr__(
            malformed,
            "authority_reference",
            "participation-alpha-authority",
        )
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(malformed, "principal_id", "principal-alpha")
        object.__setattr__(malformed, "engagement_reference", "engagement-alpha")
        source = source_with(malformed)

        result = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, MALFORMED)
        self.assertEqual(result.records, ())

    def test_31_malformed_unrelated_record_poisons_source_globally(self):
        malformed = object.__new__(
            NonProductionAssessmentEngagementParticipationAuthorityEvidence
        )
        object.__setattr__(malformed, "authority_reference", "malformed")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(malformed, "principal_id", "principal-unrelated")
        source = source_with(participation(), malformed)

        result = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(result.status, MALFORMED)
        self.assertEqual(result.records, ())

    def test_32_hostile_iterable_consumed_once_at_construction(self):
        class HostileList(list):
            iter_calls = 0

            def __iter__(self):
                type(self).iter_calls += 1
                return super().__iter__()

        records = HostileList([participation()])
        source = NonProductionAssessmentEngagementParticipationAuthoritySource(records)
        records.append(participation(engagement_reference="engagement-beta"))

        alpha = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        beta = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-beta",
        )

        self.assertEqual(HostileList.iter_calls, 1)
        self.assertEqual(alpha.status, FOUND)
        self.assertEqual(beta.status, NOT_FOUND)

    def test_33_constructor_consumes_generator_once(self):
        calls = {"count": 0}

        def records():
            calls["count"] += 1
            yield participation()

        source = NonProductionAssessmentEngagementParticipationAuthoritySource(
            records()
        )
        first = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        second = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(calls["count"], 1)
        self.assertEqual(first.status, FOUND)
        self.assertEqual(second.status, FOUND)

    def test_34_caller_collection_mutation_cannot_change_result(self):
        records = [participation()]
        source = NonProductionAssessmentEngagementParticipationAuthoritySource(records)
        records.clear()
        records.append(participation(engagement_reference="engagement-beta"))

        alpha = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        beta = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-beta",
        )

        self.assertEqual(alpha.status, FOUND)
        self.assertEqual(beta.status, NOT_FOUND)

    def test_35_caller_record_mutation_cannot_change_result(self):
        record = participation()
        source = source_with(record)
        with self.assertRaises(FrozenInstanceError):
            record.principal_id = "principal-admin"
        mutate_to_forged_participation(record)

        original = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        forged = source.resolve_assessment_engagement_participation(
            "principal-admin",
            "engagement-admin",
        )

        self.assertEqual(original.status, FOUND)
        self.assertEqual(original.records[0].principal_id, "principal-alpha")
        self.assertEqual(original.records[0].engagement_reference, "engagement-alpha")
        self.assertEqual(forged.status, NOT_FOUND)

    def test_36_found_output_is_fresh_each_lookup(self):
        source = source_with(participation())

        first = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        second = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(first, second)
        self.assertIsNot(first.records[0], second.records[0])
        self.assertIsNot(first.records[0], source._records[0])
        self.assertIsNot(second.records[0], source._records[0])

    def test_37_output_setattr_attack_cannot_change_future_lookup(self):
        source = source_with(participation())
        first = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        object.__setattr__(
            first.records[0],
            "engagement_reference",
            "engagement-forged",
        )

        second = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        forged = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-forged",
        )

        self.assertEqual(second.status, FOUND)
        self.assertEqual(second.records[0].engagement_reference, "engagement-alpha")
        self.assertEqual(forged.status, NOT_FOUND)

    def test_38_all_non_found_results_have_empty_records(self):
        cases = (
            source_with().resolve_assessment_engagement_participation(
                "principal-alpha",
                "engagement-alpha",
            ),
            source_with(
                participation(lifecycle_state=NO_LONGER_CURRENT)
            ).resolve_assessment_engagement_participation(
                "principal-alpha",
                "engagement-alpha",
            ),
            source_with(
                participation(state=AuthorityRecordState.STALE)
            ).resolve_assessment_engagement_participation(
                "principal-alpha",
                "engagement-alpha",
            ),
            source_with(participation(), participation()).resolve_assessment_engagement_participation(
                "principal-alpha",
                "engagement-alpha",
            ),
            source_with(
                participation(),
                participation(authority_reference="participation-beta-authority"),
            ).resolve_assessment_engagement_participation(
                "principal-alpha",
                "engagement-alpha",
            ),
            source_with(object()).resolve_assessment_engagement_participation(
                "principal-alpha",
                "engagement-alpha",
            ),
        )

        for result in cases:
            with self.subTest(status=result.status):
                self.assertNotEqual(result.status, FOUND)
                self.assertEqual(result.records, ())

    def test_39_repeated_lookup_is_deterministic(self):
        source = source_with(participation())

        first = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )
        second = source.resolve_assessment_engagement_participation(
            "principal-alpha",
            "engagement-alpha",
        )

        self.assertEqual(first, second)
        self.assertEqual(first.status, FOUND)

    def test_40_source_has_no_forbidden_authority_dependencies(self):
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
            "principal_mapping",
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

    def test_41_source_exposes_no_management_or_mutation_api_surface(self):
        forbidden = (
            "create",
            "establish",
            "approve",
            "activate",
            "rebind",
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
                NonProductionAssessmentEngagementParticipationAuthoritySource,
                predicate=callable,
            )
            if not name.startswith("_")
        }

        self.assertEqual(
            public_callables,
            {"resolve_assessment_engagement_participation"},
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertFalse(any(token in name.lower() for name in public_callables))

    def test_42_no_permission_binding_context_business_or_runtime_surface(self):
        public_names = [
            name
            for name in dir(source_module)
            if not name.startswith("_")
        ]
        public_names.extend(
            status.name
            for status in NonProductionAssessmentEngagementParticipationLookupStatus
        )
        public_names.extend(
            status.value
            for status in NonProductionAssessmentEngagementParticipationLookupStatus
        )
        surface = "\n".join(public_names).lower()
        forbidden = (
            "allow",
            "deny",
            "authorized",
            "permitted",
            "valid_for_request",
            "binding",
            "context_legitimate",
            "context_ready",
            "business_context_ready",
            "target_legitimacy",
            "runtime",
        )

        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, surface)

    def test_43_source_is_not_exported_from_package_root(self):
        self.assertFalse(
            hasattr(
                trusted_authorization_package,
                "NonProductionAssessmentEngagementParticipationAuthoritySource",
            )
        )

    def test_44_source_keeps_only_constructor_supplied_snapshots(self):
        original = participation()
        source = source_with(original)

        self.assertEqual(
            source.__slots__,
            ("_has_malformed_evidence", "_records"),
        )
        self.assertEqual(source._records, (original,))
        self.assertIsNot(source._records[0], original)


def _malformed_identifiers():
    class Hostile:
        comparisons = 0

        def __eq__(self, other):
            type(self).comparisons += 1
            return True

    return (
        None,
        1,
        b"value",
        Hostile(),
        "",
        " ",
        "   ",
        "\t",
        "\n",
        " value",
        "value ",
    )


if __name__ == "__main__":
    unittest.main()
