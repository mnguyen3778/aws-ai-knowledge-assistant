import dataclasses
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_resource_allocation_binding as allocation_binding_module  # noqa: E402
from trusted_authorization.models import ResourceClass  # noqa: E402
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_allocation_binding import (  # noqa: E402
    NonProductionAssessmentSubmissionAttemptResourceBindingEvidence,
    NonProductionAssessmentSubmissionResourceAllocationBindingAuthority,
    NonProductionAssessmentSubmissionResourceAllocationBindingResult,
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus,
    NonProductionAssessmentSubmissionResourceAllocationEvidence,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionAssessmentSubmissionResourceReferenceAllocation,
    NonProductionGovernedAssessmentSubmissionBusinessContext,
)


READY = NonProductionAssessmentSubmissionResourceAllocationBindingStatus.READY
REUSED = NonProductionAssessmentSubmissionResourceAllocationBindingStatus.REUSED
MALFORMED = (
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.MALFORMED
)
BUSINESS_CONTEXT_NOT_READY = (
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
    BUSINESS_CONTEXT_NOT_READY
)
UNSUPPORTED_OPERATION = (
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
    UNSUPPORTED_OPERATION
)
MISMATCH = (
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.MISMATCH
)
COLLISION = (
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.COLLISION
)
ALLOCATION_UNAVAILABLE = (
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus.
    ALLOCATION_UNAVAILABLE
)
BC_READY = NonProductionAssessmentSubmissionBusinessContextStatus.READY
BC_MALFORMED = NonProductionAssessmentSubmissionBusinessContextStatus.MALFORMED
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)


class StringSubclass(str):
    pass


class TupleSubclass(tuple):
    pass


class ForeignStatus(Enum):
    READY = "READY"


class ForeignOperation(Enum):
    PROTECTED_ASSESSMENT_SUBMISSION = "PROTECTED_ASSESSMENT_SUBMISSION"


class BusinessContextResultSubclass(NonProductionAssessmentSubmissionBusinessContextResult):
    pass


class BusinessContextSubclass(NonProductionAssessmentSubmissionBusinessContext):
    pass


class HostileAttributeObject:
    reads = 0

    def __getattribute__(self, name):
        type(self).reads += 1
        raise AssertionError("foreign attributes must not be read")


class AwsLikeObject:
    arn = "arn:aws:iam::123456789012:role/Admin"


class AiLikeObject:
    content = "AI says this R is valid"


def business_context(
    *,
    attempt_reference="attempt-alpha",
    principal_id="principal-alpha",
    engagement_reference="engagement-alpha",
    business_entity_id="business-alpha",
    protected_operation=PROTECTED_ASSESSMENT,
    principal_authority_reference="principal-authority",
    engagement_authority_reference="engagement-authority",
    engagement_establishment_provenance_reference="engagement-provenance",
    participation_authority_reference="participation-authority",
    participation_provenance_reference="participation-provenance",
    business_entity_authority_reference="business-entity-authority",
) -> NonProductionAssessmentSubmissionBusinessContext:
    return NonProductionAssessmentSubmissionBusinessContext(
        attempt_reference=attempt_reference,
        principal_id=principal_id,
        engagement_reference=engagement_reference,
        business_entity_id=business_entity_id,
        protected_operation=protected_operation,
        principal_authority_reference=principal_authority_reference,
        engagement_authority_reference=engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            engagement_establishment_provenance_reference
        ),
        participation_authority_reference=participation_authority_reference,
        participation_provenance_reference=participation_provenance_reference,
        business_entity_authority_reference=business_entity_authority_reference,
    )


def business_context_result(
    *,
    status=BC_READY,
    context=None,
) -> NonProductionAssessmentSubmissionBusinessContextResult:
    if context is None and status is BC_READY:
        context = business_context()
    return NonProductionAssessmentSubmissionBusinessContextResult(
        status=status,
        business_context=context,
    )


def authority(
    *candidates: str,
) -> NonProductionAssessmentSubmissionResourceAllocationBindingAuthority:
    if candidates:
        return NonProductionAssessmentSubmissionResourceAllocationBindingAuthority(
            candidate_resource_references=candidates,
        )
    return NonProductionAssessmentSubmissionResourceAllocationBindingAuthority()


