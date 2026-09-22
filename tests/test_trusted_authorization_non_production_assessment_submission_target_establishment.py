import dataclasses
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_target_establishment as target_module  # noqa: E402
from trusted_authorization.models import ResourceClass  # noqa: E402
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
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult,
    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionAssessmentSubmissionLifecycleState,
)
from trusted_authorization.non_production_assessment_submission_target_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
    NonProductionAssessmentSubmissionTargetEstablishmentEvidence,
    NonProductionAssessmentSubmissionTargetEstablishmentResult,
    NonProductionAssessmentSubmissionTargetEstablishmentStatus,
    NonProductionAssessmentSubmissionTargetLegitimacyFact,
)


ESTABLISHED = NonProductionAssessmentSubmissionTargetEstablishmentStatus.ESTABLISHED
REUSED = NonProductionAssessmentSubmissionTargetEstablishmentStatus.REUSED
MALFORMED = NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED
BUSINESS_CONTEXT_NOT_READY = (
    NonProductionAssessmentSubmissionTargetEstablishmentStatus.
    BUSINESS_CONTEXT_NOT_READY
)
UNSUPPORTED_OPERATION = (
    NonProductionAssessmentSubmissionTargetEstablishmentStatus.
    UNSUPPORTED_OPERATION
)
MISMATCH = NonProductionAssessmentSubmissionTargetEstablishmentStatus.MISMATCH
COLLISION = NonProductionAssessmentSubmissionTargetEstablishmentStatus.COLLISION
ALLOCATION_UNAVAILABLE = (
    NonProductionAssessmentSubmissionTargetEstablishmentStatus.
    ALLOCATION_UNAVAILABLE
)
BC_READY = NonProductionAssessmentSubmissionBusinessContextStatus.READY
BC_MALFORMED = NonProductionAssessmentSubmissionBusinessContextStatus.MALFORMED
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)
_DEFAULT = object()


class StringSubclass(str):
    pass


class ResultSubclass(NonProductionAssessmentSubmissionBusinessContextResult):
    pass


class ContextSubclass(NonProductionAssessmentSubmissionBusinessContext):
    pass


class ForeignStatus(Enum):
    READY = "READY"


class HostileObject:
    reads = 0

    def __getattribute__(self, name):
        type(self).reads += 1
        raise AssertionError("foreign attributes must not be read")


def business_context(**overrides):
    values = {
        "attempt_reference": "attempt-alpha",
        "principal_id": "principal-alpha",
        "engagement_reference": "engagement-alpha",
        "business_entity_id": "business-alpha",
        "protected_operation": PROTECTED_ASSESSMENT,
        "principal_authority_reference": "principal-authority",
        "engagement_authority_reference": "engagement-authority",
        "engagement_establishment_provenance_reference": "engagement-provenance",
        "participation_authority_reference": "participation-authority",
        "participation_provenance_reference": "participation-provenance",
        "business_entity_authority_reference": "business-authority",
    }
    values.update(overrides)
    return NonProductionAssessmentSubmissionBusinessContext(**values)


def business_context_result(*, status=BC_READY, context=_DEFAULT):
    if context is _DEFAULT:
        context = business_context() if status is BC_READY else None
    return NonProductionAssessmentSubmissionBusinessContextResult(
        status=status,
        business_context=context,
    )


def authority(*candidates):
    if candidates:
        return NonProductionAssessmentSubmissionTargetEstablishmentAuthority(
            candidate_resource_references=candidates,
        )
    return NonProductionAssessmentSubmissionTargetEstablishmentAuthority()


def establish(auth=None, *, context_result=_DEFAULT):
    if auth is None:
        auth = authority("resource-alpha")
    if context_result is _DEFAULT:
        context_result = business_context_result()
    return auth.establish_assessment_submission_target(
        business_context_result=context_result,
    )


def provisional_authority(auth):
    return object.__getattribute__(auth, "_provisional_establishment_authority")


