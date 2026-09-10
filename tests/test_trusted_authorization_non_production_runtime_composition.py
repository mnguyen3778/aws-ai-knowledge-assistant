import ast
import inspect
import sys
import textwrap
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization as trusted_authorization_package  # noqa: E402
from trusted_authorization import (  # noqa: E402
    APPLICABILITY_GOVERNANCE_VERSION,
    AUTHORIZATION_SEMANTICS_VERSION,
    BOUNDED_EVALUATION_CONTEXT,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationDecision,
    AuthorizationRequest,
    BusinessEntity,
    Entitlement,
    GovernedVersionContext,
    GovernedResource,
    Membership,
    PrincipalMapping,
    ReasonCategory,
    RequestedAction,
    ResourceActionApplicability,
    ResourceClass,
    TrustedAuthorizationEvaluator,
    TrustedSubjectEvidence,
)
from trusted_authorization import (  # noqa: E402
    non_production_runtime_composition as runtime_composition,
)
from trusted_authorization.business_entity_source import (  # noqa: E402
    NonProductionBusinessEntityAuthoritySource,
)
from trusted_authorization.entitlement_source import (  # noqa: E402
    NonProductionEntitlementAuthoritySource,
)
from trusted_authorization.membership_source import (  # noqa: E402
    NonProductionMembershipAuthoritySource,
)
from trusted_authorization.non_production_runtime_composition import (  # noqa: E402
    NonProductionTrustedAuthorizationRuntimeComposition,
)
from trusted_authorization.principal_mapping_source import (  # noqa: E402
    NonProductionPrincipalMappingAuthoritySource,
)
from trusted_authorization.resource_identity_source import (  # noqa: E402
    NonProductionResourceIdentityAuthoritySource,
)


PROVIDER = "runtime-composition-provider"
SUBJECT = "subject-alpha"
P1 = "principal-alpha"
P2 = "principal-beta"
B1 = "business-alpha"
B2 = "business-beta"
R1 = "report-alpha"
R2 = "report-beta"
REPORT_REF = "report-alpha-ref"
SUBMISSION_REF = "submission-alpha-ref"
SUBMISSION_R = "submission-alpha"
A_VIEW = RequestedAction.VIEW
A_DOWNLOAD = RequestedAction.DOWNLOAD


