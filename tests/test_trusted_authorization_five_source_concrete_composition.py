import inspect
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
from trusted_authorization.business_entity_source import (  # noqa: E402
    NonProductionBusinessEntityAuthoritySource,
)
from trusted_authorization.entitlement_source import (  # noqa: E402
    NonProductionEntitlementAuthoritySource,
)
from trusted_authorization.membership_source import (  # noqa: E402
    NonProductionMembershipAuthoritySource,
)
from trusted_authorization.principal_mapping_source import (  # noqa: E402
    NonProductionPrincipalMappingAuthoritySource,
)
from trusted_authorization.resource_identity_source import (  # noqa: E402
    NonProductionResourceIdentityAuthoritySource,
)


PROVIDER = "five-source-provider"
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


class FiveSourceConcreteAuthority:
    __slots__ = (
        "principal_source",
        "resource_source",
        "business_entity_source",
        "membership_source",
        "entitlement_source",
    )

    def __init__(
        self,
        principal_source,
        resource_source,
        business_entity_source,
        membership_source,
        entitlement_source,
    ):
        self.principal_source = principal_source
        self.resource_source = resource_source
        self.business_entity_source = business_entity_source
        self.membership_source = membership_source
        self.entitlement_source = entitlement_source

    def resolve_principal_mapping(self, subject_provider, subject):
        return self.principal_source.resolve_principal_mapping(
            subject_provider,
            subject,
        )

    def resolve_resource(self, resource_reference):
        return self.resource_source.resolve_resource(resource_reference)

    def resolve_business_entity(self, business_entity_id):
        return self.business_entity_source.resolve_business_entity(
            business_entity_id,
        )

    def resolve_membership(self, principal_id, business_entity_id):
        return self.membership_source.resolve_membership(
            principal_id,
            business_entity_id,
        )

    def resolve_entitlement(
        self,
        principal_id,
        business_entity_id,
        resource_id,
        action,
    ):
        return self.entitlement_source.resolve_entitlement(
            principal_id,
            business_entity_id,
            resource_id,
            action,
        )


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
        correlation_id="five-source-composition",
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


def malformed_membership():
    record = object.__new__(Membership)
    object.__setattr__(record, "authority_reference", "malformed-membership")
    object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
    object.__setattr__(record, "principal_id", P1)
    return record


def malformed_entitlement():
    record = object.__new__(Entitlement)
    object.__setattr__(record, "authority_reference", "malformed-entitlement")
    object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
    object.__setattr__(record, "principal_id", P1)
    object.__setattr__(record, "business_entity_id", B1)
    object.__setattr__(record, "resource_id", R1)
    return record


