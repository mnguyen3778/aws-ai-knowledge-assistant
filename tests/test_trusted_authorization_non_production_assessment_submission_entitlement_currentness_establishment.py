import dataclasses
import inspect
import sys
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_entitlement_currentness_establishment as module  # noqa: E402
from trusted_authorization.entitlement_source import (  # noqa: E402
    NonProductionEntitlementAuthoritySource,
)
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationRequest,
    Entitlement,
    RequestedAction,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_entitlement_currentness_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
    NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence,
    NonProductionAssessmentSubmissionEntitlementCurrentnessFact,
    NonProductionAssessmentSubmissionEntitlementCurrentnessResult,
    NonProductionAssessmentSubmissionEntitlementCurrentnessStatus,
)
from trusted_authorization.non_production_assessment_submission_membership_currentness_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
    NonProductionAssessmentSubmissionMembershipCurrentnessResult,
    NonProductionAssessmentSubmissionMembershipCurrentnessStatus,
)


STATUS = NonProductionAssessmentSubmissionEntitlementCurrentnessStatus
UPSTREAM_STATUS = NonProductionAssessmentSubmissionMembershipCurrentnessStatus
BC_STATUS = NonProductionAssessmentSubmissionBusinessContextStatus
OPERATION = NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
SOURCE_AUTHORITY = "non-production-entitlement-authority"
CURRENTNESS_AUTHORITY = (
    "non-production-assessment-submission-entitlement-currentness-authority"
)
GOVERNANCE = "entitlement-authority-source-governance-v1"
PROVENANCE_1 = (
    "non-production-assessment-submission-entitlement-currentness-"
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
    "membership_state", "membership_authority_reference",
    "membership_currentness_authority_reference",
    "membership_currentness_provenance_reference", "membership_governance_reference",
)
EVIDENCE_FIELDS = UPSTREAM_FIELDS + (
    "entitlement_state", "entitlement_authority_reference",
    "entitlement_currentness_authority_reference",
    "entitlement_currentness_provenance_reference", "entitlement_governance_reference",
)


class StringSubclass(str):
    pass


class EntitlementSubclass(Entitlement):
    pass


class ResultSubclass(NonProductionAssessmentSubmissionMembershipCurrentnessResult):
    pass


class ForeignStatus(Enum):
    FOUND = "FOUND"


class ForeignState(Enum):
    ACTIVE = "ACTIVE"


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
    return NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority(
        candidate_resource_references=tuple(resources),
    )


def establish(auth=None, value=_DEFAULT):
    auth = auth or authority("resource-alpha")
    value = context_result() if value is _DEFAULT else value
    return auth.establish_assessment_submission_entitlement_currentness(
        business_context_result=value,
    )


def upstream_result(value=None):
    value = value or context_result()
    return NonProductionAssessmentSubmissionMembershipCurrentnessAuthority(
        candidate_resource_references=("resource-alpha",)
    ).establish_assessment_submission_membership_currentness(
        business_context_result=value,
    )


def changed_upstream(result, **changes):
    evidence = dataclasses.replace(result.establishment_evidence, **changes)
    fact_changes = {
        name: changes[name]
        for name in ("principal_id", "business_entity_id", "membership_state")
        if name in changes
    }
    fact = dataclasses.replace(result.membership_currentness_fact, **fact_changes)
    return NonProductionAssessmentSubmissionMembershipCurrentnessResult(
        result.status,
        fact,
        evidence,
    )


def entitlement(**changes):
    values = {
        "authority_reference": SOURCE_AUTHORITY,
        "state": AuthorityRecordState.ACTIVE,
        "principal_id": "principal-alpha",
        "business_entity_id": "business-alpha",
        "resource_id": "resource-alpha",
        "action": RequestedAction.SUBMIT,
    }
    values.update(changes)
    return Entitlement(**values)


def found_entitlement(**changes):
    return AuthorityLookupResult.found(entitlement(**changes))


