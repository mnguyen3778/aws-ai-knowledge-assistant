import dataclasses
import inspect
import sys
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_membership_currentness_establishment as module  # noqa: E402
from trusted_authorization.membership_source import (  # noqa: E402
    NonProductionMembershipAuthoritySource,
)
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationRequest,
    Entitlement,
    Membership,
    RequestedAction,
    ResourceActionApplicability,
    ResourceClass,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_business_entity_currentness_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus,
)
from trusted_authorization.non_production_assessment_submission_membership_currentness_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
    NonProductionAssessmentSubmissionMembershipCurrentnessEvidence,
    NonProductionAssessmentSubmissionMembershipCurrentnessFact,
    NonProductionAssessmentSubmissionMembershipCurrentnessResult,
    NonProductionAssessmentSubmissionMembershipCurrentnessStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionAssessmentSubmissionLifecycleState,
)


STATUS = NonProductionAssessmentSubmissionMembershipCurrentnessStatus
UPSTREAM_STATUS = NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus
BC_STATUS = NonProductionAssessmentSubmissionBusinessContextStatus
OPERATION = NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
SOURCE_AUTHORITY = "non-production-membership-authority"
CURRENTNESS_AUTHORITY = (
    "non-production-assessment-submission-membership-currentness-authority"
)
GOVERNANCE = "membership-authority-source-governance-v1"
PROVENANCE_1 = (
    "non-production-assessment-submission-membership-currentness-"
    "establishment-provenance-1"
)
_DEFAULT = object()


UPSTREAM_FIELDS = (
    "attempt_reference", "resource_reference", "resource_id", "principal_id",
    "engagement_reference", "business_entity_id", "protected_operation",
    "principal_authority_reference", "engagement_authority_reference",
    "engagement_establishment_provenance_reference", "participation_authority_reference",
    "participation_provenance_reference", "business_entity_authority_reference",
    "allocation_authority_reference", "allocation_provenance_reference",
    "binding_authority_reference", "binding_provenance_reference", "resource_class",
    "resource_lifecycle_state", "lifecycle_authority_reference", "lifecycle_provenance_reference",
    "target_authority_reference", "target_provenance_reference", "target_governance_reference",
    "resource_identity_state", "resource_identity_authority_reference",
    "resource_identity_provenance_reference", "resource_identity_governance_reference",
    "requested_action", "applicability", "applicability_authority_reference",
    "applicability_provenance_reference", "applicability_governance_reference",
    "business_entity_state", "business_entity_currentness_authority_reference",
    "business_entity_currentness_provenance_reference", "business_entity_governance_reference",
)
EVIDENCE_FIELDS = UPSTREAM_FIELDS + (
    "membership_state", "membership_authority_reference",
    "membership_currentness_authority_reference",
    "membership_currentness_provenance_reference", "membership_governance_reference",
)


class StringSubclass(str):
    pass


class MembershipSubclass(Membership):
    pass


class ContextResultSubclass(NonProductionAssessmentSubmissionBusinessContextResult):
    pass


class ForeignStatus(Enum):
    FOUND = "FOUND"


class ForeignState(Enum):
    ACTIVE = "ACTIVE"


class ForeignLifecycle(Enum):
    SUBMITTED = "SUBMITTED"


class ForeignLookup:
    def __init__(self, status, records=()):
        self.status = status
        self.records = records


class Coercible:
    def __str__(self):
        return "principal-alpha"


def business_context(**overrides):
    values = {
        "attempt_reference": "attempt-alpha",
        "principal_id": "principal-alpha",
        "engagement_reference": "engagement-alpha",
        "business_entity_id": "business-alpha",
        "protected_operation": OPERATION,
        "principal_authority_reference": "principal-authority",
        "engagement_authority_reference": "engagement-authority",
        "engagement_establishment_provenance_reference": "engagement-provenance",
        "participation_authority_reference": "participation-authority",
        "participation_provenance_reference": "participation-provenance",
        "business_entity_authority_reference": "non-production-business-entity-authority",
    }
    values.update(overrides)
    return NonProductionAssessmentSubmissionBusinessContext(**values)


