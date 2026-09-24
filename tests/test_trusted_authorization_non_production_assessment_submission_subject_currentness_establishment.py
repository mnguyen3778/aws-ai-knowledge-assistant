import dataclasses
import inspect
import sys
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_subject_currentness_establishment as module  # noqa: E402
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationRequest,
    PrincipalMapping,
    RequestedAction,
    TrustedSubjectEvidence,
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
    NonProductionAssessmentSubmissionEntitlementCurrentnessResult,
    NonProductionAssessmentSubmissionEntitlementCurrentnessStatus,
)
from trusted_authorization.non_production_assessment_submission_subject_currentness_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionSubjectCurrentnessAuthority,
    NonProductionAssessmentSubmissionSubjectCurrentnessEvidence,
    NonProductionAssessmentSubmissionSubjectCurrentnessFact,
    NonProductionAssessmentSubmissionSubjectCurrentnessResult,
    NonProductionAssessmentSubmissionSubjectCurrentnessStatus,
)
from trusted_authorization.non_production_authenticated_subject_handoff import (  # noqa: E402
    NonProductionAuthenticatedSubjectHandoffResult,
    NonProductionAuthenticatedSubjectHandoffStatus,
    NonProductionVerifiedAuthenticationFact,
)
from trusted_authorization.principal_mapping_source import (  # noqa: E402
    NonProductionPrincipalMappingAuthoritySource,
)


STATUS = NonProductionAssessmentSubmissionSubjectCurrentnessStatus
UPSTREAM_STATUS = NonProductionAssessmentSubmissionEntitlementCurrentnessStatus
BC_STATUS = NonProductionAssessmentSubmissionBusinessContextStatus
OPERATION = NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
PROVENANCE_1 = (
    "non-production-assessment-submission-subject-currentness-"
    "establishment-provenance-1"
)
AUTHORITY_REFERENCE = (
    "non-production-assessment-submission-subject-currentness-authority"
)
AUTHENTICATION_GOVERNANCE = (
    "trusted-authorization-authentication-trust-provenance-governance-v1"
)
MAPPING_GOVERNANCE = "principal-mapping-authority-source-governance-v1"
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
    "entitlement_state", "entitlement_authority_reference",
    "entitlement_currentness_authority_reference",
    "entitlement_currentness_provenance_reference", "entitlement_governance_reference",
)
TAIL_FIELDS = (
    "provider", "subject", "principal_mapping_state",
    "subject_currentness_authority_reference",
    "subject_currentness_provenance_reference",
    "authentication_governance_reference",
    "principal_mapping_governance_reference",
)
EVIDENCE_FIELDS = UPSTREAM_FIELDS + TAIL_FIELDS
STATUS_NAMES = (
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
    "AUTHENTICATION_NOT_CURRENT", "AUTHENTICATION_UNAVAILABLE",
    "PRINCIPAL_MAPPING_NOT_FOUND", "PRINCIPAL_MAPPING_AMBIGUOUS",
    "PRINCIPAL_MAPPING_CONFLICTING", "PRINCIPAL_MAPPING_STALE",
    "PRINCIPAL_MAPPING_UNAVAILABLE",
)


class StringSubclass(str):
    pass


class VerifiedFactSubclass(NonProductionVerifiedAuthenticationFact):
    pass


class MappingSubclass(PrincipalMapping):
    pass


class ResultSubclass(NonProductionAssessmentSubmissionEntitlementCurrentnessResult):
    pass


class ForeignStatus(Enum):
    FOUND = "FOUND"


class ForeignLookup:
    def __init__(self, status, records=()):
        self.status = status
        self.records = records


class Coercible:
    def __str__(self):
        return "provider-alpha"


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
    return NonProductionAssessmentSubmissionSubjectCurrentnessAuthority(
        candidate_resource_references=tuple(resources),
    )


def establish(auth=None, value=_DEFAULT):
    auth = auth or authority("resource-alpha")
    value = context_result() if value is _DEFAULT else value
    return auth.establish_assessment_submission_subject_currentness(
        business_context_result=value,
    )


def verified_authentication(**changes):
    values = {"provider": "provider-alpha", "subject": "subject-alpha"}
    values.update(changes)
    return NonProductionVerifiedAuthenticationFact(**values)


def mapping(**changes):
    values = {
        "authority_reference": "principal-authority",
        "state": AuthorityRecordState.ACTIVE,
        "subject_provider": "provider-alpha",
        "subject": "subject-alpha",
        "principal_id": "principal-alpha",
    }
    values.update(changes)
    return PrincipalMapping(**values)


def mapping_source(*records):
    return NonProductionPrincipalMappingAuthoritySource(records)


def upstream_result(value=None):
    value = value or context_result()
    return NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority(
        candidate_resource_references=("resource-alpha",)
    ).establish_assessment_submission_entitlement_currentness(
        business_context_result=value,
    )


