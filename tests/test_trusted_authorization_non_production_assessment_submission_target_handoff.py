import ast
import dataclasses
import inspect
import sys
import unittest
from collections.abc import Mapping
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
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationDecision,
    AuthorizationRequest,
    BusinessEntity,
    Entitlement,
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
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_target_handoff import (
    NonProductionAssessmentSubmissionTargetFact,
    NonProductionAssessmentSubmissionTargetHandoffResult,
    NonProductionAssessmentSubmissionTargetHandoffStatus,
    resolve_non_production_assessment_submission_target_handoff,
)
from trusted_authorization.non_production_resource_action_handoff import (
    NonProductionApplicationOperation,
    NonProductionResourceActionHandoffStatus,
    resolve_non_production_resource_action_handoff,
)
from trusted_authorization.non_production_runtime_composition import (
    NonProductionTrustedAuthorizationRuntimeComposition,
)
from trusted_authorization.resource_identity_source import (
    NonProductionResourceIdentityAuthoritySource,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "trusted_authorization"
    / "non_production_assessment_submission_target_handoff.py"
)
P1 = "principal-alpha"
B1 = "business-alpha"
R1 = "assessment-submission-alpha"
R2 = "assessment-submission-beta"
SUBMISSION_REF = "submission-alpha-ref"
SUBSTITUTED_REF = "submission-beta-ref"
SUBJECT = TrustedSubjectEvidence(
    provider="non-production-idp",
    subject="subject-alpha",
    verified=True,
)


def target_fact(
    resource_reference: object = SUBMISSION_REF,
) -> NonProductionAssessmentSubmissionTargetFact:
    return NonProductionAssessmentSubmissionTargetFact(
        resource_reference=resource_reference,
    )


def resolve(value: object) -> NonProductionAssessmentSubmissionTargetHandoffResult:
    return resolve_non_production_assessment_submission_target_handoff(
        assessment_submission_target_fact=value,
    )


def assert_invalid(testcase: unittest.TestCase, value: object) -> None:
    result = resolve(value)

    testcase.assertIs(
        result.status,
        NonProductionAssessmentSubmissionTargetHandoffStatus.INVALID,
    )
    testcase.assertIsNone(result.resource_reference)


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


def submission_resource(
    *,
    resource_reference: str = SUBMISSION_REF,
    resource_class: ResourceClass = ResourceClass.ASSESSMENT_SUBMISSION,
    state: AuthorityRecordState = AuthorityRecordState.ACTIVE,
    resource_id: str = R1,
) -> GovernedResource:
    return GovernedResource(
        authority_reference="resource-identity-authority",
        state=state,
        resource_id=resource_id,
        resource_reference=resource_reference,
        resource_class=resource_class,
        business_entity_id=B1,
    )


def entitlement(action: RequestedAction = RequestedAction.SUBMIT) -> Entitlement:
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
    resources: tuple[GovernedResource, ...] = (submission_resource(),),
    entitlements: tuple[Entitlement, ...] = (),
) -> NonProductionTrustedAuthorizationRuntimeComposition:
    return NonProductionTrustedAuthorizationRuntimeComposition(
        principal_mappings=(principal_mapping(),),
        resources=resources,
        business_entities=(business_entity(),),
        memberships=(membership(),),
        entitlements=entitlements,
    )