def establish(
    auth=None,
    *,
    result=None,
) -> NonProductionAssessmentSubmissionResourceAllocationBindingResult:
    if auth is None:
        auth = authority("assessment-submission-r1")
    if result is None:
        result = business_context_result()
    return auth.establish_assessment_submission_resource_allocation_binding(
        business_context_result=result,
    )


class ResourceAllocationBindingTests(unittest.TestCase):
    def test_01_valid_first_establishment_returns_ready(self):
        result = establish()

        self.assertIs(result.status, READY)
        self.assertIsNotNone(result.allocation_evidence)
        self.assertIsNotNone(result.binding_evidence)
        self.assertIs(
            type(result.allocation_evidence),
            NonProductionAssessmentSubmissionResourceAllocationEvidence,
        )
        self.assertIs(
            type(result.binding_evidence),
            NonProductionAssessmentSubmissionAttemptResourceBindingEvidence,
        )

    def test_02_allocation_evidence_fields_are_exact_and_authority_scoped(self):
        result = establish()
        allocation = result.allocation_evidence

        self.assertEqual(allocation.resource_reference, "assessment-submission-r1")
        self.assertIs(allocation.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertEqual(
            allocation.allocation_authority_reference,
            "non-production-assessment-submission-resource-allocation-authority",
        )
        self.assertEqual(
            allocation.allocation_provenance_reference,
            "non-production-assessment-submission-resource-allocation-provenance-1",
        )

    def test_03_binding_evidence_preserves_business_context_and_provenance(self):
        result = establish()
        binding = result.binding_evidence

        self.assertEqual(binding.attempt_reference, "attempt-alpha")
        self.assertEqual(binding.resource_reference, "assessment-submission-r1")
        self.assertEqual(binding.principal_id, "principal-alpha")
        self.assertEqual(binding.engagement_reference, "engagement-alpha")
        self.assertEqual(binding.business_entity_id, "business-alpha")
        self.assertIs(binding.protected_operation, PROTECTED_ASSESSMENT)
        self.assertEqual(binding.principal_authority_reference, "principal-authority")
        self.assertEqual(binding.engagement_authority_reference, "engagement-authority")
        self.assertEqual(
            binding.engagement_establishment_provenance_reference,
            "engagement-provenance",
        )
        self.assertEqual(
            binding.participation_authority_reference,
            "participation-authority",
        )
        self.assertEqual(
            binding.participation_provenance_reference,
            "participation-provenance",
        )
        self.assertEqual(
            binding.business_entity_authority_reference,
            "business-entity-authority",
        )
        self.assertEqual(
            binding.allocation_authority_reference,
            "non-production-assessment-submission-resource-allocation-authority",
        )
        self.assertEqual(
            binding.allocation_provenance_reference,
            "non-production-assessment-submission-resource-allocation-provenance-1",
        )
        self.assertEqual(
            binding.binding_authority_reference,
            "non-production-assessment-submission-attempt-resource-binding-authority",
        )
        self.assertEqual(
            binding.binding_provenance_reference,
            "non-production-assessment-submission-attempt-resource-binding-provenance-1",
        )

    def test_04_exact_retry_returns_reused_same_r_and_original_provenance(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        first = establish(auth)
        second = establish(auth)

        self.assertIs(first.status, READY)
        self.assertIs(second.status, REUSED)
        self.assertEqual(
            second.allocation_evidence.resource_reference,
            first.allocation_evidence.resource_reference,
        )
        self.assertEqual(second.allocation_evidence, first.allocation_evidence)
        self.assertEqual(second.binding_evidence, first.binding_evidence)
        self.assertIsNot(second.allocation_evidence, first.allocation_evidence)
        self.assertIsNot(second.binding_evidence, first.binding_evidence)

    def test_05_retry_does_not_consume_candidate_or_create_new_event(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        establish(auth)
        retry = establish(auth)
        beta = establish(
            auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta"),
            ),
        )

        self.assertIs(retry.status, REUSED)
        self.assertIs(beta.status, READY)
        self.assertEqual(beta.allocation_evidence.resource_reference, "assessment-submission-r2")
        self.assertEqual(
            retry.binding_evidence.binding_provenance_reference,
            "non-production-assessment-submission-attempt-resource-binding-provenance-1",
        )
        self.assertEqual(
            beta.binding_evidence.binding_provenance_reference,
            "non-production-assessment-submission-attempt-resource-binding-provenance-2",
        )

    def test_06_same_a_different_p_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(principal_id="principal-beta"),
        )

    def test_07_same_a_different_e_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(engagement_reference="engagement-beta"),
        )

    def test_08_same_a_different_b_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(business_entity_id="business-beta"),
        )

    def test_09_same_a_different_operation_is_unsupported_without_state_mutation(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        establish(auth)
        bad = establish(
            auth,
            result=business_context_result(
                context=business_context(
                    protected_operation=object.__new__(
                        NonProductionProtectedApplicationOperation
                    )
                ),
            ),
        )
        retry = establish(auth)

        self.assertIs(bad.status, UNSUPPORTED_OPERATION)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(retry.binding_evidence.resource_reference, "assessment-submission-r1")

    def test_10_principal_authority_rotation_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(principal_authority_reference="principal-authority-2"),
        )

    def test_11_engagement_authority_rotation_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(engagement_authority_reference="engagement-authority-2"),
        )

    def test_12_engagement_provenance_rotation_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(
                engagement_establishment_provenance_reference="engagement-provenance-2"
            ),
        )

    def test_13_participation_authority_rotation_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(participation_authority_reference="participation-authority-2"),
        )

    def test_14_participation_provenance_rotation_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(participation_provenance_reference="participation-provenance-2"),
        )

    def test_15_business_entity_authority_rotation_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(business_entity_authority_reference="business-entity-authority-2"),
        )

    def test_16_same_r_second_a_is_collision_and_does_not_consume_a2(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r1", "assessment-submission-r2")
        first = establish(auth)
        collision = establish(
            auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta"),
            ),
        )
        beta = establish(
            auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta"),
            ),
        )

        self.assertIs(first.status, READY)
        self.assertIs(collision.status, COLLISION)
        self.assert_failure_empty(collision)
        self.assertIs(beta.status, READY)
        self.assertEqual(beta.binding_evidence.resource_reference, "assessment-submission-r2")
        self.assertEqual(
            establish(auth).binding_evidence.resource_reference,
            "assessment-submission-r1",
        )

    def test_17_collision_leaves_original_binding_unchanged(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r1")
        first = establish(auth)
        establish(
            auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta"),
            ),
        )
        retry = establish(auth)

        self.assertEqual(retry.binding_evidence, first.binding_evidence)
        self.assertIs(retry.status, REUSED)

    def test_18_non_ready_business_context_result_is_not_ready(self):
        result = establish(
            result=NonProductionAssessmentSubmissionBusinessContextResult(
                status=BC_MALFORMED,
                business_context=None,
            ),
        )

        self.assertIs(result.status, BUSINESS_CONTEXT_NOT_READY)
        self.assert_failure_empty(result)

    def test_19_non_ready_with_context_is_malformed(self):
        result = establish(
            result=NonProductionAssessmentSubmissionBusinessContextResult(
                status=BC_MALFORMED,
                business_context=business_context(),
            ),
        )

        self.assertIs(result.status, MALFORMED)

    def test_20_wrong_result_type_is_malformed_without_attribute_reads(self):
        hostile = HostileAttributeObject()
        HostileAttributeObject.reads = 0
        result = establish(result=hostile)

        self.assertIs(result.status, MALFORMED)
        self.assertEqual(HostileAttributeObject.reads, 0)

    def test_21_result_subclass_is_malformed(self):
        result = establish(
            result=BusinessContextResultSubclass(
                status=BC_READY,
                business_context=business_context(),
            ),
        )

        self.assertIs(result.status, MALFORMED)

    def test_22_wrong_status_enum_is_malformed(self):
        result = establish(
            result=NonProductionAssessmentSubmissionBusinessContextResult(
                status=ForeignStatus.READY,
                business_context=business_context(),
            ),
        )

        self.assertIs(result.status, MALFORMED)

    def test_23_missing_context_for_ready_is_malformed(self):
        result = establish(
            result=NonProductionAssessmentSubmissionBusinessContextResult(
                status=BC_READY,
                business_context=None,
            ),
        )

        self.assertIs(result.status, MALFORMED)

    def test_24_wrong_context_type_and_subclass_are_malformed(self):
        cases = (
            object(),
            BusinessContextSubclass(
                attempt_reference="attempt-alpha",
                principal_id="principal-alpha",
                engagement_reference="engagement-alpha",
                business_entity_id="business-alpha",
                protected_operation=PROTECTED_ASSESSMENT,
                principal_authority_reference="principal-authority",
                engagement_authority_reference="engagement-authority",
                engagement_establishment_provenance_reference="engagement-provenance",
                participation_authority_reference="participation-authority",
                participation_provenance_reference="participation-provenance",
                business_entity_authority_reference="business-entity-authority",
            ),
        )
        for value in cases:
            with self.subTest(value=type(value).__name__):
                self.assertIs(
                    establish(
                        result=NonProductionAssessmentSubmissionBusinessContextResult(
                            status=BC_READY,
                            business_context=value,
                        ),
                    ).status,
                    MALFORMED,
                )

    def test_25_malformed_business_context_strings_are_malformed(self):
        invalids = ("", " ", "   ", "\t", "\n", " x", "x ", StringSubclass("x"), 7, None)
        field_names = (
            "attempt_reference",
            "principal_id",
            "engagement_reference",
            "business_entity_id",
            "principal_authority_reference",
            "engagement_authority_reference",
            "engagement_establishment_provenance_reference",
            "participation_authority_reference",
            "participation_provenance_reference",
            "business_entity_authority_reference",
        )
        for field_name in field_names:
            for value in invalids:
                with self.subTest(field=field_name, value=repr(value)):
                    self.assertIs(
                        establish(
                            result=business_context_result(
                                context=replace(
                                    business_context(),
                                    **{field_name: value},
                                ),
                            ),
                        ).status,
                        MALFORMED,
                    )

    def test_26_foreign_operation_enum_is_malformed(self):
        result = establish(
            result=business_context_result(
                context=business_context(
                    protected_operation=ForeignOperation.PROTECTED_ASSESSMENT_SUBMISSION
                ),
            ),
        )

        self.assertIs(result.status, MALFORMED)

    def test_27_unsupported_operation_is_unsupported(self):
        result = establish(
            result=business_context_result(
                context=business_context(
                    protected_operation=object.__new__(
                        NonProductionProtectedApplicationOperation
                    )
                ),
            ),
        )

        self.assertIs(result.status, UNSUPPORTED_OPERATION)

    def test_28_exact_candidate_tuple_is_accepted(self):
        result = establish(authority("assessment-submission-r-custom"))

        self.assertIs(result.status, READY)
        self.assertEqual(
            result.allocation_evidence.resource_reference,
            "assessment-submission-r-custom",
        )

    def test_29_tuple_subclass_configuration_fails_closed(self):
        auth = NonProductionAssessmentSubmissionResourceAllocationBindingAuthority(
            candidate_resource_references=TupleSubclass(("assessment-submission-r1",)),
        )

        result = establish(auth)

        self.assertIs(result.status, MALFORMED)
        self.assert_failure_empty(result)

    def test_30_malformed_candidate_members_fail_closed(self):
        cases = ("", " ", " x", "x ", StringSubclass("x"), 7, None)
        for value in cases:
            with self.subTest(value=repr(value)):
                result = establish(
                    NonProductionAssessmentSubmissionResourceAllocationBindingAuthority(
                        candidate_resource_references=(value,),
                    ),
                )

                self.assertIs(result.status, MALFORMED)
                self.assert_failure_empty(result)

    def test_31_candidate_exhaustion_is_unavailable_and_does_not_consume_a(self):
        auth = NonProductionAssessmentSubmissionResourceAllocationBindingAuthority(
            candidate_resource_references=(),
        )
        unavailable = establish(auth)
        self.assertIs(unavailable.status, ALLOCATION_UNAVAILABLE)
        later = establish(
            auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta"),
            ),
        )

        self.assertIs(later.status, ALLOCATION_UNAVAILABLE)
        self.assert_failure_empty(unavailable)
        self.assert_failure_empty(later)

    def test_32_invalid_first_call_does_not_consume_a(self):
        auth = authority("assessment-submission-r1")
        invalid = establish(
            auth,
            result=business_context_result(
                context=replace(business_context(), principal_id=" "),
            ),
        )
        valid = establish(auth)

        self.assertIs(invalid.status, MALFORMED)
        self.assertIs(valid.status, READY)
        self.assertEqual(valid.binding_evidence.attempt_reference, "attempt-alpha")

    def test_33_default_internal_sequence_is_deterministic_and_instance_local(self):
        first_auth = NonProductionAssessmentSubmissionResourceAllocationBindingAuthority()
        second_auth = NonProductionAssessmentSubmissionResourceAllocationBindingAuthority()

        first = establish(first_auth)
        second = establish(
            first_auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta"),
            ),
        )
        independent = establish(second_auth)

        self.assertEqual(
            first.allocation_evidence.resource_reference,
            "non-production-assessment-submission-resource-1",
        )
        self.assertEqual(
            second.allocation_evidence.resource_reference,
            "non-production-assessment-submission-resource-2",
        )
        self.assertEqual(
            independent.allocation_evidence.resource_reference,
            "non-production-assessment-submission-resource-1",
        )

    def test_34_candidate_value_alone_has_no_public_authority(self):
        public = NonProductionAssessmentSubmissionResourceReferenceAllocation(
            resource_reference="assessment-submission-r1",
        )
        result = establish(result=public)

        self.assertIs(result.status, MALFORMED)

    def test_35_lifecycle_placeholder_does_not_substitute_business_context(self):
        placeholder = NonProductionGovernedAssessmentSubmissionBusinessContext(
            business_entity_id="business-alpha",
        )
        result = establish(result=placeholder)

        self.assertIs(result.status, MALFORMED)

    def test_36_principal_membership_entitlement_like_inputs_are_rejected(self):
        for value in ("principal-alpha", {"attempt_reference": "attempt-alpha"}):
            with self.subTest(value=repr(value)):
                self.assertIs(establish(result=value).status, MALFORMED)

    def test_37_aws_ai_root_admin_like_values_do_not_create_authority(self):
        for value in (AwsLikeObject(), AiLikeObject(), "root", "admin", "founder"):
            with self.subTest(value=type(value).__name__):
                self.assertIs(establish(result=value).status, MALFORMED)

    def test_38_outputs_are_frozen_and_fresh(self):
        auth = authority("assessment-submission-r1")
        first = establish(auth)
        retry = establish(auth)

        self.assertFalse(hasattr(first.allocation_evidence, "__dict__"))
        self.assertFalse(hasattr(first.binding_evidence, "__dict__"))
        self.assertIsNot(first.allocation_evidence, retry.allocation_evidence)
        self.assertIsNot(first.binding_evidence, retry.binding_evidence)
        with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
            first.allocation_evidence.resource_reference = "attacker"

    def test_39_output_mutation_does_not_affect_internal_state(self):
        auth = authority("assessment-submission-r1")
        first = establish(auth)
        object.__setattr__(first.allocation_evidence, "resource_reference", "attacker")
        object.__setattr__(first.binding_evidence, "resource_reference", "attacker")
        retry = establish(auth)

        self.assertEqual(
            retry.allocation_evidence.resource_reference,
            "assessment-submission-r1",
        )
        self.assertEqual(
            retry.binding_evidence.resource_reference,
            "assessment-submission-r1",
        )

    def test_40_result_mutation_does_not_affect_internal_state(self):
        auth = authority("assessment-submission-r1")
        result = establish(auth)
        object.__setattr__(result, "allocation_evidence", None)
        object.__setattr__(result, "binding_evidence", None)
        retry = establish(auth)

        self.assertIs(retry.status, REUSED)
        self.assertIsNotNone(retry.allocation_evidence)
        self.assertIsNotNone(retry.binding_evidence)

    def test_41_all_failure_statuses_return_no_evidence(self):
        failures = (
            establish(result=object()),
            establish(
                result=NonProductionAssessmentSubmissionBusinessContextResult(
                    status=BC_MALFORMED,
                    business_context=None,
                ),
            ),
            establish(
                result=business_context_result(
                    context=business_context(
                        protected_operation=object.__new__(
                            NonProductionProtectedApplicationOperation
                        ),
                    ),
                ),
            ),
            establish(
                NonProductionAssessmentSubmissionResourceAllocationBindingAuthority(
                    candidate_resource_references=(),
                ),
            ),
        )
        for result in failures:
            with self.subTest(status=result.status):
                self.assert_failure_empty(result)

    def test_42_public_status_members_are_exact(self):
        self.assertEqual(
            tuple(NonProductionAssessmentSubmissionResourceAllocationBindingStatus),
            (
                READY,
                REUSED,
                MALFORMED,
                BUSINESS_CONTEXT_NOT_READY,
                UNSUPPORTED_OPERATION,
                MISMATCH,
                COLLISION,
                ALLOCATION_UNAVAILABLE,
            ),
        )

    def test_43_public_shapes_are_exact(self):
        self.assertEqual(
            tuple(
                NonProductionAssessmentSubmissionResourceAllocationEvidence.
                __dataclass_fields__
            ),
            (
                "resource_reference",
                "resource_class",
                "allocation_authority_reference",
                "allocation_provenance_reference",
            ),
        )
        self.assertEqual(
            tuple(
                NonProductionAssessmentSubmissionAttemptResourceBindingEvidence.
                __dataclass_fields__
            ),
            (
                "attempt_reference",
                "resource_reference",
                "principal_id",
                "engagement_reference",
                "business_entity_id",
                "protected_operation",
                "principal_authority_reference",
                "engagement_authority_reference",
                "engagement_establishment_provenance_reference",
                "participation_authority_reference",
                "participation_provenance_reference",
                "business_entity_authority_reference",
                "allocation_authority_reference",
                "allocation_provenance_reference",
                "binding_authority_reference",
                "binding_provenance_reference",
            ),
        )
        self.assertEqual(
            tuple(
                NonProductionAssessmentSubmissionResourceAllocationBindingResult.
                __dataclass_fields__
            ),
            ("status", "allocation_evidence", "binding_evidence"),
        )

    def test_44_no_permission_lifecycle_or_resource_identity_output(self):
        result = establish()

        for name in (
            "decision",
            "allow",
            "deny",
            "permission",
            "authorized",
            "entitled",
            "can_submit",
            "provisional_resource",
            "resource_identity_record",
            "target_fact",
        ):
            with self.subTest(name=name):
                self.assertFalse(hasattr(result, name))
                self.assertFalse(hasattr(result.allocation_evidence, name))
                self.assertFalse(hasattr(result.binding_evidence, name))

    def test_45_source_import_boundary_excludes_runtime_persistence_and_downstream(self):
        source = inspect.getsource(allocation_binding_module).lower()
        for forbidden in (
            "boto",
            "aws",
            "cognito",
            "lambda",
            "requests",
            "urllib",
            "sqlite",
            "dynamodb",
            "redis",
            "open(",
            "uuid",
            "random",
            "threading",
            "lock",
            "evaluator",
            "resource_identity_source",
            "target_handoff",
            "membership",
            "entitlement",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_46_source_does_not_use_unsafe_reflection_or_dynamic_registration(self):
        source = inspect.getsource(allocation_binding_module)

        self.assertNotIn("vars(", source)
        self.assertNotIn(".__dict__", source)
        self.assertNotIn("setattr(", source)
        self.assertNotIn("getattr(", source)

    def test_47_no_unrelated_public_types(self):
        public_names = {
            name
            for name, value in vars(allocation_binding_module).items()
            if not name.startswith("_")
            and (
                isinstance(value, type)
                or isinstance(value, type(lambda: None))
            )
        }

        self.assertEqual(
            public_names,
            {
                "NonProductionAssessmentSubmissionResourceAllocationEvidence",
                "NonProductionAssessmentSubmissionAttemptResourceBindingEvidence",
                "NonProductionAssessmentSubmissionResourceAllocationBindingStatus",
                "NonProductionAssessmentSubmissionResourceAllocationBindingResult",
                "NonProductionAssessmentSubmissionResourceAllocationBindingAuthority",
            },
        )

    def assert_same_a_mismatch(
        self,
        changed_context: NonProductionAssessmentSubmissionBusinessContext,
    ) -> None:
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        establish(auth)
        mismatch = establish(
            auth,
            result=business_context_result(context=changed_context),
        )
        retry = establish(auth)

        self.assertIs(mismatch.status, MISMATCH)
        self.assert_failure_empty(mismatch)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(retry.binding_evidence.resource_reference, "assessment-submission-r1")

    def assert_failure_empty(
        self,
        result: NonProductionAssessmentSubmissionResourceAllocationBindingResult,
    ) -> None:
        self.assertIsNone(result.allocation_evidence)
        self.assertIsNone(result.binding_evidence)


if __name__ == "__main__":
    unittest.main()
