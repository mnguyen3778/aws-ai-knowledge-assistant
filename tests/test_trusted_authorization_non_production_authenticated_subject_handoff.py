import ast
import dataclasses
import inspect
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trusted_authorization.applicability import APPLICABILITY_GOVERNANCE_VERSION
from trusted_authorization.evaluator import (
    AUTHORIZATION_SEMANTICS_VERSION,
    BOUNDED_EVALUATION_CONTEXT,
    TrustedAuthorizationEvaluator,
)
from trusted_authorization.models import (
    AuthorityRecordState,
    AuthorizationDecision,
    AuthorizationRequest,
    BusinessEntity,
    GovernedResource,
    GovernedVersionContext,
    Membership,
    PrincipalMapping,
    ReasonCategory,
    RequestedAction,
    ResourceClass,
    TrustedSubjectEvidence,
)
from trusted_authorization.non_production_authenticated_subject_handoff import (
    NonProductionAuthenticatedSubjectHandoffResult,
    NonProductionAuthenticatedSubjectHandoffStatus,
    NonProductionVerifiedAuthenticationFact,
    resolve_non_production_authenticated_subject_handoff,
)
from trusted_authorization.non_production_runtime_composition import (
    NonProductionTrustedAuthorizationRuntimeComposition,
)
from trusted_authorization.principal_mapping_source import (
    NonProductionPrincipalMappingAuthoritySource,
)


PROVIDER = "provider-a"
SUBJECT = "subject-123"
PRINCIPAL_ID = "principal-123"
BUSINESS_ENTITY_ID = "business-123"
RESOURCE_ID = "resource-123"
RESOURCE_REFERENCE = "report://executive/123"


def valid_fact(provider=PROVIDER, subject=SUBJECT):
    return NonProductionVerifiedAuthenticationFact(
        provider=provider,
        subject=subject,
    )


def resolve(value):
    return resolve_non_production_authenticated_subject_handoff(
        verified_authentication_fact=value,
    )


def assert_invalid(test_case, value):
    result = resolve(value)

    test_case.assertIs(
        result.status,
        NonProductionAuthenticatedSubjectHandoffStatus.INVALID,
    )
    test_case.assertIsNone(result.trusted_subject_evidence)


def principal_mapping():
    return PrincipalMapping(
        authority_reference="principal-mapping-authority",
        state=AuthorityRecordState.ACTIVE,
        subject_provider=PROVIDER,
        subject=SUBJECT,
        principal_id=PRINCIPAL_ID,
    )