class EntitlementCurrentnessEstablishmentTests(unittest.TestCase):
    def assert_failure(self, result, status):
        self.assertIs(type(result), NonProductionAssessmentSubmissionEntitlementCurrentnessResult)
        self.assertIs(result.status, status)
        self.assertIsNone(result.entitlement_currentness_fact)
        self.assertIsNone(result.establishment_evidence)

    def test_01_public_surface_signatures_and_models_are_exact(self):
        public = {
            name for name, value in vars(module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(public, {
            "NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority",
            "NonProductionAssessmentSubmissionEntitlementCurrentnessFact",
            "NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence",
            "NonProductionAssessmentSubmissionEntitlementCurrentnessStatus",
            "NonProductionAssessmentSubmissionEntitlementCurrentnessResult",
        })
        self.assertEqual(
            str(inspect.signature(NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority)),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) -> 'None'",
        )
        self.assertEqual(
            str(inspect.signature(
                NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority.
                establish_assessment_submission_entitlement_currentness
            )),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionEntitlementCurrentnessResult'",
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(
                NonProductionAssessmentSubmissionEntitlementCurrentnessFact
            )),
            ("principal_id", "business_entity_id", "resource_id", "requested_action", "entitlement_state"),
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(
                NonProductionAssessmentSubmissionEntitlementCurrentnessEvidence
            )),
            EVIDENCE_FIELDS,
        )
        self.assertEqual(len(EVIDENCE_FIELDS), 47)
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(
                NonProductionAssessmentSubmissionEntitlementCurrentnessResult
            )),
            ("status", "entitlement_currentness_fact", "establishment_evidence"),
        )

    def test_02_status_contract_is_exact(self):
        self.assertEqual(tuple(item.name for item in STATUS), (
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
            "ENTITLEMENT_NOT_FOUND", "ENTITLEMENT_AMBIGUOUS",
            "ENTITLEMENT_CONFLICTING", "ENTITLEMENT_STALE", "ENTITLEMENT_UNAVAILABLE",
        ))

    def test_03_establishes_exact_fact_evidence_and_complete_lineage(self):
        upstream = upstream_result()
        auth = authority("resource-alpha")
        result = establish(auth)
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(dataclasses.astuple(result.entitlement_currentness_fact), (
            "principal-alpha", "business-alpha", "resource-alpha",
            RequestedAction.SUBMIT, AuthorityRecordState.ACTIVE,
        ))
        evidence = result.establishment_evidence
        self.assertEqual(
            tuple(getattr(evidence, name) for name in UPSTREAM_FIELDS),
            tuple(getattr(upstream.establishment_evidence, name) for name in UPSTREAM_FIELDS),
        )
        self.assertEqual(tuple(getattr(evidence, name) for name in EVIDENCE_FIELDS[-5:]), (
            AuthorityRecordState.ACTIVE, SOURCE_AUTHORITY, CURRENTNESS_AUTHORITY,
            PROVENANCE_1, GOVERNANCE,
        ))

    def test_04_exact_retry_is_fresh_and_preserves_original_event(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        with patch.object(
            NonProductionEntitlementAuthoritySource,
            "resolve_entitlement",
            autospec=True,
            wraps=NonProductionEntitlementAuthoritySource.resolve_entitlement,
        ) as resolver:
            second = establish(auth)
        self.assertIs(second.status, STATUS.REUSED)
        self.assertEqual(first.entitlement_currentness_fact, second.entitlement_currentness_fact)
        self.assertEqual(first.establishment_evidence, second.establishment_evidence)
        self.assertIsNot(first.entitlement_currentness_fact, second.entitlement_currentness_fact)
        self.assertIsNot(first.establishment_evidence, second.establishment_evidence)
        self.assertEqual(resolver.call_count, 1)

    def test_05_different_attempts_get_distinct_monotonic_events(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        second_context = context_result(context=business_context(
            attempt_reference="attempt-beta",
        ))
        second_upstream = upstream_result(second_context)
        with patch.object(
            NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
            "establish_assessment_submission_membership_currentness",
            return_value=second_upstream,
        ):
            second = establish(auth, second_context)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.ESTABLISHED)
        self.assertEqual(
            second.establishment_evidence.entitlement_currentness_provenance_reference,
            "non-production-assessment-submission-entitlement-currentness-"
            "establishment-provenance-2",
        )
        self.assertEqual(len(auth._entitlement_currentness_by_attempt), 2)

    def test_06_business_context_type_readiness_and_strings_fail_closed(self):
        self.assert_failure(establish(value=object()), STATUS.MALFORMED)
        self.assert_failure(
            establish(value=context_result(status=BC_STATUS.ENGAGEMENT_NOT_READY)),
            STATUS.BUSINESS_CONTEXT_NOT_READY,
        )
        self.assert_failure(
            establish(value=context_result(context=business_context(principal_id=" principal-alpha"))),
            STATUS.MALFORMED,
        )
        self.assert_failure(
            establish(value=context_result(context=business_context(principal_id=StringSubclass("principal-alpha")))),
            STATUS.MALFORMED,
        )

    def test_07_all_23_upstream_failures_map_one_to_one_without_lookup(self):
        failures = tuple(
            status for status in UPSTREAM_STATUS
            if status not in (UPSTREAM_STATUS.ESTABLISHED, UPSTREAM_STATUS.REUSED)
        )
        self.assertEqual(len(failures), 23)
        for upstream_status in failures:
            with self.subTest(status=upstream_status.name):
                auth = authority("resource-alpha")
                with patch.object(
                    NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
                    "establish_assessment_submission_membership_currentness",
                    return_value=NonProductionAssessmentSubmissionMembershipCurrentnessResult(upstream_status),
                ), patch.object(
                    NonProductionEntitlementAuthoritySource,
                    "resolve_entitlement",
                    side_effect=AssertionError("lookup must not run"),
                ):
                    self.assert_failure(establish(auth), STATUS[upstream_status.name])

    def test_08_foreign_or_malformed_upstream_shapes_fail_malformed(self):
        valid = upstream_result()
        cases = (
            object(),
            ResultSubclass(valid.status, valid.membership_currentness_fact, valid.establishment_evidence),
            NonProductionAssessmentSubmissionMembershipCurrentnessResult(ForeignStatus.FOUND),
            NonProductionAssessmentSubmissionMembershipCurrentnessResult(UPSTREAM_STATUS.ESTABLISHED),
            NonProductionAssessmentSubmissionMembershipCurrentnessResult(
                UPSTREAM_STATUS.MEMBERSHIP_NOT_FOUND,
                valid.membership_currentness_fact,
                valid.establishment_evidence,
            ),
        )
        for value in cases:
            with self.subTest(value=type(value).__name__), patch.object(
                NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
                "establish_assessment_submission_membership_currentness",
                return_value=value,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_09_upstream_fact_evidence_and_context_mismatches_fail_closed(self):
        valid = upstream_result()
        changed = (
            changed_upstream(valid, principal_id="principal-beta"),
            changed_upstream(valid, business_entity_id="business-beta"),
            changed_upstream(valid, resource_id="resource-beta"),
            changed_upstream(valid, membership_authority_reference="wrong-authority"),
            changed_upstream(valid, membership_governance_reference="wrong-governance"),
        )
        for value in changed:
            with self.subTest(value=value.establishment_evidence), patch.object(
                NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
                "establish_assessment_submission_membership_currentness",
                return_value=value,
            ):
                self.assertIn(establish().status, (STATUS.MALFORMED, STATUS.MISMATCH))

    def test_10_simple_generic_failure_mappings_and_exception_are_exact(self):
        cases = {
            AuthorityLookupStatus.NOT_FOUND: STATUS.ENTITLEMENT_NOT_FOUND,
            AuthorityLookupStatus.STALE: STATUS.ENTITLEMENT_STALE,
            AuthorityLookupStatus.UNAVAILABLE: STATUS.ENTITLEMENT_UNAVAILABLE,
            AuthorityLookupStatus.MALFORMED: STATUS.MALFORMED,
            AuthorityLookupStatus.UNSUPPORTED: STATUS.MALFORMED,
        }
        for lookup_status, expected in cases.items():
            with self.subTest(status=lookup_status), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=AuthorityLookupResult(lookup_status),
            ):
                self.assert_failure(establish(), expected)
        with patch.object(
            NonProductionEntitlementAuthoritySource,
            "resolve_entitlement",
            side_effect=RuntimeError("unavailable"),
        ):
            self.assert_failure(establish(), STATUS.ENTITLEMENT_UNAVAILABLE)

    def test_11_real_generic_duplicate_maps_ambiguous_without_consumption(self):
        record = entitlement()
        source = NonProductionEntitlementAuthoritySource((record, record))
        generic = source.resolve_entitlement(
            "principal-alpha", "business-alpha", "resource-alpha", RequestedAction.SUBMIT
        )
        self.assertIs(generic.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(generic.records), 2)
        auth = authority("resource-alpha")
        auth._entitlement_source = source
        self.assert_failure(establish(auth), STATUS.ENTITLEMENT_AMBIGUOUS)
        self.assertEqual(auth._entitlement_currentness_by_attempt, {})
        self.assertEqual(auth._next_entitlement_currentness_provenance_index, 1)

    def test_12_real_generic_conflict_maps_conflicting_without_consumption(self):
        source = NonProductionEntitlementAuthoritySource((
            entitlement(), entitlement(state=AuthorityRecordState.STALE),
        ))
        generic = source.resolve_entitlement(
            "principal-alpha", "business-alpha", "resource-alpha", RequestedAction.SUBMIT
        )
        self.assertIs(generic.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(len(generic.records), 2)
        auth = authority("resource-alpha")
        auth._entitlement_source = source
        self.assert_failure(establish(auth), STATUS.ENTITLEMENT_CONFLICTING)
        self.assertEqual(auth._entitlement_currentness_by_attempt, {})
        self.assertEqual(auth._next_entitlement_currentness_provenance_index, 1)

    def test_13_malformed_ambiguity_shapes_are_rejected(self):
        malformed = (
            AuthorityLookupResult(AuthorityLookupStatus.AMBIGUOUS),
            AuthorityLookupResult(AuthorityLookupStatus.AMBIGUOUS, (entitlement(),)),
            AuthorityLookupResult(AuthorityLookupStatus.AMBIGUOUS, [entitlement(), entitlement()]),
            AuthorityLookupResult(AuthorityLookupStatus.AMBIGUOUS, (object(), object())),
            AuthorityLookupResult(AuthorityLookupStatus.AMBIGUOUS, (
                entitlement(), entitlement(principal_id="principal-beta"),
            )),
            AuthorityLookupResult(AuthorityLookupStatus.AMBIGUOUS, (
                entitlement(), entitlement(authority_reference="alternate-authority"),
            )),
        )
        for lookup in malformed:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_14_malformed_conflict_shapes_are_rejected(self):
        malformed = (
            AuthorityLookupResult(AuthorityLookupStatus.CONFLICTING),
            AuthorityLookupResult(AuthorityLookupStatus.CONFLICTING, (entitlement(),)),
            AuthorityLookupResult(AuthorityLookupStatus.CONFLICTING, (entitlement(), entitlement())),
            AuthorityLookupResult(AuthorityLookupStatus.CONFLICTING, (
                EntitlementSubclass(**entitlement().__dict__), entitlement(state=AuthorityRecordState.STALE),
            )),
            AuthorityLookupResult(AuthorityLookupStatus.CONFLICTING, (
                entitlement(), entitlement(resource_id="resource-beta", state=AuthorityRecordState.STALE),
            )),
        )
        for lookup in malformed:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_15_foreign_lookup_result_status_and_residual_records_are_malformed(self):
        cases = (
            ForeignLookup(AuthorityLookupStatus.FOUND, (entitlement(),)),
            AuthorityLookupResult(ForeignStatus.FOUND, (entitlement(),)),
            AuthorityLookupResult(AuthorityLookupStatus.NOT_FOUND, (entitlement(),)),
            AuthorityLookupResult(AuthorityLookupStatus.STALE, (entitlement(),)),
        )
        for lookup in cases:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_16_found_structure_state_and_exact_types_remain_strict(self):
        cases = (
            AuthorityLookupResult(AuthorityLookupStatus.FOUND),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (entitlement(), entitlement())),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (object(),)),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (
                EntitlementSubclass(**entitlement().__dict__),
            )),
            found_entitlement(state=AuthorityRecordState.INACTIVE),
            found_entitlement(state=ForeignState.ACTIVE),
            found_entitlement(principal_id=StringSubclass("principal-alpha")),
            found_entitlement(resource_id=" resource-alpha"),
        )
        for lookup in cases:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_17_canonical_found_but_nonconvergent_values_map_mismatch(self):
        cases = (
            found_entitlement(principal_id="principal-beta"),
            found_entitlement(business_entity_id="business-beta"),
            found_entitlement(resource_id="resource-beta"),
            found_entitlement(action=RequestedAction.VIEW),
            found_entitlement(authority_reference="alternate-authority"),
        )
        for lookup in cases:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MISMATCH)

    def test_18_private_fixture_has_exact_negative_space(self):
        auth = authority("resource-alpha")
        source = auth._entitlement_source
        valid = source.resolve_entitlement(
            "principal-alpha", "business-alpha", "resource-alpha", RequestedAction.SUBMIT
        )
        self.assertIs(valid.status, AuthorityLookupStatus.FOUND)
        cases = (
            ("principal-beta", "business-alpha", "resource-alpha", RequestedAction.SUBMIT),
            ("principal-alpha", "business-beta", "resource-alpha", RequestedAction.SUBMIT),
            ("principal-alpha", "business-alpha", "resource-beta", RequestedAction.SUBMIT),
            ("principal-alpha", "business-alpha", "resource-alpha", RequestedAction.VIEW),
            ("principal-beta", "business-beta", "resource-alpha", RequestedAction.SUBMIT),
        )
        for key in cases:
            with self.subTest(key=key):
                self.assertIs(source.resolve_entitlement(*key).status, AuthorityLookupStatus.NOT_FOUND)

    def test_19_failure_before_success_does_not_consume_provenance(self):
        auth = authority("resource-alpha")
        with patch.object(
            NonProductionEntitlementAuthoritySource,
            "resolve_entitlement",
            return_value=AuthorityLookupResult.missing(),
        ):
            self.assert_failure(establish(auth), STATUS.ENTITLEMENT_NOT_FOUND)
            self.assert_failure(establish(auth), STATUS.ENTITLEMENT_NOT_FOUND)
        success = establish(auth)
        self.assertIs(success.status, STATUS.ESTABLISHED)
        self.assertEqual(
            success.establishment_evidence.entitlement_currentness_provenance_reference,
            PROVENANCE_1,
        )

    def test_20_post_success_real_ambiguity_defeats_reuse_then_restores(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        record = entitlement()
        with patch.object(
            auth,
            "_entitlement_source",
            NonProductionEntitlementAuthoritySource((record, record)),
        ):
            self.assert_failure(establish(auth), STATUS.ENTITLEMENT_AMBIGUOUS)
            self.assertEqual(len(auth._entitlement_currentness_by_attempt), 1)
            self.assertEqual(auth._next_entitlement_currentness_provenance_index, 2)
        restored = establish(auth)
        self.assertIs(restored.status, STATUS.REUSED)
        self.assertEqual(
            restored.establishment_evidence.entitlement_currentness_provenance_reference,
            first.establishment_evidence.entitlement_currentness_provenance_reference,
        )

    def test_21_post_success_real_conflict_defeats_reuse_then_restores(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        with patch.object(
            auth,
            "_entitlement_source",
            NonProductionEntitlementAuthoritySource((
                entitlement(), entitlement(state=AuthorityRecordState.STALE),
            )),
        ):
            self.assert_failure(establish(auth), STATUS.ENTITLEMENT_CONFLICTING)
            self.assertEqual(len(auth._entitlement_currentness_by_attempt), 1)
            self.assertEqual(auth._next_entitlement_currentness_provenance_index, 2)
        restored = establish(auth)
        self.assertIs(restored.status, STATUS.REUSED)
        self.assertEqual(restored.establishment_evidence, first.establishment_evidence)

    def test_22_post_success_stale_absent_unavailable_and_exception_defeat_reuse(self):
        cases = (
            (AuthorityLookupResult.stale(), STATUS.ENTITLEMENT_STALE),
            (AuthorityLookupResult.missing(), STATUS.ENTITLEMENT_NOT_FOUND),
            (AuthorityLookupResult.unavailable(), STATUS.ENTITLEMENT_UNAVAILABLE),
        )
        for lookup, expected in cases:
            with self.subTest(expected=expected):
                auth = authority("resource-alpha")
                establish(auth)
                with patch.object(
                    NonProductionEntitlementAuthoritySource,
                    "resolve_entitlement",
                    return_value=lookup,
                ):
                    self.assert_failure(establish(auth), expected)
                self.assertIs(establish(auth).status, STATUS.REUSED)
        auth = authority("resource-alpha")
        establish(auth)
        with patch.object(
            NonProductionEntitlementAuthoritySource,
            "resolve_entitlement",
            side_effect=RuntimeError("unavailable"),
        ):
            self.assert_failure(establish(auth), STATUS.ENTITLEMENT_UNAVAILABLE)

    def test_23_fresh_upstream_failure_after_success_defeats_reuse(self):
        auth = authority("resource-alpha")
        establish(auth)
        with patch.object(
            NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
            "establish_assessment_submission_membership_currentness",
            return_value=NonProductionAssessmentSubmissionMembershipCurrentnessResult(
                UPSTREAM_STATUS.MEMBERSHIP_STALE
            ),
        ):
            self.assert_failure(establish(auth), STATUS.MEMBERSHIP_STALE)
        self.assertIs(establish(auth).status, STATUS.REUSED)

    def test_24_returned_mutation_cannot_change_canonical_authority(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        object.__setattr__(first.entitlement_currentness_fact, "principal_id", "principal-beta")
        object.__setattr__(first.establishment_evidence, "resource_id", "resource-beta")
        object.__setattr__(first, "status", STATUS.MALFORMED)
        retry = establish(auth)
        self.assertIs(retry.status, STATUS.REUSED)
        self.assertEqual(retry.entitlement_currentness_fact.principal_id, "principal-alpha")
        self.assertEqual(retry.establishment_evidence.resource_id, "resource-alpha")
        self.assertEqual(
            retry.establishment_evidence.entitlement_currentness_provenance_reference,
            PROVENANCE_1,
        )

    def test_25_retained_dependencies_are_exact_and_called_once(self):
        auth = authority("resource-alpha")
        self.assertIs(type(auth._membership_currentness_authority),
                      NonProductionAssessmentSubmissionMembershipCurrentnessAuthority)
        self.assertIs(type(auth._entitlement_source), NonProductionEntitlementAuthoritySource)
        with patch.object(
            NonProductionAssessmentSubmissionMembershipCurrentnessAuthority,
            "establish_assessment_submission_membership_currentness",
            autospec=True,
            wraps=NonProductionAssessmentSubmissionMembershipCurrentnessAuthority.
            establish_assessment_submission_membership_currentness,
        ) as upstream, patch.object(
            NonProductionEntitlementAuthoritySource,
            "resolve_entitlement",
            autospec=True,
            wraps=NonProductionEntitlementAuthoritySource.resolve_entitlement,
        ) as lookup:
            result = establish(auth)
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(upstream.call_count, 1)
        self.assertEqual(lookup.call_count, 1)

    def test_26_dependency_replacement_fails_closed(self):
        auth = authority("resource-alpha")
        auth._membership_currentness_authority = object()
        self.assert_failure(establish(auth), STATUS.MALFORMED)
        auth = authority("resource-alpha")
        auth._entitlement_source = object()
        self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_27_attempt_collision_never_reuses_different_lineage(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        changed = context_result(context=business_context(
            engagement_reference="engagement-beta",
        ))
        self.assertNotEqual(establish(auth, changed).status, STATUS.REUSED)

    def test_28_no_public_authority_injection_or_forbidden_behavior(self):
        signature = inspect.signature(NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority)
        self.assertEqual(tuple(signature.parameters), ("candidate_resource_references",))
        method = inspect.signature(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority.
            establish_assessment_submission_entitlement_currentness
        )
        self.assertEqual(tuple(method.parameters), ("self", "business_context_result"))
        source = Path(module.__file__).read_text()
        forbidden_imports = (
            "boto3", "cognito", "dynamodb", "botocore", "requests", "openai", "mcp"
        )
        self.assertFalse(any(name in source.lower() for name in forbidden_imports))
        self.assertNotIn("AuthorizationDecision", source)
        self.assertNotIn("ALLOW", source)
        self.assertNotIn("DENY", source)
        self.assertNotIn("SUBMITTED", source)

    def test_29_authorization_request_and_context_cannot_launder_entitlement(self):
        request = AuthorizationRequest(
            subject_evidence=None,
            resource_reference="resource-alpha",
            requested_action=RequestedAction.SUBMIT,
            governed_version_context=None,
            correlation_id="correlation-alpha",
            evaluation_context="assessment-submission",
        )
        self.assert_failure(establish(value=request), STATUS.MALFORMED)
        context = business_context()
        self.assertFalse(hasattr(context, "entitlement"))
        self.assertFalse(hasattr(context, "entitlement_source"))

    def test_30_generic_source_remains_strict_for_malformed_fixture_records(self):
        sources = (
            NonProductionEntitlementAuthoritySource((object(),)),
            NonProductionEntitlementAuthoritySource((
                Entitlement(
                    authority_reference=" authority",
                    state=AuthorityRecordState.ACTIVE,
                    principal_id="principal-alpha",
                    business_entity_id="business-alpha",
                    resource_id="resource-alpha",
                    action=RequestedAction.SUBMIT,
                ),
            )),
        )
        for source in sources:
            with self.subTest(source=source):
                auth = authority("resource-alpha")
                auth._entitlement_source = source
                self.assert_failure(establish(auth), STATUS.MALFORMED)

    def test_31_canonical_state_contains_only_attempt_snapshots_and_counter(self):
        auth = authority("resource-alpha")
        self.assertEqual(set(auth.__slots__), {
            "_membership_currentness_authority", "_entitlement_source",
            "_entitlement_currentness_by_attempt",
            "_next_entitlement_currentness_provenance_index",
        })
        establish(auth)
        stored = auth._entitlement_currentness_by_attempt["attempt-alpha"]
        self.assertIs(type(stored.evidence_values), tuple)
        self.assertIs(type(stored.retry_identity), tuple)
        self.assertFalse(any(isinstance(value, Entitlement) for value in stored.evidence_values))

    def test_32_wrong_key_ambiguity_and_conflict_cannot_gain_failure_authority(self):
        cases = (
            AuthorityLookupResult.ambiguous((
                entitlement(), entitlement(business_entity_id="business-beta"),
            )),
            AuthorityLookupResult.conflicting((
                entitlement(), entitlement(action=RequestedAction.VIEW),
            )),
        )
        for lookup in cases:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_33_strings_are_not_normalized_or_coerced(self):
        invalid = (" principal-alpha", "principal-alpha ", "principal-alpha\n", "", " ", Coercible())
        for principal_id in invalid:
            with self.subTest(principal_id=principal_id), patch.object(
                NonProductionEntitlementAuthoritySource,
                "resolve_entitlement",
                return_value=found_entitlement(principal_id=principal_id),
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)


if __name__ == "__main__":
    unittest.main()
