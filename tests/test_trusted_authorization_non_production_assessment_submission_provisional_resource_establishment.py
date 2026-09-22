import dataclasses
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_provisional_resource_establishment as establishment_module  # noqa: E402
import trusted_authorization.non_production_assessment_submission_resource_lifecycle as old_lifecycle_module  # noqa: E402
from trusted_authorization.models import GovernedResource, ResourceClass  # noqa: E402
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_provisional_resource_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority,
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence,
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult,
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus,
    NonProductionAssessmentSubmissionProvisionalResourceFact,
)
from trusted_authorization.non_production_assessment_submission_resource_allocation_binding import (  # noqa: E402
    NonProductionAssessmentSubmissionResourceAllocationBindingAuthority,
    NonProductionAssessmentSubmissionResourceAllocationBindingResult,
    NonProductionAssessmentSubmissionResourceAllocationBindingStatus,
    NonProductionAssessmentSubmissionResourceAllocationEvidence,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionAssessmentSubmissionLifecycleState,
    NonProductionAssessmentSubmissionResourceReferenceAllocation,
    NonProductionGovernedAssessmentSubmissionBusinessContext,
)


ESTABLISHED = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
    ESTABLISHED
)
REUSED = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.REUSED
)
MALFORMED = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
    MALFORMED
)
BUSINESS_CONTEXT_NOT_READY = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
    BUSINESS_CONTEXT_NOT_READY
)
UNSUPPORTED_OPERATION = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
    UNSUPPORTED_OPERATION
)
MISMATCH = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
    MISMATCH
)
COLLISION = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
    COLLISION
)
ALLOCATION_UNAVAILABLE = (
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
    ALLOCATION_UNAVAILABLE
)
BC_READY = NonProductionAssessmentSubmissionBusinessContextStatus.READY
BC_MALFORMED = NonProductionAssessmentSubmissionBusinessContextStatus.MALFORMED
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)
_DEFAULT_RESULT = object()


class StringSubclass(str):
    pass


class TupleSubclass(tuple):
    pass


class ForeignStatus(Enum):
    READY = "READY"


class ForeignOperation(Enum):
    PROTECTED_ASSESSMENT_SUBMISSION = "PROTECTED_ASSESSMENT_SUBMISSION"


class BusinessContextResultSubclass(
    NonProductionAssessmentSubmissionBusinessContextResult
):
    pass


class BusinessContextSubclass(NonProductionAssessmentSubmissionBusinessContext):
    pass


class AllocationBindingAuthoritySubclass(
    NonProductionAssessmentSubmissionResourceAllocationBindingAuthority
):
    pass


class HostileAttributeObject:
    reads = 0

    def __getattribute__(self, name):
        type(self).reads += 1
        raise AssertionError("foreign attributes must not be read")


class FakeAllocationBindingAuthority:
    def establish_assessment_submission_resource_allocation_binding(self, **kwargs):
        raise AssertionError("fake authority must never be invoked")


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
) -> NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority:
    if candidates:
        return (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority(
                candidate_resource_references=candidates,
            )
        )
    return NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority()


def establish(
    auth=None,
    *,
    result=_DEFAULT_RESULT,
) -> NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult:
    if auth is None:
        auth = authority("assessment-submission-r1")
    if result is _DEFAULT_RESULT:
        result = business_context_result()
    return auth.establish_assessment_submission_provisional_resource(
        business_context_result=result,
    )