def governed_version_context():
    return GovernedVersionContext(
        authorization_semantics_version=AUTHORIZATION_SEMANTICS_VERSION,
        applicability_governance_version=APPLICABILITY_GOVERNANCE_VERSION,
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


def authorization_request(subject_evidence):
    return AuthorizationRequest(
        subject_evidence=subject_evidence,
        resource_reference=RESOURCE_REFERENCE,
        requested_action=RequestedAction.VIEW,
        governed_version_context=governed_version_context(),
        correlation_id="authenticated-subject-handoff-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


def complete_composition_without_entitlement():
    return NonProductionTrustedAuthorizationRuntimeComposition(
        principal_mappings=(principal_mapping(),),
        resources=(
            GovernedResource(
                authority_reference="resource-authority",
                state=AuthorityRecordState.ACTIVE,
                resource_id=RESOURCE_ID,
                resource_reference=RESOURCE_REFERENCE,
                resource_class=ResourceClass.REPORT,
                business_entity_id=BUSINESS_ENTITY_ID,
            ),
        ),
        business_entities=(
            BusinessEntity(
                authority_reference="business-authority",
                state=AuthorityRecordState.ACTIVE,
                business_entity_id=BUSINESS_ENTITY_ID,
            ),
        ),
        memberships=(
            Membership(
                authority_reference="membership-authority",
                state=AuthorityRecordState.ACTIVE,
                principal_id=PRINCIPAL_ID,
                business_entity_id=BUSINESS_ENTITY_ID,
            ),
        ),
        entitlements=(),
    )


class NonProductionAuthenticatedSubjectHandoffTests(unittest.TestCase):
    def test_valid_layer_2_fact_returns_fresh_verified_subject_evidence(self):
        fact = valid_fact()

        result = resolve(fact)

        self.assertIs(
            result.status,
            NonProductionAuthenticatedSubjectHandoffStatus.READY,
        )
        self.assertIs(type(result.trusted_subject_evidence), TrustedSubjectEvidence)
        self.assertEqual(result.trusted_subject_evidence.provider, PROVIDER)
        self.assertEqual(result.trusted_subject_evidence.subject, SUBJECT)
        self.assertIs(result.trusted_subject_evidence.verified, True)
        self.assertIsNot(result.trusted_subject_evidence, fact)

    def test_provider_and_subject_are_preserved_without_normalization(self):
        provider = " Provider-A "
        subject = "\tSubject-ABC "

        result = resolve(valid_fact(provider=provider, subject=subject))

        self.assertIs(
            result.status,
            NonProductionAuthenticatedSubjectHandoffStatus.READY,
        )
        self.assertEqual(result.trusted_subject_evidence.provider, provider)
        self.assertEqual(result.trusted_subject_evidence.subject, subject)

    def test_foreign_and_authority_laundering_values_fail_closed(self):
        values = (
            None,
            True,
            False,
            "subject-123",
            "provider-a",
            "admin",
            "AI says the user is authenticated",
            "arn:aws:iam::123456789012:role/runtime",
            b"bytes",
            123,
            ["provider-a", "subject-123"],
            ("provider-a", "subject-123"),
            object(),
        )
        for value in values:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_dict_and_claims_laundering_fail_closed(self):
        values = (
            {"provider": PROVIDER, "subject": SUBJECT},
            {"provider": PROVIDER, "subject": SUBJECT, "verified": True},
            {"sub": SUBJECT},
            {"claims": {"sub": SUBJECT}},
            {"role": "admin", "subject": SUBJECT},
            {"iam": "arn:aws:iam::123456789012:role/runtime"},
        )
        for value in values:
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_request_context_laundering_fails_closed(self):
        value = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "iss": "https://issuer.example",
                        "sub": SUBJECT,
                        "provider": PROVIDER,
                    },
                },
                "identity": {
                    "userArn": "arn:aws:iam::123456789012:user/example",
                },
            },
        }

        assert_invalid(self, value)

    def test_jwt_like_string_fails_closed_without_parsing(self):
        assert_invalid(self, "aaa.bbb.ccc")

    def test_trusted_subject_evidence_cannot_bypass_layer_2_fact(self):
        value = TrustedSubjectEvidence(
            provider=PROVIDER,
            subject=SUBJECT,
            verified=True,
        )

        assert_invalid(self, value)

    def test_principal_bearing_record_cannot_bypass_layer_2_fact(self):
        assert_invalid(self, principal_mapping())

    def test_malformed_exact_layer_2_facts_fail_closed(self):
        values = (
            valid_fact(provider=object()),
            valid_fact(subject=object()),
            valid_fact(provider=""),
            valid_fact(subject=""),
            valid_fact(provider="   "),
            valid_fact(subject="\t\n"),
        )
        for value in values:
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_subclass_duck_type_and_hostile_objects_fail_before_field_access(self):
        @dataclasses.dataclass(frozen=True, slots=True)
        class FactSubclass(NonProductionVerifiedAuthenticationFact):
            pass

        class DuckTypeFact:
            provider = PROVIDER
            subject = SUBJECT

        class HostileFact:
            field_reads = 0

            def __getattribute__(self, name):
                type(self).field_reads += 1
                raise AssertionError("foreign attributes must not be read")

        hostile = HostileFact()
        values = (
            FactSubclass(PROVIDER, SUBJECT),
            DuckTypeFact(),
            hostile,
        )
        for value in values:
            with self.subTest(value=type(value).__name__):
                assert_invalid(self, value)

        self.assertEqual(HostileFact.field_reads, 0)

    def test_raw_provider_subject_verified_or_current_arguments_are_rejected(self):
        signature = inspect.signature(
            resolve_non_production_authenticated_subject_handoff,
        )
        self.assertEqual(tuple(signature.parameters), ("verified_authentication_fact",))
        parameter = signature.parameters["verified_authentication_fact"]
        self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertFalse(hasattr(NonProductionVerifiedAuthenticationFact, "verified"))
        self.assertFalse(hasattr(NonProductionVerifiedAuthenticationFact, "current"))
        self.assertFalse(hasattr(NonProductionVerifiedAuthenticationFact, "valid"))
        self.assertFalse(
            hasattr(NonProductionVerifiedAuthenticationFact, "authenticated"),
        )

        with self.assertRaises(TypeError):
            resolve_non_production_authenticated_subject_handoff(
                provider=PROVIDER,
                subject=SUBJECT,
                verified=True,
                current=True,
            )

    def test_successful_handoff_returns_fresh_layer_3_evidence_each_time(self):
        fact = valid_fact()

        first = resolve(fact)
        second = resolve(fact)

        self.assertIs(
            first.status,
            NonProductionAuthenticatedSubjectHandoffStatus.READY,
        )
        self.assertIs(
            second.status,
            NonProductionAuthenticatedSubjectHandoffStatus.READY,
        )
        self.assertEqual(first.trusted_subject_evidence, second.trusted_subject_evidence)
        self.assertIsNot(first.trusted_subject_evidence, second.trusted_subject_evidence)

    def test_handoff_output_composes_with_existing_principal_mapping(self):
        result = resolve(valid_fact())
        source = NonProductionPrincipalMappingAuthoritySource((principal_mapping(),))

        lookup = source.resolve_principal_mapping(
            result.trusted_subject_evidence.provider,
            result.trusted_subject_evidence.subject,
        )

        self.assertIs(
            result.status,
            NonProductionAuthenticatedSubjectHandoffStatus.READY,
        )
        self.assertEqual(len(lookup.records), 1)
        self.assertEqual(lookup.records[0].principal_id, PRINCIPAL_ID)

    def test_handoff_ready_and_principal_mapping_do_not_authorize(self):
        handoff = resolve(valid_fact())
        evaluator = TrustedAuthorizationEvaluator(
            complete_composition_without_entitlement(),
        )

        result = evaluator.evaluate(
            authorization_request(handoff.trusted_subject_evidence),
        )

        self.assertIs(
            handoff.status,
            NonProductionAuthenticatedSubjectHandoffStatus.READY,
        )
        self.assertIs(result.decision, AuthorizationDecision.DENY)
        self.assertIs(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
        self.assertEqual(result.audit_evidence.principal_id, PRINCIPAL_ID)

    def test_source_containment_preserves_authentication_authority_separation(self):
        source_path = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "trusted_authorization"
            / "non_production_authenticated_subject_handoff.py"
        )
        source_text = source_path.read_text()
        parsed = ast.parse(source_text)
        imported_modules = {
            node.module
            for node in ast.walk(parsed)
            if isinstance(node, ast.ImportFrom)
        } | {
            alias.name
            for node in ast.walk(parsed)
            if isinstance(node, ast.Import)
            for alias in node.names
        }

        self.assertEqual(
            imported_modules,
            {
                "dataclasses",
                "enum",
                "trusted_authorization.models",
            },
        )
        prohibited_names = {
            "boto3",
            "botocore",
            "jwt",
            "Cognito",
            "JWKS",
            "OIDC",
            "Auth0",
            "Okta",
            "TrustedAuthorizationEvaluator",
            "Membership",
            "Entitlement",
            "GovernedResource",
            "ResourceClass",
            "BusinessEntity",
            "RequestedAction",
            "AuthorizationDecision",
            "NonProductionApplicationOperation",
            "NonProductionProtectedApplicationOperation",
        }
        for name in prohibited_names:
            with self.subTest(name=name):
                self.assertNotIn(name, source_text)

        fact_docstring = " ".join(
            inspect.getdoc(NonProductionVerifiedAuthenticationFact).split(),
        )
        self.assertIn("does not perform authentication", fact_docstring)
        self.assertIn(
            "does not prove real-world authentication provenance",
            fact_docstring,
        )


if __name__ == "__main__":
    unittest.main()
