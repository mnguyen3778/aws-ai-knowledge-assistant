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
from trusted_authorization.non_production_application_operation_selection import (
    NonProductionApplicationOperationSelectionResult,
    NonProductionApplicationOperationSelectionStatus,
    NonProductionProtectedApplicationOperation,
    resolve_non_production_application_operation_selection,
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
    / "non_production_application_operation_selection.py"
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
        correlation_id="application-operation-selection-test",
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


def select_assessment_submission() -> NonProductionApplicationOperationSelectionResult:
    return resolve_non_production_application_operation_selection(
        protected_operation=(
            NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
        ),
    )


def invalid_selection(value: object) -> NonProductionApplicationOperationSelectionResult:
    return resolve_non_production_application_operation_selection(
        protected_operation=value,
    )


class ForeignProtectedOperation(Enum):
    PROTECTED_ASSESSMENT_SUBMISSION = "PROTECTED_ASSESSMENT_SUBMISSION"


class EnumLikeOperation:
    name = "PROTECTED_ASSESSMENT_SUBMISSION"
    value = "PROTECTED_ASSESSMENT_SUBMISSION"


class NonProductionApplicationOperationSelectionTest(unittest.TestCase):
    def test_valid_selection_returns_submit_assessment_operation(self):
        result = select_assessment_submission()

        self.assertIsInstance(result, NonProductionApplicationOperationSelectionResult)
        self.assertIs(
            result.status,
            NonProductionApplicationOperationSelectionStatus.READY,
        )
        self.assertIs(
            result.selected_application_operation,
            NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
        )
        self.assertNotIsInstance(result.selected_application_operation, RequestedAction)

    def test_layer_two_catalog_contains_only_protected_assessment_submission(self):
        self.assertEqual(
            tuple(NonProductionProtectedApplicationOperation),
            (
                NonProductionProtectedApplicationOperation.
                PROTECTED_ASSESSMENT_SUBMISSION,
            ),
        )
        self.assertFalse(
            hasattr(NonProductionProtectedApplicationOperation, "PROTECTED_VIEW_RESOURCE")
        )
        self.assertFalse(
            hasattr(
                NonProductionProtectedApplicationOperation,
                "PROTECTED_DOWNLOAD_RESOURCE",
            )
        )
        self.assertFalse(
            hasattr(NonProductionProtectedApplicationOperation, "ASSISTANT")
        )
        self.assertFalse(
            hasattr(NonProductionProtectedApplicationOperation, "EXPLAIN")
        )

    def test_external_strings_and_transport_values_fail_closed(self):
        cases = (
            "PROTECTED_ASSESSMENT_SUBMISSION",
            "SUBMIT_ASSESSMENT",
            "SUBMIT",
            "/assessment",
            "POST",
            "VIEW_RESOURCE",
            "DOWNLOAD_RESOURCE",
            "/v1/assistant",
        )

        for value in cases:
            with self.subTest(value=value):
                result = invalid_selection(value)

                self.assertIs(
                    result.status,
                    NonProductionApplicationOperationSelectionStatus.INVALID,
                )
                self.assertIsNone(result.selected_application_operation)

    def test_layer_three_and_requested_action_values_fail_closed(self):
        cases = tuple(NonProductionApplicationOperation) + tuple(RequestedAction)

        for value in cases:
            with self.subTest(value=value):
                result = invalid_selection(value)

                self.assertIs(
                    result.status,
                    NonProductionApplicationOperationSelectionStatus.INVALID,
                )
                self.assertIsNone(result.selected_application_operation)

    def test_foreign_enum_duck_type_and_malformed_values_fail_closed(self):
        cases = (
            None,
            True,
            1,
            b"SUBMIT",
            [],
            {},
            object(),
            ForeignProtectedOperation.PROTECTED_ASSESSMENT_SUBMISSION,
            EnumLikeOperation(),
        )

        for value in cases:
            with self.subTest(value=repr(value)):
                result = invalid_selection(value)

                self.assertIs(
                    result.status,
                    NonProductionApplicationOperationSelectionStatus.INVALID,
                )
                self.assertIsNone(result.selected_application_operation)

    def test_failure_result_shape_and_public_api_have_no_authority_inputs(self):
        result = invalid_selection(object())

        self.assertIs(
            result.status,
            NonProductionApplicationOperationSelectionStatus.INVALID,
        )
        self.assertIsNone(result.selected_application_operation)
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(result)),
            ("status", "selected_application_operation"),
        )

        signature = inspect.signature(
            resolve_non_production_application_operation_selection
        )
        self.assertEqual(tuple(signature.parameters), ("protected_operation",))
        for parameter in signature.parameters.values():
            self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)

        forbidden_inputs = {
            "resource_reference",
            "resource_id",
            "requested_action",
            "action",
            "subject",
            "principal",
            "context",
            "route",
            "path",
            "http_method",
            "method",
            "provider",
            "model",
            "ai",
            "role",
            "rbac",
            "membership",
            "entitlement",
            "mapping",
            "registry",
        }
        self.assertTrue(forbidden_inputs.isdisjoint(signature.parameters))

    def test_selection_composes_with_resource_action_handoff_to_submit_only(self):
        selection = select_assessment_submission()
        handoff = resolve_non_production_resource_action_handoff(
            resource_reference=SUBMISSION_REF,
            operation=selection.selected_application_operation,
        )

        self.assertIs(
            selection.status,
            NonProductionApplicationOperationSelectionStatus.READY,
        )
        self.assertIs(
            selection.selected_application_operation,
            NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
        )
        self.assertIs(
            handoff.status,
            NonProductionResourceActionHandoffStatus.READY,
        )
        self.assertIs(handoff.requested_action, RequestedAction.SUBMIT)
        self.assertIsNot(
            selection.selected_application_operation,
            NonProductionApplicationOperation.VIEW_RESOURCE,
        )
        self.assertIsNot(
            selection.selected_application_operation,
            NonProductionApplicationOperation.DOWNLOAD_RESOURCE,
        )

    def test_valid_selection_does_not_create_permission(self):
        selection = select_assessment_submission()
        handoff = resolve_non_production_resource_action_handoff(
            resource_reference=SUBMISSION_REF,
            operation=selection.selected_application_operation,
        )
        result = TrustedAuthorizationEvaluator(composition()).evaluate(
            request_from_handoff(handoff),
        )

        self.assertIs(
            selection.status,
            NonProductionApplicationOperationSelectionStatus.READY,
        )
        self.assertIs(
            handoff.status,
            NonProductionResourceActionHandoffStatus.READY,
        )
        self.assertIs(result.decision, AuthorizationDecision.DENY)
        self.assertIs(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
        self.assertEqual(result.audit_evidence.principal_id, P1)
        self.assertEqual(result.audit_evidence.business_entity_id, B1)
        self.assertEqual(result.audit_evidence.resource_id, R1)
        self.assertIs(
            result.audit_evidence.resource_class,
            ResourceClass.ASSESSMENT_SUBMISSION,
        )
        self.assertIs(result.audit_evidence.requested_action, RequestedAction.SUBMIT)

    def test_structural_non_production_containment_has_no_runtime_authority_surface(self):
        module = __import__(
            "trusted_authorization.non_production_application_operation_selection",
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
                "NonProductionApplicationOperationSelectionResult",
                "NonProductionApplicationOperationSelectionStatus",
                "NonProductionProtectedApplicationOperation",
                "resolve_non_production_application_operation_selection",
            },
        )
        self.assertIn("non_production", module.__name__)
        self.assertNotIn(
            "NonProductionProtectedApplicationOperation",
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
                "trusted_authorization.non_production_resource_action_handoff",
            },
        )

        forbidden_calls = {
            "resolve_non_production_resource_action_handoff",
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
            "RequestedAction",
            "resource_reference",
            "TrustedSubjectEvidence",
            "AuthorizationRequest",
            "TrustedAuthorizationEvaluator",
            "NonProductionTrustedAuthorizationRuntimeComposition",
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
            "ALLOW",
            "DENY",
            "VIEW_RESOURCE",
            "DOWNLOAD_RESOURCE",
        )
        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, module_source)

        ready_outputs = {
            resolve_non_production_application_operation_selection(
                protected_operation=protected_operation,
            ).selected_application_operation
            for protected_operation in NonProductionProtectedApplicationOperation
        }
        self.assertEqual(
            ready_outputs,
            {NonProductionApplicationOperation.SUBMIT_ASSESSMENT},
        )


if __name__ == "__main__":
    unittest.main()