class ProvisionalResourceEstablishmentTests(unittest.TestCase):
    def test_01_public_surface_is_exactly_the_five_frozen_types(self):
        public_names = {
            name
            for name, value in vars(establishment_module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(
            public_names,
            {
                "NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority",
                "NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence",
                "NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult",
                "NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus",
                "NonProductionAssessmentSubmissionProvisionalResourceFact",
            },
        )

    def test_02_constructor_and_method_signatures_are_exact(self):
        self.assertEqual(
            str(
                inspect.signature(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority
                )
            ),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) -> 'None'",
        )
        self.assertEqual(
            str(
                inspect.signature(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority.
                    establish_assessment_submission_provisional_resource
                )
            ),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult'",
        )

    def test_03_no_evidence_or_dependency_injection_public_api_exists(self):
        authority_signature = inspect.signature(
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority
        )
        method_signature = inspect.signature(
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority.
            establish_assessment_submission_provisional_resource
        )
        self.assertEqual(
            tuple(authority_signature.parameters),
            ("candidate_resource_references",),
        )
        self.assertEqual(
            tuple(method_signature.parameters),
            ("self", "business_context_result"),
        )
        public_methods = {
            name
            for name, value in inspect.getmembers(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority
            )
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(
            public_methods,
            {"establish_assessment_submission_provisional_resource"},
        )

    def test_04_authority_privately_owns_exact_allocation_binding_authority(self):
        auth = authority("assessment-submission-r1")
        owned = object.__getattribute__(auth, "_allocation_binding_authority")
        self.assertIs(
            type(owned),
            NonProductionAssessmentSubmissionResourceAllocationBindingAuthority,
        )

    def test_05_valid_first_establishment_returns_complete_outputs(self):
        result = establish()
        self.assertIs(result.status, ESTABLISHED)
        self.assertIs(
            type(result.provisional_resource),
            NonProductionAssessmentSubmissionProvisionalResourceFact,
        )
        self.assertIs(
            type(result.establishment_evidence),
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence,
        )

    def test_06_resource_fact_is_exactly_provisional_and_non_generic(self):
        resource = establish().provisional_resource
        self.assertEqual(resource.resource_reference, "assessment-submission-r1")
        self.assertEqual(resource.business_entity_id, "business-alpha")
        self.assertIs(resource.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(
            resource.lifecycle_state,
            NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL,
        )
        self.assertNotIsInstance(resource, GovernedResource)

    def test_07_establishment_evidence_preserves_complete_lineage(self):
        evidence = establish().establishment_evidence
        self.assertEqual(evidence.attempt_reference, "attempt-alpha")
        self.assertEqual(evidence.resource_reference, "assessment-submission-r1")
        self.assertEqual(evidence.principal_id, "principal-alpha")
        self.assertEqual(evidence.engagement_reference, "engagement-alpha")
        self.assertEqual(evidence.business_entity_id, "business-alpha")
        self.assertIs(evidence.protected_operation, PROTECTED_ASSESSMENT)
        self.assertEqual(evidence.principal_authority_reference, "principal-authority")
        self.assertEqual(evidence.engagement_authority_reference, "engagement-authority")
        self.assertEqual(
            evidence.engagement_establishment_provenance_reference,
            "engagement-provenance",
        )
        self.assertEqual(
            evidence.participation_authority_reference,
            "participation-authority",
        )
        self.assertEqual(
            evidence.participation_provenance_reference,
            "participation-provenance",
        )
        self.assertEqual(
            evidence.business_entity_authority_reference,
            "business-entity-authority",
        )
        self.assertEqual(
            evidence.allocation_authority_reference,
            "non-production-assessment-submission-resource-allocation-authority",
        )
        self.assertEqual(
            evidence.allocation_provenance_reference,
            "non-production-assessment-submission-resource-allocation-provenance-1",
        )
        self.assertEqual(
            evidence.binding_authority_reference,
            "non-production-assessment-submission-attempt-resource-binding-authority",
        )
        self.assertEqual(
            evidence.binding_provenance_reference,
            "non-production-assessment-submission-attempt-resource-binding-provenance-1",
        )
        self.assertIs(evidence.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(
            evidence.lifecycle_state,
            NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL,
        )
        self.assertEqual(
            evidence.lifecycle_authority_reference,
            "non-production-assessment-submission-resource-lifecycle-establishment-authority",
        )
        self.assertEqual(
            evidence.lifecycle_provenance_reference,
            "non-production-assessment-submission-provisional-resource-establishment-provenance-1",
        )

    def test_08_status_enum_and_result_fields_are_exact(self):
        self.assertEqual(
            tuple(
                NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.
                __members__
            ),
            (
                "ESTABLISHED",
                "REUSED",
                "MALFORMED",
                "BUSINESS_CONTEXT_NOT_READY",
                "UNSUPPORTED_OPERATION",
                "MISMATCH",
                "COLLISION",
                "ALLOCATION_UNAVAILABLE",
            ),
        )
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult
                )
            ),
            ("status", "provisional_resource", "establishment_evidence"),
        )

    def test_09_resource_and_evidence_field_contracts_are_exact(self):
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionProvisionalResourceFact
                )
            ),
            (
                "resource_reference",
                "business_entity_id",
                "resource_class",
                "lifecycle_state",
            ),
        )
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentEvidence
                )
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
                "resource_class",
                "lifecycle_state",
                "lifecycle_authority_reference",
                "lifecycle_provenance_reference",
            ),
        )

    def test_10_exact_retry_reuses_same_semantics_and_fresh_outputs(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        first = establish(auth)
        second = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(second.status, REUSED)
        self.assertEqual(first.provisional_resource, second.provisional_resource)
        self.assertEqual(first.establishment_evidence, second.establishment_evidence)
        self.assertIsNot(first, second)
        self.assertIsNot(first.provisional_resource, second.provisional_resource)
        self.assertIsNot(
            first.establishment_evidence,
            second.establishment_evidence,
        )

    def test_11_retry_does_not_consume_candidate_or_create_lifecycle_event(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        first = establish(auth)
        retry = establish(auth)
        beta = establish(
            auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta")
            ),
        )
        self.assertIs(retry.status, REUSED)
        self.assertIs(beta.status, ESTABLISHED)
        self.assertEqual(
            retry.provisional_resource.resource_reference,
            first.provisional_resource.resource_reference,
        )
        self.assertEqual(
            retry.establishment_evidence.lifecycle_provenance_reference,
            "non-production-assessment-submission-provisional-resource-establishment-provenance-1",
        )
        self.assertEqual(
            beta.provisional_resource.resource_reference,
            "assessment-submission-r2",
        )
        self.assertEqual(
            beta.establishment_evidence.lifecycle_provenance_reference,
            "non-production-assessment-submission-provisional-resource-establishment-provenance-2",
        )

    def test_12_same_a_changed_principal_is_mismatch(self):
        self.assert_same_a_mismatch(business_context(principal_id="principal-beta"))

    def test_13_same_a_changed_engagement_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(engagement_reference="engagement-beta")
        )

    def test_14_same_a_changed_business_entity_is_mismatch(self):
        self.assert_same_a_mismatch(
            business_context(business_entity_id="business-beta")
        )

    def test_15_business_context_authority_rotation_is_mismatch(self):
        changes = {
            "principal_authority_reference": "principal-authority-2",
            "engagement_authority_reference": "engagement-authority-2",
            "engagement_establishment_provenance_reference": "engagement-provenance-2",
            "participation_authority_reference": "participation-authority-2",
            "participation_provenance_reference": "participation-provenance-2",
            "business_entity_authority_reference": "business-entity-authority-2",
        }
        for field, value in changes.items():
            with self.subTest(field=field):
                self.assert_same_a_mismatch(business_context(**{field: value}))

    def test_16_changed_operation_is_unsupported_and_preserves_state(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        first = establish(auth)
        changed = establish(
            auth,
            result=business_context_result(
                context=business_context(
                    protected_operation=object.__new__(
                        NonProductionProtectedApplicationOperation
                    )
                )
            ),
        )
        retry = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(changed.status, UNSUPPORTED_OPERATION)
        self.assert_failure_payloads(changed)
        self.assertIs(retry.status, REUSED)

    def test_17_same_r_second_a_is_collision_and_second_a_is_unconsumed(self):
        auth = authority(
            "assessment-submission-r1",
            "assessment-submission-r1",
            "assessment-submission-r2",
        )
        first = establish(auth)
        beta_context = business_context_result(
            context=business_context(attempt_reference="attempt-beta")
        )
        collision = establish(auth, result=beta_context)
        beta = establish(auth, result=beta_context)
        retry = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(collision.status, COLLISION)
        self.assert_failure_payloads(collision)
        self.assertIs(beta.status, ESTABLISHED)
        self.assertEqual(
            beta.provisional_resource.resource_reference,
            "assessment-submission-r2",
        )
        self.assertIs(retry.status, REUSED)

    def test_18_allocation_unavailable_creates_no_lifecycle_state(self):
        auth = (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority(
                candidate_resource_references=(),
            )
        )
        result = establish(auth)
        self.assertIs(result.status, ALLOCATION_UNAVAILABLE)
        self.assert_failure_payloads(result)
        self.assertEqual(
            object.__getattribute__(auth, "_establishments_by_attempt"),
            {},
        )

    def test_19_malformed_candidate_and_tuple_subclass_fail_closed(self):
        cases = (
            authority(""),
            authority(" candidate"),
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority(
                candidate_resource_references=TupleSubclass(("r1",))
            ),
        )
        for auth in cases:
            with self.subTest(auth=auth):
                result = establish(auth)
                self.assertIs(result.status, MALFORMED)
                self.assert_failure_payloads(result)

    def test_20_foreign_inputs_are_malformed_without_attribute_reads(self):
        HostileAttributeObject.reads = 0
        for value in (None, "raw", {}, object(), HostileAttributeObject()):
            with self.subTest(value=type(value)):
                result = establish(result=value)
                self.assertIs(result.status, MALFORMED)
                self.assert_failure_payloads(result)
        self.assertEqual(HostileAttributeObject.reads, 0)

    def test_21_non_ready_and_invalid_ready_shapes_fail_closed(self):
        not_ready = establish(
            result=business_context_result(status=BC_MALFORMED, context=None)
        )
        ready_without_context = establish(
            result=NonProductionAssessmentSubmissionBusinessContextResult(
                status=BC_READY,
                business_context=None,
            )
        )
        not_ready_with_context = establish(
            result=NonProductionAssessmentSubmissionBusinessContextResult(
                status=BC_MALFORMED,
                business_context=business_context(),
            )
        )
        self.assertIs(not_ready.status, BUSINESS_CONTEXT_NOT_READY)
        self.assertIs(ready_without_context.status, MALFORMED)
        self.assertIs(not_ready_with_context.status, MALFORMED)

    def test_22_result_context_subclasses_and_foreign_status_are_rejected(self):
        cases = (
            BusinessContextResultSubclass(
                status=BC_READY,
                business_context=business_context(),
            ),
            business_context_result(context=BusinessContextSubclass(**{
                field.name: getattr(business_context(), field.name)
                for field in dataclasses.fields(NonProductionAssessmentSubmissionBusinessContext)
            })),
            NonProductionAssessmentSubmissionBusinessContextResult(
                status=ForeignStatus.READY,
                business_context=business_context(),
            ),
        )
        for value in cases:
            with self.subTest(value=type(value)):
                self.assertIs(establish(result=value).status, MALFORMED)

    def test_23_every_business_context_string_is_exact_nonblank(self):
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
        for field in field_names:
            for value in ("", " ", " edge", "edge ", StringSubclass("edge")):
                with self.subTest(field=field, value=repr(value)):
                    result = establish(
                        result=business_context_result(
                            context=business_context(**{field: value})
                        )
                    )
                    self.assertIs(result.status, MALFORMED)

    def test_24_foreign_operation_type_is_malformed(self):
        result = establish(
            result=business_context_result(
                context=business_context(
                    protected_operation=ForeignOperation.
                    PROTECTED_ASSESSMENT_SUBMISSION
                )
            )
        )
        self.assertIs(result.status, MALFORMED)

    def test_25_fake_or_subclass_dependency_is_rejected_before_invocation(self):
        for fake in (
            FakeAllocationBindingAuthority(),
            AllocationBindingAuthoritySubclass(),
        ):
            auth = authority("assessment-submission-r1")
            object.__setattr__(auth, "_allocation_binding_authority", fake)
            with self.subTest(fake=type(fake)):
                result = establish(auth)
                self.assertIs(result.status, MALFORMED)
                self.assert_failure_payloads(result)

    def test_26_old_lifecycle_placeholders_cannot_enter_public_method(self):
        old_values = (
            NonProductionGovernedAssessmentSubmissionBusinessContext(
                business_entity_id="business-alpha"
            ),
            NonProductionAssessmentSubmissionResourceReferenceAllocation(
                resource_reference="assessment-submission-r1"
            ),
        )
        for value in old_values:
            with self.subTest(value=type(value)):
                self.assertIs(establish(result=value).status, MALFORMED)

    def test_27_manually_constructed_upstream_evidence_has_no_input_path(self):
        allocation = NonProductionAssessmentSubmissionResourceAllocationEvidence(
            resource_reference="assessment-submission-r1",
            resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
            allocation_authority_reference="fake-authority",
            allocation_provenance_reference="fake-provenance",
        )
        forged_result = NonProductionAssessmentSubmissionResourceAllocationBindingResult(
            status=NonProductionAssessmentSubmissionResourceAllocationBindingStatus.READY,
            allocation_evidence=allocation,
            binding_evidence=None,
        )
        auth = authority("assessment-submission-r1")
        for kwargs in (
            {"allocation_evidence": allocation},
            {"binding_evidence": object()},
            {"allocation_binding_result": forged_result},
            {"resource_reference": "assessment-submission-r1"},
        ):
            with self.subTest(argument=tuple(kwargs)):
                with self.assertRaises(TypeError):
                    auth.establish_assessment_submission_provisional_resource(
                        business_context_result=business_context_result(),
                        **kwargs,
                    )

    def test_28_old_lifecycle_producer_is_not_invoked(self):
        with patch.object(
            old_lifecycle_module,
            "establish_non_production_provisional_assessment_submission_resource",
            side_effect=AssertionError("old lifecycle must remain separate"),
        ):
            self.assertIs(establish().status, ESTABLISHED)

    def test_29_precommit_failure_preserves_upstream_binding_for_retry(self):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        original_fact_type = (
            establishment_module.
            NonProductionAssessmentSubmissionProvisionalResourceFact
        )
        with patch.object(
            establishment_module,
            "NonProductionAssessmentSubmissionProvisionalResourceFact",
            side_effect=RuntimeError("controlled precommit construction failure"),
        ):
            failed = establish(auth)
        self.assertIs(failed.status, MALFORMED)
        self.assert_failure_payloads(failed)
        self.assertEqual(
            object.__getattribute__(auth, "_establishments_by_attempt"),
            {},
        )
        self.assertIs(
            establishment_module.
            NonProductionAssessmentSubmissionProvisionalResourceFact,
            original_fact_type,
        )
        recovered = establish(auth)
        beta = establish(
            auth,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta")
            ),
        )
        self.assertIs(recovered.status, ESTABLISHED)
        self.assertEqual(
            recovered.provisional_resource.resource_reference,
            "assessment-submission-r1",
        )
        self.assertIs(beta.status, ESTABLISHED)
        self.assertEqual(
            beta.provisional_resource.resource_reference,
            "assessment-submission-r2",
        )

    def test_30_returned_mutation_cannot_change_internal_state(self):
        auth = authority("assessment-submission-r1")
        first = establish(auth)
        object.__setattr__(
            first.provisional_resource,
            "resource_reference",
            "attacker-resource",
        )
        object.__setattr__(
            first.establishment_evidence,
            "lifecycle_provenance_reference",
            "attacker-provenance",
        )
        object.__setattr__(first, "provisional_resource", None)
        retry = establish(auth)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(
            retry.provisional_resource.resource_reference,
            "assessment-submission-r1",
        )
        self.assertEqual(
            retry.establishment_evidence.lifecycle_provenance_reference,
            "non-production-assessment-submission-provisional-resource-establishment-provenance-1",
        )

    def test_31_outputs_are_frozen_and_internal_snapshot_is_not_returned(self):
        auth = authority("assessment-submission-r1")
        result = establish(auth)
        with self.assertRaises(FrozenInstanceError):
            result.provisional_resource.resource_reference = "attacker"
        with self.assertRaises(FrozenInstanceError):
            result.establishment_evidence.attempt_reference = "attacker"
        snapshot = object.__getattribute__(
            auth, "_establishments_by_attempt"
        )["attempt-alpha"]
        resource_snapshot = object.__getattribute__(
            snapshot, "provisional_resource"
        )
        evidence_snapshot = object.__getattribute__(
            snapshot, "establishment_evidence"
        )
        self.assertIsNot(result.provisional_resource, resource_snapshot)
        self.assertIsNot(result.establishment_evidence, evidence_snapshot)

    def test_32_both_indexes_reference_one_canonical_snapshot(self):
        auth = authority("assessment-submission-r1")
        establish(auth)
        by_attempt = object.__getattribute__(
            auth, "_establishments_by_attempt"
        )
        by_resource = object.__getattribute__(
            auth, "_establishments_by_resource_reference"
        )
        self.assertIs(
            by_attempt["attempt-alpha"],
            by_resource["assessment-submission-r1"],
        )

    def test_33_instance_state_is_independent(self):
        first_authority = authority("shared-r")
        second_authority = authority("shared-r")
        first = establish(first_authority)
        second = establish(second_authority)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(second.status, ESTABLISHED)
        self.assertEqual(
            first.provisional_resource.resource_reference,
            second.provisional_resource.resource_reference,
        )
        self.assertIsNot(
            object.__getattribute__(
                first_authority, "_establishments_by_attempt"
            ),
            object.__getattribute__(
                second_authority, "_establishments_by_attempt"
            ),
        )

    def test_34_default_candidate_sequence_is_deterministic_and_instance_local(self):
        first_authority = authority()
        second_authority = authority()
        first = establish(first_authority)
        second = establish(
            first_authority,
            result=business_context_result(
                context=business_context(attempt_reference="attempt-beta")
            ),
        )
        independent = establish(second_authority)
        self.assertEqual(
            first.provisional_resource.resource_reference,
            "non-production-assessment-submission-resource-1",
        )
        self.assertEqual(
            second.provisional_resource.resource_reference,
            "non-production-assessment-submission-resource-2",
        )
        self.assertEqual(
            independent.provisional_resource.resource_reference,
            "non-production-assessment-submission-resource-1",
        )

    def test_35_all_failure_statuses_have_no_payloads_or_lifecycle_state(self):
        cases = (
            (
                establish(result=None),
                MALFORMED,
            ),
            (
                establish(
                    result=business_context_result(
                        status=BC_MALFORMED,
                        context=None,
                    )
                ),
                BUSINESS_CONTEXT_NOT_READY,
            ),
            (
                establish(
                    result=business_context_result(
                        context=business_context(
                            protected_operation=object.__new__(
                                NonProductionProtectedApplicationOperation
                            )
                        )
                    )
                ),
                UNSUPPORTED_OPERATION,
            ),
            (
                establish(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority(
                        candidate_resource_references=(),
                    )
                ),
                ALLOCATION_UNAVAILABLE,
            ),
        )
        for result, expected in cases:
            with self.subTest(status=expected):
                self.assertIs(result.status, expected)
                self.assert_failure_payloads(result)

    def test_36_rotated_upstream_allocation_provenance_cannot_reuse(self):
        auth = authority("assessment-submission-r1")
        self.assertIs(establish(auth).status, ESTABLISHED)
        upstream = object.__getattribute__(
            auth, "_allocation_binding_authority"
        )
        snapshot = object.__getattribute__(
            upstream, "_bindings_by_attempt"
        )["attempt-alpha"]
        allocation = object.__getattribute__(snapshot, "allocation")
        binding = object.__getattribute__(snapshot, "binding")
        object.__setattr__(
            allocation,
            "allocation_provenance_reference",
            "rotated-allocation-provenance",
        )
        object.__setattr__(
            binding,
            "allocation_provenance_reference",
            "rotated-allocation-provenance",
        )
        result = establish(auth)
        self.assertIs(result.status, MISMATCH)
        self.assert_failure_payloads(result)

    def test_37_rotated_upstream_binding_provenance_cannot_reuse(self):
        auth = authority("assessment-submission-r1")
        self.assertIs(establish(auth).status, ESTABLISHED)
        upstream = object.__getattribute__(
            auth, "_allocation_binding_authority"
        )
        snapshot = object.__getattribute__(
            upstream, "_bindings_by_attempt"
        )["attempt-alpha"]
        binding = object.__getattribute__(snapshot, "binding")
        object.__setattr__(
            binding,
            "binding_provenance_reference",
            "rotated-binding-provenance",
        )
        result = establish(auth)
        self.assertIs(result.status, MISMATCH)
        self.assert_failure_payloads(result)

    def test_38_same_attempt_forged_second_resource_cannot_reuse(self):
        auth = authority("assessment-submission-r1")
        self.assertIs(establish(auth).status, ESTABLISHED)
        upstream = object.__getattribute__(
            auth, "_allocation_binding_authority"
        )
        snapshot = object.__getattribute__(
            upstream, "_bindings_by_attempt"
        )["attempt-alpha"]
        allocation = object.__getattribute__(snapshot, "allocation")
        binding = object.__getattribute__(snapshot, "binding")
        object.__setattr__(
            allocation,
            "resource_reference",
            "assessment-submission-r2",
        )
        object.__setattr__(
            binding,
            "resource_reference",
            "assessment-submission-r2",
        )
        result = establish(auth)
        self.assertIs(result.status, MISMATCH)
        self.assert_failure_payloads(result)

    def test_39_malformed_upstream_convergence_is_not_lifecycle_authority(self):
        auth = authority("assessment-submission-r1")
        upstream = object.__getattribute__(
            auth, "_allocation_binding_authority"
        )
        ready = upstream.establish_assessment_submission_resource_allocation_binding(
            business_context_result=business_context_result()
        )
        object.__setattr__(
            ready.binding_evidence,
            "allocation_provenance_reference",
            "mismatched-provenance",
        )
        with patch.object(
            NonProductionAssessmentSubmissionResourceAllocationBindingAuthority,
            "establish_assessment_submission_resource_allocation_binding",
            return_value=ready,
        ):
            result = establish(auth)
        self.assertIs(result.status, MALFORMED)
        self.assert_failure_payloads(result)

    def test_40_source_has_no_downstream_or_permission_integration(self):
        source_path = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "trusted_authorization"
            / "non_production_assessment_submission_provisional_resource_establishment.py"
        )
        source = source_path.read_text(encoding="utf-8")
        forbidden = (
            "GovernedResource",
            "resource_identity_source",
            "target_handoff",
            "Membership",
            "Entitlement",
            "ALLOW",
            "DENY",
            "SUBMITTED",
            "ABANDONED",
            "DynamoDB",
            "sqlite",
            "threading",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)
        self.assertNotIn(
            "establish_non_production_provisional_assessment_submission_resource",
            source,
        )

    def test_41_constructor_candidate_is_not_public_authority_evidence(self):
        auth = authority("assessment-submission-r1")
        self.assertFalse(
            hasattr(auth, "resource_reference")
        )
        self.assertEqual(
            object.__getattribute__(auth, "_establishments_by_attempt"),
            {},
        )

    def test_42_structurally_valid_exact_business_context_is_bounded_input(self):
        constructed = business_context_result()
        result = establish(result=constructed)
        self.assertIs(result.status, ESTABLISHED)
        self.assertEqual(
            result.establishment_evidence.attempt_reference,
            "attempt-alpha",
        )

    def test_43_internal_map_incoherence_fails_closed(self):
        auth = authority("assessment-submission-r1")
        self.assertIs(establish(auth).status, ESTABLISHED)
        by_resource = object.__getattribute__(
            auth, "_establishments_by_resource_reference"
        )
        by_resource.clear()
        result = establish(auth)
        self.assertIs(result.status, MISMATCH)
        self.assert_failure_payloads(result)

    def test_44_dataclasses_are_slotted_and_exact_output_types_are_fresh(self):
        result = establish()
        for value in (
            result,
            result.provisional_resource,
            result.establishment_evidence,
        ):
            with self.subTest(value=type(value)):
                self.assertFalse(hasattr(value, "__dict__"))
        copied = replace(result)
        self.assertEqual(copied, result)
        self.assertIsNot(copied, result)

    def assert_same_a_mismatch(self, changed_context):
        auth = authority("assessment-submission-r1", "assessment-submission-r2")
        first = establish(auth)
        changed = establish(
            auth,
            result=business_context_result(context=changed_context),
        )
        retry = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(changed.status, MISMATCH)
        self.assert_failure_payloads(changed)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(
            retry.provisional_resource.resource_reference,
            "assessment-submission-r1",
        )

    def assert_failure_payloads(self, result):
        self.assertIsNone(result.provisional_resource)
        self.assertIsNone(result.establishment_evidence)


if __name__ == "__main__":
    unittest.main()