def changed_upstream(result, **changes):
    evidence = dataclasses.replace(result.establishment_evidence, **changes)
    fact_changes = {
        name: changes[name]
        for name in (
            "principal_id", "business_entity_id", "resource_id",
            "requested_action", "entitlement_state",
        )
        if name in changes
    }
    fact = dataclasses.replace(result.entitlement_currentness_fact, **fact_changes)
    return NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
        result.status,
        fact,
        evidence,
    )


class SubjectCurrentnessEstablishmentTests(unittest.TestCase):
    def assert_failure(self, result, status):
        self.assertIs(type(result), NonProductionAssessmentSubmissionSubjectCurrentnessResult)
        self.assertIs(result.status, status)
        self.assertIsNone(result.subject_currentness_fact)
        self.assertIsNone(result.establishment_evidence)

    def test_01_public_surface_signatures_and_models_are_exact(self):
        public = {
            name for name, value in vars(module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(public, {
            "NonProductionAssessmentSubmissionSubjectCurrentnessAuthority",
            "NonProductionAssessmentSubmissionSubjectCurrentnessFact",
            "NonProductionAssessmentSubmissionSubjectCurrentnessEvidence",
            "NonProductionAssessmentSubmissionSubjectCurrentnessStatus",
            "NonProductionAssessmentSubmissionSubjectCurrentnessResult",
        })
        self.assertEqual(
            str(inspect.signature(NonProductionAssessmentSubmissionSubjectCurrentnessAuthority)),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) -> 'None'",
        )
        method = (
            NonProductionAssessmentSubmissionSubjectCurrentnessAuthority.
            establish_assessment_submission_subject_currentness
        )
        self.assertEqual(
            str(inspect.signature(method)),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionSubjectCurrentnessResult'",
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(
                NonProductionAssessmentSubmissionSubjectCurrentnessFact
            )),
            ("provider", "subject", "principal_id", "principal_mapping_state"),
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(
                NonProductionAssessmentSubmissionSubjectCurrentnessEvidence
            )),
            EVIDENCE_FIELDS,
        )
        self.assertEqual(len(EVIDENCE_FIELDS), 54)
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(
                NonProductionAssessmentSubmissionSubjectCurrentnessResult
            )),
            ("status", "subject_currentness_fact", "establishment_evidence"),
        )

    def test_02_status_contract_is_exact(self):
        self.assertEqual(tuple(item.name for item in STATUS), STATUS_NAMES)
        self.assertEqual(len(STATUS_NAMES), 37)
        self.assertEqual(len(STATUS.__members__), 37)

    def test_03_establishes_exact_fact_evidence_and_complete_lineage(self):
        upstream = upstream_result()
        result = establish()
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(dataclasses.astuple(result.subject_currentness_fact), (
            "provider-alpha", "subject-alpha", "principal-alpha",
            AuthorityRecordState.ACTIVE,
        ))
        evidence = result.establishment_evidence
        self.assertEqual(
            tuple(getattr(evidence, name) for name in UPSTREAM_FIELDS),
            tuple(getattr(upstream.establishment_evidence, name) for name in UPSTREAM_FIELDS),
        )
        self.assertTrue(all(
            type(getattr(evidence, name)) is type(getattr(upstream.establishment_evidence, name))
            for name in UPSTREAM_FIELDS
        ))
        self.assertEqual(tuple(getattr(evidence, name) for name in TAIL_FIELDS), (
            "provider-alpha", "subject-alpha", AuthorityRecordState.ACTIVE,
            AUTHORITY_REFERENCE, PROVENANCE_1,
            AUTHENTICATION_GOVERNANCE, MAPPING_GOVERNANCE,
        ))

    def test_04_exact_retry_is_fresh_and_preserves_original_event(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        with patch.object(
            module._ControlledAuthenticationAdapter,
            "current_verified_authentication",
            autospec=True,
            wraps=module._ControlledAuthenticationAdapter.current_verified_authentication,
        ) as authentication, patch.object(
            NonProductionPrincipalMappingAuthoritySource,
            "resolve_principal_mapping",
            autospec=True,
            wraps=NonProductionPrincipalMappingAuthoritySource.resolve_principal_mapping,
        ) as lookup, patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            autospec=True,
            wraps=NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority.
            establish_assessment_submission_entitlement_currentness,
        ) as upstream:
            second = establish(auth)
        self.assertIs(second.status, STATUS.REUSED)
        self.assertEqual(first.subject_currentness_fact, second.subject_currentness_fact)
        self.assertEqual(first.establishment_evidence, second.establishment_evidence)
        self.assertIsNot(first.subject_currentness_fact, second.subject_currentness_fact)
        self.assertIsNot(first.establishment_evidence, second.establishment_evidence)
        self.assertEqual(authentication.call_count, 1)
        self.assertEqual(lookup.call_count, 1)
        self.assertEqual(upstream.call_count, 1)
        self.assertEqual(second.establishment_evidence.subject_currentness_provenance_reference,
                         PROVENANCE_1)

    def test_05_distinct_attempts_get_independent_monotonic_events(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        second_context = context_result(context=business_context(
            attempt_reference="attempt-beta",
        ))
        second_upstream = changed_upstream(
            upstream_result(),
            attempt_reference="attempt-beta",
        )
        with patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            return_value=second_upstream,
        ):
            second = establish(auth, second_context)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(second.status, STATUS.ESTABLISHED)
        self.assertEqual(
            second.establishment_evidence.subject_currentness_provenance_reference,
            "non-production-assessment-submission-subject-currentness-"
            "establishment-provenance-2",
        )
        self.assertEqual(set(auth._subject_currentness_by_attempt),
                         {"attempt-alpha", "attempt-beta"})

    def test_06_business_context_root_fails_closed_before_authentication(self):
        cases = (
            (object(), STATUS.MALFORMED),
            (context_result(status=BC_STATUS.ENGAGEMENT_NOT_READY),
             STATUS.BUSINESS_CONTEXT_NOT_READY),
            (context_result(context=business_context(
                protected_operation=RequestedAction.SUBMIT,
            )), STATUS.MALFORMED),
            (context_result(context=business_context(principal_id=" principal-alpha")),
             STATUS.MALFORMED),
            (context_result(context=business_context(
                principal_id=StringSubclass("principal-alpha"),
            )), STATUS.MALFORMED),
        )
        for value, expected in cases:
            with self.subTest(expected=expected), patch.object(
                module._ControlledAuthenticationAdapter,
                "current_verified_authentication",
                side_effect=AssertionError("authentication must not run"),
            ):
                self.assert_failure(establish(value=value), expected)

    def test_07_authentication_outcomes_and_exact_type_are_enforced(self):
        cases = (
            (None, STATUS.AUTHENTICATION_NOT_CURRENT),
            (object(), STATUS.MALFORMED),
            ({"provider": "provider-alpha", "subject": "subject-alpha"}, STATUS.MALFORMED),
            (VerifiedFactSubclass("provider-alpha", "subject-alpha"), STATUS.MALFORMED),
            (verified_authentication(provider="provider-beta"), STATUS.MISMATCH),
            (verified_authentication(subject="subject-beta"), STATUS.MISMATCH),
        )
        for value, expected in cases:
            with self.subTest(value=type(value).__name__), patch.object(
                module._ControlledAuthenticationAdapter,
                "current_verified_authentication",
                return_value=value,
            ):
                self.assert_failure(establish(), expected)
        with patch.object(
            module._ControlledAuthenticationAdapter,
            "current_verified_authentication",
            side_effect=RuntimeError("owner unavailable"),
        ):
            self.assert_failure(establish(), STATUS.AUTHENTICATION_UNAVAILABLE)

    def test_08_authentication_strings_are_canonical_without_coercion(self):
        invalid = (
            "", " ", " provider-alpha", "provider-alpha ", "provider-alpha\n",
            StringSubclass("provider-alpha"), Coercible(),
        )
        for value in invalid:
            for field in ("provider", "subject"):
                changes = {field: value}
                with self.subTest(field=field, value=value), patch.object(
                    module._ControlledAuthenticationAdapter,
                    "current_verified_authentication",
                    return_value=verified_authentication(**changes),
                ):
                    self.assert_failure(establish(), STATUS.MALFORMED)

    def test_09_handoff_ready_is_reused_and_exactly_converged(self):
        with patch.object(
            module,
            "_resolve_handoff",
            wraps=module._resolve_handoff,
        ) as handoff:
            result = establish()
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(handoff.call_count, 1)
        supplied = handoff.call_args.kwargs["verified_authentication_fact"]
        self.assertIs(type(supplied), NonProductionVerifiedAuthenticationFact)
        self.assertEqual((supplied.provider, supplied.subject),
                         ("provider-alpha", "subject-alpha"))

    def test_10_handoff_failures_are_malformed_or_mismatch(self):
        invalid = NonProductionAuthenticatedSubjectHandoffResult(
            NonProductionAuthenticatedSubjectHandoffStatus.INVALID
        )
        malformed = (
            object(),
            invalid,
            NonProductionAuthenticatedSubjectHandoffResult(ForeignStatus.FOUND),
            NonProductionAuthenticatedSubjectHandoffResult(
                NonProductionAuthenticatedSubjectHandoffStatus.READY
            ),
            NonProductionAuthenticatedSubjectHandoffResult(
                NonProductionAuthenticatedSubjectHandoffStatus.READY,
                TrustedSubjectEvidence("provider-alpha", "subject-alpha", False),
            ),
            NonProductionAuthenticatedSubjectHandoffResult(
                NonProductionAuthenticatedSubjectHandoffStatus.READY,
                {"provider": "provider-alpha", "subject": "subject-alpha", "verified": True},
            ),
        )
        for value in malformed:
            with self.subTest(value=value), patch.object(
                module, "_resolve_handoff", return_value=value
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)
        for evidence in (
            TrustedSubjectEvidence("provider-beta", "subject-alpha", True),
            TrustedSubjectEvidence("provider-alpha", "subject-beta", True),
        ):
            value = NonProductionAuthenticatedSubjectHandoffResult(
                NonProductionAuthenticatedSubjectHandoffStatus.READY,
                evidence,
            )
            with self.subTest(evidence=evidence), patch.object(
                module, "_resolve_handoff", return_value=value
            ):
                self.assert_failure(establish(), STATUS.MISMATCH)
        with patch.object(module, "_resolve_handoff", side_effect=RuntimeError("invalid")):
            self.assert_failure(establish(), STATUS.MALFORMED)

    def test_11_principal_mapping_fixture_and_negative_space_are_exact(self):
        auth = authority("resource-alpha")
        source = auth._principal_mapping_source
        found = source.resolve_principal_mapping("provider-alpha", "subject-alpha")
        self.assertIs(found.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(found.records, (mapping(),))
        for key in (
            ("provider-beta", "subject-alpha"),
            ("provider-alpha", "subject-beta"),
            ("provider-beta", "subject-beta"),
        ):
            with self.subTest(key=key):
                self.assertIs(source.resolve_principal_mapping(*key).status,
                              AuthorityLookupStatus.NOT_FOUND)

    def test_12_real_generic_ambiguity_maps_exactly(self):
        record = mapping()
        source = mapping_source(record, record)
        generic = source.resolve_principal_mapping("provider-alpha", "subject-alpha")
        self.assertIs(generic.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(generic.records, (record, record))
        auth = authority("resource-alpha")
        auth._principal_mapping_source = source
        self.assert_failure(establish(auth), STATUS.PRINCIPAL_MAPPING_AMBIGUOUS)

    def test_13_real_generic_conflict_maps_exactly(self):
        active = mapping()
        stale = mapping(state=AuthorityRecordState.STALE)
        source = mapping_source(active, stale)
        generic = source.resolve_principal_mapping("provider-alpha", "subject-alpha")
        self.assertIs(generic.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(generic.records, (active, stale))
        auth = authority("resource-alpha")
        auth._principal_mapping_source = source
        self.assert_failure(establish(auth), STATUS.PRINCIPAL_MAPPING_CONFLICTING)

    def test_14_real_mapping_not_found_stale_and_malformed_are_mapped(self):
        cases = (
            (mapping_source(), STATUS.PRINCIPAL_MAPPING_NOT_FOUND),
            (mapping_source(mapping(state=AuthorityRecordState.STALE)),
             STATUS.PRINCIPAL_MAPPING_STALE),
            (mapping_source(object()), STATUS.MALFORMED),
        )
        for source, expected in cases:
            with self.subTest(expected=expected):
                auth = authority("resource-alpha")
                auth._principal_mapping_source = source
                self.assert_failure(establish(auth), expected)

    def test_15_mapping_simple_statuses_and_exception_are_mapped(self):
        cases = {
            AuthorityLookupStatus.NOT_FOUND: STATUS.PRINCIPAL_MAPPING_NOT_FOUND,
            AuthorityLookupStatus.STALE: STATUS.PRINCIPAL_MAPPING_STALE,
            AuthorityLookupStatus.UNAVAILABLE: STATUS.PRINCIPAL_MAPPING_UNAVAILABLE,
            AuthorityLookupStatus.MALFORMED: STATUS.MALFORMED,
            AuthorityLookupStatus.UNSUPPORTED: STATUS.MALFORMED,
        }
        for lookup_status, expected in cases.items():
            with self.subTest(status=lookup_status), patch.object(
                NonProductionPrincipalMappingAuthoritySource,
                "resolve_principal_mapping",
                return_value=AuthorityLookupResult(lookup_status),
            ):
                self.assert_failure(establish(), expected)
        with patch.object(
            NonProductionPrincipalMappingAuthoritySource,
            "resolve_principal_mapping",
            side_effect=RuntimeError("unavailable"),
        ):
            self.assert_failure(establish(), STATUS.PRINCIPAL_MAPPING_UNAVAILABLE)

    def test_16_mapping_result_container_and_record_shapes_are_strict(self):
        malformed = (
            ForeignLookup(AuthorityLookupStatus.FOUND, (mapping(),)),
            AuthorityLookupResult(ForeignStatus.FOUND, (mapping(),)),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (mapping(), mapping())),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, [mapping()]),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (object(),)),
            AuthorityLookupResult(AuthorityLookupStatus.FOUND, (
                MappingSubclass(**mapping().__dict__),
            )),
            AuthorityLookupResult(AuthorityLookupStatus.NOT_FOUND, (mapping(),)),
        )
        for lookup in malformed:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionPrincipalMappingAuthoritySource,
                "resolve_principal_mapping",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_17_mapping_ambiguity_and_conflict_shapes_are_strict(self):
        malformed = (
            AuthorityLookupResult.ambiguous(),
            AuthorityLookupResult.ambiguous((mapping(),)),
            AuthorityLookupResult.ambiguous((mapping(), mapping(principal_id="principal-beta"))),
            AuthorityLookupResult.ambiguous((mapping(), mapping(subject="subject-beta"))),
            AuthorityLookupResult.conflicting(),
            AuthorityLookupResult.conflicting((mapping(),)),
            AuthorityLookupResult.conflicting((mapping(), mapping())),
            AuthorityLookupResult.conflicting((mapping(), mapping(subject="subject-beta"))),
        )
        for lookup in malformed:
            with self.subTest(lookup=lookup), patch.object(
                NonProductionPrincipalMappingAuthoritySource,
                "resolve_principal_mapping",
                return_value=lookup,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_18_canonical_found_mapping_nonconvergence_is_mismatch(self):
        cases = (
            mapping(subject_provider="provider-beta"),
            mapping(subject="subject-beta"),
            mapping(principal_id="principal-beta"),
            mapping(authority_reference="principal-authority-beta"),
            mapping(state=AuthorityRecordState.INACTIVE),
        )
        for record in cases:
            with self.subTest(record=record), patch.object(
                NonProductionPrincipalMappingAuthoritySource,
                "resolve_principal_mapping",
                return_value=AuthorityLookupResult.found(record),
            ):
                self.assert_failure(establish(), STATUS.MISMATCH)

    def test_19_mapping_strings_and_enums_are_exact(self):
        invalid = (
            mapping(authority_reference=StringSubclass("principal-authority")),
            mapping(subject_provider=" provider-alpha"),
            mapping(subject="subject-alpha "),
            mapping(principal_id=""),
            mapping(state=ForeignStatus.FOUND),
        )
        for record in invalid:
            with self.subTest(record=record), patch.object(
                NonProductionPrincipalMappingAuthoritySource,
                "resolve_principal_mapping",
                return_value=AuthorityLookupResult.found(record),
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)

    def test_20_all_28_entitlement_failures_map_one_to_one(self):
        failures = tuple(
            status for status in UPSTREAM_STATUS
            if status not in (UPSTREAM_STATUS.ESTABLISHED, UPSTREAM_STATUS.REUSED)
        )
        self.assertEqual(len(failures), 28)
        for upstream_status in failures:
            with self.subTest(status=upstream_status.name), patch.object(
                NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
                "establish_assessment_submission_entitlement_currentness",
                return_value=NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
                    upstream_status
                ),
            ):
                self.assert_failure(establish(), STATUS[upstream_status.name])

    def test_21_entitlement_established_and_reused_both_continue(self):
        valid = upstream_result()
        reused = NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
            UPSTREAM_STATUS.REUSED,
            valid.entitlement_currentness_fact,
            valid.establishment_evidence,
        )
        for upstream in (valid, reused):
            with self.subTest(status=upstream.status), patch.object(
                NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
                "establish_assessment_submission_entitlement_currentness",
                return_value=upstream,
            ):
                self.assertIs(establish().status, STATUS.ESTABLISHED)

    def test_22_foreign_and_malformed_entitlement_shapes_are_malformed(self):
        valid = upstream_result()
        cases = (
            object(),
            ResultSubclass(valid.status, valid.entitlement_currentness_fact,
                           valid.establishment_evidence),
            NonProductionAssessmentSubmissionEntitlementCurrentnessResult(ForeignStatus.FOUND),
            NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
                UPSTREAM_STATUS.ESTABLISHED
            ),
            NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
                UPSTREAM_STATUS.ENTITLEMENT_NOT_FOUND,
                valid.entitlement_currentness_fact,
                valid.establishment_evidence,
            ),
            NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
                UPSTREAM_STATUS.ESTABLISHED,
                object(),
                valid.establishment_evidence,
            ),
            NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
                UPSTREAM_STATUS.ESTABLISHED,
                valid.entitlement_currentness_fact,
                object(),
            ),
        )
        for value in cases:
            with self.subTest(value=type(value).__name__), patch.object(
                NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
                "establish_assessment_submission_entitlement_currentness",
                return_value=value,
            ):
                self.assert_failure(establish(), STATUS.MALFORMED)
        with patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            side_effect=RuntimeError("invalid upstream"),
        ):
            self.assert_failure(establish(), STATUS.MALFORMED)

    def test_23_entitlement_fact_and_lineage_mismatches_fail_closed(self):
        valid = upstream_result()
        cases = (
            changed_upstream(valid, principal_id="principal-beta"),
            changed_upstream(valid, principal_authority_reference="principal-authority-beta"),
            changed_upstream(valid, business_entity_id="business-beta"),
            changed_upstream(valid, resource_reference="resource-beta",
                             resource_id="resource-beta"),
            changed_upstream(valid, requested_action=RequestedAction.VIEW),
            changed_upstream(valid, membership_authority_reference="wrong-authority"),
            changed_upstream(valid, entitlement_governance_reference="wrong-governance"),
        )
        for upstream in cases:
            with self.subTest(upstream=upstream), patch.object(
                NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
                "establish_assessment_submission_entitlement_currentness",
                return_value=upstream,
            ):
                self.assertIn(establish().status, (STATUS.MALFORMED, STATUS.MISMATCH))

    def test_24_failure_before_success_does_not_consume_provenance(self):
        auth = authority("resource-alpha")
        with patch.object(
            module._ControlledAuthenticationAdapter,
            "current_verified_authentication",
            return_value=None,
        ):
            self.assert_failure(establish(auth), STATUS.AUTHENTICATION_NOT_CURRENT)
            self.assert_failure(establish(auth), STATUS.AUTHENTICATION_NOT_CURRENT)
        success = establish(auth)
        self.assertIs(success.status, STATUS.ESTABLISHED)
        self.assertEqual(success.establishment_evidence.subject_currentness_provenance_reference,
                         PROVENANCE_1)
        self.assertEqual(auth._next_subject_currentness_provenance_index, 2)

    def test_25_post_success_authentication_failures_defeat_reuse_then_restore(self):
        cases = (
            (None, STATUS.AUTHENTICATION_NOT_CURRENT),
            (object(), STATUS.MALFORMED),
            (verified_authentication(provider="provider-beta"), STATUS.MISMATCH),
        )
        for value, expected in cases:
            with self.subTest(expected=expected):
                auth = authority("resource-alpha")
                first = establish(auth)
                with patch.object(
                    module._ControlledAuthenticationAdapter,
                    "current_verified_authentication",
                    return_value=value,
                ):
                    self.assert_failure(establish(auth), expected)
                restored = establish(auth)
                self.assertIs(restored.status, STATUS.REUSED)
                self.assertEqual(restored.establishment_evidence.
                                 subject_currentness_provenance_reference,
                                 first.establishment_evidence.
                                 subject_currentness_provenance_reference)
        auth = authority("resource-alpha")
        establish(auth)
        with patch.object(
            module._ControlledAuthenticationAdapter,
            "current_verified_authentication",
            side_effect=RuntimeError("unavailable"),
        ):
            self.assert_failure(establish(auth), STATUS.AUTHENTICATION_UNAVAILABLE)

    def test_26_post_success_handoff_failures_defeat_reuse(self):
        auth = authority("resource-alpha")
        establish(auth)
        values = (
            NonProductionAuthenticatedSubjectHandoffResult(
                NonProductionAuthenticatedSubjectHandoffStatus.INVALID
            ),
            object(),
            NonProductionAuthenticatedSubjectHandoffResult(
                NonProductionAuthenticatedSubjectHandoffStatus.READY,
                TrustedSubjectEvidence("provider-beta", "subject-alpha", True),
            ),
        )
        for value in values:
            with self.subTest(value=value), patch.object(
                module, "_resolve_handoff", return_value=value
            ):
                self.assertNotEqual(establish(auth).status, STATUS.REUSED)
        self.assertIs(establish(auth).status, STATUS.REUSED)

    def test_27_post_success_mapping_failures_defeat_reuse_then_restore(self):
        record = mapping()
        sources = (
            (mapping_source(), STATUS.PRINCIPAL_MAPPING_NOT_FOUND),
            (mapping_source(record, record), STATUS.PRINCIPAL_MAPPING_AMBIGUOUS),
            (mapping_source(record, mapping(state=AuthorityRecordState.STALE)),
             STATUS.PRINCIPAL_MAPPING_CONFLICTING),
            (mapping_source(mapping(state=AuthorityRecordState.STALE)),
             STATUS.PRINCIPAL_MAPPING_STALE),
            (mapping_source(object()), STATUS.MALFORMED),
        )
        for source, expected in sources:
            with self.subTest(expected=expected):
                auth = authority("resource-alpha")
                first = establish(auth)
                with patch.object(auth, "_principal_mapping_source", source):
                    self.assert_failure(establish(auth), expected)
                restored = establish(auth)
                self.assertIs(restored.status, STATUS.REUSED)
                self.assertEqual(restored.establishment_evidence.
                                 subject_currentness_provenance_reference,
                                 first.establishment_evidence.
                                 subject_currentness_provenance_reference)
        auth = authority("resource-alpha")
        establish(auth)
        with patch.object(
            NonProductionPrincipalMappingAuthoritySource,
            "resolve_principal_mapping",
            return_value=AuthorityLookupResult.unavailable(),
        ):
            self.assert_failure(establish(auth), STATUS.PRINCIPAL_MAPPING_UNAVAILABLE)

    def test_28_post_success_entitlement_failure_defeats_reuse_then_restores(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        failure = NonProductionAssessmentSubmissionEntitlementCurrentnessResult(
            UPSTREAM_STATUS.ENTITLEMENT_STALE
        )
        with patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            return_value=failure,
        ):
            self.assert_failure(establish(auth), STATUS.ENTITLEMENT_STALE)
        restored = establish(auth)
        self.assertIs(restored.status, STATUS.REUSED)
        self.assertEqual(restored.establishment_evidence.
                         subject_currentness_provenance_reference,
                         first.establishment_evidence.
                         subject_currentness_provenance_reference)

    def test_29_same_attempt_different_fresh_lineage_never_reuses(self):
        auth = authority("resource-alpha")
        establish(auth)
        changed_context = context_result(context=business_context(
            engagement_reference="engagement-beta",
        ))
        changed = changed_upstream(
            upstream_result(),
            engagement_reference="engagement-beta",
        )
        with patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            return_value=changed,
        ):
            result = establish(auth, changed_context)
        self.assertIs(result.status, STATUS.MISMATCH)
        self.assertEqual(len(auth._subject_currentness_by_attempt), 1)
        self.assertEqual(auth._next_subject_currentness_provenance_index, 2)

    def test_30_returned_and_caller_mutation_cannot_change_canonical_authority(self):
        auth = authority("resource-alpha")
        caller = context_result()
        first = establish(auth, caller)
        object.__setattr__(caller.business_context, "principal_id", "principal-beta")
        object.__setattr__(first.subject_currentness_fact, "principal_id", "principal-beta")
        object.__setattr__(first.establishment_evidence, "resource_id", "resource-beta")
        object.__setattr__(first, "status", STATUS.MALFORMED)
        retry = establish(auth)
        self.assertIs(retry.status, STATUS.REUSED)
        self.assertEqual(retry.subject_currentness_fact.principal_id, "principal-alpha")
        self.assertEqual(retry.establishment_evidence.resource_id, "resource-alpha")
        self.assertEqual(retry.establishment_evidence.
                         subject_currentness_provenance_reference, PROVENANCE_1)

    def test_31_mapping_source_snapshot_mutation_is_isolated(self):
        record = mapping()
        source = mapping_source(record)
        auth = authority("resource-alpha")
        auth._principal_mapping_source = source
        first = establish(auth)
        object.__setattr__(record, "principal_id", "principal-beta")
        retry = establish(auth)
        self.assertIs(first.status, STATUS.ESTABLISHED)
        self.assertIs(retry.status, STATUS.REUSED)
        self.assertEqual(retry.subject_currentness_fact.principal_id, "principal-alpha")

    def test_32_canonical_state_is_immutable_scalar_enum_snapshot_only(self):
        auth = authority("resource-alpha")
        result = establish(auth)
        self.assertIs(result.status, STATUS.ESTABLISHED)
        self.assertEqual(set(auth.__slots__), {
            "_authentication_adapter", "_principal_mapping_source",
            "_entitlement_currentness_authority", "_subject_currentness_by_attempt",
            "_next_subject_currentness_provenance_index",
        })
        stored = auth._subject_currentness_by_attempt["attempt-alpha"]
        self.assertIs(type(stored.evidence_values), tuple)
        self.assertIs(type(stored.retry_identity), tuple)
        forbidden = (
            NonProductionVerifiedAuthenticationFact, PrincipalMapping,
            NonProductionAssessmentSubmissionSubjectCurrentnessFact,
            NonProductionAssessmentSubmissionSubjectCurrentnessEvidence,
            NonProductionAssessmentSubmissionSubjectCurrentnessResult,
        )
        self.assertFalse(any(isinstance(value, forbidden)
                             for value in stored.evidence_values))
        self.assertEqual(len(stored.evidence_values), 54)
        self.assertEqual(len(stored.retry_identity), 53)

    def test_33_dependency_replacement_and_caller_authority_fail_closed(self):
        for slot in (
            "_authentication_adapter", "_principal_mapping_source",
            "_entitlement_currentness_authority",
        ):
            auth = authority("resource-alpha")
            setattr(auth, slot, object())
            with self.subTest(slot=slot):
                self.assert_failure(establish(auth), STATUS.MALFORMED)
        request = AuthorizationRequest(
            subject_evidence=TrustedSubjectEvidence(
                "provider-alpha", "subject-alpha", True
            ),
            resource_reference="resource-alpha",
            requested_action=RequestedAction.SUBMIT,
            governed_version_context=None,
            correlation_id="correlation-alpha",
            evaluation_context="assessment-submission",
        )
        self.assert_failure(establish(value=request), STATUS.MALFORMED)

    def test_34_composition_order_and_failure_precedence_are_exact(self):
        with patch.object(
            module._ControlledAuthenticationAdapter,
            "current_verified_authentication",
            return_value=None,
        ), patch.object(
            NonProductionPrincipalMappingAuthoritySource,
            "resolve_principal_mapping",
            side_effect=AssertionError("mapping must not run"),
        ), patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            side_effect=AssertionError("entitlement must not run"),
        ):
            self.assert_failure(establish(), STATUS.AUTHENTICATION_NOT_CURRENT)
        with patch.object(
            NonProductionPrincipalMappingAuthoritySource,
            "resolve_principal_mapping",
            return_value=AuthorityLookupResult.missing(),
        ), patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            side_effect=AssertionError("entitlement must not run"),
        ):
            self.assert_failure(establish(), STATUS.PRINCIPAL_MAPPING_NOT_FOUND)

    def test_35_no_public_injection_or_forbidden_authority_boundary(self):
        signature = inspect.signature(NonProductionAssessmentSubmissionSubjectCurrentnessAuthority)
        self.assertEqual(tuple(signature.parameters), ("candidate_resource_references",))
        method = inspect.signature(
            NonProductionAssessmentSubmissionSubjectCurrentnessAuthority.
            establish_assessment_submission_subject_currentness
        )
        self.assertEqual(tuple(method.parameters), ("self", "business_context_result"))
        source = Path(module.__file__).read_text()
        forbidden = (
            "boto3", "botocore", "cognito", "dynamodb", "api gateway",
            "requests", "openai", "mcp", "authorizationrequest",
            "trustedauthorizationevaluator", "authorizationdecision",
        )
        self.assertFalse(any(value in source.lower() for value in forbidden))
        self.assertNotIn("ALLOW", source)
        self.assertNotIn("DENY", source)
        self.assertNotIn("SUBMITTED", source)
        self.assertNotIn("permission", source.lower())

    def test_36_private_adapter_and_sources_are_invoked_once_per_call(self):
        auth = authority("resource-alpha")
        with patch.object(
            module._ControlledAuthenticationAdapter,
            "current_verified_authentication",
            autospec=True,
            wraps=module._ControlledAuthenticationAdapter.current_verified_authentication,
        ) as authentication, patch.object(
            NonProductionPrincipalMappingAuthoritySource,
            "resolve_principal_mapping",
            autospec=True,
            wraps=NonProductionPrincipalMappingAuthoritySource.resolve_principal_mapping,
        ) as mapping_lookup, patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            autospec=True,
            wraps=NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority.
            establish_assessment_submission_entitlement_currentness,
        ) as entitlement:
            self.assertIs(establish(auth).status, STATUS.ESTABLISHED)
        self.assertEqual(authentication.call_count, 1)
        self.assertEqual(mapping_lookup.call_count, 1)
        self.assertEqual(entitlement.call_count, 1)

    def test_37_post_success_exceptions_and_unrepresentable_failures_defeat_reuse(self):
        operations = (
            (
                patch.object(
                    module._ControlledAuthenticationAdapter,
                    "current_verified_authentication",
                    side_effect=RuntimeError("authentication unavailable"),
                ),
                STATUS.AUTHENTICATION_UNAVAILABLE,
            ),
            (
                patch.object(module, "_resolve_handoff", side_effect=RuntimeError("invalid")),
                STATUS.MALFORMED,
            ),
            (
                patch.object(
                    NonProductionPrincipalMappingAuthoritySource,
                    "resolve_principal_mapping",
                    side_effect=RuntimeError("mapping unavailable"),
                ),
                STATUS.PRINCIPAL_MAPPING_UNAVAILABLE,
            ),
            (
                patch.object(
                    NonProductionPrincipalMappingAuthoritySource,
                    "resolve_principal_mapping",
                    return_value=AuthorityLookupResult(AuthorityLookupStatus.MALFORMED),
                ),
                STATUS.MALFORMED,
            ),
            (
                patch.object(
                    NonProductionPrincipalMappingAuthoritySource,
                    "resolve_principal_mapping",
                    return_value=AuthorityLookupResult(AuthorityLookupStatus.UNSUPPORTED),
                ),
                STATUS.MALFORMED,
            ),
            (
                patch.object(
                    NonProductionPrincipalMappingAuthoritySource,
                    "resolve_principal_mapping",
                    return_value=AuthorityLookupResult.found(
                        mapping(principal_id="principal-beta")
                    ),
                ),
                STATUS.MISMATCH,
            ),
            (
                patch.object(
                    NonProductionPrincipalMappingAuthoritySource,
                    "resolve_principal_mapping",
                    return_value=AuthorityLookupResult.found(
                        mapping(authority_reference="principal-authority-beta")
                    ),
                ),
                STATUS.MISMATCH,
            ),
            (
                patch.object(
                    NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
                    "establish_assessment_submission_entitlement_currentness",
                    return_value=object(),
                ),
                STATUS.MALFORMED,
            ),
        )
        for operation, expected in operations:
            with self.subTest(expected=expected):
                auth = authority("resource-alpha")
                first = establish(auth)
                with operation:
                    self.assert_failure(establish(auth), expected)
                self.assertEqual(len(auth._subject_currentness_by_attempt), 1)
                self.assertEqual(auth._next_subject_currentness_provenance_index, 2)
                restored = establish(auth)
                self.assertIs(restored.status, STATUS.REUSED)
                self.assertEqual(
                    restored.establishment_evidence.
                    subject_currentness_provenance_reference,
                    first.establishment_evidence.
                    subject_currentness_provenance_reference,
                )

    def test_38_post_success_entitlement_lineage_mismatch_defeats_reuse(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        changed = changed_upstream(
            upstream_result(),
            principal_authority_reference="principal-authority-beta",
        )
        with patch.object(
            NonProductionAssessmentSubmissionEntitlementCurrentnessAuthority,
            "establish_assessment_submission_entitlement_currentness",
            return_value=changed,
        ):
            self.assert_failure(establish(auth), STATUS.MISMATCH)
        self.assertEqual(len(auth._subject_currentness_by_attempt), 1)
        self.assertEqual(auth._next_subject_currentness_provenance_index, 2)
        restored = establish(auth)
        self.assertIs(restored.status, STATUS.REUSED)
        self.assertEqual(
            restored.establishment_evidence.subject_currentness_provenance_reference,
            first.establishment_evidence.subject_currentness_provenance_reference,
        )


if __name__ == "__main__":
    unittest.main()
