import dataclasses
import inspect
import sys
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_business_entity_currentness_establishment as currentness_module  # noqa: E402
from trusted_authorization.business_entity_source import (  # noqa: E402
    NonProductionBusinessEntityAuthoritySource,
)
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationRequest,
    BusinessEntity,
    Entitlement,
    GovernedResource,
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
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult,
    NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_action_applicability_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority,
    NonProductionAssessmentSubmissionResourceActionApplicabilityResult,
    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionAssessmentSubmissionLifecycleState,
)


STATUS = NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus
APP_STATUS = NonProductionAssessmentSubmissionResourceActionApplicabilityStatus
BC_STATUS = NonProductionAssessmentSubmissionBusinessContextStatus
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)
SOURCE_AUTHORITY = "non-production-business-entity-authority"
CURRENTNESS_AUTHORITY = (
    "non-production-assessment-submission-business-entity-currentness-authority"
)
GOVERNANCE = "business-entity-authority-source-governance-v1"
PROVENANCE_1 = (
    "non-production-assessment-submission-business-entity-currentness-"
    "establishment-provenance-1"
)
_DEFAULT = object()


APPLICABILITY_FIELDS = (
    "attempt_reference",
    "resource_reference",
    "resource_id",
    "principal_id",
    "engagement_reference",
    "business_entity_id",
    "protected_operation",
    "principal_authority_reference",
    "engagement_authority_reference",
    "engagement_establishment_provenance_reference",
    "participation_authority_reference",
    "participation_provenance_reference",
    "business_entity_authority_reference",
    "allocation_authority_reference",
    "allocation_provenance_reference",
    "binding_authority_reference",
    "binding_provenance_reference",
    "resource_class",
    "resource_lifecycle_state",
    "lifecycle_authority_reference",
    "lifecycle_provenance_reference",
    "target_authority_reference",
    "target_provenance_reference",
    "target_governance_reference",
    "resource_identity_state",
    "resource_identity_authority_reference",
    "resource_identity_provenance_reference",
    "resource_identity_governance_reference",
    "requested_action",
    "applicability",
    "applicability_authority_reference",
    "applicability_provenance_reference",
    "applicability_governance_reference",
)

EVIDENCE_FIELDS = APPLICABILITY_FIELDS + (
    "business_entity_state",
    "business_entity_currentness_authority_reference",
    "business_entity_currentness_provenance_reference",
    "business_entity_governance_reference",
)


class StringSubclass(str):
    pass


class ContextResultSubclass(NonProductionAssessmentSubmissionBusinessContextResult):
    pass


class BusinessEntitySubclass(BusinessEntity):
    pass


class ForeignStatus(Enum):
    FOUND = "FOUND"


class ForeignLifecycle(Enum):
    SUBMITTED = "SUBMITTED"


class ForeignLookup:
    def __init__(self, status, records=()):
        self.status = status
        self.records = records


class Coercible:
    def __str__(self):
        return "business-alpha"


def business_context(**overrides):
    values = {
        "attempt_reference": "attempt-alpha",
        "principal_id": "principal-alpha",
        "engagement_reference": "engagement-alpha",
        "business_entity_id": "business-alpha",
        "protected_operation": PROTECTED_ASSESSMENT,
        "principal_authority_reference": "principal-authority",
        "engagement_authority_reference": "engagement-authority",
        "engagement_establishment_provenance_reference": "engagement-provenance",
        "participation_authority_reference": "participation-authority",
        "participation_provenance_reference": "participation-provenance",
        "business_entity_authority_reference": SOURCE_AUTHORITY,
    }
    values.update(overrides)
    return NonProductionAssessmentSubmissionBusinessContext(**values)


def business_context_result(*, status=BC_STATUS.READY, context=_DEFAULT):
    if context is _DEFAULT:
        context = business_context() if status is BC_STATUS.READY else None
    return NonProductionAssessmentSubmissionBusinessContextResult(status, context)


def authority(*resources):
    return NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority(
        candidate_resource_references=tuple(resources),
    )


def establish(auth=None, context_result=_DEFAULT):
    if auth is None:
        auth = authority("resource-alpha")
    if context_result is _DEFAULT:
        context_result = business_context_result()
    return auth.establish_assessment_submission_business_entity_currentness(
        business_context_result=context_result,
    )