def authority(
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

    return FiveSourceConcreteAuthority(
        NonProductionPrincipalMappingAuthoritySource(principal_mappings),
        NonProductionResourceIdentityAuthoritySource(resources),
        NonProductionBusinessEntityAuthoritySource(business_entities),
        NonProductionMembershipAuthoritySource(memberships),
        NonProductionEntitlementAuthoritySource(entitlements),
    )


def evaluate(auth_source=None, auth_request=None):
    evaluator = TrustedAuthorizationEvaluator(auth_source or authority())
    return evaluator.evaluate(auth_request or request())


class FiveSourceConcreteCompositionTests(unittest.TestCase):
    def test_full_five_source_allow_with_deterministic_audit(self):
        auth_source = authority()
        first = evaluate(auth_source)
        second = evaluate(auth_source)

        self.assertEqual(first.decision, AuthorizationDecision.ALLOW)
        self.assertIsNone(first.reason)
        self.assertEqual(first, second)
        self.assertEqual(first.audit_evidence.principal_id, P1)
        self.assertEqual(first.audit_evidence.business_entity_id, B1)
        self.assertEqual(first.audit_evidence.resource_id, R1)
        self.assertEqual(first.audit_evidence.resource_class, ResourceClass.REPORT)
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

    def test_routing_only_adapter_delegates_each_category(self):
        auth_source = authority()
        cases = (
            (
                "principal",
                auth_source.resolve_principal_mapping(PROVIDER, SUBJECT),
                auth_source.principal_source.resolve_principal_mapping(
                    PROVIDER,
                    SUBJECT,
                ),
            ),
            (
                "resource",
                auth_source.resolve_resource(REPORT_REF),
                auth_source.resource_source.resolve_resource(REPORT_REF),
            ),
            (
                "business",
                auth_source.resolve_business_entity(B1),
                auth_source.business_entity_source.resolve_business_entity(B1),
            ),
            (
                "membership",
                auth_source.resolve_membership(P1, B1),
                auth_source.membership_source.resolve_membership(P1, B1),
            ),
            (
                "entitlement",
                auth_source.resolve_entitlement(P1, B1, R1, A_VIEW),
                auth_source.entitlement_source.resolve_entitlement(P1, B1, R1, A_VIEW),
            ),
        )

        for label, routed, direct in cases:
            with self.subTest(label=label):
                self.assertEqual(routed, direct)
                self.assertIs(routed.status, AuthorityLookupStatus.FOUND)

        router_source = inspect.getsource(FiveSourceConcreteAuthority)
        self.assertNotIn("AuthorityLookupResult", router_source)
        self.assertNotIn("for ", router_source)
        self.assertNotIn("try:", router_source)
        self.assertIn("return self.principal_source.resolve_principal_mapping", router_source)
        self.assertIn("return self.resource_source.resolve_resource", router_source)
        self.assertIn("return self.business_entity_source.resolve_business_entity", router_source)
        self.assertIn("return self.membership_source.resolve_membership", router_source)
        self.assertIn("return self.entitlement_source.resolve_entitlement", router_source)

    def test_applicability_blocks_otherwise_matching_entitlement(self):
        auth_source = authority(
            resources=[
                resource(
                    authority_reference="resource-submission-alpha",
                    resource_id=SUBMISSION_R,
                    resource_reference=SUBMISSION_REF,
                    resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
                    business_entity_id=B1,
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

    def test_missing_principal_cannot_be_repaired_downstream(self):
        auth_source = authority(principal_mappings=[])

        result = evaluate(auth_source)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)
        self.assertIn(
            "principal_mapping:NOT_FOUND",
            result.audit_evidence.authority_inputs,
        )
        self.assertNotIn(
            "membership:membership-alpha-business-alpha",
            result.audit_evidence.authority_inputs,
        )

    def test_missing_resource_cannot_be_repaired_downstream(self):
        auth_source = authority(resources=[])

        result = evaluate(auth_source)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.RESOURCE_UNRESOLVED)
        self.assertEqual(result.audit_evidence.principal_id, P1)
        self.assertIn("resource_identity:NOT_FOUND", result.audit_evidence.authority_inputs)
        self.assertNotIn(
            "business_entity:business-alpha-authority",
            result.audit_evidence.authority_inputs,
        )

    def test_business_entity_failure_cannot_be_repaired_downstream(self):
        cases = (
            ("missing", [], ReasonCategory.BUSINESS_ENTITY_INVALID),
            (
                "stale",
                [business_entity(state=AuthorityRecordState.STALE)],
                ReasonCategory.STATE_STALE,
            ),
        )
        for label, business_entities, reason in cases:
            with self.subTest(label=label):
                result = evaluate(authority(business_entities=business_entities))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, reason)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)
                self.assertNotIn(
                    "membership:membership-alpha-business-alpha",
                    result.audit_evidence.authority_inputs,
                )

    def test_missing_or_stale_membership_with_valid_entitlement_denies(self):
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
                result = evaluate(authority(memberships=memberships))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, reason)
                self.assertNotIn(
                    "entitlement:entitlement-alpha-report-view",
                    result.audit_evidence.authority_inputs,
                )

    def test_missing_or_stale_entitlement_with_valid_upstream_denies(self):
        cases = (
            ("missing", [], ReasonCategory.ENTITLEMENT_MISSING),
            (
                "stale",
                [entitlement(state=AuthorityRecordState.STALE)],
                ReasonCategory.STATE_STALE,
            ),
        )
        for label, entitlements, reason in cases:
            with self.subTest(label=label):
                result = evaluate(authority(entitlements=entitlements))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, reason)
                self.assertEqual(result.audit_evidence.principal_id, P1)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)
                self.assertEqual(result.audit_evidence.resource_id, R1)

    def test_wrong_membership_principal_or_business_entity_denies(self):
        cases = (
            ("wrong-principal", [membership(principal_id=P2)]),
            ("wrong-business", [membership(business_entity_id=B2)]),
        )
        for label, memberships in cases:
            with self.subTest(label=label):
                result = evaluate(authority(memberships=memberships))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)
                self.assertEqual(result.audit_evidence.principal_id, P1)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)

    def test_wrong_entitlement_identity_denies(self):
        cases = (
            ("wrong-principal", [entitlement(principal_id=P2)]),
            ("wrong-business", [entitlement(business_entity_id=B2)]),
            ("wrong-resource", [entitlement(resource_id=R2)]),
            ("wrong-action", [entitlement(action=A_DOWNLOAD)]),
        )
        for label, entitlements in cases:
            with self.subTest(label=label):
                result = evaluate(authority(entitlements=entitlements))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
                self.assertEqual(result.audit_evidence.principal_id, P1)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)
                self.assertEqual(result.audit_evidence.resource_id, R1)

    def test_b1_resource_cannot_bridge_b2_membership_or_entitlement(self):
        auth_source = authority(
            business_entities=[business_entity(), business_entity(business_entity_id=B2)],
            memberships=[membership(business_entity_id=B2)],
            entitlements=[entitlement(business_entity_id=B2)],
        )

        result = evaluate(auth_source)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)
        self.assertEqual(result.audit_evidence.business_entity_id, B1)
        self.assertEqual(result.audit_evidence.resource_id, R1)
        self.assertIn("membership:NOT_FOUND", result.audit_evidence.authority_inputs)

    def test_bad_membership_evidence_denies_despite_valid_entitlement(self):
        cases = (
            ("ambiguous", [membership(), membership()], ReasonCategory.AUTHORIZATION_CONFLICT),
            (
                "conflicting",
                [membership(), membership(authority_reference="membership-conflict")],
                ReasonCategory.AUTHORIZATION_CONFLICT,
            ),
            (
                "malformed",
                [membership(), malformed_membership()],
                ReasonCategory.UNKNOWN_STATE,
            ),
        )
        for label, memberships, reason in cases:
            with self.subTest(label=label):
                result = evaluate(authority(memberships=memberships))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, reason)
                self.assertNotIn(
                    "entitlement:entitlement-alpha-report-view",
                    result.audit_evidence.authority_inputs,
                )

    def test_bad_entitlement_evidence_denies(self):
        cases = (
            ("ambiguous", [entitlement(), entitlement()], ReasonCategory.AUTHORIZATION_CONFLICT),
            (
                "conflicting",
                [entitlement(), entitlement(authority_reference="entitlement-conflict")],
                ReasonCategory.AUTHORIZATION_CONFLICT,
            ),
            (
                "malformed",
                [entitlement(), malformed_entitlement()],
                ReasonCategory.UNKNOWN_STATE,
            ),
        )
        for label, entitlements, reason in cases:
            with self.subTest(label=label):
                result = evaluate(authority(entitlements=entitlements))

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, reason)
                self.assertEqual(result.audit_evidence.principal_id, P1)
                self.assertEqual(result.audit_evidence.business_entity_id, B1)

    def test_representative_failure_audit_integrity(self):
        result = evaluate(authority(entitlements=[entitlement(action=A_DOWNLOAD)]))

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
        self.assertEqual(result.audit_evidence.authority_inputs[-1], "entitlement:NOT_FOUND")

    def test_no_fixture_fallback_or_runtime_surface_is_present(self):
        module_source = Path(__file__).read_text(encoding="utf-8")
        router_source = inspect.getsource(FiveSourceConcreteAuthority)
        forbidden_runtime_terms = (
            "bo" + "to3",
            "Dynamo" + "DB",
            "Cog" + "nito",
            "os." + "environ",
            "sub" + "process",
            "requests" + ".",
        )

        self.assertIn("NonProductionPrincipalMappingAuthoritySource", module_source)
        self.assertIn("NonProductionResourceIdentityAuthoritySource", module_source)
        self.assertIn("NonProductionBusinessEntityAuthoritySource", module_source)
        self.assertIn("NonProductionMembershipAuthoritySource", module_source)
        self.assertIn("NonProductionEntitlementAuthoritySource", module_source)
        self.assertNotIn("Local" + "CompositionAuthoritySource", module_source)
        self.assertNotIn("Fixture" + "AuthoritySource", module_source)
        harness_module = "test_trusted_authorization_" + "local_integration_harness"
        self.assertNotIn(harness_module, module_source)
        self.assertNotIn("TrustedAuthorizationEvaluator" + "._", module_source)
        self.assertNotIn("setattr(" + "TrustedAuthorizationEvaluator", module_source)
        self.assertNotIn("setattr(" + "NonProduction", module_source)
        for term in forbidden_runtime_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, module_source)
        self.assertNotIn("AuthorityLookupResult", router_source)
        self.assertNotIn("AuthorizationDecision", router_source)
        self.assertNotIn("resolve_applicability", router_source)


if __name__ == "__main__":
    unittest.main()