def context_result(*, status=BC_STATUS.READY, context=_DEFAULT):
    if context is _DEFAULT:
        context = business_context() if status is BC_STATUS.READY else None
    return NonProductionAssessmentSubmissionBusinessContextResult(status, context)


def authority(*resources):
    return NonProductionAssessmentSubmissionMembershipCurrentnessAuthority(
        candidate_resource_references=tuple(resources),
    )


def establish(auth=None, value=_DEFAULT):
    auth = auth or authority("resource-alpha")
    value = context_result() if value is _DEFAULT else value
    return auth.establish_assessment_submission_membership_currentness(
        business_context_result=value,
    )


def upstream_result(value=None):
    value = value or context_result()
    return NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority(
        candidate_resource_references=("resource-alpha",)
    ).establish_assessment_submission_business_entity_currentness(
        business_context_result=value,
    )


def changed_upstream(result, **changes):
    evidence = dataclasses.replace(result.establishment_evidence, **changes)
    fact_changes = {
        name: changes[name]
        for name in ("business_entity_id", "business_entity_state")
        if name in changes
    }
    fact = dataclasses.replace(result.business_entity_currentness_fact, **fact_changes)
    return NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(
        result.status,
        fact,
        evidence,
    )


def found_membership(**changes):
    values = {
        "authority_reference": SOURCE_AUTHORITY,
        "state": AuthorityRecordState.ACTIVE,
        "principal_id": "principal-alpha",
        "business_entity_id": "business-alpha",
    }
    values.update(changes)
    return AuthorityLookupResult.found(Membership(**values))