def governed_context():
    return GovernedVersionContext(
        authorization_semantics_version=AUTHORIZATION_SEMANTICS_VERSION,
        applicability_governance_version=APPLICABILITY_GOVERNANCE_VERSION,
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


def subject_evidence(subject=SUBJECT):
    return TrustedSubjectEvidence(
        provider=PROVIDER,
        subject=subject,
        verified=True,
    )


def request(resource_reference=REPORT_REF, action=A_VIEW, subject=SUBJECT):
    return AuthorizationRequest(
        subject_evidence=subject_evidence(subject),
        resource_reference=resource_reference,
        requested_action=action,
        governed_version_context=governed_context(),
        correlation_id="non-production-runtime-composition",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


def principal_mapping(
    authority_reference="principal-map-alpha",
    state=AuthorityRecordState.ACTIVE,
    subject=SUBJECT,
    principal_id=P1,
):
    return PrincipalMapping(
        authority_reference=authority_reference,
        state=state,
        subject_provider=PROVIDER,
        subject=subject,
        principal_id=principal_id,
    )


def resource(
    authority_reference="resource-report-alpha",
    state=AuthorityRecordState.ACTIVE,
    resource_id=R1,
    resource_reference=REPORT_REF,
    resource_class=ResourceClass.REPORT,
    business_entity_id=B1,
):
    return GovernedResource(
        authority_reference=authority_reference,
        state=state,
        resource_id=resource_id,
        resource_reference=resource_reference,
        resource_class=resource_class,
        business_entity_id=business_entity_id,
    )


def business_entity(
    authority_reference="business-alpha-authority",
    state=AuthorityRecordState.ACTIVE,
    business_entity_id=B1,
):
    return BusinessEntity(
        authority_reference=authority_reference,
        state=state,
        business_entity_id=business_entity_id,
    )


def membership(
    authority_reference="membership-alpha-business-alpha",
    state=AuthorityRecordState.ACTIVE,
    principal_id=P1,
    business_entity_id=B1,
):
    return Membership(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        business_entity_id=business_entity_id,
    )


def entitlement(
    authority_reference="entitlement-alpha-report-view",
    state=AuthorityRecordState.ACTIVE,
    principal_id=P1,
    business_entity_id=B1,
    resource_id=R1,
    action=A_VIEW,
):
    return Entitlement(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        business_entity_id=business_entity_id,
        resource_id=resource_id,
        action=action,
    )


def composition(
    principal_mappings=None,
    resources=None,
    business_entities=None,
    memberships=None,
    entitlements=None,
):
    if principal_mappings is None:
        principal_mappings = [principal_mapping()]
    if resources is None:
        resources = [resource()]
    if business_entities is None:
        business_entities = [business_entity()]
    if memberships is None:
        memberships = [membership()]
    if entitlements is None:
        entitlements = [entitlement()]

    return NonProductionTrustedAuthorizationRuntimeComposition(
        principal_mappings=principal_mappings,
        resources=resources,
        business_entities=business_entities,
        memberships=memberships,
        entitlements=entitlements,
    )


def evaluate(auth_source=None, auth_request=None):
    evaluator = TrustedAuthorizationEvaluator(auth_source or composition())
    return evaluator.evaluate(auth_request or request())


def method_body(method):
    source = textwrap.dedent(inspect.getsource(method))
    return ast.parse(source).body[0]


def returned_attribute_call(method):
    body = method_body(method)
    returns = [node for node in ast.walk(body) if isinstance(node, ast.Return)]
    if len(returns) != 1:
        return None
    value = returns[0].value
    if not isinstance(value, ast.Call):
        return None
    return value.func


class NonProductionRuntimeCompositionTests(unittest.TestCase):
    def test_exact_construction_uses_accepted_non_production_sources(self):
        auth_source = composition()

        self.assertIs(
            type(auth_source._principal_mapping_source),
            NonProductionPrincipalMappingAuthoritySource,
        )
        self.assertIs(
            type(auth_source._resource_identity_source),
            NonProductionResourceIdentityAuthoritySource,
        )
        self.assertIs(
            type(auth_source._business_entity_source),
            NonProductionBusinessEntityAuthoritySource,
        )
        self.assertIs(
            type(auth_source._membership_source),
            NonProductionMembershipAuthoritySource,
        )
        self.assertIs(
            type(auth_source._entitlement_source),
            NonProductionEntitlementAuthoritySource,
        )
        with self.assertRaises(TypeError):
            NonProductionTrustedAuthorizationRuntimeComposition(
                principal_source=object(),
            )

    def test_valid_allow_chain_preserves_deterministic_audit(self):
        auth_source = composition()

        first = evaluate(auth_source)
        second = evaluate(auth_source)

        self.assertEqual(first, second)
        self.assertEqual(first.decision, AuthorizationDecision.ALLOW)
        self.assertIsNone(first.reason)
        self.assertEqual(first.audit_evidence.principal_id, P1)
        self.assertEqual(first.audit_evidence.business_entity_id, B1)
        self.assertEqual(first.audit_evidence.resource_id, R1)
        self.assertIs(first.audit_evidence.resource_class, ResourceClass.REPORT)
        self.assertIs(first.audit_evidence.requested_action, A_VIEW)
        self.assertIs(
            first.audit_evidence.applicability,
            ResourceActionApplicability.APPLICABLE,
        )
        self.assertEqual(
            first.audit_evidence.authority_inputs,
            (
                "authentication_evidence:verified",
                f"authorization_semantics:{AUTHORIZATION_SEMANTICS_VERSION}",
                f"resource_action_applicability:{APPLICABILITY_GOVERNANCE_VERSION}",
                f"evaluation_context:{BOUNDED_EVALUATION_CONTEXT}",
                "principal_mapping:principal-map-alpha",
                "resource_identity:resource-report-alpha",
                f"resource_action_applicability:{APPLICABILITY_GOVERNANCE_VERSION}",
                "business_entity:business-alpha-authority",
                "membership:membership-alpha-business-alpha",
                "entitlement:entitlement-alpha-report-view",
            ),
        )

    def test_exact_routing_delegates_to_matching_source_without_conversion(self):
        auth_source = composition()
        cases = (
            (
                "principal",
                auth_source.resolve_principal_mapping(PROVIDER, SUBJECT),
                auth_source._principal_mapping_source.resolve_principal_mapping(
                    PROVIDER,
                    SUBJECT,
                ),
            ),
            (
                "resource",
                auth_source.resolve_resource(REPORT_REF),
                auth_source._resource_identity_source.resolve_resource(REPORT_REF),
            ),
            (
                "business",
                auth_source.resolve_business_entity(B1),
                auth_source._business_entity_source.resolve_business_entity(B1),
            ),
            (
                "membership",
                auth_source.resolve_membership(P1, B1),
                auth_source._membership_source.resolve_membership(P1, B1),
            ),
            (
                "entitlement",
                auth_source.resolve_entitlement(P1, B1, R1, A_VIEW),
                auth_source._entitlement_source.resolve_entitlement(
                    P1,
                    B1,
                    R1,
                    A_VIEW,
                ),
            ),
        )
        for label, routed, direct in cases:
            with self.subTest(label=label):
                self.assertEqual(routed, direct)
                self.assertIs(routed.status, AuthorityLookupStatus.FOUND)

        expected_targets = {
            "resolve_principal_mapping": "_principal_mapping_source",
            "resolve_resource": "_resource_identity_source",
            "resolve_business_entity": "_business_entity_source",
            "resolve_membership": "_membership_source",
            "resolve_entitlement": "_entitlement_source",
        }
        for method_name, attribute_name in expected_targets.items():
            with self.subTest(method=method_name):
                method = getattr(
                    NonProductionTrustedAuthorizationRuntimeComposition,
                    method_name,
                )
                body = method_body(method)
                self.assertFalse(any(isinstance(node, ast.Try) for node in ast.walk(body)))
                self.assertFalse(any(isinstance(node, ast.For) for node in ast.walk(body)))
                self.assertFalse(any(isinstance(node, ast.If) for node in ast.walk(body)))
                call = returned_attribute_call(method)
                self.assertIsNotNone(call)
                self.assertIsInstance(call, ast.Attribute)
                self.assertEqual(call.attr, method_name)
                self.assertIsInstance(call.value, ast.Attribute)
                self.assertEqual(call.value.attr, attribute_name)

    def test_empty_evidence_fails_closed_without_default_authority(self):
        auth_source = NonProductionTrustedAuthorizationRuntimeComposition(
            principal_mappings=(),
            resources=(),
            business_entities=(),
            memberships=(),
            entitlements=(),
        )

        result = evaluate(auth_source)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)
        self.assertIn(
            "principal_mapping:NOT_FOUND",
            result.audit_evidence.authority_inputs,
        )
        self.assertNotIn("resource_identity:resource-report-alpha", result.audit_evidence.authority_inputs)

    def test_non_production_containment_has_no_prohibited_runtime_surface(self):
        source = inspect.getsource(runtime_composition)

        self.assertIn("non_production_runtime_composition", runtime_composition.__name__)
        self.assertEqual(
            NonProductionTrustedAuthorizationRuntimeComposition.__name__,
            "NonProductionTrustedAuthorizationRuntimeComposition",
        )
        self.assertFalse(
            hasattr(
                trusted_authorization_package,
                "NonProductionTrustedAuthorizationRuntimeComposition",
            ),
        )
        self.assertNotIn("Local" + "CompositionAuthoritySource", source)
        self.assertNotIn("from tests", source)
        self.assertNotIn("import tests", source)
        self.assertNotIn("os." + "environ", source)
        self.assertNotIn("get" + "env", source)
        self.assertNotIn("bo" + "to3", source)
        self.assertNotIn("bo" + "tocore", source)
        self.assertNotIn("Dynamo" + "DB", source)
        self.assertNotIn("Cog" + "nito", source)
        self.assertNotIn("importlib", source)
        self.assertNotIn("__import__", source)
        self.assertNotIn("lambda_" + "handler", source)
        self.assertNotIn("production=False", source)
        self.assertNotIn("is_production", source)
        self.assertNotIn("registry", source)
        self.assertNotIn("plugin", source)

    def test_applicability_denies_before_matching_entitlement_can_authorize(self):
        auth_source = composition(
            resources=[
                resource(
                    authority_reference="resource-submission-alpha",
                    resource_id=SUBMISSION_R,
                    resource_reference=SUBMISSION_REF,
                    resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
                )
            ],
            entitlements=[entitlement(resource_id=SUBMISSION_R)],
        )

        result = evaluate(auth_source, request(resource_reference=SUBMISSION_REF))

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ACTION_NOT_APPLICABLE)
        self.assertIs(
            result.audit_evidence.applicability,
            ResourceActionApplicability.NOT_APPLICABLE,
        )
        self.assertNotIn(
            "entitlement:entitlement-alpha-report-view",
            result.audit_evidence.authority_inputs,
        )

    def test_upstream_authority_cannot_be_repaired_by_downstream_evidence(self):
        cases = (
            (
                "missing-principal",
                {"principal_mappings": []},
                ReasonCategory.PRINCIPAL_UNRESOLVED,
                "principal_mapping:NOT_FOUND",
            ),
            (
                "missing-resource",
                {"resources": []},
                ReasonCategory.RESOURCE_UNRESOLVED,
                "resource_identity:NOT_FOUND",
            ),
            (
                "stale-business-entity",
                {"business_entities": [business_entity(state=AuthorityRecordState.STALE)]},
                ReasonCategory.STATE_STALE,
                "business_entity:STALE",
            ),
        )
        for label, overrides, reason, audit_input in cases:
            with self.subTest(label=label):
                result = evaluate(composition(**overrides))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, reason)
                self.assertIn(audit_input, result.audit_evidence.authority_inputs)

    def test_missing_or_stale_membership_denies_despite_valid_entitlement(self):
        cases = (
            ("missing", [], ReasonCategory.MEMBERSHIP_INVALID),
            (
                "stale",
                [membership(state=AuthorityRecordState.STALE)],
                ReasonCategory.STATE_STALE,
            ),
        )
        for label, memberships, reason in cases:
            with self.subTest(label=label):
                result = evaluate(composition(memberships=memberships))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, reason)
                self.assertEqual(result.audit_evidence.principal_id, P1)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)
                self.assertNotIn(
                    "entitlement:entitlement-alpha-report-view",
                    result.audit_evidence.authority_inputs,
                )

    def test_business_entity_bridge_and_wrong_membership_identity_deny(self):
        cases = (
            (
                "b1-b2-bridge",
                {
                    "business_entities": [
                        business_entity(),
                        business_entity(business_entity_id=B2),
                    ],
                    "memberships": [membership(business_entity_id=B2)],
                    "entitlements": [entitlement(business_entity_id=B2)],
                },
            ),
            ("wrong-membership-principal", {"memberships": [membership(principal_id=P2)]}),
            ("wrong-membership-business", {"memberships": [membership(business_entity_id=B2)]}),
        )
        for label, overrides in cases:
            with self.subTest(label=label):
                result = evaluate(composition(**overrides))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)
                self.assertEqual(result.audit_evidence.principal_id, P1)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)
                self.assertEqual(result.audit_evidence.resource_id, R1)

    def test_wrong_entitlement_resource_or_action_denies_with_failure_audit(self):
        cases = (
            ("wrong-resource", [entitlement(resource_id=R2)]),
            ("wrong-action", [entitlement(action=A_DOWNLOAD)]),
        )
        for label, entitlements in cases:
            with self.subTest(label=label):
                result = evaluate(composition(entitlements=entitlements))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
                self.assertEqual(result.audit_evidence.principal_id, P1)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)
                self.assertEqual(result.audit_evidence.resource_id, R1)
                self.assertIs(result.audit_evidence.resource_class, ResourceClass.REPORT)
                self.assertIs(result.audit_evidence.requested_action, A_VIEW)
                self.assertIs(
                    result.audit_evidence.applicability,
                    ResourceActionApplicability.APPLICABLE,
                )
                self.assertEqual(
                    result.audit_evidence.authority_inputs[-1],
                    "entitlement:NOT_FOUND",
                )

        auth_source = composition()
        with self.assertRaises(FrozenInstanceError):
            auth_source._entitlement_source = NonProductionEntitlementAuthoritySource(())
        public_methods = {
            name
            for name, value in inspect.getmembers(
                NonProductionTrustedAuthorizationRuntimeComposition,
                inspect.isfunction,
            )
            if not name.startswith("_")
        }
        self.assertEqual(
            public_methods,
            {
                "resolve_principal_mapping",
                "resolve_resource",
                "resolve_business_entity",
                "resolve_membership",
                "resolve_entitlement",
            },
        )


if __name__ == "__main__":
    unittest.main()
