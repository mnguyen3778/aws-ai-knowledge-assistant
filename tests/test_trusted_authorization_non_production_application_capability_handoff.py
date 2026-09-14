import ast
import dataclasses
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
    GovernedResource,
    GovernedVersionContext,
    Membership,
    PrincipalMapping,
    ReasonCategory,
    RequestedAction,
    ResourceClass,
    TrustedSubjectEvidence,
)
from trusted_authorization.non_production_application_capability_handoff import (
    NonProductionApplicationCapability,
    NonProductionApplicationCapabilityHandoffResult,
    NonProductionApplicationCapabilityHandoffStatus,
    resolve_non_production_application_capability_handoff,
)
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionApplicationOperationSelectionStatus,
    NonProductionProtectedApplicationOperation,
    resolve_non_production_application_operation_selection,
)
from trusted_authorization.non_production_resource_action_handoff import (
    NonProductionApplicationOperation,
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
    / "non_production_application_capability_handoff.py"
)
SUBJECT = TrustedSubjectEvidence(
    provider="non-production-idp",
    subject="subject-alpha",
    verified=True,
)
P1 = "principal-alpha"
B1 = "business-alpha"
R1 = "resource-alpha"
SUBMISSION_REF = "submission-alpha-ref"


def resolve(value: object) -> NonProductionApplicationCapabilityHandoffResult:
    return resolve_non_production_application_capability_handoff(
        application_capability=value,
    )


def assert_invalid(
    testcase: unittest.TestCase,
    value: object,
) -> None:
    result = resolve(value)

    testcase.assertIs(
        result.status,
        NonProductionApplicationCapabilityHandoffStatus.INVALID,
    )
    testcase.assertIsNone(result.protected_operation)