class MembershipCurrentnessEstablishmentTests(unittest.TestCase):
    def assert_failure(self, result, status):
        self.assertIs(type(result), NonProductionAssessmentSubmissionMembershipCurrentnessResult)
        self.assertIs(result.status, status)
        self.assertIsNone(result.membership_currentness_fact)
        self.assertIsNone(result.establishment_evidence)

    def test_01_public_surface_signatures_and_models_are_exact(self):
        public = {
            name for name, value in vars(module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(public, {
            "NonProductionAssessmentSubmissionMembershipCurrentnessAuthority",
            "NonProductionAssessmentSubmissionMembershipCurrentnessFact",
            "NonProductionAssessmentSubmissionMembershipCurrentnessEvidence",
            "NonProductionAssessmentSubmissionMembershipCurrentnessStatus",
            "NonProductionAssessmentSubmissionMembershipCurrentnessResult",
        })
        self.assertEqual(
            str(inspect.signature(NonProductionAssessmentSubmissionMembershipCurrentnessAuthority)),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) -> 'None'",
        )
        self.assertEqual(
            str(inspect.signature(NonProductionAssessmentSubmissionMembershipCurrentnessAuthority.establish_assessment_submission_membership_currentness)),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionMembershipCurrentnessResult'",
        )
        self.assertEqual(tuple(field.name for field in dataclasses.fields(NonProductionAssessmentSubmissionMembershipCurrentnessFact)), ("principal_id", "business_entity_id", "membership_state"))
        self.assertEqual(tuple(field.name for field in dataclasses.fields(NonProductionAssessmentSubmissionMembershipCurrentnessEvidence)), EVIDENCE_FIELDS)
        self.assertEqual(tuple(field.name for field in dataclasses.fields(NonProductionAssessmentSubmissionMembershipCurrentnessResult)), ("status", "membership_currentness_fact", "establishment_evidence"))

    def test_02_status_enum_is_exactly_twenty_five_members(self):
        self.assertEqual(tuple(member.name for member in STATUS), (
            "ESTABLISHED", "REUSED", "MALFORMED", "BUSINESS_CONTEXT_NOT_READY",
            "UNSUPPORTED_OPERATION", "MISMATCH", "COLLISION", "ALLOCATION_UNAVAILABLE",
            "RESOURCE_IDENTITY_NOT_FOUND", "RESOURCE_IDENTITY_AMBIGUOUS",
            "RESOURCE_IDENTITY_CONFLICTING", "RESOURCE_IDENTITY_STALE",
            "RESOURCE_IDENTITY_UNAVAILABLE", "APPLICABILITY_NOT_APPLICABLE",
            "APPLICABILITY_UNRESOLVED", "BUSINESS_ENTITY_NOT_FOUND",
            "BUSINESS_ENTITY_AMBIGUOUS", "BUSINESS_ENTITY_CONFLICTING",
            "BUSINESS_ENTITY_STALE", "BUSINESS_ENTITY_UNAVAILABLE",
            "MEMBERSHIP_NOT_FOUND", "MEMBERSHIP_AMBIGUOUS",
            "MEMBERSHIP_CONFLICTING", "MEMBERSHIP_STALE", "MEMBERSHIP_UNAVAILABLE",
        ))

    def test_03_private_authorities_and_fixed_fixture_are_exact(self):
        auth = authority("resource-alpha")
        upstream = object.__getattribute__(auth, "_business_entity_currentness_authority")
        source = object.__getattribute__(auth, "_membership_source")
        self.assertIs(type(upstream), NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority)
        self.assertIs(type(source), NonProductionMembershipAuthoritySource)
        found = source.resolve_membership("principal-alpha", "business-alpha")
        self.assertEqual(found.records, (Membership(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha"),))
        self.assertIs(source.resolve_membership("principal-beta", "business-alpha").status, AuthorityLookupStatus.NOT_FOUND)
        self.assertIs(source.resolve_membership("principal-alpha", "business-beta").status, AuthorityLookupStatus.NOT_FOUND)

    def test_04_success_preserves_all_upstream_lineage_and_appends_authority(self):
        upstream = upstream_result()
        result = establish()
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(
            tuple(getattr(result.establishment_evidence, name) for name in UPSTREAM_FIELDS),
            tuple(getattr(upstream.establishment_evidence, name) for name in UPSTREAM_FIELDS),
        )
        self.assertEqual(result.membership_currentness_fact, NonProductionAssessmentSubmissionMembershipCurrentnessFact("principal-alpha", "business-alpha", AuthorityRecordState.ACTIVE))
        evidence = result.establishment_evidence
        self.assertIs(evidence.membership_state, AuthorityRecordState.ACTIVE)
        self.assertEqual(evidence.membership_authority_reference, SOURCE_AUTHORITY)
        self.assertEqual(evidence.membership_currentness_authority_reference, CURRENTNESS_AUTHORITY)
        self.assertEqual(evidence.membership_currentness_provenance_reference, PROVENANCE_1)
        self.assertEqual(evidence.membership_governance_reference, GOVERNANCE)

    def test_05_retry_revalidates_b_and_membership_and_returns_fresh_outputs(self):
        auth = authority("resource-alpha")
        upstream = object.__getattribute__(auth, "_business_entity_currentness_authority")
        source = object.__getattribute__(auth, "_membership_source")
        upstream_method = type(upstream).establish_assessment_submission_business_entity_currentness
        source_method = type(source).resolve_membership
        with patch.object(type(upstream), upstream_method.__name__, autospec=True, wraps=upstream_method) as up_probe:
            with patch.object(type(source), source_method.__name__, autospec=True, wraps=source_method) as source_probe:
                first = establish(auth)
                second = establish(auth)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.REUSED)
        self.assertEqual(up_probe.call_count, 2)
        self.assertEqual(source_probe.call_count, 2)
        self.assertEqual(first.membership_currentness_fact, second.membership_currentness_fact)
        self.assertEqual(first.establishment_evidence, second.establishment_evidence)
        self.assertIsNot(first, second)
        self.assertIsNot(first.membership_currentness_fact, second.membership_currentness_fact)
        self.assertIsNot(first.establishment_evidence, second.establishment_evidence)
        self.assertEqual(len(object.__getattribute__(auth, "_currentness_by_attempt")), 1)
        self.assertEqual(object.__getattribute__(auth, "_next_membership_currentness_provenance_index"), 2)

    def test_06_all_eighteen_upstream_failures_map_one_to_one(self):
        failures = tuple(status for status in UPSTREAM_STATUS if status not in (UPSTREAM_STATUS.ESTABLISHED, UPSTREAM_STATUS.REUSED))
        self.assertEqual(len(failures), 18)
        for upstream_status in failures:
            with self.subTest(status=upstream_status):
                auth = authority("resource-alpha")
                private = object.__getattribute__(auth, "_business_entity_currentness_authority")
                with patch.object(type(private), "establish_assessment_submission_business_entity_currentness", return_value=NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(upstream_status)):
                    self.assert_failure(establish(auth), STATUS[upstream_status.name])
                self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})

    def test_07_malformed_upstream_outputs_fail_before_membership_lookup(self):
        valid = upstream_result()
        malformed = (
            object(),
            NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(UPSTREAM_STATUS.MALFORMED, valid.business_entity_currentness_fact, valid.establishment_evidence),
            NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(UPSTREAM_STATUS.ESTABLISHED, None, valid.establishment_evidence),
        )
        for output in malformed:
            with self.subTest(output=type(output)):
                auth = authority("resource-alpha")
                upstream = object.__getattribute__(auth, "_business_entity_currentness_authority")
                source = object.__getattribute__(auth, "_membership_source")
                with patch.object(type(upstream), "establish_assessment_submission_business_entity_currentness", return_value=output):
                    with patch.object(type(source), "resolve_membership") as probe:
                        self.assert_failure(establish(auth), STATUS.MALFORMED)
                probe.assert_not_called()

    def test_08_all_lookup_statuses_map_exactly(self):
        mappings = {
            AuthorityLookupStatus.NOT_FOUND: STATUS.MEMBERSHIP_NOT_FOUND,
            AuthorityLookupStatus.STALE: STATUS.MEMBERSHIP_STALE,
            AuthorityLookupStatus.UNAVAILABLE: STATUS.MEMBERSHIP_UNAVAILABLE,
            AuthorityLookupStatus.MALFORMED: STATUS.MALFORMED,
            AuthorityLookupStatus.UNSUPPORTED: STATUS.MALFORMED,
        }
        for lookup, expected in mappings.items():
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_membership_source")
                with patch.object(type(source), "resolve_membership", return_value=AuthorityLookupResult(lookup)):
                    self.assert_failure(establish(auth), expected)

    def test_09_lookup_exception_is_unavailable_and_does_not_consume(self):
        auth = authority("resource-alpha")
        source = object.__getattribute__(auth, "_membership_source")
        with patch.object(type(source), "resolve_membership", side_effect=RuntimeError):
            self.assert_failure(establish(auth), STATUS.MEMBERSHIP_UNAVAILABLE)
        recovered = establish(auth)
        self.assertIs(recovered.status, STATUS.ESTABLISHED)
        self.assertEqual(recovered.establishment_evidence.membership_currentness_provenance_reference, PROVENANCE_1)

    def test_10_found_payload_requires_one_exact_active_membership(self):
        invalid = (
            AuthorityLookupResult(AuthorityLookupStatus.FOUND),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (object(),)),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (Membership(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha"),) * 2),
            AuthorityLookupResult.found(MembershipSubclass(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha")),
            found_membership(state=AuthorityRecordState.REVOKED),
            found_membership(state=ForeignState.ACTIVE),
        )
        for lookup in invalid:
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_membership_source")
                with patch.object(type(source), "resolve_membership", return_value=lookup):
                    self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_11_wrong_p_b_or_authority_is_mismatch(self):
        for lookup in (
            found_membership(principal_id="principal-beta"),
            found_membership(business_entity_id="business-beta"),
            found_membership(authority_reference="other-authority"),
        ):
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_membership_source")
                with patch.object(type(source), "resolve_membership", return_value=lookup):
                    self.assert_failure(establish(auth), STATUS.MISMATCH)

    def test_12_lookup_types_strings_and_coercion_are_hardened(self):
        invalid = (
            ForeignLookup(AuthorityLookupStatus.FOUND, found_membership().records),
            AuthorityLookupResult(ForeignStatus.FOUND, found_membership().records),
            found_membership(authority_reference=StringSubclass(SOURCE_AUTHORITY)),
            found_membership(authority_reference=" " + SOURCE_AUTHORITY),
            found_membership(principal_id="principal-alpha "),
            found_membership(business_entity_id=" "),
            found_membership(principal_id=Coercible()),
        )
        for lookup in invalid:
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_membership_source")
                with patch.object(type(source), "resolve_membership", return_value=lookup):
                    self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_13_public_input_and_dependency_types_are_hardened(self):
        cases = (
            object(), {}, ContextResultSubclass(BC_STATUS.READY, business_context()),
            context_result(context=business_context(principal_id=StringSubclass("principal-alpha"))),
            context_result(context=business_context(engagement_reference=" engagement-alpha")),
            context_result(context=business_context(business_entity_id=Coercible())),
        )
        for value in cases:
            with self.subTest(value=type(value)):
                self.assert_failure(establish(value=value), STATUS.MALFORMED)
        self.assert_failure(establish(value=context_result(status=BC_STATUS.ENGAGEMENT_NOT_READY)), STATUS.BUSINESS_CONTEXT_NOT_READY)

    def test_14_public_input_precedes_upstream_and_upstream_precedes_membership(self):
        auth = authority("resource-alpha")
        upstream = object.__getattribute__(auth, "_business_entity_currentness_authority")
        source = object.__getattribute__(auth, "_membership_source")
        with patch.object(type(upstream), "establish_assessment_submission_business_entity_currentness") as upstream_probe:
            with patch.object(type(source), "resolve_membership") as source_probe:
                self.assert_failure(establish(auth, object()), STATUS.MALFORMED)
        upstream_probe.assert_not_called()
        source_probe.assert_not_called()
        with patch.object(type(upstream), "establish_assessment_submission_business_entity_currentness", return_value=NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(UPSTREAM_STATUS.MISMATCH)):
            with patch.object(type(source), "resolve_membership") as source_probe:
                self.assert_failure(establish(auth), STATUS.MISMATCH)
        source_probe.assert_not_called()

    def test_15_cross_context_and_invalid_lineage_substitutions_fail_closed(self):
        valid = upstream_result()
        substitutions = {
            "attempt_reference": "attempt-beta",
            "principal_id": "principal-beta",
            "engagement_reference": "engagement-beta",
            "business_entity_id": "business-beta",
            "resource_reference": "resource-beta",
            "resource_id": "resource-beta",
            "resource_class": ResourceClass.REPORT,
            "resource_lifecycle_state": ForeignLifecycle.SUBMITTED,
            "protected_operation": "wrong",
            "requested_action": RequestedAction.VIEW,
            "applicability": ResourceActionApplicability.NOT_APPLICABLE,
            "business_entity_currentness_authority_reference": "wrong-authority",
            "business_entity_governance_reference": "wrong-governance",
        }
        for field, value in substitutions.items():
            with self.subTest(field=field):
                auth = authority("resource-alpha")
                private = object.__getattribute__(auth, "_business_entity_currentness_authority")
                with patch.object(type(private), "establish_assessment_submission_business_entity_currentness", return_value=changed_upstream(valid, **{field: value})):
                    result = establish(auth)
                self.assertIn(result.status, (STATUS.MALFORMED, STATUS.MISMATCH))

    def test_16_changed_provenance_after_success_cannot_reuse(self):
        for field in (
            "target_provenance_reference",
            "resource_identity_provenance_reference",
            "applicability_provenance_reference",
            "business_entity_currentness_provenance_reference",
        ):
            with self.subTest(field=field):
                auth = authority("resource-alpha")
                self.assertIs(establish(auth).status, STATUS.ESTABLISHED)
                private = object.__getattribute__(auth, "_business_entity_currentness_authority")
                changed = changed_upstream(upstream_result(), **{field: "changed-provenance"})
                with patch.object(type(private), "establish_assessment_submission_business_entity_currentness", return_value=changed):
                    self.assert_failure(establish(auth), STATUS.MISMATCH)
                self.assertIs(establish(auth).status, STATUS.REUSED)

    def test_17_fresh_membership_failures_defeat_prior_success(self):
        statuses = (
            (AuthorityLookupResult.missing(), STATUS.MEMBERSHIP_NOT_FOUND),
            (AuthorityLookupResult.stale(), STATUS.MEMBERSHIP_STALE),
            (AuthorityLookupResult.unavailable(), STATUS.MEMBERSHIP_UNAVAILABLE),
            (AuthorityLookupResult(AuthorityLookupStatus.MALFORMED), STATUS.MALFORMED),
        )
        for lookup, expected in statuses:
            with self.subTest(status=expected):
                auth = authority("resource-alpha")
                first = establish(auth)
                source = object.__getattribute__(auth, "_membership_source")
                with patch.object(type(source), "resolve_membership", return_value=lookup):
                    self.assert_failure(establish(auth), expected)
                retry = establish(auth)
                self.assertIs(first.status, STATUS.ESTABLISHED)
                self.assertIs(retry.status, STATUS.REUSED)
                self.assertEqual(retry.establishment_evidence.membership_currentness_provenance_reference, PROVENANCE_1)

    def test_18_cardinality_multiple_attempts_and_no_extra_indexes(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        second = establish(auth, context_result(context=business_context(attempt_reference="attempt-beta")))
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.ESTABLISHED)
        self.assertNotEqual(first.establishment_evidence.membership_currentness_provenance_reference, second.establishment_evidence.membership_currentness_provenance_reference)
        self.assertEqual(set(object.__getattribute__(auth, "_currentness_by_attempt")), {"attempt-alpha", "attempt-beta"})
        self.assertNotIn("_currentness_by_membership", dir(auth))
        self.assertNotIn("_currentness_by_principal_id", dir(auth))

    def test_19_returned_mutation_does_not_change_canonical_state(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        object.__setattr__(first.membership_currentness_fact, "principal_id", "attacker")
        object.__setattr__(first.establishment_evidence, "membership_authority_reference", "attacker")
        object.__setattr__(first, "status", STATUS.MALFORMED)
        retry = establish(auth)
        self.assertIs(retry.status, STATUS.REUSED)
        self.assertEqual(retry.membership_currentness_fact.principal_id, "principal-alpha")
        self.assertEqual(retry.establishment_evidence.membership_authority_reference, SOURCE_AUTHORITY)

    def test_20_instances_and_provenance_are_isolated(self):
        first = establish(authority("resource-alpha"))
        second = establish(authority("resource-alpha"))
        self.assertEqual(first.establishment_evidence.membership_currentness_provenance_reference, PROVENANCE_1)
        self.assertEqual(second.establishment_evidence.membership_currentness_provenance_reference, PROVENANCE_1)

    def test_21_no_public_dependency_injection_or_authority_laundering(self):
        auth = authority("resource-alpha")
        method = auth.establish_assessment_submission_membership_currentness
        prohibited = {
            "principal_id": "principal-alpha",
            "business_entity_id": "business-alpha",
            "membership": Membership(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha"),
            "membership_source": NonProductionMembershipAuthoritySource(),
            "lookup_result": AuthorityLookupResult.missing(),
            "upstream_result": upstream_result(),
        }
        for name, value in prohibited.items():
            with self.subTest(name=name):
                with self.assertRaises(TypeError):
                    method(business_context_result=context_result(), **{name: value})
        for value in (
            prohibited["membership"], prohibited["lookup_result"],
            Entitlement(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha", "resource-alpha", RequestedAction.SUBMIT),
            AuthorizationRequest(None, None, None, None, "correlation", "context"),
            {"principal_id": "principal-alpha"}, Coercible(),
        ):
            self.assert_failure(establish(value=value), STATUS.MALFORMED)

    def test_22_fixture_does_not_expand_to_p2_or_b2(self):
        auth = authority("resource-alpha")
        private = object.__getattribute__(auth, "_business_entity_currentness_authority")
        p2_context = context_result(context=business_context(principal_id="principal-beta"))
        p2_upstream = upstream_result(p2_context)
        with patch.object(type(private), "establish_assessment_submission_business_entity_currentness", return_value=p2_upstream):
            self.assert_failure(establish(auth, p2_context), STATUS.MEMBERSHIP_NOT_FOUND)
        source = object.__getattribute__(auth, "_membership_source")
        self.assertIs(source.resolve_membership("principal-alpha", "business-beta").status, AuthorityLookupStatus.NOT_FOUND)

    def test_23_output_construction_failure_does_not_commit_or_consume(self):
        auth = authority("resource-alpha")
        with patch.object(module, "_success_output", side_effect=RuntimeError):
            self.assert_failure(establish(auth), STATUS.MALFORMED)
        self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})
        self.assertEqual(object.__getattribute__(auth, "_next_membership_currentness_provenance_index"), 1)
        self.assertIs(establish(auth).status, STATUS.ESTABLISHED)

    def test_24_no_entitlement_evaluator_lifecycle_runtime_or_production_effects(self):
        source = Path(module.__file__).read_text()
        forbidden = (
            "resolve_entitlement", "TrustedAuthorizationEvaluator", "AuthorizationDecision",
            "boto3", "cognito", "dynamodb", "boto3.client", "api_gateway",
            "os.environ", "open(", "SUBMITTED", "ABANDONED",
        )
        for value in forbidden:
            self.assertNotIn(value, source)
        result = establish()
        names = {field.name for field in dataclasses.fields(type(result.membership_currentness_fact))}
        names |= {field.name for field in dataclasses.fields(type(result.establishment_evidence))}
        self.assertTrue({"entitlement", "permission", "allow", "deny", "role"}.isdisjoint(names))

    def test_25_generic_sources_are_reused_unchanged(self):
        self.assertIs(module._MembershipSource, NonProductionMembershipAuthoritySource)
        self.assertIs(module._UpstreamAuthority, NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority)

    def test_26_foreign_same_shaped_records_ducks_and_failure_payloads_fail(self):
        @dataclasses.dataclass(frozen=True)
        class ForeignMembership:
            authority_reference: str
            state: object
            principal_id: str
            business_entity_id: str

        class DuckMembership:
            authority_reference = SOURCE_AUTHORITY
            state = AuthorityRecordState.ACTIVE
            principal_id = "principal-alpha"
            business_entity_id = "business-alpha"

        invalid = (
            AuthorityLookupResult.found(ForeignMembership(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha")),
            AuthorityLookupResult.found(DuckMembership()),
            AuthorityLookupResult(AuthorityLookupStatus.NOT_FOUND, found_membership().records),
            AuthorityLookupResult(AuthorityLookupStatus.AMBIGUOUS),
            AuthorityLookupResult(AuthorityLookupStatus.CONFLICTING),
            AuthorityLookupResult.ambiguous(
                found_membership(principal_id="principal-beta").records * 2
            ),
            AuthorityLookupResult.conflicting(found_membership().records * 2),
            AuthorityLookupResult.ambiguous((object(), object())),
            {"status": AuthorityLookupStatus.FOUND, "records": found_membership().records},
        )
        for lookup in invalid:
            with self.subTest(lookup=type(lookup)):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_membership_source")
                with patch.object(type(source), "resolve_membership", return_value=lookup):
                    self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_27_private_dependency_replacement_fails_exact_type_checks(self):
        auth = authority("resource-alpha")
        object.__setattr__(auth, "_business_entity_currentness_authority", object())
        self.assert_failure(establish(auth), STATUS.MALFORMED)
        auth = authority("resource-alpha")
        object.__setattr__(auth, "_membership_source", object())
        self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_28_b2_upstream_lineage_cannot_create_membership_authority(self):
        b2_context = context_result(context=business_context(business_entity_id="business-beta"))
        forged_success = changed_upstream(
            upstream_result(),
            business_entity_id="business-beta",
        )
        auth = authority("resource-alpha")
        private = object.__getattribute__(auth, "_business_entity_currentness_authority")
        with patch.object(
            type(private),
            "establish_assessment_submission_business_entity_currentness",
            return_value=forged_success,
        ):
            self.assert_failure(establish(auth, b2_context), STATUS.MEMBERSHIP_NOT_FOUND)
        self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})

    def test_29_fresh_upstream_failure_after_success_defeats_reuse(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        private = object.__getattribute__(auth, "_business_entity_currentness_authority")
        with patch.object(
            type(private),
            "establish_assessment_submission_business_entity_currentness",
            return_value=NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult(
                UPSTREAM_STATUS.BUSINESS_ENTITY_STALE
            ),
        ):
            self.assert_failure(establish(auth), STATUS.BUSINESS_ENTITY_STALE)
        retry = establish(auth)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(retry.status, STATUS.REUSED)
        self.assertEqual(
            retry.establishment_evidence.membership_currentness_provenance_reference,
            PROVENANCE_1,
        )

    def test_30_real_generic_ambiguity_and_conflict_map_without_consuming(self):
        record = Membership(
            SOURCE_AUTHORITY,
            AuthorityRecordState.ACTIVE,
            "principal-alpha",
            "business-alpha",
        )
        cases = (
            (
                NonProductionMembershipAuthoritySource((record, record)),
                AuthorityLookupStatus.AMBIGUOUS,
                STATUS.MEMBERSHIP_AMBIGUOUS,
            ),
            (
                NonProductionMembershipAuthoritySource(
                    (
                        record,
                        dataclasses.replace(record, authority_reference="conflicting-authority"),
                    )
                ),
                AuthorityLookupStatus.CONFLICTING,
                STATUS.MEMBERSHIP_CONFLICTING,
            ),
        )
        for source, generic_status, specialized_status in cases:
            with self.subTest(status=generic_status):
                generic = source.resolve_membership("principal-alpha", "business-alpha")
                self.assertIs(generic.status, generic_status)
                self.assertEqual(len(generic.records), 2)
                auth = authority("resource-alpha")
                object.__setattr__(auth, "_membership_source", source)
                self.assert_failure(establish(auth), specialized_status)
                self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})
                self.assertEqual(
                    object.__getattribute__(auth, "_next_membership_currentness_provenance_index"),
                    1,
                )

    def test_31_fresh_real_ambiguity_and_conflict_defeat_reuse(self):
        record = Membership(
            SOURCE_AUTHORITY,
            AuthorityRecordState.ACTIVE,
            "principal-alpha",
            "business-alpha",
        )
        cases = (
            (
                NonProductionMembershipAuthoritySource((record, record)),
                STATUS.MEMBERSHIP_AMBIGUOUS,
            ),
            (
                NonProductionMembershipAuthoritySource(
                    (
                        record,
                        dataclasses.replace(record, authority_reference="conflicting-authority"),
                    )
                ),
                STATUS.MEMBERSHIP_CONFLICTING,
            ),
        )
        for failing_source, expected in cases:
            with self.subTest(status=expected):
                auth = authority("resource-alpha")
                valid_source = object.__getattribute__(auth, "_membership_source")
                first = establish(auth)
                object.__setattr__(auth, "_membership_source", failing_source)
                self.assert_failure(establish(auth), expected)
                self.assertEqual(len(object.__getattribute__(auth, "_currentness_by_attempt")), 1)
                self.assertEqual(
                    object.__getattribute__(auth, "_next_membership_currentness_provenance_index"),
                    2,
                )
                object.__setattr__(auth, "_membership_source", valid_source)
                retry = establish(auth)
                self.assertIs(first.status, STATUS.ESTABLISHED)
                self.assertIs(retry.status, STATUS.REUSED)
                self.assertEqual(
                    retry.establishment_evidence.membership_currentness_provenance_reference,
                    PROVENANCE_1,
                )


if __name__ == "__main__":
    unittest.main()