def provisional_snapshot(auth, attempt="attempt-alpha"):
    upstream = provisional_authority(auth)
    return object.__getattribute__(upstream, "_establishments_by_attempt")[attempt]


class TargetEstablishmentTests(unittest.TestCase):
    def assert_failure(self, result, status):
        self.assertIs(result.status, status)
        self.assertIsNone(result.target_fact)
        self.assertIsNone(result.establishment_evidence)

    def test_01_public_surface_is_exactly_five_types(self):
        public_types = {
            name
            for name, value in vars(target_module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(
            public_types,
            {
                "NonProductionAssessmentSubmissionTargetEstablishmentAuthority",
                "NonProductionAssessmentSubmissionTargetLegitimacyFact",
                "NonProductionAssessmentSubmissionTargetEstablishmentEvidence",
                "NonProductionAssessmentSubmissionTargetEstablishmentStatus",
                "NonProductionAssessmentSubmissionTargetEstablishmentResult",
            },
        )

    def test_02_constructor_and_method_signatures_are_exact(self):
        self.assertEqual(
            str(inspect.signature(NonProductionAssessmentSubmissionTargetEstablishmentAuthority)),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) -> 'None'",
        )
        self.assertEqual(
            str(inspect.signature(
                NonProductionAssessmentSubmissionTargetEstablishmentAuthority.
                establish_assessment_submission_target
            )),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionTargetEstablishmentResult'",
        )

    def test_03_public_api_has_no_dependency_or_evidence_injection(self):
        constructor = inspect.signature(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority
        )
        method = inspect.signature(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority.
            establish_assessment_submission_target
        )
        self.assertEqual(tuple(constructor.parameters), ("candidate_resource_references",))
        self.assertEqual(tuple(method.parameters), ("self", "business_context_result"))
        public_methods = {
            name
            for name, value in inspect.getmembers(
                NonProductionAssessmentSubmissionTargetEstablishmentAuthority
            )
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(public_methods, {"establish_assessment_submission_target"})

    def test_04_exact_private_provisional_authority_is_retained(self):
        auth = authority("resource-alpha")
        owned = provisional_authority(auth)
        self.assertIs(type(owned), NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority)
        self.assertIs(provisional_authority(auth), owned)

    def test_05_first_success_returns_exact_output_types(self):
        result = establish()
        self.assertIs(result.status, ESTABLISHED)
        self.assertIs(type(result), NonProductionAssessmentSubmissionTargetEstablishmentResult)
        self.assertIs(type(result.target_fact), NonProductionAssessmentSubmissionTargetLegitimacyFact)
        self.assertIs(type(result.establishment_evidence), NonProductionAssessmentSubmissionTargetEstablishmentEvidence)

    def test_06_fact_fields_and_values_are_exact(self):
        fact = establish().target_fact
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(fact))),
            (
                "attempt_reference", "engagement_reference", "business_entity_id",
                "resource_reference", "resource_class", "protected_operation",
            ),
        )
        self.assertEqual(fact.attempt_reference, "attempt-alpha")
        self.assertEqual(fact.engagement_reference, "engagement-alpha")
        self.assertEqual(fact.business_entity_id, "business-alpha")
        self.assertEqual(fact.resource_reference, "resource-alpha")
        self.assertIs(fact.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(fact.protected_operation, PROTECTED_ASSESSMENT)

    def test_07_evidence_fields_are_exact_and_complete(self):
        evidence = establish().establishment_evidence
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(evidence))),
            (
                "attempt_reference", "resource_reference", "principal_id",
                "engagement_reference", "business_entity_id", "protected_operation",
                "principal_authority_reference", "engagement_authority_reference",
                "engagement_establishment_provenance_reference",
                "participation_authority_reference", "participation_provenance_reference",
                "business_entity_authority_reference", "allocation_authority_reference",
                "allocation_provenance_reference", "binding_authority_reference",
                "binding_provenance_reference", "resource_class",
                "resource_lifecycle_state", "lifecycle_authority_reference",
                "lifecycle_provenance_reference", "target_authority_reference",
                "target_provenance_reference", "target_governance_reference",
            ),
        )
        self.assertEqual(evidence.principal_id, "principal-alpha")
        self.assertEqual(evidence.allocation_authority_reference, "non-production-assessment-submission-resource-allocation-authority")
        self.assertEqual(evidence.binding_authority_reference, "non-production-assessment-submission-attempt-resource-binding-authority")
        self.assertEqual(evidence.lifecycle_authority_reference, "non-production-assessment-submission-resource-lifecycle-establishment-authority")
        self.assertIs(evidence.resource_lifecycle_state, NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL)

    def test_08_fixed_target_authority_governance_and_provenance(self):
        evidence = establish().establishment_evidence
        self.assertEqual(evidence.target_authority_reference, "non-production-assessment-submission-resource-target-authority")
        self.assertEqual(evidence.target_governance_reference, "trusted-authorization-resource-reference-provenance-governance-v1")
        self.assertEqual(evidence.target_provenance_reference, "non-production-assessment-submission-target-establishment-provenance-1")

    def test_09_status_and_result_contracts_are_exact(self):
        self.assertEqual(
            tuple(NonProductionAssessmentSubmissionTargetEstablishmentStatus.__members__),
            (
                "ESTABLISHED", "REUSED", "MALFORMED",
                "BUSINESS_CONTEXT_NOT_READY", "UNSUPPORTED_OPERATION",
                "MISMATCH", "COLLISION", "ALLOCATION_UNAVAILABLE",
            ),
        )
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(NonProductionAssessmentSubmissionTargetEstablishmentResult)),
            ("status", "target_fact", "establishment_evidence"),
        )

    def test_10_exact_retry_reuses_event_with_fresh_outputs(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        retry = establish(auth)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(first.target_fact, retry.target_fact)
        self.assertEqual(first.establishment_evidence, retry.establishment_evidence)
        self.assertIsNot(first, retry)
        self.assertIsNot(first.target_fact, retry.target_fact)
        self.assertIsNot(first.establishment_evidence, retry.establishment_evidence)

    def test_11_retry_preserves_r_and_target_provenance_without_new_event(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        retry = establish(auth)
        beta = establish(auth, context_result=business_context_result(
            context=business_context(attempt_reference="attempt-beta")
        ))
        self.assertEqual(retry.target_fact.resource_reference, first.target_fact.resource_reference)
        self.assertEqual(retry.establishment_evidence.target_provenance_reference, first.establishment_evidence.target_provenance_reference)
        self.assertEqual(beta.establishment_evidence.target_provenance_reference, "non-production-assessment-submission-target-establishment-provenance-2")

    def test_12_distinct_valid_events_have_unique_target_provenance(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        second = establish(auth, context_result=business_context_result(
            context=business_context(attempt_reference="attempt-beta")
        ))
        self.assertIs(second.status, ESTABLISHED)
        self.assertNotEqual(first.establishment_evidence.target_provenance_reference, second.establishment_evidence.target_provenance_reference)

    def test_13_both_indexes_reference_one_canonical_snapshot(self):
        auth = authority("resource-alpha")
        establish(auth)
        by_attempt = object.__getattribute__(auth, "_targets_by_attempt")
        by_resource = object.__getattribute__(auth, "_targets_by_resource_reference")
        self.assertIs(by_attempt["attempt-alpha"], by_resource["resource-alpha"])

    def test_14_same_r_conflicting_a_is_collision_without_target_state(self):
        auth = authority("resource-alpha")
        establish(auth)
        beta_context = business_context_result(context=business_context(attempt_reference="attempt-beta"))
        independent_upstream = (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority(
                candidate_resource_references=("resource-alpha",)
            )
        )
        beta_result = independent_upstream.establish_assessment_submission_provisional_resource(
            business_context_result=beta_context
        )
        with patch.object(
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority,
            "establish_assessment_submission_provisional_resource",
            return_value=beta_result,
        ):
            collision = establish(auth, context_result=beta_context)
        self.assert_failure(collision, COLLISION)
        self.assertNotIn("attempt-beta", object.__getattribute__(auth, "_targets_by_attempt"))

    def test_15_same_a_different_r_is_target_mismatch(self):
        auth = authority("resource-alpha")
        establish(auth)
        independent_upstream = (
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority(
                candidate_resource_references=("resource-beta",)
            )
        )
        different_r = independent_upstream.establish_assessment_submission_provisional_resource(
            business_context_result=business_context_result()
        )
        with patch.object(
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority,
            "establish_assessment_submission_provisional_resource",
            return_value=different_r,
        ):
            result = establish(auth)
        self.assert_failure(result, MISMATCH)
        self.assertEqual(
            object.__getattribute__(auth, "_targets_by_attempt")["attempt-alpha"].resource_reference,
            "resource-alpha",
        )

    def test_16_changed_principal_engagement_or_business_is_mismatch(self):
        changes = (
            {"principal_id": "principal-beta"},
            {"engagement_reference": "engagement-beta"},
            {"business_entity_id": "business-beta"},
        )
        for change in changes:
            with self.subTest(change=change):
                auth = authority("resource-alpha", "resource-beta")
                establish(auth)
                result = establish(auth, context_result=business_context_result(context=business_context(**change)))
                self.assert_failure(result, MISMATCH)

    def test_17_each_business_context_authority_rotation_is_mismatch(self):
        fields = (
            "principal_authority_reference", "engagement_authority_reference",
            "engagement_establishment_provenance_reference",
            "participation_authority_reference", "participation_provenance_reference",
            "business_entity_authority_reference",
        )
        for field in fields:
            with self.subTest(field=field):
                auth = authority("resource-alpha", "resource-beta")
                establish(auth)
                changed = business_context(**{field: f"rotated-{field}"})
                self.assert_failure(establish(auth, context_result=business_context_result(context=changed)), MISMATCH)

    def test_18_allocation_binding_and_lifecycle_rotation_are_mismatch(self):
        fields = (
            "allocation_authority_reference", "allocation_provenance_reference",
            "binding_authority_reference", "binding_provenance_reference",
            "lifecycle_authority_reference", "lifecycle_provenance_reference",
        )
        for field in fields:
            with self.subTest(field=field):
                auth = authority("resource-alpha")
                establish(auth)
                evidence = object.__getattribute__(provisional_snapshot(auth), "establishment_evidence")
                object.__setattr__(evidence, field, f"rotated-{field}")
                self.assert_failure(establish(auth), MISMATCH)

    def test_18_foreign_inputs_fail_without_attribute_reads(self):
        HostileObject.reads = 0
        for value in (None, "raw", {}, object(), HostileObject()):
            with self.subTest(value=type(value)):
                self.assert_failure(establish(context_result=value), MALFORMED)
        self.assertEqual(HostileObject.reads, 0)

    def test_19_result_and_context_subclasses_are_rejected(self):
        result_subclass = ResultSubclass(status=BC_READY, business_context=business_context())
        context_subclass = ContextSubclass(**{
            field.name: getattr(business_context(), field.name)
            for field in dataclasses.fields(NonProductionAssessmentSubmissionBusinessContext)
        })
        self.assert_failure(establish(context_result=result_subclass), MALFORMED)
        self.assert_failure(establish(context_result=business_context_result(context=context_subclass)), MALFORMED)

    def test_20_non_ready_and_malformed_ready_shapes_fail_closed(self):
        self.assert_failure(
            establish(context_result=business_context_result(status=BC_MALFORMED)),
            BUSINESS_CONTEXT_NOT_READY,
        )
        self.assert_failure(
            establish(context_result=business_context_result(context=None)),
            MALFORMED,
        )
        malformed = NonProductionAssessmentSubmissionBusinessContextResult(
            status=ForeignStatus.READY,
            business_context=business_context(),
        )
        self.assert_failure(establish(context_result=malformed), MALFORMED)

    def test_21_every_string_field_rejects_blank_whitespace_and_subclass(self):
        fields = (
            "attempt_reference", "principal_id", "engagement_reference",
            "business_entity_id", "principal_authority_reference",
            "engagement_authority_reference",
            "engagement_establishment_provenance_reference",
            "participation_authority_reference", "participation_provenance_reference",
            "business_entity_authority_reference",
        )
        for field in fields:
            for value in ("", " value", "value ", StringSubclass("value")):
                with self.subTest(field=field, value=repr(value)):
                    malformed = business_context(**{field: value})
                    self.assert_failure(establish(context_result=business_context_result(context=malformed)), MALFORMED)

    def test_22_wrong_operation_type_is_malformed(self):
        context = business_context(protected_operation="PROTECTED_ASSESSMENT_SUBMISSION")
        self.assert_failure(establish(context_result=business_context_result(context=context)), MALFORMED)

    def test_23_candidate_references_are_not_target_authority(self):
        auth = authority("resource-alpha")
        self.assertEqual(object.__getattribute__(auth, "_targets_by_attempt"), {})
        self.assertFalse(hasattr(auth, "resource_reference"))

    def test_24_all_six_upstream_failures_map_one_to_one_without_payload(self):
        cases = (
            (NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.MALFORMED, MALFORMED),
            (NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.BUSINESS_CONTEXT_NOT_READY, BUSINESS_CONTEXT_NOT_READY),
            (NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.UNSUPPORTED_OPERATION, UNSUPPORTED_OPERATION),
            (NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.MISMATCH, MISMATCH),
            (NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.COLLISION, COLLISION),
            (NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.ALLOCATION_UNAVAILABLE, ALLOCATION_UNAVAILABLE),
        )
        for upstream_status, expected in cases:
            with self.subTest(status=upstream_status):
                auth = authority("resource-alpha")
                upstream_result = NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult(status=upstream_status)
                with patch.object(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority,
                    "establish_assessment_submission_provisional_resource",
                    return_value=upstream_result,
                ):
                    result = establish(auth)
                self.assert_failure(result, expected)
                self.assertEqual(object.__getattribute__(auth, "_targets_by_attempt"), {})

    def test_25_allocation_unavailable_is_reachable_without_target_consumption(self):
        auth = NonProductionAssessmentSubmissionTargetEstablishmentAuthority(candidate_resource_references=())
        self.assert_failure(establish(auth), ALLOCATION_UNAVAILABLE)
        self.assertEqual(object.__getattribute__(auth, "_targets_by_attempt"), {})
        self.assertEqual(object.__getattribute__(auth, "_next_target_provenance_index"), 1)

    def test_26_malformed_candidate_is_mapped_without_target_consumption(self):
        auth = authority("")
        self.assert_failure(establish(auth), MALFORMED)
        self.assertEqual(object.__getattribute__(auth, "_targets_by_resource_reference"), {})
        self.assertEqual(object.__getattribute__(auth, "_next_target_provenance_index"), 1)

    def test_27_success_looking_upstream_payload_must_be_exact(self):
        auth = authority("resource-alpha")
        for upstream_result in (object(), {"status": "ESTABLISHED"}):
            with self.subTest(value=type(upstream_result)):
                with patch.object(
                    NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority,
                    "establish_assessment_submission_provisional_resource",
                    return_value=upstream_result,
                ):
                    self.assert_failure(establish(auth), MALFORMED)

    def test_28_success_status_without_exact_payloads_is_malformed(self):
        auth = authority("resource-alpha")
        upstream_result = NonProductionAssessmentSubmissionProvisionalResourceEstablishmentResult(
            status=NonProductionAssessmentSubmissionProvisionalResourceEstablishmentStatus.ESTABLISHED,
        )
        with patch.object(
            NonProductionAssessmentSubmissionProvisionalResourceEstablishmentAuthority,
            "establish_assessment_submission_provisional_resource",
            return_value=upstream_result,
        ):
            self.assert_failure(establish(auth), MALFORMED)

    def test_29_resource_class_mismatch_fails_closed(self):
        auth = authority("resource-alpha")
        upstream = provisional_authority(auth)
        upstream.establish_assessment_submission_provisional_resource(
            business_context_result=business_context_result()
        )
        snapshot = provisional_snapshot(auth)
        resource = object.__getattribute__(snapshot, "provisional_resource")
        evidence = object.__getattribute__(snapshot, "establishment_evidence")
        object.__setattr__(resource, "resource_class", object())
        object.__setattr__(evidence, "resource_class", object())
        self.assert_failure(establish(auth), MALFORMED)

    def test_30_lifecycle_state_mismatch_fails_closed(self):
        auth = authority("resource-alpha")
        upstream = provisional_authority(auth)
        upstream.establish_assessment_submission_provisional_resource(
            business_context_result=business_context_result()
        )
        snapshot = provisional_snapshot(auth)
        resource = object.__getattribute__(snapshot, "provisional_resource")
        evidence = object.__getattribute__(snapshot, "establishment_evidence")
        object.__setattr__(resource, "lifecycle_state", object())
        object.__setattr__(evidence, "lifecycle_state", object())
        self.assert_failure(establish(auth), MALFORMED)

    def test_31_precommit_failure_preserves_upstream_for_exact_recovery(self):
        auth = authority("resource-alpha", "resource-beta")
        original_type = target_module.NonProductionAssessmentSubmissionTargetLegitimacyFact
        with patch.object(
            target_module,
            "NonProductionAssessmentSubmissionTargetLegitimacyFact",
            side_effect=RuntimeError("controlled target precommit failure"),
        ):
            failed = establish(auth)
        self.assert_failure(failed, MALFORMED)
        self.assertEqual(object.__getattribute__(auth, "_targets_by_attempt"), {})
        self.assertEqual(object.__getattribute__(auth, "_next_target_provenance_index"), 1)
        self.assertIs(target_module.NonProductionAssessmentSubmissionTargetLegitimacyFact, original_type)
        recovered = establish(auth)
        self.assertIs(recovered.status, ESTABLISHED)
        self.assertEqual(recovered.target_fact.resource_reference, "resource-alpha")
        self.assertEqual(recovered.establishment_evidence.lifecycle_provenance_reference, "non-production-assessment-submission-provisional-resource-establishment-provenance-1")
        self.assertEqual(recovered.establishment_evidence.target_provenance_reference, "non-production-assessment-submission-target-establishment-provenance-1")

    def test_32_returned_mutation_cannot_change_canonical_state(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        object.__setattr__(first.target_fact, "resource_reference", "attacker-resource")
        object.__setattr__(first.establishment_evidence, "target_provenance_reference", "attacker-provenance")
        object.__setattr__(first, "target_fact", None)
        retry = establish(auth)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(retry.target_fact.resource_reference, "resource-alpha")
        self.assertEqual(retry.establishment_evidence.target_provenance_reference, "non-production-assessment-submission-target-establishment-provenance-1")

    def test_33_outputs_are_frozen_and_not_internal_snapshots(self):
        auth = authority("resource-alpha")
        result = establish(auth)
        with self.assertRaises(FrozenInstanceError):
            result.target_fact.resource_reference = "attacker"
        with self.assertRaises(FrozenInstanceError):
            result.establishment_evidence.attempt_reference = "attacker"
        snapshot = object.__getattribute__(auth, "_targets_by_attempt")["attempt-alpha"]
        self.assertIsNot(result.target_fact, snapshot)
        self.assertIsNot(result.establishment_evidence, snapshot)

    def test_34_instance_state_is_isolated(self):
        first_auth = authority("shared-resource")
        second_auth = authority("shared-resource")
        first = establish(first_auth)
        second = establish(second_auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(second.status, ESTABLISHED)
        self.assertIsNot(
            object.__getattribute__(first_auth, "_targets_by_attempt"),
            object.__getattribute__(second_auth, "_targets_by_attempt"),
        )

    def test_35_private_dependency_tampering_fails_closed(self):
        auth = authority("resource-alpha")
        object.__setattr__(auth, "_provisional_establishment_authority", object())
        self.assert_failure(establish(auth), MALFORMED)

    def test_36_no_caller_authority_arguments_are_accepted(self):
        auth = authority("resource-alpha")
        forbidden = (
            "resource_reference", "attempt_reference", "engagement_reference",
            "business_entity_id", "provisional_result", "target_fact",
            "establishment_evidence", "authority_reference", "provenance_reference",
        )
        for name in forbidden:
            with self.subTest(name=name):
                with self.assertRaises(TypeError):
                    auth.establish_assessment_submission_target(
                        business_context_result=business_context_result(),
                        **{name: object()},
                    )

    def test_37_failure_does_not_consume_target_provenance(self):
        auth = authority("resource-alpha")
        self.assert_failure(establish(auth, context_result=None), MALFORMED)
        success = establish(auth)
        self.assertEqual(success.establishment_evidence.target_provenance_reference, "non-production-assessment-submission-target-establishment-provenance-1")

    def test_38_internal_attempt_index_incoherence_fails_closed(self):
        auth = authority("resource-alpha")
        establish(auth)
        object.__getattribute__(auth, "_targets_by_resource_reference").clear()
        self.assert_failure(establish(auth), MISMATCH)

    def test_39_target_does_not_reselect_upstream_resource(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        retry = establish(auth)
        self.assertEqual(first.target_fact.resource_reference, "resource-alpha")
        self.assertEqual(retry.target_fact.resource_reference, "resource-alpha")
        upstream = provisional_authority(auth)
        allocation = object.__getattribute__(upstream, "_allocation_binding_authority")
        self.assertEqual(object.__getattribute__(allocation, "_next_candidate_index"), 1)

    def test_40_source_has_no_forbidden_downstream_imports(self):
        source = (Path(__file__).resolve().parents[1] / "src" / "trusted_authorization" / "non_production_assessment_submission_target_establishment.py").read_text(encoding="utf-8")
        forbidden = (
            "non_production_assessment_submission_target_handoff",
            "resource_identity_source", "GovernedResource", "Membership",
            "Entitlement", "evaluator", "ALLOW", "DENY", "SUBMITTED",
            "DynamoDB", "sqlite", "threading",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_41_old_lifecycle_is_only_used_for_enum_type(self):
        source = (Path(__file__).resolve().parents[1] / "src" / "trusted_authorization" / "non_production_assessment_submission_target_establishment.py").read_text(encoding="utf-8")
        self.assertIn("NonProductionAssessmentSubmissionLifecycleState as _LifecycleState", source)
        self.assertNotIn("establish_non_production_provisional_assessment_submission_resource", source)

    def test_42_exact_structural_business_context_is_bounded_start(self):
        result = establish(context_result=business_context_result())
        self.assertIs(result.status, ESTABLISHED)
        self.assertEqual(result.establishment_evidence.attempt_reference, "attempt-alpha")

    def test_43_public_dataclasses_cannot_be_submitted_as_authority(self):
        fact = establish().target_fact
        evidence = establish().establishment_evidence
        result = NonProductionAssessmentSubmissionTargetEstablishmentResult(
            status=ESTABLISHED,
            target_fact=fact,
            establishment_evidence=evidence,
        )
        auth = authority("resource-alpha")
        for value in (fact, evidence, result):
            with self.subTest(value=type(value)):
                self.assert_failure(establish(auth, context_result=value), MALFORMED)

    def test_44_dataclasses_are_slotted_and_carry_no_mutable_nested_payload(self):
        result = establish()
        for value in (result, result.target_fact, result.establishment_evidence):
            with self.subTest(value=type(value)):
                self.assertFalse(hasattr(value, "__dict__"))
        for field in dataclasses.fields(type(result.establishment_evidence)):
            self.assertNotIsInstance(getattr(result.establishment_evidence, field.name), (dict, list, set))


if __name__ == "__main__":
    unittest.main()