def applicability_result(*, resource="resource-alpha", context_result=None):
    if context_result is None:
        context_result = business_context_result()
    source = NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority(
        candidate_resource_references=(resource,),
    )
    return source.establish_assessment_submission_resource_action_applicability(
        business_context_result=context_result,
    )


def changed_applicability(result, **changes):
    evidence = dataclasses.replace(result.establishment_evidence, **changes)
    fact_changes = {
        name: changes[name]
        for name in (
            "resource_reference",
            "resource_id",
            "resource_class",
            "requested_action",
            "applicability",
        )
        if name in changes
    }
    fact = dataclasses.replace(result.applicability_fact, **fact_changes)
    return NonProductionAssessmentSubmissionResourceActionApplicabilityResult(
        status=result.status,
        applicability_fact=fact,
        establishment_evidence=evidence,
    )


def found_record(**changes):
    values = {
        "authority_reference": SOURCE_AUTHORITY,
        "state": AuthorityRecordState.ACTIVE,
        "business_entity_id": "business-alpha",
    }
    values.update(changes)
    return AuthorityLookupResult.found(BusinessEntity(**values))


class BusinessEntityCurrentnessEstablishmentTests(unittest.TestCase):
    def assert_failure(self, result, status):
        self.assertIs(type(result), NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult)
        self.assertIs(result.status, status)
        self.assertIsNone(result.business_entity_currentness_fact)
        self.assertIsNone(result.establishment_evidence)

    def test_01_public_surface_is_exactly_five_types(self):
        public = {
            name
            for name, value in vars(currentness_module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(
            public,
            {
                "NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority",
                "NonProductionAssessmentSubmissionBusinessEntityCurrentnessFact",
                "NonProductionAssessmentSubmissionBusinessEntityCurrentnessEvidence",
                "NonProductionAssessmentSubmissionBusinessEntityCurrentnessStatus",
                "NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult",
            },
        )

    def test_02_signatures_and_public_authority_input_are_exact(self):
        constructor = inspect.signature(
            NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority
        )
        self.assertEqual(
            str(constructor),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) -> 'None'",
        )
        method = inspect.signature(
            NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority.
            establish_assessment_submission_business_entity_currentness
        )
        self.assertEqual(
            str(method),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionBusinessEntityCurrentnessResult'",
        )
        with self.assertRaises(TypeError):
            NonProductionAssessmentSubmissionBusinessEntityCurrentnessAuthority(
                business_entity_id="business-alpha"
            )
        with self.assertRaises(TypeError):
            establish(authority("resource-alpha"), business_entity_result=object())

    def test_03_private_authorities_and_fixed_fixture_are_retained(self):
        auth = authority("resource-alpha")
        app = object.__getattribute__(auth, "_applicability_authority")
        source = object.__getattribute__(auth, "_business_entity_source")
        self.assertIs(type(app), NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority)
        self.assertIs(type(source), NonProductionBusinessEntityAuthoritySource)
        first = source.resolve_business_entity("business-alpha")
        second = source.resolve_business_entity("business-alpha")
        self.assertIs(first.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(first.records, second.records)
        self.assertEqual(
            first.records,
            (
                BusinessEntity(
                    authority_reference=SOURCE_AUTHORITY,
                    state=AuthorityRecordState.ACTIVE,
                    business_entity_id="business-alpha",
                ),
            ),
        )

    def test_04_first_success_has_exact_fact_evidence_and_result_models(self):
        result = establish()
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(result.business_entity_currentness_fact))),
            ("business_entity_id", "business_entity_state"),
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(result.establishment_evidence))),
            EVIDENCE_FIELDS,
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(result))),
            ("status", "business_entity_currentness_fact", "establishment_evidence"),
        )
        self.assertEqual(result.business_entity_currentness_fact.business_entity_id, "business-alpha")
        self.assertIs(result.business_entity_currentness_fact.business_entity_state, AuthorityRecordState.ACTIVE)

    def test_05_all_upstream_lineage_is_preserved_exactly(self):
        upstream = applicability_result()
        result = establish()
        self.assertIs(upstream.status, APP_STATUS.ESTABLISHED)
        self.assertEqual(
            tuple(getattr(result.establishment_evidence, name) for name in APPLICABILITY_FIELDS),
            tuple(getattr(upstream.establishment_evidence, name) for name in APPLICABILITY_FIELDS),
        )
        evidence = result.establishment_evidence
        self.assertIs(evidence.business_entity_state, AuthorityRecordState.ACTIVE)
        self.assertEqual(evidence.business_entity_currentness_authority_reference, CURRENTNESS_AUTHORITY)
        self.assertEqual(evidence.business_entity_currentness_provenance_reference, PROVENANCE_1)
        self.assertEqual(evidence.business_entity_governance_reference, GOVERNANCE)

    def test_06_status_enum_is_exactly_twenty_members(self):
        self.assertEqual(
            tuple(member.name for member in STATUS),
            (
                "ESTABLISHED", "REUSED", "MALFORMED",
                "BUSINESS_CONTEXT_NOT_READY", "UNSUPPORTED_OPERATION",
                "MISMATCH", "COLLISION", "ALLOCATION_UNAVAILABLE",
                "RESOURCE_IDENTITY_NOT_FOUND", "RESOURCE_IDENTITY_AMBIGUOUS",
                "RESOURCE_IDENTITY_CONFLICTING", "RESOURCE_IDENTITY_STALE",
                "RESOURCE_IDENTITY_UNAVAILABLE", "APPLICABILITY_NOT_APPLICABLE",
                "APPLICABILITY_UNRESOLVED", "BUSINESS_ENTITY_NOT_FOUND",
                "BUSINESS_ENTITY_AMBIGUOUS", "BUSINESS_ENTITY_CONFLICTING",
                "BUSINESS_ENTITY_STALE", "BUSINESS_ENTITY_UNAVAILABLE",
            ),
        )

    def test_07_retry_is_revalidated_stable_and_returns_fresh_outputs(self):
        auth = authority("resource-alpha")
        app = object.__getattribute__(auth, "_applicability_authority")
        source = object.__getattribute__(auth, "_business_entity_source")
        app_method = type(app).establish_assessment_submission_resource_action_applicability
        source_method = type(source).resolve_business_entity
        with patch.object(type(app), app_method.__name__, autospec=True, wraps=app_method) as app_probe:
            with patch.object(type(source), source_method.__name__, autospec=True, wraps=source_method) as source_probe:
                first = establish(auth)
                second = establish(auth)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.REUSED)
        self.assertEqual(app_probe.call_count, 2)
        self.assertEqual(source_probe.call_count, 2)
        self.assertEqual(first.business_entity_currentness_fact, second.business_entity_currentness_fact)
        self.assertEqual(first.establishment_evidence, second.establishment_evidence)
        self.assertIsNot(first, second)
        self.assertIsNot(first.business_entity_currentness_fact, second.business_entity_currentness_fact)
        self.assertIsNot(first.establishment_evidence, second.establishment_evidence)
        self.assertEqual(len(object.__getattribute__(auth, "_currentness_by_attempt")), 1)
        self.assertEqual(object.__getattribute__(auth, "_next_business_entity_currentness_provenance_index"), 2)

    def test_08_all_thirteen_applicability_failures_map_one_to_one(self):
        mappings = {
            APP_STATUS.MALFORMED: STATUS.MALFORMED,
            APP_STATUS.BUSINESS_CONTEXT_NOT_READY: STATUS.BUSINESS_CONTEXT_NOT_READY,
            APP_STATUS.UNSUPPORTED_OPERATION: STATUS.UNSUPPORTED_OPERATION,
            APP_STATUS.MISMATCH: STATUS.MISMATCH,
            APP_STATUS.COLLISION: STATUS.COLLISION,
            APP_STATUS.ALLOCATION_UNAVAILABLE: STATUS.ALLOCATION_UNAVAILABLE,
            APP_STATUS.RESOURCE_IDENTITY_NOT_FOUND: STATUS.RESOURCE_IDENTITY_NOT_FOUND,
            APP_STATUS.RESOURCE_IDENTITY_AMBIGUOUS: STATUS.RESOURCE_IDENTITY_AMBIGUOUS,
            APP_STATUS.RESOURCE_IDENTITY_CONFLICTING: STATUS.RESOURCE_IDENTITY_CONFLICTING,
            APP_STATUS.RESOURCE_IDENTITY_STALE: STATUS.RESOURCE_IDENTITY_STALE,
            APP_STATUS.RESOURCE_IDENTITY_UNAVAILABLE: STATUS.RESOURCE_IDENTITY_UNAVAILABLE,
            APP_STATUS.APPLICABILITY_NOT_APPLICABLE: STATUS.APPLICABILITY_NOT_APPLICABLE,
            APP_STATUS.APPLICABILITY_UNRESOLVED: STATUS.APPLICABILITY_UNRESOLVED,
        }
        for upstream, expected in mappings.items():
            with self.subTest(upstream=upstream):
                auth = authority("resource-alpha")
                private = object.__getattribute__(auth, "_applicability_authority")
                with patch.object(
                    type(private),
                    "establish_assessment_submission_resource_action_applicability",
                    return_value=NonProductionAssessmentSubmissionResourceActionApplicabilityResult(upstream),
                ):
                    self.assert_failure(establish(auth), expected)
                self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})
                self.assertEqual(object.__getattribute__(auth, "_next_business_entity_currentness_provenance_index"), 1)

    def test_09_malformed_applicability_outputs_fail_closed(self):
        valid = applicability_result()
        malformed = (
            object(),
            NonProductionAssessmentSubmissionResourceActionApplicabilityResult(
                APP_STATUS.MALFORMED,
                valid.applicability_fact,
                valid.establishment_evidence,
            ),
            NonProductionAssessmentSubmissionResourceActionApplicabilityResult(
                APP_STATUS.ESTABLISHED,
                None,
                valid.establishment_evidence,
            ),
        )
        for output in malformed:
            with self.subTest(output=type(output)):
                auth = authority("resource-alpha")
                private = object.__getattribute__(auth, "_applicability_authority")
                with patch.object(
                    type(private),
                    "establish_assessment_submission_resource_action_applicability",
                    return_value=output,
                ):
                    self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_10_all_generic_lookup_failures_map_exactly(self):
        mappings = {
            AuthorityLookupStatus.NOT_FOUND: STATUS.BUSINESS_ENTITY_NOT_FOUND,
            AuthorityLookupStatus.AMBIGUOUS: STATUS.BUSINESS_ENTITY_AMBIGUOUS,
            AuthorityLookupStatus.CONFLICTING: STATUS.BUSINESS_ENTITY_CONFLICTING,
            AuthorityLookupStatus.STALE: STATUS.BUSINESS_ENTITY_STALE,
            AuthorityLookupStatus.UNAVAILABLE: STATUS.BUSINESS_ENTITY_UNAVAILABLE,
            AuthorityLookupStatus.MALFORMED: STATUS.MALFORMED,
            AuthorityLookupStatus.UNSUPPORTED: STATUS.MALFORMED,
        }
        for lookup, expected in mappings.items():
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_business_entity_source")
                with patch.object(
                    type(source), "resolve_business_entity",
                    return_value=AuthorityLookupResult(lookup),
                ):
                    self.assert_failure(establish(auth), expected)
                self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})

    def test_11_lookup_exception_is_unavailable_and_recovery_uses_first_event(self):
        auth = authority("resource-alpha")
        source = object.__getattribute__(auth, "_business_entity_source")
        with patch.object(type(source), "resolve_business_entity", side_effect=RuntimeError):
            self.assert_failure(establish(auth), STATUS.BUSINESS_ENTITY_UNAVAILABLE)
        recovered = establish(auth)
        self.assertIs(recovered.status, STATUS.ESTABLISHED)
        self.assertEqual(recovered.establishment_evidence.business_entity_currentness_provenance_reference, PROVENANCE_1)

    def test_12_found_requires_one_exact_active_business_entity(self):
        invalid = (
            AuthorityLookupResult(AuthorityLookupStatus.FOUND),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (object(),)),
            AuthorityLookupResult(
                AuthorityLookupStatus.FOUND,
                (
                    BusinessEntity(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "business-alpha"),
                    BusinessEntity(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "business-alpha"),
                ),
            ),
            AuthorityLookupResult.found(
                BusinessEntitySubclass(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "business-alpha")
            ),
            found_record(state=AuthorityRecordState.INACTIVE),
        )
        for lookup in invalid:
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_business_entity_source")
                with patch.object(type(source), "resolve_business_entity", return_value=lookup):
                    self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_13_wrong_business_entity_or_source_authority_is_mismatch(self):
        for lookup in (
            found_record(business_entity_id="business-beta"),
            found_record(authority_reference="other-authority"),
        ):
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_business_entity_source")
                with patch.object(type(source), "resolve_business_entity", return_value=lookup):
                    self.assert_failure(establish(auth), STATUS.MISMATCH)

    def test_14_lookup_result_type_status_and_strings_are_hardened(self):
        invalid = (
            ForeignLookup(AuthorityLookupStatus.FOUND, found_record().records),
            AuthorityLookupResult(ForeignStatus.FOUND, found_record().records),
            found_record(authority_reference=StringSubclass(SOURCE_AUTHORITY)),
            found_record(authority_reference=" " + SOURCE_AUTHORITY),
            found_record(business_entity_id="business-alpha "),
            found_record(business_entity_id=Coercible()),
        )
        for lookup in invalid:
            with self.subTest(lookup=lookup):
                auth = authority("resource-alpha")
                source = object.__getattribute__(auth, "_business_entity_source")
                with patch.object(type(source), "resolve_business_entity", return_value=lookup):
                    self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_15_public_business_context_types_readiness_and_strings_are_hardened(self):
        cases = (
            object(),
            {},
            ContextResultSubclass(BC_STATUS.READY, business_context()),
            business_context_result(context=business_context(business_entity_id=StringSubclass("business-alpha"))),
            business_context_result(context=business_context(principal_id=" principal-alpha")),
            business_context_result(context=business_context(engagement_reference=" ")),
            business_context_result(context=business_context(business_entity_id=Coercible())),
        )
        for value in cases:
            with self.subTest(value=type(value)):
                self.assert_failure(establish(context_result=value), STATUS.MALFORMED)
        self.assert_failure(
            establish(context_result=business_context_result(status=BC_STATUS.ENGAGEMENT_NOT_READY)),
            STATUS.BUSINESS_CONTEXT_NOT_READY,
        )

    def test_16_unsupported_operation_precedes_private_applicability(self):
        auth = authority("resource-alpha")
        private = object.__getattribute__(auth, "_applicability_authority")
        context = business_context(protected_operation="wrong")
        with patch.object(
            type(private),
            "establish_assessment_submission_resource_action_applicability",
        ) as probe:
            self.assert_failure(
                establish(auth, business_context_result(context=context)),
                STATUS.MALFORMED,
            )
        probe.assert_not_called()

    def test_17_lineage_substitutions_fail_closed(self):
        valid = applicability_result()
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
            "target_authority_reference": "wrong-authority",
            "target_governance_reference": "wrong-governance",
            "resource_identity_governance_reference": "wrong-ri-governance",
            "applicability_governance_reference": "wrong-applicability-governance",
        }
        for field, value in substitutions.items():
            with self.subTest(field=field):
                auth = authority("resource-alpha")
                private = object.__getattribute__(auth, "_applicability_authority")
                output = changed_applicability(valid, **{field: value})
                with patch.object(
                    type(private),
                    "establish_assessment_submission_resource_action_applicability",
                    return_value=output,
                ):
                    result = establish(auth)
                self.assertIn(result.status, (STATUS.MALFORMED, STATUS.MISMATCH))
                self.assertIsNone(result.business_entity_currentness_fact)
                self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})

    def test_18_changed_lineage_after_success_cannot_reuse(self):
        changes = {
            "target_provenance_reference": "changed-target-provenance",
            "resource_identity_provenance_reference": "changed-ri-provenance",
            "applicability_provenance_reference": "changed-applicability-provenance",
        }
        for field, value in changes.items():
            with self.subTest(field=field):
                auth = authority("resource-alpha")
                first = establish(auth)
                valid = applicability_result()
                changed = changed_applicability(valid, **{field: value})
                private = object.__getattribute__(auth, "_applicability_authority")
                with patch.object(
                    type(private),
                    "establish_assessment_submission_resource_action_applicability",
                    return_value=changed,
                ):
                    self.assert_failure(establish(auth), STATUS.MISMATCH)
                self.assertIs(first.status, STATUS.ESTABLISHED)
                self.assertIs(establish(auth).status, STATUS.REUSED)

    def test_19_changed_currentness_after_success_cannot_reuse(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        source = object.__getattribute__(auth, "_business_entity_source")
        with patch.object(
            type(source),
            "resolve_business_entity",
            return_value=AuthorityLookupResult.stale(),
        ):
            self.assert_failure(establish(auth), STATUS.BUSINESS_ENTITY_STALE)
        recovered = establish(auth)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(recovered.status, STATUS.REUSED)
        self.assertEqual(
            recovered.establishment_evidence.business_entity_currentness_provenance_reference,
            PROVENANCE_1,
        )

    def test_20_one_attempt_index_enforces_cardinality_without_b_index(self):
        auth = authority("resource-alpha")
        establish(auth)
        attributes = set(dir(auth))
        self.assertIn("_currentness_by_attempt", attributes)
        self.assertNotIn("_currentness_by_business_entity_id", attributes)
        self.assertNotIn("_currentness_by_resource_id", attributes)
        stored = object.__getattribute__(auth, "_currentness_by_attempt")
        self.assertEqual(tuple(stored), ("attempt-alpha",))
        self.assertTrue(dataclasses.is_dataclass(stored["attempt-alpha"]))
        self.assertTrue(type(stored["attempt-alpha"]).__dataclass_params__.frozen)

    def test_21_different_attempts_may_create_events_for_same_b(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        second_context = business_context_result(
            context=business_context(attempt_reference="attempt-beta")
        )
        second = establish(auth, second_context)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.ESTABLISHED)
        self.assertEqual(first.business_entity_currentness_fact.business_entity_id, second.business_entity_currentness_fact.business_entity_id)
        self.assertNotEqual(
            first.establishment_evidence.business_entity_currentness_provenance_reference,
            second.establishment_evidence.business_entity_currentness_provenance_reference,
        )

    def test_22_returned_object_mutation_cannot_change_canonical_state(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        object.__setattr__(first.business_entity_currentness_fact, "business_entity_id", "attacker")
        object.__setattr__(first.establishment_evidence, "business_entity_id", "attacker")
        object.__setattr__(first, "status", STATUS.MALFORMED)
        retry = establish(auth)
        self.assertIs(retry.status, STATUS.REUSED)
        self.assertEqual(retry.business_entity_currentness_fact.business_entity_id, "business-alpha")
        self.assertEqual(retry.establishment_evidence.business_entity_id, "business-alpha")
        self.assertEqual(retry.establishment_evidence.business_entity_currentness_provenance_reference, PROVENANCE_1)

    def test_23_instance_state_and_provenance_are_isolated(self):
        first = establish(authority("resource-alpha"))
        second = establish(authority("resource-alpha"))
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.ESTABLISHED)
        self.assertEqual(first.establishment_evidence.business_entity_currentness_provenance_reference, PROVENANCE_1)
        self.assertEqual(second.establishment_evidence.business_entity_currentness_provenance_reference, PROVENANCE_1)

    def test_24_caller_authority_payloads_have_no_public_entry(self):
        auth = authority("resource-alpha")
        prohibited = {
            "business_entity_id": "business-alpha",
            "business_entity": BusinessEntity(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "business-alpha"),
            "business_entity_source": NonProductionBusinessEntityAuthoritySource(),
            "business_entity_result": AuthorityLookupResult.missing(),
            "applicability_result": applicability_result(),
            "resource_id": "resource-alpha",
            "requested_action": RequestedAction.SUBMIT,
        }
        method = auth.establish_assessment_submission_business_entity_currentness
        for name, value in prohibited.items():
            with self.subTest(name=name):
                with self.assertRaises(TypeError):
                    method(business_context_result=business_context_result(), **{name: value})

    def test_25_unrelated_authority_objects_cannot_enter_boundary(self):
        unrelated = (
            BusinessEntity(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "business-alpha"),
            AuthorityLookupResult.missing(),
            Membership(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha"),
            Entitlement(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "principal-alpha", "business-alpha", "resource-alpha", RequestedAction.SUBMIT),
            GovernedResource(SOURCE_AUTHORITY, AuthorityRecordState.ACTIVE, "resource-alpha", "resource-alpha", ResourceClass.ASSESSMENT_SUBMISSION, "business-alpha"),
            AuthorizationRequest(None, None, None, None, "correlation", "evaluation"),
            {"business_entity_id": "business-alpha"},
            Coercible(),
        )
        for value in unrelated:
            with self.subTest(value=type(value)):
                self.assert_failure(establish(context_result=value), STATUS.MALFORMED)

    def test_26_no_membership_entitlement_evaluator_or_lifecycle_authority(self):
        result = establish()
        fact_names = {field.name for field in dataclasses.fields(type(result.business_entity_currentness_fact))}
        evidence_names = {field.name for field in dataclasses.fields(type(result.establishment_evidence))}
        forbidden = {
            "membership", "entitlement", "permission", "decision", "allow", "deny",
            "submitted", "abandoned", "runtime", "persistence", "deployment", "production",
        }
        self.assertTrue(forbidden.isdisjoint(fact_names | evidence_names))
        source = Path(currentness_module.__file__).read_text()
        self.assertNotIn("resolve_membership", source)
        self.assertNotIn("resolve_entitlement", source)
        self.assertNotIn("AuthorizationEvaluator", source)
        self.assertNotIn("SUBMITTED", source)

    def test_27_failure_precedence_validates_public_input_before_private_calls(self):
        auth = authority("resource-alpha")
        app = object.__getattribute__(auth, "_applicability_authority")
        source = object.__getattribute__(auth, "_business_entity_source")
        with patch.object(type(app), "establish_assessment_submission_resource_action_applicability") as app_probe:
            with patch.object(type(source), "resolve_business_entity") as source_probe:
                self.assert_failure(establish(auth, object()), STATUS.MALFORMED)
        app_probe.assert_not_called()
        source_probe.assert_not_called()

    def test_28_applicability_failure_precedes_business_entity_lookup(self):
        auth = authority("resource-alpha")
        app = object.__getattribute__(auth, "_applicability_authority")
        source = object.__getattribute__(auth, "_business_entity_source")
        with patch.object(
            type(app),
            "establish_assessment_submission_resource_action_applicability",
            return_value=NonProductionAssessmentSubmissionResourceActionApplicabilityResult(APP_STATUS.MISMATCH),
        ):
            with patch.object(type(source), "resolve_business_entity") as source_probe:
                self.assert_failure(establish(auth), STATUS.MISMATCH)
        source_probe.assert_not_called()

    def test_29_output_construction_failure_does_not_commit_or_consume(self):
        auth = authority("resource-alpha")
        with patch.object(currentness_module, "_currentness_evidence", side_effect=RuntimeError):
            self.assert_failure(establish(auth), STATUS.MALFORMED)
        self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})
        self.assertEqual(object.__getattribute__(auth, "_next_business_entity_currentness_provenance_index"), 1)
        self.assertIs(establish(auth).status, STATUS.ESTABLISHED)

    def test_30_business_entity_source_and_applicability_are_reused_unchanged(self):
        self.assertIs(currentness_module._BusinessEntitySource, NonProductionBusinessEntityAuthoritySource)
        self.assertIs(
            currentness_module._ApplicabilityAuthority,
            NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority,
        )

    def test_31_candidate_resource_configuration_cannot_create_current_b(self):
        auth = authority("resource-alpha")
        self.assert_failure(establish(auth, object()), STATUS.MALFORMED)
        self.assertEqual(object.__getattribute__(auth, "_currentness_by_attempt"), {})

    def test_32_non_found_does_not_infer_revocation_or_inactivity(self):
        auth = authority("resource-alpha")
        source = object.__getattribute__(auth, "_business_entity_source")
        with patch.object(
            type(source),
            "resolve_business_entity",
            return_value=AuthorityLookupResult.missing(),
        ):
            result = establish(auth)
        self.assert_failure(result, STATUS.BUSINESS_ENTITY_NOT_FOUND)
        self.assertFalse(hasattr(STATUS, "BUSINESS_ENTITY_REVOKED"))
        self.assertFalse(hasattr(STATUS, "BUSINESS_ENTITY_INACTIVE"))


if __name__ == "__main__":
    unittest.main()
