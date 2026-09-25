import dataclasses
import inspect
import sys
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_governed_version_context_establishment as module  # noqa: E402
from trusted_authorization.models import (  # noqa: E402
    AuthorityRecordState,
    GovernedVersionContext,
)
from trusted_authorization.non_production_assessment_submission_governed_version_context_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionGovernedVersionContextAuthority,
    NonProductionAssessmentSubmissionGovernedVersionContextEvidence,
    NonProductionAssessmentSubmissionGovernedVersionContextFact,
    NonProductionAssessmentSubmissionGovernedVersionContextResult,
    NonProductionAssessmentSubmissionGovernedVersionContextStatus,
)


STATUS = NonProductionAssessmentSubmissionGovernedVersionContextStatus
ADAPTER_STATUS = module._ControlledGovernedVersionContextAdapterStatus
OWNER = "nguyen-ai-platform-governance-control-plane"
AUTHORITY = (
    "non-production-assessment-submission-governed-version-context-authority"
)
SOURCE = (
    "non-production-assessment-submission-governed-version-context-"
    "controlled-evidence-source"
)
GOVERNANCE = (
    "trusted-authorization-implementation-readiness-governance-v1",
    "trusted-authorization-corrective-implementation-governance-v1",
    "trusted-authorization-production-authority-source-ownership-governance-v1",
    "deterministic-authorization-decision-semantics-v1",
    "resource-action-applicability-governance-v1",
)
SCOPE = "bounded-non-production-assessment-submission-submit"
SEMANTICS = "deterministic-authorization-decision-semantics-v1"
APPLICABILITY = "resource-action-applicability-governance-v1"
EVALUATION = "local-deterministic-fixture"


class StringSubclass(str):
    pass


class ForeignState(Enum):
    ACTIVE = "ACTIVE"


class ForeignStatus(Enum):
    AVAILABLE = "AVAILABLE"


class RecordSubclass(module._ControlledGovernedVersionContextRecord):
    pass


class AdapterResultSubclass(module._ControlledGovernedVersionContextAdapterResult):
    pass


class DuckRecord:
    semantic_owner_reference = OWNER
    authority_reference = AUTHORITY
    source_reference = SOURCE
    governance_references = GOVERNANCE
    scope_reference = SCOPE
    state = AuthorityRecordState.ACTIVE
    compatible = True
    authorization_semantics_version = SEMANTICS
    applicability_governance_version = APPLICABILITY
    evaluation_context = EVALUATION


def record(**overrides):
    values = {
        "semantic_owner_reference": OWNER,
        "authority_reference": AUTHORITY,
        "source_reference": SOURCE,
        "governance_references": GOVERNANCE,
        "scope_reference": SCOPE,
        "state": AuthorityRecordState.ACTIVE,
        "compatible": True,
        "authorization_semantics_version": SEMANTICS,
        "applicability_governance_version": APPLICABILITY,
        "evaluation_context": EVALUATION,
    }
    values.update(overrides)
    return module._ControlledGovernedVersionContextRecord(**values)


def adapter_result(records=(), status=ADAPTER_STATUS.AVAILABLE):
    return module._ControlledGovernedVersionContextAdapterResult(
        status=status,
        records=records,
    )


def establish_with(result):
    authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
    controlled_adapter = Mock()
    controlled_adapter.resolve_current_governed_version_context.return_value = result
    with patch.object(
        authority,
        "_governed_version_context_adapter",
        controlled_adapter,
    ):
        return authority.establish_assessment_submission_governed_version_context()


