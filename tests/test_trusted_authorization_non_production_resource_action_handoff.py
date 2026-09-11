import ast
import inspect
import sys
import unittest
from enum import Enum
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
    Entitlement,
    GovernedVersionContext,
    GovernedResource,
    Membership,
    PrincipalMapping,
    ReasonCategory,
    RequestedAction,
    ResourceClass,
    TrustedSubjectEvidence,
)
from trusted_authorization.non_production_resource_action_handoff import (
    NonProductionApplicationOperation,
    NonProductionResourceActionHandoffResult,
    NonProductionResourceActionHandoffStatus,
    resolve_non_production_resource_action_handoff,
)
from trusted_authorization.non_production_runtime_composition import (
    NonProductionTrustedAuthorizationRuntimeComposition,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "trusted_authorization"
    / "non_production_resource_action_handoff.py"
)
SUBJECT = TrustedSubjectEvidence(
    provider="non-production-idp",
    subject="subject-alpha",
    verified=True,
)
P1 = "principal-alpha"
B1 = "business-alpha"
R1 = "resource-alpha"
REPORT_REF = "report-alpha-ref"
SUBMISSION_REF = "submission-alpha-ref"


def context() -> GovernedVersionContext:
    return GovernedVersionContext(
        authorization_semantics_version=AUTHORIZATION_SEMANTICS_VERSION,
        applicability_governance_version=APPLICABILITY_GOVERNANCE_VERSION,
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


def request_from_handoff(
    handoff: NonProductionResourceActionHandoffResult,
) -> AuthorizationRequest:
    return AuthorizationRequest(
        subject_evidence=SUBJECT,
        resource_reference=handoff.resource_reference,
        requested_action=handoff.requested_action,
        governed_version_context=context(),
        correlation_id="resource-action-handoff-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


def principal_mapping() -> PrincipalMapping:
    return PrincipalMapping(
        authority_reference="principal-mapping-authority",
        state=AuthorityRecordState.ACTIVE,
        subject_provider=SUBJECT.provider,
        subject=SUBJECT.subject,
        principal_id=P1,
    )


def business_entity() -> BusinessEntity:
    return BusinessEntity(
        authority_reference="business-entity-authority",
        state=AuthorityRecordState.ACTIVE,
        business_entity_id=B1,
    )


def membership() -> Membership:
    return Membership(
        authority_reference="membership-authority",
        state=AuthorityRecordState.ACTIVE,
        principal_id=P1,
        business_entity_id=B1,
    )


def report_resource(reference: str = REPORT_REF) -> GovernedResource:
    return GovernedResource(
        authority_reference="resource-identity-authority",
        state=AuthorityRecordState.ACTIVE,
        resource_id=R1,
        resource_reference=reference,
        resource_class=ResourceClass.REPORT,
        business_entity_id=B1,
    )


def submission_resource(reference: str = SUBMISSION_REF) -> GovernedResource:
    return GovernedResource(
        authority_reference="submission-resource-authority",
        state=AuthorityRecordState.ACTIVE,
        resource_id=R1,
        resource_reference=reference,
        resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
        business_entity_id=B1,
    )


def entitlement(action: RequestedAction = RequestedAction.VIEW) -> Entitlement:
    return Entitlement(
        authority_reference="entitlement-authority",
        state=AuthorityRecordState.ACTIVE,
        principal_id=P1,
        business_entity_id=B1,
        resource_id=R1,
        action=action,
    )


def composition(
    *,
    resources: tuple[GovernedResource, ...] = (report_resource(),),
    entitlements: tuple[Entitlement, ...] = (entitlement(),),
) -> NonProductionTrustedAuthorizationRuntimeComposition:
    return NonProductionTrustedAuthorizationRuntimeComposition(
        principal_mappings=(principal_mapping(),),
        resources=resources,
        business_entities=(business_entity(),),
        memberships=(membership(),),
        entitlements=entitlements,
    )


def evaluate(
    handoff: NonProductionResourceActionHandoffResult,
    authority_source: NonProductionTrustedAuthorizationRuntimeComposition,
):
    return TrustedAuthorizationEvaluator(authority_source).evaluate(
        request_from_handoff(handoff),
    )


class StrSubclass(str):
    pass


class ForeignOperation(Enum):
    VIEW_RESOURCE = "VIEW_RESOURCE"


class NonProductionResourceActionHandoffTest(unittest.TestCase):
    def test_valid_view_handoff_returns_exact_resource_and_action(self):
        result = resolve_non_production_resource_action_handoff(
            resource_reference=REPORT_REF,
            operation=NonProductionApplicationOperation.VIEW_RESOURCE,
        )

        self.assertIsInstance(result, NonProductionResourceActionHandoffResult)
        self.assertIs(result.status, NonProductionResourceActionHandoffStatus.READY)
        self.assertEqual(result.resource_reference, REPORT_REF)
        self.assertIs(result.requested_action, RequestedAction.VIEW)

    def test_multi_action_exact_mapping_preserves_cross_action_isolation(self):
        cases = (
            (
                NonProductionApplicationOperation.VIEW_RESOURCE,
                RequestedAction.VIEW,
                {RequestedAction.DOWNLOAD, RequestedAction.SUBMIT},
            ),
            (
                NonProductionApplicationOperation.DOWNLOAD_RESOURCE,
                RequestedAction.DOWNLOAD,
                {RequestedAction.VIEW, RequestedAction.SUBMIT},
            ),
            (
                NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
                RequestedAction.SUBMIT,
                {RequestedAction.VIEW, RequestedAction.DOWNLOAD},
            ),
        )

        for operation, expected_action, forbidden_actions in cases:
            with self.subTest(operation=operation):
                result = resolve_non_production_resource_action_handoff(
                    resource_reference="resource-for-action-test",
                    operation=operation,
                )

                self.assertIs(result.status, NonProductionResourceActionHandoffStatus.READY)
                self.assertIs(result.requested_action, expected_action)
                self.assertNotIn(result.requested_action, forbidden_actions)

    def test_exact_resource_preservation_has_no_normalization_or_substitution(self):
        cases = (
            "Report.Ref-001",
            "client:Alpha.resource/report_2026",
            "MIXED.Case:Resource-42",
        )

        for resource_reference in cases:
            with self.subTest(resource_reference=resource_reference):
                result = resolve_non_production_resource_action_handoff(
                    resource_reference=resource_reference,
                    operation=NonProductionApplicationOperation.DOWNLOAD_RESOURCE,
                )

                self.assertIs(result.status, NonProductionResourceActionHandoffStatus.READY)
                self.assertEqual(result.resource_reference, resource_reference)
                self.assertNotEqual(result.resource_reference, resource_reference.lower())
                self.assertNotEqual(result.resource_reference, "resource-for-action-test")
                self.assertIs(result.requested_action, RequestedAction.DOWNLOAD)

    def test_invalid_resource_reference_fails_without_resource_or_action_pair(self):
        cases = (
            "",
            " ",
            " resource-alpha",
            "resource-alpha ",
            123,
            None,
            StrSubclass("resource-alpha"),
        )

        for resource_reference in cases:
            with self.subTest(resource_reference=repr(resource_reference)):
                result = resolve_non_production_resource_action_handoff(
                    resource_reference=resource_reference,
                    operation=NonProductionApplicationOperation.VIEW_RESOURCE,
                )

                self.assertIs(result.status, NonProductionResourceActionHandoffStatus.INVALID)
                self.assertIsNone(result.resource_reference)
                self.assertIsNone(result.requested_action)

    def test_invalid_operation_fails_without_default_action(self):
        cases = (
            "VIEW_RESOURCE",
            "view",
            RequestedAction.VIEW,
            None,
            object(),
            ForeignOperation.VIEW_RESOURCE,
        )

        for operation in cases:
            with self.subTest(operation=repr(operation)):
                result = resolve_non_production_resource_action_handoff(
                    resource_reference=REPORT_REF,
                    operation=operation,
                )

                self.assertIs(result.status, NonProductionResourceActionHandoffStatus.INVALID)
                self.assertIsNone(result.resource_reference)
                self.assertIsNone(result.requested_action)

    def test_public_api_accepts_no_authority_bearing_inputs_or_action_override(self):
        signature = inspect.signature(resolve_non_production_resource_action_handoff)

        self.assertEqual(
            tuple(signature.parameters),
            ("resource_reference", "operation"),
        )
        for parameter in signature.parameters.values():
            self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)

        forbidden_inputs = {
            "requested_action",
            "principal",
            "principal_id",
            "subject",
            "business_entity",
            "business_entity_id",
            "resource_class",
            "membership",
            "entitlement",
            "permission",
            "role",
            "scope",
            "admin",
            "owner",
            "context",
            "provider",
            "route",
            "http_method",
            "mapping",
            "registry",
            "callback",
        }
        self.assertTrue(forbidden_inputs.isdisjoint(signature.parameters))

    def test_resource_reference_is_not_governed_resource_authority(self):
        handoff = resolve_non_production_resource_action_handoff(
            resource_reference="unknown-resource-ref",
            operation=NonProductionApplicationOperation.VIEW_RESOURCE,
        )

        result = evaluate(handoff, composition(resources=()))

        self.assertIs(result.decision, AuthorizationDecision.DENY)
        self.assertIs(result.reason, ReasonCategory.RESOURCE_UNRESOLVED)
        self.assertEqual(result.audit_evidence.principal_id, P1)
        self.assertIsNone(result.audit_evidence.resource_id)
        self.assertIs(result.audit_evidence.requested_action, RequestedAction.VIEW)

    def test_requested_action_is_not_entitlement(self):
        handoff = resolve_non_production_resource_action_handoff(
            resource_reference=REPORT_REF,
            operation=NonProductionApplicationOperation.VIEW_RESOURCE,
        )

        result = evaluate(handoff, composition(entitlements=()))

        self.assertIs(result.decision, AuthorizationDecision.DENY)
        self.assertIs(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
        self.assertEqual(result.audit_evidence.principal_id, P1)
        self.assertEqual(result.audit_evidence.business_entity_id, B1)
        self.assertEqual(result.audit_evidence.resource_id, R1)
        self.assertIs(result.audit_evidence.requested_action, RequestedAction.VIEW)

    def test_applicability_remains_downstream_from_handoff(self):
        handoff = resolve_non_production_resource_action_handoff(
            resource_reference=SUBMISSION_REF,
            operation=NonProductionApplicationOperation.VIEW_RESOURCE,
        )

        result = evaluate(
            handoff,
            composition(
                resources=(submission_resource(),),
                entitlements=(entitlement(RequestedAction.VIEW),),
            ),
        )

        self.assertIs(result.decision, AuthorizationDecision.DENY)
        self.assertIs(result.reason, ReasonCategory.ACTION_NOT_APPLICABLE)
        self.assertEqual(result.audit_evidence.principal_id, P1)
        self.assertEqual(result.audit_evidence.business_entity_id, B1)
        self.assertEqual(result.audit_evidence.resource_id, R1)
        self.assertIs(result.audit_evidence.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(result.audit_evidence.requested_action, RequestedAction.VIEW)

    def test_structural_non_production_containment_has_no_runtime_authority_surface(self):
        module = __import__(
            "trusted_authorization.non_production_resource_action_handoff",
            fromlist=["unused"],
        )
        module_source = MODULE_PATH.read_text()
        tree = ast.parse(module_source)

        public_names = {
            name
            for name in dir(module)
            if not name.startswith("_")
        }
        self.assertEqual(
            public_names,
            {
                "NonProductionApplicationOperation",
                "NonProductionResourceActionHandoffResult",
                "NonProductionResourceActionHandoffStatus",
                "resolve_non_production_resource_action_handoff",
            },
        )
        self.assertIn("non_production", module.__name__)
        self.assertNotIn(
            "NonProductionApplicationOperation",
            __import__("trusted_authorization").__all__,
        )

        imported_modules = {
            alias.name
            for node in tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
        }
        self.assertEqual(
            imported_modules,
            {
                "dataclasses",
                "enum",
                "trusted_authorization.models",
            },
        )

        forbidden_calls = {
            "AuthorizationRequest",
            "TrustedAuthorizationEvaluator",
            "resolve_applicability",
            "getattr",
            "open",
        }
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(forbidden_calls.isdisjoint(called_names))

        forbidden_terms = (
            "boto",
            "Cognito",
            "DynamoDB",
            "os.environ",
            "getenv",
            "handler",
            "lambda",
            "Bedrock",
            "LLM",
            "MCP",
            "registry",
            "plugin",
            "loader",
            "factory",
            "callback",
            "production=False",
            "mode=",
            "ALLOW",
            "DENY",
        )
        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, module_source)


if __name__ == "__main__":
    unittest.main()