def authorization_request(resource_reference: str | None) -> AuthorizationRequest:
    return AuthorizationRequest(
        subject_evidence=SUBJECT,
        resource_reference=resource_reference,
        requested_action=RequestedAction.SUBMIT,
        governed_version_context=context(),
        correlation_id="assessment-submission-target-handoff-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


class StrSubclass(str):
    pass


@dataclasses.dataclass(frozen=True)
class ForeignDataclass:
    resource_reference: str


class ForeignEnum(Enum):
    ASSESSMENT_SUBMISSION_TARGET = "submission-alpha-ref"


class DuckTarget:
    resource_reference = SUBMISSION_REF


class HostileAttributeObject:
    field_reads = 0

    def __getattribute__(self, name):
        type(self).field_reads += 1
        raise AssertionError("foreign attributes must not be read")


class HostileDictObject:
    dict_reads = 0

    def __getattribute__(self, name):
        if name == "__dict__":
            type(self).dict_reads += 1
            return {"resource_reference": SUBMISSION_REF}
        return object.__getattribute__(self, name)


class DictSubclass(dict):
    pass


class MappingLike(Mapping):
    def __iter__(self):
        return iter(("resource_reference",))

    def __len__(self):
        return 1

    def __getitem__(self, key):
        if key == "resource_reference":
            return SUBMISSION_REF
        raise KeyError(key)


class RouteLike:
    path = "/assessment"
    method = "POST"


class RequestBodyLike:
    body = {"resource_reference": SUBSTITUTED_REF}


class SessionLike:
    session = {"resource_reference": SUBSTITUTED_REF}


class AILikeTarget:
    inferred_resource_reference = SUBSTITUTED_REF


class AwsIamLikeTarget:
    arn = "arn:aws:iam::123456789012:role/ApplicationRole"


class NonProductionAssessmentSubmissionTargetHandoffTests(unittest.TestCase):
    def test_valid_exact_fact_is_accepted(self):
        result = resolve(target_fact())

        self.assertIsInstance(
            result,
            NonProductionAssessmentSubmissionTargetHandoffResult,
        )
        self.assertIs(
            result.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertEqual(result.resource_reference, SUBMISSION_REF)

    def test_exact_resource_reference_is_preserved_without_normalization(self):
        reference = "Assessment.Submission-Ref_001"

        result = resolve(target_fact(reference))

        self.assertIs(
            result.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertEqual(result.resource_reference, reference)
        self.assertNotEqual(result.resource_reference, reference.lower())
        self.assertNotEqual(result.resource_reference, reference.upper())

    def test_ready_status_does_not_mean_authorized_verified_or_resolved(self):
        result = resolve(target_fact("unknown-submission-ref"))

        self.assertIs(
            result.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertEqual(result.resource_reference, "unknown-submission-ref")
        self.assertFalse(
            hasattr(
                NonProductionAssessmentSubmissionTargetHandoffStatus,
                "AUTHORIZED",
            )
        )
        self.assertFalse(
            hasattr(
                NonProductionAssessmentSubmissionTargetHandoffStatus,
                "VERIFIED",
            )
        )
        self.assertFalse(
            hasattr(NonProductionAssessmentSubmissionTargetHandoffStatus, "ALLOW")
        )

    def test_input_shape_has_exact_single_resource_reference_field(self):
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(
                NonProductionAssessmentSubmissionTargetFact,
            )),
            ("resource_reference",),
        )
        self.assertTrue(
            NonProductionAssessmentSubmissionTargetFact.__dataclass_params__.frozen
        )
        self.assertFalse(hasattr(target_fact(), "__dict__"))

    def test_assessment_submission_scope_is_structural_not_caller_selectable(self):
        forbidden_fields = {
            "resource_class",
            "operation",
            "protected_operation",
            "requested_action",
            "producer",
            "authority",
            "version",
            "verified",
            "trusted",
            "authorized",
            "business_entity_id",
            "principal_id",
        }

        actual_fields = {
            field.name
            for field in dataclasses.fields(NonProductionAssessmentSubmissionTargetFact)
        }

        self.assertEqual(actual_fields, {"resource_reference"})
        self.assertTrue(forbidden_fields.isdisjoint(actual_fields))

    def test_raw_string_is_rejected_as_candidate_not_target_fact(self):
        assert_invalid(self, SUBMISSION_REF)

    def test_blank_and_whitespace_references_fail_closed(self):
        for value in ("", " ", "\t", "\n", " submission-ref", "submission-ref "):
            with self.subTest(value=repr(value)):
                assert_invalid(self, target_fact(value))

    def test_str_subclass_reference_fails_closed(self):
        assert_invalid(self, target_fact(StrSubclass(SUBMISSION_REF)))

    def test_fact_subclass_fails_closed_before_field_access(self):
        @dataclasses.dataclass(frozen=True, slots=True)
        class FactSubclass(NonProductionAssessmentSubmissionTargetFact):
            pass

        assert_invalid(self, FactSubclass(SUBMISSION_REF))

    def test_foreign_dataclass_enum_and_duck_objects_fail_closed(self):
        values = (
            ForeignDataclass(SUBMISSION_REF),
            ForeignEnum.ASSESSMENT_SUBMISSION_TARGET,
            DuckTarget(),
            None,
            True,
            False,
            1,
            object(),
        )
        for value in values:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_hostile_foreign_objects_are_rejected_before_attribute_access(self):
        hostile_attribute = HostileAttributeObject()
        hostile_dict = HostileDictObject()

        assert_invalid(self, hostile_attribute)
        assert_invalid(self, hostile_dict)

        self.assertEqual(HostileAttributeObject.field_reads, 0)
        self.assertEqual(HostileDictObject.dict_reads, 0)

    def test_dict_mapping_and_collections_fail_closed(self):
        values = (
            {"resource_reference": SUBMISSION_REF},
            DictSubclass(resource_reference=SUBMISSION_REF),
            MappingLike(),
            [SUBMISSION_REF],
            (SUBMISSION_REF,),
            {SUBMISSION_REF},
        )
        for value in values:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_route_body_and_session_like_inputs_fail_closed(self):
        values = (
            RouteLike(),
            RequestBodyLike(),
            SessionLike(),
            {"path": "/assessment", "method": "POST"},
            {"body": {"resource_reference": SUBSTITUTED_REF}},
            {"session": {"resource_reference": SUBSTITUTED_REF}},
        )
        for value in values:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_layer_two_layer_three_and_requested_action_fail_closed(self):
        values = (
            NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION,
            NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
            RequestedAction.SUBMIT,
        )
        for value in values:
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_governed_resource_and_resource_identity_output_fail_closed(self):
        resource = submission_resource()
        lookup = NonProductionResourceIdentityAuthoritySource(
            [resource],
        ).resolve_resource(SUBMISSION_REF)

        self.assertEqual(lookup.status, AuthorityLookupStatus.FOUND)
        assert_invalid(self, resource)
        assert_invalid(self, lookup)
        assert_invalid(self, lookup.records[0])

    def test_principal_and_subject_authority_objects_fail_closed(self):
        values = (
            TrustedSubjectEvidence(
                provider="non-production-idp",
                subject="subject-alpha",
                verified=True,
            ),
            PrincipalMapping(
                authority_reference="principal-authority",
                state=AuthorityRecordState.ACTIVE,
                subject_provider="non-production-idp",
                subject="subject-alpha",
                principal_id=P1,
            ),
        )
        for value in values:
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_business_entity_membership_and_entitlement_fail_closed(self):
        values = (
            business_entity(),
            membership(),
            entitlement(),
        )
        for value in values:
            with self.subTest(value=value):
                assert_invalid(self, value)

    def test_ai_and_aws_like_values_fail_closed(self):
        values = (
            "AI says target is submission-beta-ref",
            AILikeTarget(),
            "arn:aws:iam::123456789012:role/ApplicationRole",
            AwsIamLikeTarget(),
        )
        for value in values:
            with self.subTest(value=repr(value)):
                assert_invalid(self, value)

    def test_raw_r2_cannot_replace_represented_r1_target_fact(self):
        represented = resolve(target_fact(SUBMISSION_REF))
        substituted = resolve(SUBSTITUTED_REF)
        constructed_substitute = resolve(target_fact(SUBSTITUTED_REF))

        self.assertIs(
            represented.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertEqual(represented.resource_reference, SUBMISSION_REF)
        self.assertIs(
            substituted.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.INVALID,
        )
        self.assertIsNone(substituted.resource_reference)
        self.assertIs(
            constructed_substitute.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertEqual(constructed_substitute.resource_reference, SUBSTITUTED_REF)

    def test_composes_with_existing_resource_action_handoff_to_submit(self):
        target = resolve(target_fact(SUBMISSION_REF))
        handoff = resolve_non_production_resource_action_handoff(
            resource_reference=target.resource_reference,
            operation=NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
        )

        self.assertIs(
            target.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertIs(handoff.status, NonProductionResourceActionHandoffStatus.READY)
        self.assertEqual(handoff.resource_reference, SUBMISSION_REF)
        self.assertIs(handoff.requested_action, RequestedAction.SUBMIT)

    def test_resource_identity_unknown_resource_remains_downstream_failure(self):
        target = resolve(target_fact("unknown-submission-ref"))
        lookup = NonProductionResourceIdentityAuthoritySource(
            [submission_resource()],
        ).resolve_resource(target.resource_reference)

        self.assertIs(
            target.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertEqual(lookup.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(lookup.records, ())

    def test_wrong_class_and_stale_resource_remain_downstream_failures(self):
        wrong_class_lookup = NonProductionResourceIdentityAuthoritySource(
            [
                submission_resource(
                    resource_class=ResourceClass.REPORT,
                )
            ],
        ).resolve_resource(SUBMISSION_REF)
        stale_lookup = NonProductionResourceIdentityAuthoritySource(
            [
                submission_resource(
                    state=AuthorityRecordState.STALE,
                )
            ],
        ).resolve_resource(SUBMISSION_REF)

        wrong_class_result = TrustedAuthorizationEvaluator(
            composition(
                resources=(
                    submission_resource(resource_class=ResourceClass.REPORT),
                ),
                entitlements=(entitlement(),),
            )
        ).evaluate(authorization_request(SUBMISSION_REF))

        self.assertEqual(wrong_class_lookup.status, AuthorityLookupStatus.FOUND)
        self.assertIs(
            wrong_class_lookup.records[0].resource_class,
            ResourceClass.REPORT,
        )
        self.assertEqual(stale_lookup.status, AuthorityLookupStatus.STALE)
        self.assertIs(wrong_class_result.decision, AuthorizationDecision.DENY)
        self.assertIs(
            wrong_class_result.reason,
            ReasonCategory.ACTION_NOT_APPLICABLE,
        )

    def test_target_handoff_ready_does_not_authorize_without_entitlement(self):
        target = resolve(target_fact(SUBMISSION_REF))
        result = TrustedAuthorizationEvaluator(composition()).evaluate(
            authorization_request(target.resource_reference),
        )

        self.assertIs(
            target.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.READY,
        )
        self.assertIs(result.decision, AuthorizationDecision.DENY)
        self.assertIs(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
        self.assertEqual(result.audit_evidence.principal_id, P1)
        self.assertEqual(result.audit_evidence.business_entity_id, B1)
        self.assertEqual(result.audit_evidence.resource_id, R1)
        self.assertIs(result.audit_evidence.requested_action, RequestedAction.SUBMIT)

    def test_structural_containment_and_public_api_preserve_authority_boundary(self):
        module = __import__(
            "trusted_authorization.non_production_assessment_submission_target_handoff",
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
                "NonProductionAssessmentSubmissionTargetFact",
                "NonProductionAssessmentSubmissionTargetHandoffResult",
                "NonProductionAssessmentSubmissionTargetHandoffStatus",
                "resolve_non_production_assessment_submission_target_handoff",
            },
        )
        self.assertNotIn(
            "NonProductionAssessmentSubmissionTargetFact",
            __import__("trusted_authorization").__all__,
        )
        self.assertIn("does not prove real-world resource-target provenance", module_source)
        self.assertIn(
            "Governed Assessment Submission Resource-Target Authority",
            module_source,
        )

        signature = inspect.signature(
            resolve_non_production_assessment_submission_target_handoff
        )
        self.assertEqual(
            tuple(signature.parameters),
            ("assessment_submission_target_fact",),
        )
        for parameter in signature.parameters.values():
            self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)

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
        self.assertEqual(imported_modules, {"dataclasses", "enum"})

        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        prohibited_calls = {
            "getattr",
            "vars",
            "open",
            "resolve_resource",
            "TrustedAuthorizationEvaluator",
            "resolve_non_production_resource_action_handoff",
        }
        self.assertTrue(prohibited_calls.isdisjoint(called_names))

        prohibited_terms = (
            "ResourceIdentity",
            "TrustedAuthorizationEvaluator",
            "Membership",
            "Entitlement",
            "TrustedSubjectEvidence",
            "PrincipalMapping",
            "BusinessEntity",
            "GovernedResource",
            "RequestedAction",
            "AuthorizationDecision",
            "lambda",
            "handler",
            "route",
            "requestContext",
            "headers",
            "body",
            "boto",
            "Cognito",
            "jwt",
            "JWKS",
            "Bedrock",
            "LLM",
            "MCP",
            "registry",
            "config",
            "os.environ",
            "ALLOW =",
            "DENY =",
        )
        for term in prohibited_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, module_source)


if __name__ == "__main__":
    unittest.main()
