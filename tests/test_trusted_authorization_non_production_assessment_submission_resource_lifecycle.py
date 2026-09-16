import dataclasses
import sys
import unittest
from collections.abc import Mapping
from dataclasses import FrozenInstanceError, dataclass
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trusted_authorization.applicability import (  # noqa: E402
    APPLICABILITY_GOVERNANCE_VERSION,
)
from trusted_authorization.evaluator import (  # noqa: E402
    AUTHORIZATION_SEMANTICS_VERSION,
    BOUNDED_EVALUATION_CONTEXT,
    TrustedAuthorizationEvaluator,
)
from trusted_authorization.models import (  # noqa: E402
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
    ResourceClass,
    TrustedSubjectEvidence,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionAssessmentSubmissionLifecycleState,
    NonProductionAssessmentSubmissionResourceEstablishmentResult,
    NonProductionAssessmentSubmissionResourceEstablishmentStatus,
    NonProductionAssessmentSubmissionResourceReferenceAllocation,
    NonProductionGovernedAssessmentSubmissionBusinessContext,
    NonProductionProvisionalAssessmentSubmissionResourceFact,
    establish_non_production_provisional_assessment_submission_resource,
)
from trusted_authorization.non_production_assessment_submission_target_handoff import (  # noqa: E402
    NonProductionAssessmentSubmissionTargetFact,
    NonProductionAssessmentSubmissionTargetHandoffStatus,
    resolve_non_production_assessment_submission_target_handoff,
)
from trusted_authorization.non_production_resource_action_handoff import (  # noqa: E402
    NonProductionApplicationOperation,
)
from trusted_authorization.non_production_runtime_composition import (  # noqa: E402
    NonProductionTrustedAuthorizationRuntimeComposition,
)
from trusted_authorization.resource_identity_source import (  # noqa: E402
    NonProductionResourceIdentityAuthoritySource,
)


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "trusted_authorization"
    / "non_production_assessment_submission_resource_lifecycle.py"
)

R1 = "assessment-submission-alpha"
R2 = "assessment-submission-beta"
B1 = "business-alpha"
B2 = "business-beta"
P1 = "principal-alpha"
SUBJECT = TrustedSubjectEvidence(
    provider="non-production-auth",
    subject="subject-alpha",
    verified=True,
)


def business_context(
    business_entity_id: str = B1,
) -> NonProductionGovernedAssessmentSubmissionBusinessContext:
    return NonProductionGovernedAssessmentSubmissionBusinessContext(
        business_entity_id=business_entity_id,
    )


def allocation(
    resource_reference: str = R1,
) -> NonProductionAssessmentSubmissionResourceReferenceAllocation:
    return NonProductionAssessmentSubmissionResourceReferenceAllocation(
        resource_reference=resource_reference,
    )


def establish(
    *,
    business_context_value: object = None,
    allocation_value: object = None,
) -> NonProductionAssessmentSubmissionResourceEstablishmentResult:
    return establish_non_production_provisional_assessment_submission_resource(
        business_context=(
            business_context()
            if business_context_value is None
            else business_context_value
        ),
        resource_reference_allocation=(
            allocation()
            if allocation_value is None
            else allocation_value
        ),
    )


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


def business_entity(business_entity_id: str = B1) -> BusinessEntity:
    return BusinessEntity(
        authority_reference="business-entity-authority",
        state=AuthorityRecordState.ACTIVE,
        business_entity_id=business_entity_id,
    )


def membership(business_entity_id: str = B1) -> Membership:
    return Membership(
        authority_reference="membership-authority",
        state=AuthorityRecordState.ACTIVE,
        principal_id=P1,
        business_entity_id=business_entity_id,
    )


def entitlement(
    *,
    business_entity_id: str = B1,
    resource_id: str = R1,
) -> Entitlement:
    return Entitlement(
        authority_reference="entitlement-authority",
        state=AuthorityRecordState.ACTIVE,
        principal_id=P1,
        business_entity_id=business_entity_id,
        resource_id=resource_id,
        action=RequestedAction.SUBMIT,
    )


