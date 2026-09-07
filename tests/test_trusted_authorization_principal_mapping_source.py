import sys
import unittest
from dataclasses import replace
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trusted_authorization import (  # noqa: E402
    APPLICABILITY_GOVERNANCE_VERSION,
    AUTHORIZATION_SEMANTICS_VERSION,
    BOUNDED_EVALUATION_CONTEXT,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationDecision,
    AuthorizationRequest,
    GovernedVersionContext,
    ReasonCategory,
    RequestedAction,
    TrustedAuthorizationEvaluator,
    TrustedSubjectEvidence,
)
from trusted_authorization.models import PrincipalMapping  # noqa: E402
from trusted_authorization.principal_mapping_source import (  # noqa: E402
    NonProductionPrincipalMappingAuthoritySource,
)


SUBJECT = TrustedSubjectEvidence(
    provider="local-principal-source",
    subject="subject-alpha",
    verified=True,
)


def mapping(
    authority_reference="principal-map-alpha",
    state=AuthorityRecordState.ACTIVE,
    subject_provider="local-principal-source",
    subject="subject-alpha",
    principal_id="principal-alpha",
):
    return PrincipalMapping(
        authority_reference=authority_reference,
        state=state,
        subject_provider=subject_provider,
        subject=subject,
        principal_id=principal_id,
    )


def governed_context(
    semantics_version=AUTHORIZATION_SEMANTICS_VERSION,
    applicability_version=APPLICABILITY_GOVERNANCE_VERSION,
    evaluation_context=BOUNDED_EVALUATION_CONTEXT,
):
    return GovernedVersionContext(
        authorization_semantics_version=semantics_version,
        applicability_governance_version=applicability_version,
        evaluation_context=evaluation_context,
    )