class GovernedVersionContextContractTests(unittest.TestCase):
    def test_public_surface_and_signatures_are_exact(self):
        public_specialized = sorted(
            name
            for name in vars(module)
            if name.startswith(
                "NonProductionAssessmentSubmissionGovernedVersionContext"
            )
        )
        self.assertEqual(
            public_specialized,
            sorted(
                (
                    "NonProductionAssessmentSubmissionGovernedVersionContextAuthority",
                    "NonProductionAssessmentSubmissionGovernedVersionContextEvidence",
                    "NonProductionAssessmentSubmissionGovernedVersionContextFact",
                    "NonProductionAssessmentSubmissionGovernedVersionContextResult",
                    "NonProductionAssessmentSubmissionGovernedVersionContextStatus",
                )
            ),
        )
        self.assertEqual(
            tuple(
                inspect.signature(
                    NonProductionAssessmentSubmissionGovernedVersionContextAuthority.__init__
                ).parameters
            ),
            ("self",),
        )
        self.assertEqual(
            tuple(
                inspect.signature(
                    NonProductionAssessmentSubmissionGovernedVersionContextAuthority.establish_assessment_submission_governed_version_context
                ).parameters
            ),
            ("self",),
        )
        authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
        with self.assertRaises(TypeError):
            NonProductionAssessmentSubmissionGovernedVersionContextAuthority(
                GovernedVersionContext(SEMANTICS, APPLICABILITY, EVALUATION)
            )
        with self.assertRaises(TypeError):
            authority.establish_assessment_submission_governed_version_context(
                GovernedVersionContext(SEMANTICS, APPLICABILITY, EVALUATION)
            )

    def test_private_adapter_contract_is_exact(self):
        self.assertEqual(
            tuple(item.name for item in ADAPTER_STATUS),
            ("AVAILABLE", "UNAVAILABLE"),
        )
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    module._ControlledGovernedVersionContextAdapterResult
                )
            ),
            ("status", "records"),
        )
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    module._ControlledGovernedVersionContextRecord
                )
            ),
            (
                "semantic_owner_reference",
                "authority_reference",
                "source_reference",
                "governance_references",
                "scope_reference",
                "state",
                "compatible",
                "authorization_semantics_version",
                "applicability_governance_version",
                "evaluation_context",
            ),
        )

    def test_public_dataclass_and_status_contracts_are_exact(self):
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionGovernedVersionContextFact
                )
            ),
            ("governed_version_context",),
        )
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionGovernedVersionContextEvidence
                )
            ),
            (
                "semantic_owner_reference",
                "governed_version_context_authority_reference",
                "governed_version_context_source_reference",
                "governance_references",
                "scope_reference",
                "source_state",
                "source_record_count",
                "compatible",
                "authorization_semantics_version",
                "applicability_governance_version",
                "evaluation_context",
            ),
        )
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionGovernedVersionContextResult
                )
            ),
            (
                "status",
                "governed_version_context_fact",
                "establishment_evidence",
            ),
        )
        self.assertEqual(
            tuple(item.name for item in STATUS),
            (
                "ESTABLISHED",
                "MALFORMED",
                "NOT_CURRENT",
                "UNAVAILABLE",
                "AMBIGUOUS",
                "CONFLICTING",
                "STALE",
                "UNSUPPORTED",
                "INCOMPATIBLE",
            ),
        )
        self.assertNotIn("REUSED", STATUS.__members__)

    def test_default_singleton_establishes_exact_fact_and_evidence(self):
        result = (
            NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
            .establish_assessment_submission_governed_version_context()
        )
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(
            result.governed_version_context_fact,
            NonProductionAssessmentSubmissionGovernedVersionContextFact(
                governed_version_context=GovernedVersionContext(
                    authorization_semantics_version=SEMANTICS,
                    applicability_governance_version=APPLICABILITY,
                    evaluation_context=EVALUATION,
                )
            ),
        )
        self.assertEqual(
            result.establishment_evidence,
            NonProductionAssessmentSubmissionGovernedVersionContextEvidence(
                semantic_owner_reference=OWNER,
                governed_version_context_authority_reference=AUTHORITY,
                governed_version_context_source_reference=SOURCE,
                governance_references=GOVERNANCE,
                scope_reference=SCOPE,
                source_state=AuthorityRecordState.ACTIVE,
                source_record_count=1,
                compatible=True,
                authorization_semantics_version=SEMANTICS,
                applicability_governance_version=APPLICABILITY,
                evaluation_context=EVALUATION,
            ),
        )

    def test_each_call_freshly_resolves_and_establishes_fresh_objects(self):
        authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
        adapter = authority._governed_version_context_adapter
        wrapped = Mock(wraps=adapter)
        with patch.object(authority, "_governed_version_context_adapter", wrapped):
            first = authority.establish_assessment_submission_governed_version_context()
            second = authority.establish_assessment_submission_governed_version_context()
        self.assertEqual(wrapped.resolve_current_governed_version_context.call_count, 2)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.ESTABLISHED)
        self.assertIsNot(first, second)
        self.assertIsNot(
            first.governed_version_context_fact,
            second.governed_version_context_fact,
        )
        self.assertIsNot(first.establishment_evidence, second.establishment_evidence)
        self.assertIsNot(
            first.governed_version_context_fact.governed_version_context,
            second.governed_version_context_fact.governed_version_context,
        )

    def test_authority_has_no_canonical_state_or_counter(self):
        authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
        self.assertEqual(
            authority.__slots__, ("_governed_version_context_adapter",)
        )
        for name in (
            "_by_attempt",
            "_canonical",
            "_cache",
            "_counter",
            "_next_provenance_index",
            "_stored_fact",
            "_stored_evidence",
            "_stored_result",
        ):
            self.assertFalse(hasattr(authority, name))

    def test_zero_records_is_not_current(self):
        self.assert_failure(establish_with(adapter_result()), STATUS.NOT_CURRENT)

    def test_unavailable_empty_and_exception_are_unavailable(self):
        self.assert_failure(
            establish_with(adapter_result(status=ADAPTER_STATUS.UNAVAILABLE)),
            STATUS.UNAVAILABLE,
        )
        authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
        unavailable_adapter = Mock()
        unavailable_adapter.resolve_current_governed_version_context.side_effect = (
            RuntimeError("unavailable")
        )
        with patch.object(
            authority,
            "_governed_version_context_adapter",
            unavailable_adapter,
        ):
            self.assert_failure(
                authority.establish_assessment_submission_governed_version_context(),
                STATUS.UNAVAILABLE,
            )

    def test_unavailable_with_records_is_malformed(self):
        self.assert_failure(
            establish_with(
                adapter_result((record(),), ADAPTER_STATUS.UNAVAILABLE)
            ),
            STATUS.MALFORMED,
        )

    def test_foreign_result_status_and_records_container_are_malformed(self):
        for bad_result in (object(), {"status": ADAPTER_STATUS.AVAILABLE}):
            with self.subTest(result=type(bad_result).__name__):
                self.assert_failure(
                    establish_with(bad_result),
                    STATUS.MALFORMED,
                )
        foreign_status = adapter_result()
        object.__setattr__(foreign_status, "status", ForeignStatus.AVAILABLE)
        self.assert_failure(establish_with(foreign_status), STATUS.MALFORMED)
        list_records = adapter_result()
        object.__setattr__(list_records, "records", [record()])
        self.assert_failure(establish_with(list_records), STATUS.MALFORMED)

    def test_foreign_mapping_and_duck_records_are_malformed(self):
        candidates = (
            object(),
            {"authorization_semantics_version": SEMANTICS},
            DuckRecord(),
            RecordSubclass(
                OWNER,
                AUTHORITY,
                SOURCE,
                GOVERNANCE,
                SCOPE,
                AuthorityRecordState.ACTIVE,
                True,
                SEMANTICS,
                APPLICABILITY,
                EVALUATION,
            ),
            GovernedVersionContext(SEMANTICS, APPLICABILITY, EVALUATION),
        )
        for candidate in candidates:
            with self.subTest(candidate=type(candidate).__name__):
                self.assert_failure(
                    establish_with(adapter_result((candidate,))),
                    STATUS.MALFORMED,
                )

    def test_adapter_result_subclass_is_malformed(self):
        self.assert_failure(
            establish_with(
                AdapterResultSubclass(
                    status=ADAPTER_STATUS.AVAILABLE,
                    records=(record(),),
                )
            ),
            STATUS.MALFORMED,
        )

    def test_each_string_field_rejects_blank_whitespace_and_edges(self):
        fields = (
            "semantic_owner_reference",
            "authority_reference",
            "source_reference",
            "scope_reference",
            "authorization_semantics_version",
            "applicability_governance_version",
            "evaluation_context",
        )
        for field in fields:
            for value in ("", " ", "\t", " x", "x ", "\nx"):
                with self.subTest(field=field, value=repr(value)):
                    self.assert_failure(
                        establish_with(adapter_result((record(**{field: value}),))),
                        STATUS.MALFORMED,
                    )

    def test_string_subclasses_non_strings_and_coercion_are_malformed(self):
        for value in (StringSubclass(OWNER), 1, object()):
            with self.subTest(value=type(value).__name__):
                self.assert_failure(
                    establish_with(
                        adapter_result((record(semantic_owner_reference=value),))
                    ),
                    STATUS.MALFORMED,
                )

    def test_compatible_requires_exact_builtin_bool(self):
        for value in (1, 0, "True", object()):
            with self.subTest(value=repr(value)):
                self.assert_failure(
                    establish_with(adapter_result((record(compatible=value),))),
                    STATUS.MALFORMED,
                )

    def test_state_requires_exact_governed_enum(self):
        self.assert_failure(
            establish_with(adapter_result((record(state=ForeignState.ACTIVE),))),
            STATUS.MALFORMED,
        )

    def test_governance_tuple_type_elements_order_and_values_are_exact(self):
        bad_governance = (
            list(GOVERNANCE),
            GOVERNANCE[:-1],
            tuple(reversed(GOVERNANCE)),
            GOVERNANCE[:-1] + ("foreign-governance-v1",),
            GOVERNANCE[:-1] + (StringSubclass(GOVERNANCE[-1]),),
            GOVERNANCE[:-1] + (" ",),
        )
        for value in bad_governance:
            with self.subTest(value=value):
                self.assert_failure(
                    establish_with(
                        adapter_result((record(governance_references=value),))
                    ),
                    STATUS.MALFORMED,
                )

    def test_authoritative_identity_substitution_is_malformed(self):
        substitutions = (
            ("semantic_owner_reference", OWNER + "2"),
            ("authority_reference", AUTHORITY + "2"),
            ("source_reference", SOURCE + "2"),
            ("scope_reference", SCOPE + "2"),
        )
        for field, value in substitutions:
            with self.subTest(field=field):
                self.assert_failure(
                    establish_with(adapter_result((record(**{field: value}),))),
                    STATUS.MALFORMED,
                )

    def test_singleton_stale_and_other_nonactive_states_fail_currentness(self):
        self.assert_failure(
            establish_with(
                adapter_result((record(state=AuthorityRecordState.STALE),))
            ),
            STATUS.STALE,
        )
        for state in (
            AuthorityRecordState.INACTIVE,
            AuthorityRecordState.DISABLED,
            AuthorityRecordState.REVOKED,
            AuthorityRecordState.EXPIRED,
            AuthorityRecordState.TERMINATED,
            AuthorityRecordState.UNKNOWN,
        ):
            with self.subTest(state=state):
                self.assert_failure(
                    establish_with(adapter_result((record(state=state),))),
                    STATUS.NOT_CURRENT,
                )

    def test_each_unsupported_context_value_is_unsupported(self):
        substitutions = (
            ("authorization_semantics_version", SEMANTICS + "2"),
            ("applicability_governance_version", APPLICABILITY + "2"),
            ("evaluation_context", EVALUATION + "2"),
        )
        for field, value in substitutions:
            with self.subTest(field=field):
                self.assert_failure(
                    establish_with(adapter_result((record(**{field: value}),))),
                    STATUS.UNSUPPORTED,
                )

    def test_exact_supported_context_with_false_compatibility_is_incompatible(self):
        self.assert_failure(
            establish_with(adapter_result((record(compatible=False),))),
            STATUS.INCOMPATIBLE,
        )

    def test_identical_duplicates_are_ambiguous_without_deduplication(self):
        first = record()
        second = record()
        self.assertIsNot(first, second)
        self.assert_failure(
            establish_with(adapter_result((first, second))),
            STATUS.AMBIGUOUS,
        )

    def test_distinct_complete_records_are_conflicting(self):
        variants = (
            record(state=AuthorityRecordState.STALE),
            record(authorization_semantics_version=SEMANTICS + "2"),
            record(compatible=False),
        )
        for variant in variants:
            with self.subTest(variant=variant):
                self.assert_failure(
                    establish_with(adapter_result((record(), variant))),
                    STATUS.CONFLICTING,
                )

    def test_malformed_candidate_precedes_cardinality_and_is_not_filtered(self):
        malformed = record()
        object.__setattr__(malformed, "scope_reference", " ")
        self.assert_failure(
            establish_with(adapter_result((record(), malformed))),
            STATUS.MALFORMED,
        )

    def test_prior_success_never_bypasses_fresh_failure(self):
        authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
        first = authority.establish_assessment_submission_governed_version_context()
        self.assertIs(first.status, STATUS.ESTABLISHED)
        failures = (
            adapter_result(),
            adapter_result(status=ADAPTER_STATUS.UNAVAILABLE),
            adapter_result((record(state=AuthorityRecordState.STALE),)),
            adapter_result(
                (record(authorization_semantics_version=SEMANTICS + "2"),)
            ),
            adapter_result((record(compatible=False),)),
            adapter_result((record(), record())),
            adapter_result((record(), record(compatible=False))),
        )
        for controlled_result in failures:
            controlled_adapter = Mock()
            controlled_adapter.resolve_current_governed_version_context.return_value = (
                controlled_result
            )
            with self.subTest(status=controlled_result.status), patch.object(
                authority,
                "_governed_version_context_adapter",
                controlled_adapter,
            ):
                self.assertIsNot(
                    authority.establish_assessment_submission_governed_version_context().status,
                    STATUS.ESTABLISHED,
                )
        malformed_adapter = Mock()
        malformed_adapter.resolve_current_governed_version_context.return_value = (
            object()
        )
        with patch.object(
            authority,
            "_governed_version_context_adapter",
            malformed_adapter,
        ):
            self.assert_failure(
                authority.establish_assessment_submission_governed_version_context(),
                STATUS.MALFORMED,
            )
        unavailable_adapter = Mock()
        unavailable_adapter.resolve_current_governed_version_context.side_effect = (
            RuntimeError("unavailable")
        )
        with patch.object(
            authority,
            "_governed_version_context_adapter",
            unavailable_adapter,
        ):
            self.assert_failure(
                authority.establish_assessment_submission_governed_version_context(),
                STATUS.UNAVAILABLE,
            )

    def test_returned_mutation_cannot_change_adapter_or_future_authority(self):
        authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
        first = authority.establish_assessment_submission_governed_version_context()
        object.__setattr__(first, "status", STATUS.MALFORMED)
        object.__setattr__(
            first.governed_version_context_fact,
            "governed_version_context",
            GovernedVersionContext("forged", "forged", "forged"),
        )
        object.__setattr__(
            first.establishment_evidence,
            "semantic_owner_reference",
            "forged",
        )
        second = authority.establish_assessment_submission_governed_version_context()
        self.assertIs(second.status, STATUS.ESTABLISHED)
        self.assertEqual(
            second.governed_version_context_fact.governed_version_context,
            GovernedVersionContext(SEMANTICS, APPLICABILITY, EVALUATION),
        )
        self.assertEqual(
            second.establishment_evidence.semantic_owner_reference,
            OWNER,
        )

    def test_source_mutation_after_snapshot_does_not_change_returned_snapshot(self):
        authority = NonProductionAssessmentSubmissionGovernedVersionContextAuthority()
        source_record = authority._governed_version_context_adapter._records[0]
        first = authority.establish_assessment_submission_governed_version_context()
        object.__setattr__(
            source_record,
            "authorization_semantics_version",
            SEMANTICS + "2",
        )
        self.assertEqual(
            first.governed_version_context_fact.governed_version_context.authorization_semantics_version,
            SEMANTICS,
        )
        self.assertEqual(
            first.establishment_evidence.authorization_semantics_version,
            SEMANTICS,
        )
        self.assert_failure(
            authority.establish_assessment_submission_governed_version_context(),
            STATUS.UNSUPPORTED,
        )

    def test_correct_strings_cannot_launder_wrong_custody_or_currentness(self):
        substitutions = (
            {"authority_reference": AUTHORITY + "2"},
            {"source_reference": SOURCE + "2"},
            {"governance_references": GOVERNANCE[:-1]},
            {"scope_reference": SCOPE + "2"},
            {"state": AuthorityRecordState.REVOKED},
        )
        for substitution in substitutions:
            with self.subTest(substitution=substitution):
                result = establish_with(adapter_result((record(**substitution),)))
                self.assertIsNot(result.status, STATUS.ESTABLISHED)
                self.assertIsNone(result.governed_version_context_fact)
                self.assertIsNone(result.establishment_evidence)

    def test_version_authority_is_independent_and_separation_is_preserved(self):
        source = inspect.getsource(module)
        forbidden = (
            "AuthorizationRequest",
            "TrustedAuthorizationEvaluator",
            "AuthorizationDecision",
            "SubjectCurrentness",
            "BusinessContext",
            "correlation_id",
            "resource_reference",
            "requested_action",
            "boto3",
            "Cognito",
            "AppConfig",
            "DynamoDB",
        )
        for term in forbidden:
            with self.subTest(term=term):
                self.assertNotIn(term, source)
        self.assertNotIn("evaluator", source.lower())
        self.assertNotIn("permission", source.lower())
        self.assertNotIn("allow", source.lower())
        self.assertNotIn("deny", source.lower())
        self.assertNotIn("lifecycle", source.lower())
        self.assertNotIn("persist", source.lower())

    def test_failure_results_never_carry_partial_authority(self):
        failures = (
            adapter_result(),
            adapter_result(status=ADAPTER_STATUS.UNAVAILABLE),
            adapter_result((record(state=AuthorityRecordState.STALE),)),
            adapter_result(
                (record(authorization_semantics_version=SEMANTICS + "2"),)
            ),
            adapter_result((record(compatible=False),)),
            adapter_result((record(), record())),
            adapter_result((record(), record(compatible=False))),
        )
        for controlled_result in failures:
            with self.subTest(controlled_result=controlled_result):
                result = establish_with(controlled_result)
                self.assertIsNone(result.governed_version_context_fact)
                self.assertIsNone(result.establishment_evidence)

    def assert_failure(self, result, expected_status):
        self.assertIs(result.status, expected_status)
        self.assertIsNone(result.governed_version_context_fact)
        self.assertIsNone(result.establishment_evidence)


if __name__ == "__main__":
    unittest.main()