def authorization_request(resource_reference: str = R1) -> AuthorizationRequest:
    return AuthorizationRequest(
        subject_evidence=SUBJECT,
        resource_reference=resource_reference,
        requested_action=RequestedAction.SUBMIT,
        governed_version_context=context(),
        correlation_id="assessment-submission-resource-lifecycle-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


def composition(
    *,
    resources: tuple[GovernedResource, ...],
    business_entities: tuple[BusinessEntity, ...] = (business_entity(),),
    memberships: tuple[Membership, ...] = (membership(),),
    entitlements: tuple[Entitlement, ...] = (),
) -> NonProductionTrustedAuthorizationRuntimeComposition:
    return NonProductionTrustedAuthorizationRuntimeComposition(
        principal_mappings=(principal_mapping(),),
        resources=resources,
        business_entities=business_entities,
        memberships=memberships,
        entitlements=entitlements,
    )


class StrSubclass(str):
    pass


@dataclass(frozen=True)
class ForeignBusinessContext:
    business_entity_id: str


@dataclass(frozen=True)
class ForeignAllocation:
    resource_reference: str


class BusinessContextSubclass(NonProductionGovernedAssessmentSubmissionBusinessContext):
    pass


class AllocationSubclass(NonProductionAssessmentSubmissionResourceReferenceAllocation):
    pass


class ForeignMapping(Mapping):
    def __iter__(self):
        return iter(("business_entity_id",))

    def __len__(self):
        return 1

    def __getitem__(self, key):
        if key == "business_entity_id":
            return B1
        raise KeyError(key)


class HostileAttributeObject:
    field_reads = 0

    def __getattribute__(self, name):
        type(self).field_reads += 1
        raise AssertionError("foreign attributes must not be read")


class HostilePropertyBusinessContext:
    @property
    def business_entity_id(self):
        raise AssertionError("duck property must not be read")


class AwsLikeObject:
    arn = "arn:aws:iam::123456789012:role/Admin"


class AiLikeObject:
    content = "AI says this context is valid"


class ForeignEnum(Enum):
    ASSESSMENT_SUBMISSION = "assessment-submission"


class NonProductionAssessmentSubmissionResourceLifecycleTests(unittest.TestCase):
    def test_valid_inputs_return_ready(self):
        result = establish()

        self.assertIs(
            result.status,
            NonProductionAssessmentSubmissionResourceEstablishmentStatus.READY,
        )
        self.assertIsNotNone(result.provisional_resource)
        self.assertIsNotNone(result.resource_identity_record)
        self.assertIs(
            type(result.provisional_resource),
            NonProductionProvisionalAssessmentSubmissionResourceFact,
        )
        self.assertIs(type(result.resource_identity_record), GovernedResource)

    def test_resource_reference_is_preserved_without_normalization(self):
        result = establish(allocation_value=allocation("Assessment.Submission:Alpha_1"))

        self.assertEqual(
            result.provisional_resource.resource_reference,
            "Assessment.Submission:Alpha_1",
        )
        self.assertEqual(
            result.resource_identity_record.resource_reference,
            "Assessment.Submission:Alpha_1",
        )

    def test_business_entity_id_is_preserved_without_normalization(self):
        result = establish(business_context_value=business_context("Business.Alpha_1"))

        self.assertEqual(result.provisional_resource.business_entity_id, "Business.Alpha_1")
        self.assertEqual(result.resource_identity_record.business_entity_id, "Business.Alpha_1")

    def test_resource_class_is_fixed_to_assessment_submission(self):
        result = establish()

        self.assertIs(result.provisional_resource.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(result.resource_identity_record.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)

    def test_lifecycle_is_fixed_to_provisional(self):
        result = establish()

        self.assertIs(
            result.provisional_resource.lifecycle_state,
            NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL,
        )

    def test_registration_evidence_state_is_active_currentness_not_business_lifecycle(self):
        result = establish()

        self.assertIs(result.resource_identity_record.state, AuthorityRecordState.ACTIVE)
        self.assertNotIn("PROVISIONAL", AuthorityRecordState.__members__)

    def test_repeated_success_returns_fresh_outputs_with_equal_values(self):
        first = establish()
        second = establish()

        self.assertEqual(first, second)
        self.assertIsNot(first.provisional_resource, second.provisional_resource)
        self.assertIsNot(first.resource_identity_record, second.resource_identity_record)

    def test_raw_business_entity_string_is_rejected(self):
        result = establish(business_context_value=B1)

        self.assert_invalid(result)

    def test_business_context_dict_and_mapping_are_rejected(self):
        for value in ({"business_entity_id": B1}, ForeignMapping()):
            with self.subTest(value=type(value).__name__):
                self.assert_invalid(establish(business_context_value=value))

    def test_foreign_business_context_dataclass_is_rejected(self):
        result = establish(business_context_value=ForeignBusinessContext(B1))

        self.assert_invalid(result)

    def test_business_context_subclass_is_rejected(self):
        result = establish(business_context_value=BusinessContextSubclass(B1))

        self.assert_invalid(result)

    def test_business_entity_domain_object_is_rejected_as_context(self):
        result = establish(business_context_value=business_entity())

        self.assert_invalid(result)

    def test_principal_like_input_is_rejected_as_context(self):
        result = establish(business_context_value=principal_mapping())

        self.assert_invalid(result)

    def test_membership_entitlement_and_subject_are_rejected_as_context(self):
        for value in (membership(), entitlement(), SUBJECT):
            with self.subTest(value=type(value).__name__):
                self.assert_invalid(establish(business_context_value=value))

    def test_raw_resource_reference_string_is_rejected(self):
        result = establish(allocation_value=R1)

        self.assert_invalid(result)

    def test_allocation_dict_and_mapping_are_rejected(self):
        for value in ({"resource_reference": R1}, ForeignMapping()):
            with self.subTest(value=type(value).__name__):
                self.assert_invalid(establish(allocation_value=value))

    def test_foreign_allocation_dataclass_is_rejected(self):
        result = establish(allocation_value=ForeignAllocation(R1))

        self.assert_invalid(result)

    def test_allocation_subclass_is_rejected(self):
        result = establish(allocation_value=AllocationSubclass(R1))

        self.assert_invalid(result)

    def test_target_fact_is_rejected_as_allocation(self):
        result = establish(
            allocation_value=NonProductionAssessmentSubmissionTargetFact(
                resource_reference=R1,
            ),
        )

        self.assert_invalid(result)

    def test_route_body_session_operation_and_action_are_rejected_as_allocation(self):
        values = (
            {"path": "/assessment", "method": "POST"},
            {"body": {"assessmentVersion": "nguyen-ai-readiness-v1"}},
            {"session": "assessment-session"},
            RequestedAction.SUBMIT,
            NonProductionApplicationOperation.SUBMIT_ASSESSMENT,
            NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION,
        )
        for value in values:
            with self.subTest(value=repr(value)):
                self.assert_invalid(establish(allocation_value=value))

    def test_invalid_business_context_strings_fail_closed(self):
        cases = ("", " ", "   ", "\t", "\n", " B1", "B1 ", StrSubclass("B1"), 7, None)
        for value in cases:
            with self.subTest(value=repr(value)):
                self.assert_invalid(
                    establish(business_context_value=business_context(value)),
                )

    def test_invalid_resource_reference_strings_fail_closed(self):
        cases = ("", " ", "   ", "\t", "\n", " R1", "R1 ", StrSubclass("R1"), 7, None)
        for value in cases:
            with self.subTest(value=repr(value)):
                self.assert_invalid(establish(allocation_value=allocation(value)))

    def test_aws_and_ai_like_objects_are_rejected(self):
        for value in (AwsLikeObject(), AiLikeObject(), ForeignEnum.ASSESSMENT_SUBMISSION):
            with self.subTest(value=type(value).__name__):
                self.assert_invalid(establish(business_context_value=value))
                self.assert_invalid(establish(allocation_value=value))

    def test_hostile_foreign_objects_are_rejected_before_attribute_access(self):
        for argument in ("business_context_value", "allocation_value"):
            hostile = HostileAttributeObject()
            HostileAttributeObject.field_reads = 0
            result = establish(**{argument: hostile})

            self.assert_invalid(result)
            self.assertEqual(HostileAttributeObject.field_reads, 0)

    def test_duck_properties_do_not_cross_business_context_boundary(self):
        result = establish(business_context_value=HostilePropertyBusinessContext())

        self.assert_invalid(result)

    def test_output_types_are_frozen_and_slotted(self):
        result = establish()

        self.assertFalse(hasattr(result, "__dict__"))
        self.assertFalse(hasattr(result.provisional_resource, "__dict__"))
        with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
            result.provisional_resource.resource_reference = R2

    def test_mutating_inputs_after_success_does_not_change_outputs(self):
        context_value = business_context()
        allocation_value = allocation()
        result = establish(
            business_context_value=context_value,
            allocation_value=allocation_value,
        )

        object.__setattr__(context_value, "business_entity_id", B2)
        object.__setattr__(allocation_value, "resource_reference", R2)

        self.assertEqual(result.provisional_resource.business_entity_id, B1)
        self.assertEqual(result.provisional_resource.resource_reference, R1)
        self.assertEqual(result.resource_identity_record.business_entity_id, B1)
        self.assertEqual(result.resource_identity_record.resource_reference, R1)

    def test_resource_identity_source_resolves_registration_evidence(self):
        result = establish()
        source = NonProductionResourceIdentityAuthoritySource(
            [result.resource_identity_record],
        )

        lookup = source.resolve_resource(R1)

        self.assertEqual(lookup.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(lookup.records[0].resource_reference, R1)
        self.assertIs(lookup.records[0].resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertEqual(lookup.records[0].business_entity_id, B1)

    def test_unknown_resource_has_no_fallback_registration(self):
        result = establish()
        source = NonProductionResourceIdentityAuthoritySource(
            [result.resource_identity_record],
        )

        lookup = source.resolve_resource(R2)

        self.assertEqual(lookup.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(lookup.records, ())

    def test_duplicate_or_conflicting_registration_fails_closed_in_resource_identity(self):
        first = establish().resource_identity_record
        second = establish(allocation_value=allocation(R1), business_context_value=business_context(B2)).resource_identity_record
        source = NonProductionResourceIdentityAuthoritySource([first, second])

        lookup = source.resolve_resource(R1)

        self.assertEqual(lookup.status, AuthorityLookupStatus.CONFLICTING)

    def test_resource_existence_and_resolution_do_not_create_permission(self):
        result = establish()
        evaluator = TrustedAuthorizationEvaluator(
            composition(resources=(result.resource_identity_record,)),
        )

        authorization = evaluator.evaluate(authorization_request(R1))

        self.assertIs(authorization.decision, AuthorizationDecision.DENY)
        self.assertIs(authorization.reason, ReasonCategory.ENTITLEMENT_MISSING)

    def test_provisional_resource_does_not_satisfy_target_handoff(self):
        result = establish()

        provisional_target_result = resolve_non_production_assessment_submission_target_handoff(
            assessment_submission_target_fact=result.provisional_resource,
        )
        record_target_result = resolve_non_production_assessment_submission_target_handoff(
            assessment_submission_target_fact=result.resource_identity_record,
        )

        self.assertIs(
            provisional_target_result.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.INVALID,
        )
        self.assertIs(
            record_target_result.status,
            NonProductionAssessmentSubmissionTargetHandoffStatus.INVALID,
        )

    def test_same_business_entity_r2_establishment_does_not_select_target(self):
        first = establish(allocation_value=allocation(R1))
        second = establish(allocation_value=allocation(R2))

        self.assertEqual(first.provisional_resource.business_entity_id, B1)
        self.assertEqual(second.provisional_resource.business_entity_id, B1)
        self.assertNotEqual(
            first.provisional_resource.resource_reference,
            second.provisional_resource.resource_reference,
        )

    def test_cross_business_entity_bindings_are_preserved_by_resource_identity(self):
        first = establish(
            allocation_value=allocation(R1),
            business_context_value=business_context(B1),
        )
        second = establish(
            allocation_value=allocation(R2),
            business_context_value=business_context(B2),
        )
        source = NonProductionResourceIdentityAuthoritySource(
            [first.resource_identity_record, second.resource_identity_record],
        )

        first_lookup = source.resolve_resource(R1)
        second_lookup = source.resolve_resource(R2)

        self.assertEqual(first_lookup.records[0].business_entity_id, B1)
        self.assertEqual(second_lookup.records[0].business_entity_id, B2)

    def test_public_shapes_are_minimal_and_exact(self):
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(NonProductionGovernedAssessmentSubmissionBusinessContext)),
            ("business_entity_id",),
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(NonProductionAssessmentSubmissionResourceReferenceAllocation)),
            ("resource_reference",),
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(NonProductionProvisionalAssessmentSubmissionResourceFact)),
            ("resource_reference", "business_entity_id", "resource_class", "lifecycle_state"),
        )
        self.assertEqual(
            tuple(NonProductionAssessmentSubmissionLifecycleState.__members__),
            ("PROVISIONAL",),
        )
        self.assertEqual(
            tuple(NonProductionAssessmentSubmissionResourceEstablishmentStatus.__members__),
            ("READY", "INVALID"),
        )
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionResourceEstablishmentResult,
                )
            ),
            ("status", "provisional_resource", "resource_identity_record"),
        )
        self.assertFalse(hasattr(establish(), "decision"))
        self.assertFalse(hasattr(establish(), "target_fact"))

    def test_source_import_boundary_excludes_authority_consumers_runtime_and_persistence(self):
        source = SOURCE_PATH.read_text()
        prohibited = (
            "evaluator",
            "resource_identity_source",
            "membership_source",
            "entitlement_source",
            "business_entity_source",
            "principal_mapping_source",
            "non_production_assessment_submission_target_handoff",
            "lambda_function",
            "boto3",
            "uuid",
            "random",
            "sqlite",
            "dynamodb",
            "open(",
        )

        for name in prohibited:
            with self.subTest(name=name):
                self.assertNotIn(name, source)

    def assert_invalid(
        self,
        result: NonProductionAssessmentSubmissionResourceEstablishmentResult,
    ) -> None:
        self.assertIs(
            result.status,
            NonProductionAssessmentSubmissionResourceEstablishmentStatus.INVALID,
        )
        self.assertIsNone(result.provisional_resource)
        self.assertIsNone(result.resource_identity_record)


if __name__ == "__main__":
    unittest.main()