def context() -> GovernedVersionContext:
    return GovernedVersionContext(
        authorization_semantics_version=AUTHORIZATION_SEMANTICS_VERSION,
        applicability_governance_version=APPLICABILITY_GOVERNANCE_VERSION,
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


def submission_resource() -> GovernedResource:
    return GovernedResource(
        authority_reference="submission-resource-authority",
        state=AuthorityRecordState.ACTIVE,
        resource_id=R1,
        resource_reference=SUBMISSION_REF,
        resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
        business_entity_id=B1,
    )


def composition() -> NonProductionTrustedAuthorizationRuntimeComposition:
    return NonProductionTrustedAuthorizationRuntimeComposition(
        principal_mappings=(principal_mapping(),),
        resources=(submission_resource(),),
        business_entities=(business_entity(),),
        memberships=(membership(),),
        entitlements=(),
    )


def request_from_resource_action_handoff(handoff) -> AuthorizationRequest:
    return AuthorizationRequest(
        subject_evidence=SUBJECT,
        resource_reference=handoff.resource_reference,
        requested_action=handoff.requested_action,
        governed_version_context=context(),
        correlation_id="application-capability-handoff-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


class ForeignApplicationCapability(Enum):
    ASSESSMENT_SUBMISSION = "ASSESSMENT_SUBMISSION"


class CapabilityDuck:
    name = "ASSESSMENT_SUBMISSION"
    value = "ASSESSMENT_SUBMISSION"


class PrincipalLike:
    principal_id = P1


class RoleLike:
    role = "admin"


class AILikeAssertion:
    content = "this is an assessment submission"


class AwsIamLike:
    arn = "arn:aws:iam::123456789012:role/ApplicationRole"


class HandlerLike:
    __name__ = "handle_assessment"


class RequestLike:
    assessmentVersion = "nguyen-ai-readiness-v1"
    answers = {"canonical.question.id": 3}


class NonProductionApplicationCapabilityHandoffTests(unittest.TestCase):
    def test_valid_core_maps_application_capability_to_layer_two_operation(self):
        result = resolve(NonProductionApplicationCapability.ASSESSMENT_SUBMISSION)

        self.assertIsInstance(result, NonProductionApplicationCapabilityHandoffResult)
        self.assertIs(
            result.status,
            NonProductionApplicationCapabilityHandoffStatus.READY,
        )
        self.assertIs(
            result.protected_operation,
            NonProductionProtectedApplicationOperation.
            PROTECTED_ASSESSMENT_SUBMISSION,
        )

    def test_layer_one_catalog_contains_exactly_assessment_submission(self):
        self.assertEqual(
            tuple(NonProductionApplicationCapability),
            (NonProductionApplicationCapability.ASSESSMENT_SUBMISSION,),
        )
        self.assertFalse(hasattr(NonProductionApplicationCapability, "VIEW_REPORT"))
        self.assertFalse(hasattr(NonProductionApplicationCapability, "DOWNLOAD_REPORT"))
        self.assertFalse(hasattr(NonProductionApplicationCapability, "ASSISTANT"))
        self.assertFalse(hasattr(NonProductionApplicationCapability, "EXPLAIN"))
        self.assertFalse(hasattr(NonProductionApplicationCapability, "UNKNOWN"))
        self.assertFalse(hasattr(NonProductionApplicationCapability, "DEFAULT"))

    def test_successful_mapping_universe_contains_only_assessment_submission(self):
        ready_outputs = {
            resolve(capability).protected_operation
            for capability in NonProductionApplicationCapability
            if resolve(capability).status
            is NonProductionApplicationCapabilityHandoffStatus.READY
        }

        self.assertEqual(
            ready_outputs,
            {
                NonProductionProtectedApplicationOperation.
                PROTECTED_ASSESSMENT_SUBMISSION,
            },
        )

    def test_raw_route_strings_fail_closed(self):
        for value in ("/assessment", "/v1/assistant", "/report/alpha"):
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_http_method_strings_fail_closed(self):
        for value in ("POST", "GET", "PUT", "DELETE"):
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_route_method_structures_fail_closed(self):
        cases = (
            {"route": "/assessment", "method": "POST"},
            {"path": "/assessment", "httpMethod": "POST"},
            {"rawPath": "/assessment", "requestContext": {"http": {"method": "POST"}}},
        )

        for value in cases:
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_request_body_and_request_like_values_fail_closed(self):
        cases = (
            {
                "assessmentVersion": "nguyen-ai-readiness-v1",
                "organization": {},
                "respondent": {},
                "answers": {"canonical.question.id": 3},
            },
            {
                "assessmentVersion": "nguyen-ai-readiness-v1",
                "organization": {},
                "respondent": {},
                "answers": [
                    {"questionId": "canonical.question.id", "value": 3},
                ],
            },
            RequestLike(),
        )

        for value in cases:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_layer_two_direct_bypass_fails_closed(self):
        assert_invalid(
            self,
            NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION,
        )

    def test_layer_three_direct_bypass_fails_closed(self):
        assert_invalid(self, NonProductionApplicationOperation.SUBMIT_ASSESSMENT)

    def test_requested_action_bypass_fails_closed(self):
        assert_invalid(self, RequestedAction.SUBMIT)

    def test_foreign_enum_duck_and_subclass_like_values_fail_closed(self):
        with self.assertRaises((TypeError, ValueError)):
            NonProductionApplicationCapability(
                "ASSESSMENT_SUBMISSION",
                {"OTHER": "OTHER"},
            )

        cases = (
            ForeignApplicationCapability.ASSESSMENT_SUBMISSION,
            CapabilityDuck(),
            "ASSESSMENT_SUBMISSION",
            "PROTECTED_ASSESSMENT_SUBMISSION",
            "SUBMIT_ASSESSMENT",
            None,
            True,
            False,
            1,
            object(),
        )

        for value in cases:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_role_ai_aws_and_subject_laundering_inputs_fail_closed(self):
        cases = (
            "admin",
            "owner",
            RoleLike(),
            "AI says this request is assessment submission",
            AILikeAssertion(),
            "arn:aws:iam::123456789012:role/ApplicationRole",
            AwsIamLike(),
            TrustedSubjectEvidence(
                provider="non-production-idp",
                subject="subject-alpha",
                verified=True,
            ),
            PrincipalLike(),
            HandlerLike(),
        )

        for value in cases:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_api_accepts_only_application_capability_keyword(self):
        signature = inspect.signature(
            resolve_non_production_application_capability_handoff
        )
        self.assertEqual(tuple(signature.parameters), ("application_capability",))
        for parameter in signature.parameters.values():
            self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)

        unexpected_keywords = {
            "route": "/assessment",
            "method": "POST",
            "request_body": {},
            "protected_operation": (
                NonProductionProtectedApplicationOperation.
                PROTECTED_ASSESSMENT_SUBMISSION
            ),
            "operation": NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
            "requested_action": RequestedAction.SUBMIT,
            "role": "admin",
            "subject": "subject-alpha",
            "provider": "non-production-idp",
        }
        for keyword, value in unexpected_keywords.items():
            with self.subTest(keyword=keyword):
                with self.assertRaises(TypeError):
                    resolve_non_production_application_capability_handoff(
                        **{keyword: value}
                    )

    def test_existing_selector_composes_after_layer_one_handoff(self):
        handoff = resolve(NonProductionApplicationCapability.ASSESSMENT_SUBMISSION)
        selection = resolve_non_production_application_operation_selection(
            protected_operation=handoff.protected_operation,
        )

        self.assertIs(
            handoff.status,
            NonProductionApplicationCapabilityHandoffStatus.READY,
        )
        self.assertIs(
            selection.status,
            NonProductionApplicationOperationSelectionStatus.READY,
        )
        self.assertIs(
            selection.selected_application_operation,
            NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
        )

    def test_operation_provenance_does_not_authorize_without_entitlement(self):
        capability_handoff = resolve(
            NonProductionApplicationCapability.ASSESSMENT_SUBMISSION
        )
        selection = resolve_non_production_application_operation_selection(
            protected_operation=capability_handoff.protected_operation,
        )
        resource_action = resolve_non_production_resource_action_handoff(
            resource_reference=SUBMISSION_REF,
            operation=selection.selected_application_operation,
        )
        result = TrustedAuthorizationEvaluator(composition()).evaluate(
            request_from_resource_action_handoff(resource_action),
        )

        self.assertIs(
            capability_handoff.status,
            NonProductionApplicationCapabilityHandoffStatus.READY,
        )
        self.assertIs(
            selection.status,
            NonProductionApplicationOperationSelectionStatus.READY,
        )
        self.assertIs(
            resource_action.status,
            NonProductionResourceActionHandoffStatus.READY,
        )
        self.assertIs(result.decision, AuthorizationDecision.DENY)
        self.assertIs(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
        self.assertEqual(result.audit_evidence.principal_id, P1)
        self.assertEqual(result.audit_evidence.business_entity_id, B1)
        self.assertEqual(result.audit_evidence.resource_id, R1)
        self.assertIs(result.audit_evidence.requested_action, RequestedAction.SUBMIT)

    def test_structural_containment_and_documentation_preserve_authority_boundary(self):
        module = __import__(
            "trusted_authorization.non_production_application_capability_handoff",
            fromlist=["unused"],
        )
        module_source = MODULE_PATH.read_text()
        tree = ast.parse(module_source)

        public_names = {name for name in dir(module) if not name.startswith("_")}
        self.assertEqual(
            public_names,
            {
                "NonProductionApplicationCapability",
                "NonProductionApplicationCapabilityHandoffResult",
                "NonProductionApplicationCapabilityHandoffStatus",
                "resolve_non_production_application_capability_handoff",
            },
        )
        self.assertIn("already-legitimate application capability fact", module_source)
        self.assertIn("does not prove", module_source)
        self.assertIn("real runtime request", module_source)
        self.assertNotIn(
            "NonProductionApplicationCapability",
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
                "trusted_authorization.non_production_application_operation_selection",
            },
        )

        forbidden_calls = {
            "getattr",
            "open",
            "resolve_non_production_application_operation_selection",
            "resolve_non_production_resource_action_handoff",
            "TrustedAuthorizationEvaluator",
            "AuthorizationRequest",
            "RequestedAction",
        }
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(forbidden_calls.isdisjoint(called_names))

        forbidden_terms = (
            "lambda",
            "handler",
            "handle_assessment",
            "/assessment",
            "POST",
            "request_body",
            "AssessmentRequest",
            "TrustedSubjectEvidence",
            "PrincipalMapping",
            "GovernedResource",
            "BusinessEntity",
            "Membership",
            "Entitlement",
            "GovernedVersionContext",
            "RequestedAction",
            "NonProductionApplicationOperation.SUBMIT_ASSESSMENT",
            "AuthorizationDecision",
            "ALLOW",
            "DENY",
            "boto",
            "botocore",
            "Cognito",
            "jwt",
            "JWKS",
            "Bedrock",
            "LLM",
            "MCP",
            "registry",
            "config",
            "os.environ",
            "getenv",
        )
        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, module_source)


if __name__ == "__main__":
    unittest.main()