def request(subject=SUBJECT):
    return AuthorizationRequest(
        subject_evidence=subject,
        resource_reference="resource-alpha",
        requested_action=RequestedAction.VIEW,
        governed_version_context=governed_context(),
        correlation_id="principal-source-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


class NonProductionPrincipalMappingAuthoritySourceTests(unittest.TestCase):
    def test_known_subject_resolves_expected_stable_principal_mapping(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0].principal_id, "principal-alpha")

    def test_unknown_subject_and_empty_source_return_no_positive_mapping(self):
        populated = NonProductionPrincipalMappingAuthoritySource([mapping()])
        empty = NonProductionPrincipalMappingAuthoritySource()

        unknown = populated.resolve_principal_mapping(
            "local-principal-source",
            "unknown-subject",
        )
        absent = empty.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(unknown.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(unknown.records, ())
        self.assertEqual(absent.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(absent.records, ())

    def test_malformed_lookup_inputs_fail_closed_before_matching(self):
        class Hostile:
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        cases = (
            ("hostile provider", Hostile(), "subject-alpha"),
            ("hostile subject", "local-principal-source", Hostile()),
            ("empty provider", "", "subject-alpha"),
            ("whitespace provider", "   ", "subject-alpha"),
            ("empty subject", "local-principal-source", ""),
            ("whitespace subject", "local-principal-source", "   "),
        )

        for label, subject_provider, subject in cases:
            with self.subTest(case=label):
                Hostile.comparisons = 0

                result = source.resolve_principal_mapping(
                    subject_provider,
                    subject,
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(Hostile.comparisons, 0)

    def test_str_subclass_lookup_inputs_fail_closed_before_behavior_invocation(self):
        class HostileStr(str):
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        class HostileStripStr(str):
            strip_calls = 0

            def strip(self):
                type(self).strip_calls += 1
                return object()

        class RaisingStripStr(str):
            strip_calls = 0

            def strip(self):
                type(self).strip_calls += 1
                raise RuntimeError("strip unavailable")

        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        cases = (
            (
                "hostile str subclass provider",
                HostileStr("wrong-provider"),
                "subject-alpha",
                HostileStr,
                "comparisons",
            ),
            (
                "hostile str subclass subject",
                "local-principal-source",
                HostileStr("wrong-subject"),
                HostileStr,
                "comparisons",
            ),
            (
                "both hostile str subclass inputs",
                HostileStr("wrong-provider"),
                HostileStr("wrong-subject"),
                HostileStr,
                "comparisons",
            ),
            (
                "hostile strip provider",
                HostileStripStr("wrong-provider"),
                "subject-alpha",
                HostileStripStr,
                "strip_calls",
            ),
            (
                "raising strip provider",
                RaisingStripStr("local-principal-source"),
                "subject-alpha",
                RaisingStripStr,
                "strip_calls",
            ),
        )

        for label, subject_provider, subject, instrumented, counter in cases:
            with self.subTest(case=label):
                setattr(instrumented, counter, 0)

                result = source.resolve_principal_mapping(
                    subject_provider,
                    subject,
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_mapping_evidence_fails_closed(self):
        malformed = object.__new__(PrincipalMapping)
        object.__setattr__(malformed, "authority_reference", "bad-map")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(
            malformed,
            "subject_provider",
            "local-principal-source",
        )
        object.__setattr__(malformed, "subject", "subject-alpha")
        source = NonProductionPrincipalMappingAuthoritySource([malformed])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_non_current_mapping_states_return_no_positive_mapping(self):
        cases = (
            (AuthorityRecordState.INACTIVE, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.DISABLED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.REVOKED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.EXPIRED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.TERMINATED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.UNKNOWN, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.STALE, AuthorityLookupStatus.STALE),
        )
        for state, expected_status in cases:
            with self.subTest(state=state):
                source = NonProductionPrincipalMappingAuthoritySource(
                    [mapping(state=state)]
                )

                result = source.resolve_principal_mapping(
                    "local-principal-source",
                    "subject-alpha",
                )

                self.assertEqual(result.status, expected_status)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_conflicting_principal_mappings_fail_closed(self):
        source = NonProductionPrincipalMappingAuthoritySource(
            [
                mapping(authority_reference="principal-map-alpha"),
                mapping(
                    authority_reference="principal-map-beta",
                    principal_id="principal-beta",
                ),
            ]
        )

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(len(result.records), 2)

    def test_duplicate_applicable_mappings_fail_closed_without_deduplication(self):
        source = NonProductionPrincipalMappingAuthoritySource(
            [
                mapping(authority_reference="principal-map-alpha"),
                mapping(authority_reference="principal-map-alpha-copy"),
            ]
        )

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)

    def test_repeated_lookup_is_deterministic(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])

        first = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )
        second = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(first, second)

    def test_lookup_uses_captured_instance_identity_fields(self):
        class ConfusedPrincipalMapping(PrincipalMapping):
            def __getattribute__(self, name):
                if name == "subject_provider":
                    return "local-principal-source"
                if name == "subject":
                    return "subject-alpha"
                return object.__getattribute__(self, name)

        record = object.__new__(ConfusedPrincipalMapping)
        object.__setattr__(record, "authority_reference", "principal-map-spoof")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "subject_provider", "other-source")
        object.__setattr__(record, "subject", "other-subject")
        object.__setattr__(record, "principal_id", "principal-alpha")
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.NOT_FOUND)

    def test_verified_subject_evidence_does_not_create_mapping(self):
        source = NonProductionPrincipalMappingAuthoritySource()
        evaluator = TrustedAuthorizationEvaluator(source)

        result = evaluator.evaluate(request())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)

    def test_principal_mapping_alone_does_not_create_downstream_authority(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        evaluator = TrustedAuthorizationEvaluator(source)

        result = evaluator.evaluate(request())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)
        self.assertEqual(result.audit_evidence.principal_id, "principal-alpha")
        self.assertIn(
            "principal_mapping:principal-map-alpha",
            result.audit_evidence.authority_inputs,
        )
        self.assertIn(
            "resource_identity:UNSUPPORTED",
            result.audit_evidence.authority_inputs,
        )

    def test_unsupported_authority_categories_return_no_positive_authority(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        lookups = (
            source.resolve_resource("resource-alpha"),
            source.resolve_business_entity("business-alpha"),
            source.resolve_membership("principal-alpha", "business-alpha"),
            source.resolve_entitlement(
                "principal-alpha",
                "business-alpha",
                "resource-alpha",
                RequestedAction.VIEW,
            ),
        )

        for lookup in lookups:
            with self.subTest(lookup=lookup):
                self.assertEqual(lookup.status, AuthorityLookupStatus.UNSUPPORTED)
                self.assertEqual(lookup.records, ())

    def test_source_exposes_no_authority_management_surface(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        forbidden_names = (
            "add_mapping",
            "create_mapping",
            "update_mapping",
            "delete_mapping",
            "remove_mapping",
            "revoke_mapping",
            "restore_mapping",
            "reactivate_mapping",
            "assign_principal",
        )

        for name in forbidden_names:
            with self.subTest(name=name):
                self.assertFalse(hasattr(source, name))

    def test_source_keeps_only_constructor_supplied_records(self):
        first = mapping()
        second = replace(first, authority_reference="principal-map-beta")
        source = NonProductionPrincipalMappingAuthoritySource([first, second])

        self.assertEqual(source.__slots__, ("_principal_mappings",))
        self.assertEqual(source._principal_mappings, (first, second))


if __name__ == "__main__":
    unittest.main()
