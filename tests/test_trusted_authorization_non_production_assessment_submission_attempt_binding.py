import ast
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_attempt_binding as binding_module  # noqa: E402
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    PrincipalMapping,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_engagement_participation_source import (  # noqa: E402
    NonProductionAssessmentEngagementParticipationAuthorityEvidence,
    NonProductionAssessmentEngagementParticipationLifecycleState,
    NonProductionAssessmentEngagementParticipationLookupResult,
    NonProductionAssessmentEngagementParticipationLookupStatus,
)
from trusted_authorization.non_production_assessment_engagement_source import (  # noqa: E402
    NonProductionAssessmentEngagementAuthorityEvidence,
    NonProductionAssessmentEngagementLifecycleState,
    NonProductionAssessmentEngagementLookupResult,
    NonProductionAssessmentEngagementLookupStatus,
)
from trusted_authorization.non_production_assessment_submission_attempt_binding import (  # noqa: E402
    NonProductionAssessmentSubmissionAttemptBinding,
    NonProductionAssessmentSubmissionAttemptBindingDeriver,
    NonProductionAssessmentSubmissionAttemptBindingResult,
    NonProductionAssessmentSubmissionAttemptBindingStatus,
    NonProductionAssessmentSubmissionAttemptContext,
)


READY = NonProductionAssessmentSubmissionAttemptBindingStatus.READY
MALFORMED = NonProductionAssessmentSubmissionAttemptBindingStatus.MALFORMED
ENGAGEMENT_NOT_READY = (
    NonProductionAssessmentSubmissionAttemptBindingStatus.ENGAGEMENT_NOT_READY
)
PARTICIPATION_NOT_READY = (
    NonProductionAssessmentSubmissionAttemptBindingStatus.PARTICIPATION_NOT_READY
)
UNSUPPORTED_OPERATION = (
    NonProductionAssessmentSubmissionAttemptBindingStatus.UNSUPPORTED_OPERATION
)
MISMATCH = NonProductionAssessmentSubmissionAttemptBindingStatus.MISMATCH
REPLAYED = NonProductionAssessmentSubmissionAttemptBindingStatus.REPLAYED
REBINDING = NonProductionAssessmentSubmissionAttemptBindingStatus.REBINDING
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)


def attempt(
    attempt_reference="attempt-alpha",
    principal_id="principal-alpha",
    candidate_engagement_reference="engagement-alpha",
    protected_operation=PROTECTED_ASSESSMENT,
):
    return NonProductionAssessmentSubmissionAttemptContext(
        attempt_reference=attempt_reference,
        principal_id=principal_id,
        candidate_engagement_reference=candidate_engagement_reference,
        protected_operation=protected_operation,
    )


def principal_record(
    authority_reference="principal-authority",
    state=AuthorityRecordState.ACTIVE,
    principal_id="principal-alpha",
):
    return PrincipalMapping(
        authority_reference=authority_reference,
        state=state,
        subject_provider="provider-alpha",
        subject="subject-alpha",
        principal_id=principal_id,
    )


def principal_result(record=None, status=AuthorityLookupStatus.FOUND, records=None):
    if records is not None:
        return AuthorityLookupResult(status=status, records=records)
    if record is None:
        record = principal_record()
    return AuthorityLookupResult(status=status, records=(record,))


def engagement_record(
    authority_reference="engagement-authority",
    state=AuthorityRecordState.ACTIVE,
    engagement_reference="engagement-alpha",
    business_entity_id="business-alpha",
    lifecycle_state=NonProductionAssessmentEngagementLifecycleState.CURRENT,
    establishment_provenance_reference="engagement-provenance",
):
    return NonProductionAssessmentEngagementAuthorityEvidence(
        authority_reference=authority_reference,
        state=state,
        engagement_reference=engagement_reference,
        business_entity_id=business_entity_id,
        lifecycle_state=lifecycle_state,
        establishment_provenance_reference=establishment_provenance_reference,
    )


def engagement_result(
    status=NonProductionAssessmentEngagementLookupStatus.FOUND,
    records=None,
):
    if records is None:
        records = (engagement_record(),) if status.name == "FOUND" else ()
    return NonProductionAssessmentEngagementLookupResult(
        status=status,
        records=records,
    )


def participation_record(
    authority_reference="participation-authority",
    state=AuthorityRecordState.ACTIVE,
    principal_id="principal-alpha",
    engagement_reference="engagement-alpha",
    lifecycle_state=(
        NonProductionAssessmentEngagementParticipationLifecycleState.CURRENT
    ),
    participation_provenance_reference="participation-provenance",
):
    return NonProductionAssessmentEngagementParticipationAuthorityEvidence(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        engagement_reference=engagement_reference,
        lifecycle_state=lifecycle_state,
        participation_provenance_reference=participation_provenance_reference,
    )


def participation_result(
    status=NonProductionAssessmentEngagementParticipationLookupStatus.FOUND,
    records=None,
):
    if records is None:
        records = (participation_record(),) if status.name == "FOUND" else ()
    return NonProductionAssessmentEngagementParticipationLookupResult(
        status=status,
        records=records,
    )


def derive(
    *,
    deriver=None,
    attempt_context=None,
    principal_mapping_result=None,
    engagement_lookup_result=None,
    participation_lookup_result=None,
):
    if deriver is None:
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
    if attempt_context is None:
        attempt_context = attempt()
    if principal_mapping_result is None:
        principal_mapping_result = principal_result()
    if engagement_lookup_result is None:
        engagement_lookup_result = engagement_result()
    if participation_lookup_result is None:
        participation_lookup_result = participation_result()
    return deriver.derive_assessment_submission_attempt_binding(
        attempt_context=attempt_context,
        principal_mapping_result=principal_mapping_result,
        engagement_result=engagement_lookup_result,
        participation_result=participation_lookup_result,
    )


class NonProductionAssessmentSubmissionAttemptBindingTests(unittest.TestCase):
    def test_01_valid_first_derivation_returns_ready(self):
        result = derive()

        self.assertEqual(result.status, READY)
        self.assertIsInstance(
            result.binding,
            NonProductionAssessmentSubmissionAttemptBinding,
        )

    def test_02_ready_returns_exact_fresh_binding(self):
        result = derive()

        self.assertIs(type(result.binding), NonProductionAssessmentSubmissionAttemptBinding)
        self.assertEqual(result.binding.attempt_reference, "attempt-alpha")
        self.assertEqual(result.binding.engagement_reference, "engagement-alpha")

    def test_03_binding_preserves_structural_provenance(self):
        result = derive()
        binding = result.binding

        self.assertEqual(binding.attempt_reference, "attempt-alpha")
        self.assertEqual(binding.principal_id, "principal-alpha")
        self.assertEqual(binding.candidate_engagement_reference, "engagement-alpha")
        self.assertEqual(binding.engagement_reference, "engagement-alpha")
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

    def test_04_candidate_e_must_equal_resolved_e(self):
        result = derive(
            attempt_context=attempt(candidate_engagement_reference="engagement-beta")
        )

        self.assertEqual(result.status, MISMATCH)
        self.assertIsNone(result.binding)

    def test_05_candidate_e_must_equal_participation_e(self):
        result = derive(
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            )
        )

        self.assertEqual(result.status, MISMATCH)

    def test_06_resolved_e_must_equal_participation_e(self):
        result = derive(
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
        )

        self.assertEqual(result.status, MISMATCH)

    def test_07_authoritative_p_must_equal_attempt_p(self):
        result = derive(attempt_context=attempt(principal_id="principal-beta"))

        self.assertEqual(result.status, MISMATCH)

    def test_08_participation_p_must_equal_authoritative_p(self):
        result = derive(
            participation_lookup_result=participation_result(
                records=(participation_record(principal_id="principal-beta"),)
            )
        )

        self.assertEqual(result.status, MISMATCH)

    def test_09_same_b_different_e_cannot_substitute(self):
        result = derive(
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        engagement_reference="engagement-beta",
                        business_entity_id="business-alpha",
                    ),
                )
            ),
        )

        self.assertEqual(result.status, MISMATCH)

    def test_10_cross_b_e_cannot_substitute(self):
        result = derive(
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        engagement_reference="engagement-beta",
                        business_entity_id="business-beta",
                    ),
                )
            ),
        )

        self.assertEqual(result.status, MISMATCH)

    def test_11_no_single_participation_shortcut(self):
        result = derive(
            attempt_context=attempt(candidate_engagement_reference="")
        )

        self.assertEqual(result.status, MALFORMED)

    def test_12_multiple_participation_scenario_is_exact_e_scoped(self):
        alpha = derive().status
        beta = derive(
            attempt_context=attempt(
                attempt_reference="attempt-beta",
                candidate_engagement_reference="engagement-beta",
            ),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        ).status
        mismatch = derive(
            attempt_context=attempt(
                attempt_reference="attempt-gamma",
                candidate_engagement_reference="engagement-alpha",
            ),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-alpha"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        ).status

        self.assertEqual(alpha, READY)
        self.assertEqual(beta, READY)
        self.assertEqual(mismatch, MISMATCH)

    def test_13_invalid_attempt_type_returns_malformed(self):
        self.assertEqual(derive(attempt_context=object()).status, MALFORMED)

    def test_14_attempt_subclass_returns_malformed(self):
        class AttemptSubclass(NonProductionAssessmentSubmissionAttemptContext):
            pass

        result = derive(
            attempt_context=AttemptSubclass(
                attempt_reference="attempt-alpha",
                principal_id="principal-alpha",
                candidate_engagement_reference="engagement-alpha",
                protected_operation=PROTECTED_ASSESSMENT,
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_15_invalid_attempt_reference_returns_malformed(self):
        self.assertEqual(
            derive(attempt_context=attempt(attempt_reference=None)).status,
            MALFORMED,
        )

    def test_16_blank_attempt_reference_returns_malformed(self):
        self.assertEqual(
            derive(attempt_context=attempt(attempt_reference="   ")).status,
            MALFORMED,
        )

    def test_17_edge_whitespace_attempt_reference_returns_malformed(self):
        self.assertEqual(
            derive(attempt_context=attempt(attempt_reference=" attempt-alpha")).status,
            MALFORMED,
        )
        self.assertEqual(
            derive(attempt_context=attempt(attempt_reference="attempt-alpha ")).status,
            MALFORMED,
        )

    def test_18_attempt_reference_str_subclass_returns_malformed(self):
        class HostileStr(str):
            pass

        self.assertEqual(
            derive(
                attempt_context=attempt(attempt_reference=HostileStr("attempt-alpha"))
            ).status,
            MALFORMED,
        )

    def test_19_invalid_principal_id_returns_malformed(self):
        self.assertEqual(
            derive(attempt_context=attempt(principal_id="")).status,
            MALFORMED,
        )

    def test_20_principal_id_str_subclass_returns_malformed(self):
        class HostileStr(str):
            pass

        self.assertEqual(
            derive(attempt_context=attempt(principal_id=HostileStr("principal-alpha"))).status,
            MALFORMED,
        )

    def test_21_invalid_candidate_e_returns_malformed(self):
        self.assertEqual(
            derive(attempt_context=attempt(candidate_engagement_reference=None)).status,
            MALFORMED,
        )

    def test_22_candidate_e_str_subclass_returns_malformed(self):
        class HostileStr(str):
            pass

        self.assertEqual(
            derive(
                attempt_context=attempt(
                    candidate_engagement_reference=HostileStr("engagement-alpha")
                )
            ).status,
            MALFORMED,
        )

    def test_23_unsupported_operation_returns_unsupported_operation(self):
        result = derive(
            attempt_context=attempt(
                protected_operation=object.__new__(
                    NonProductionProtectedApplicationOperation
                )
            )
        )

        self.assertEqual(result.status, UNSUPPORTED_OPERATION)

    def test_24_foreign_operation_type_fails_closed(self):
        class ForeignOperation(Enum):
            PROTECTED_ASSESSMENT_SUBMISSION = "PROTECTED_ASSESSMENT_SUBMISSION"

        result = derive(attempt_context=attempt(protected_operation=ForeignOperation.PROTECTED_ASSESSMENT_SUBMISSION))

        self.assertEqual(result.status, MALFORMED)

    def test_25_malformed_principal_mapping_result_returns_malformed(self):
        for value in (object(), AuthorityLookupResult(AuthorityLookupStatus.NOT_FOUND)):
            with self.subTest(value=value):
                self.assertEqual(
                    derive(principal_mapping_result=value).status,
                    MALFORMED,
                )

    def test_26_principal_mapping_result_subclass_rejected(self):
        class ResultSubclass(AuthorityLookupResult):
            pass

        result = derive(
            principal_mapping_result=ResultSubclass(
                AuthorityLookupStatus.FOUND,
                (principal_record(),),
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_27_malformed_engagement_result_object_returns_malformed(self):
        self.assertEqual(
            derive(engagement_lookup_result=object()).status,
            MALFORMED,
        )

    def test_28_engagement_result_subclass_rejected(self):
        class ResultSubclass(NonProductionAssessmentEngagementLookupResult):
            pass

        result = derive(
            engagement_lookup_result=ResultSubclass(
                NonProductionAssessmentEngagementLookupStatus.FOUND,
                (engagement_record(),),
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_29_engagement_not_found_returns_engagement_not_ready(self):
        result = derive(
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.NOT_FOUND
            )
        )

        self.assertEqual(result.status, ENGAGEMENT_NOT_READY)

    def test_30_engagement_non_current_returns_engagement_not_ready(self):
        result = derive(
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.NON_CURRENT
            )
        )

        self.assertEqual(result.status, ENGAGEMENT_NOT_READY)

    def test_31_engagement_stale_returns_engagement_not_ready(self):
        result = derive(
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.STALE
            )
        )

        self.assertEqual(result.status, ENGAGEMENT_NOT_READY)

    def test_32_engagement_ambiguous_returns_engagement_not_ready(self):
        result = derive(
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.AMBIGUOUS
            )
        )

        self.assertEqual(result.status, ENGAGEMENT_NOT_READY)

    def test_33_engagement_conflicting_returns_engagement_not_ready(self):
        result = derive(
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.CONFLICTING
            )
        )

        self.assertEqual(result.status, ENGAGEMENT_NOT_READY)

    def test_34_engagement_malformed_status_returns_engagement_not_ready(self):
        result = derive(
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.MALFORMED
            )
        )

        self.assertEqual(result.status, ENGAGEMENT_NOT_READY)

    def test_35_malformed_participation_result_object_returns_malformed(self):
        self.assertEqual(
            derive(participation_lookup_result=object()).status,
            MALFORMED,
        )

    def test_36_participation_result_subclass_rejected(self):
        class ResultSubclass(NonProductionAssessmentEngagementParticipationLookupResult):
            pass

        result = derive(
            participation_lookup_result=ResultSubclass(
                NonProductionAssessmentEngagementParticipationLookupStatus.FOUND,
                (participation_record(),),
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_37_participation_not_found_returns_participation_not_ready(self):
        result = derive(
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.NOT_FOUND
            )
        )

        self.assertEqual(result.status, PARTICIPATION_NOT_READY)

    def test_38_participation_non_current_returns_participation_not_ready(self):
        result = derive(
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.NON_CURRENT
            )
        )

        self.assertEqual(result.status, PARTICIPATION_NOT_READY)

    def test_39_participation_stale_returns_participation_not_ready(self):
        result = derive(
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.STALE
            )
        )

        self.assertEqual(result.status, PARTICIPATION_NOT_READY)

    def test_40_participation_ambiguous_returns_participation_not_ready(self):
        result = derive(
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.AMBIGUOUS
            )
        )

        self.assertEqual(result.status, PARTICIPATION_NOT_READY)

    def test_41_participation_conflicting_returns_participation_not_ready(self):
        result = derive(
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.CONFLICTING
            )
        )

        self.assertEqual(result.status, PARTICIPATION_NOT_READY)

    def test_42_participation_malformed_status_returns_participation_not_ready(self):
        result = derive(
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.MALFORMED
            )
        )

        self.assertEqual(result.status, PARTICIPATION_NOT_READY)

    def test_43_same_valid_use_after_ready_returns_replayed(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        first = derive(deriver=deriver)
        second = derive(deriver=deriver)

        self.assertEqual(first.status, READY)
        self.assertEqual(second.status, REPLAYED)

    def test_44_same_a_different_e_after_ready_returns_rebinding(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        first = derive(deriver=deriver)
        second = derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        )

        self.assertEqual(first.status, READY)
        self.assertEqual(second.status, REBINDING)

    def test_45_same_a_different_p_after_ready_returns_rebinding(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        first = derive(deriver=deriver)
        second = derive(
            deriver=deriver,
            attempt_context=attempt(principal_id="principal-beta"),
            principal_mapping_result=principal_result(
                principal_record(principal_id="principal-beta")
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(principal_id="principal-beta"),)
            ),
        )

        self.assertEqual(first.status, READY)
        self.assertEqual(second.status, REBINDING)

    def test_46_same_a_different_operation_cannot_replace_prior_binding(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        first = derive(deriver=deriver)
        second = derive(
            deriver=deriver,
            attempt_context=attempt(
                protected_operation=object.__new__(
                    NonProductionProtectedApplicationOperation
                )
            ),
        )
        third = derive(deriver=deriver)

        self.assertEqual(first.status, READY)
        self.assertEqual(second.status, UNSUPPORTED_OPERATION)
        self.assertEqual(third.status, REPLAYED)

    def test_47_invalid_first_attempt_does_not_consume_a(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        invalid = derive(
            deriver=deriver,
            attempt_context=attempt(attempt_reference=""),
        )
        valid = derive(deriver=deriver)

        self.assertEqual(invalid.status, MALFORMED)
        self.assertEqual(valid.status, READY)

    def test_48_mismatch_first_attempt_does_not_consume_a(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        mismatch = derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
        )
        valid = derive(deriver=deriver)

        self.assertEqual(mismatch.status, MISMATCH)
        self.assertEqual(valid.status, READY)

    def test_49_engagement_not_ready_first_attempt_does_not_consume_a(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        not_ready = derive(
            deriver=deriver,
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.NOT_FOUND
            ),
        )
        valid = derive(deriver=deriver)

        self.assertEqual(not_ready.status, ENGAGEMENT_NOT_READY)
        self.assertEqual(valid.status, READY)

    def test_50_participation_not_ready_first_attempt_does_not_consume_a(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        not_ready = derive(
            deriver=deriver,
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.NOT_FOUND
            ),
        )
        valid = derive(deriver=deriver)

        self.assertEqual(not_ready.status, PARTICIPATION_NOT_READY)
        self.assertEqual(valid.status, READY)

    def test_51_unsupported_operation_first_attempt_does_not_consume_a(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        unsupported = derive(
            deriver=deriver,
            attempt_context=attempt(
                protected_operation=object.__new__(
                    NonProductionProtectedApplicationOperation
                )
            ),
        )
        valid = derive(deriver=deriver)

        self.assertEqual(unsupported.status, UNSUPPORTED_OPERATION)
        self.assertEqual(valid.status, READY)

    def test_52_valid_retry_after_prior_invalid_attempt_may_ready(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        self.assertEqual(
            derive(deriver=deriver, attempt_context=attempt(principal_id=" ")).status,
            MALFORMED,
        )
        self.assertEqual(derive(deriver=deriver).status, READY)

    def test_53_replay_returns_no_binding(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        replay = derive(deriver=deriver)

        self.assertEqual(replay.status, REPLAYED)
        self.assertIsNone(replay.binding)

    def test_54_rebinding_returns_no_binding(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        rebinding = derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        )

        self.assertEqual(rebinding.status, REBINDING)
        self.assertIsNone(rebinding.binding)

    def test_55_replay_does_not_alter_stored_identity(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        self.assertEqual(derive(deriver=deriver).status, REPLAYED)
        rebinding = derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        )
        self.assertEqual(rebinding.status, REBINDING)

    def test_56_rebinding_does_not_alter_stored_identity(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        )
        self.assertEqual(derive(deriver=deriver).status, REPLAYED)

    def test_57_fresh_deriver_instance_has_independent_state(self):
        self.assertEqual(derive().status, READY)
        self.assertEqual(derive().status, READY)

    def test_58_no_global_replay_registry(self):
        first = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        second = NonProductionAssessmentSubmissionAttemptBindingDeriver()

        self.assertEqual(derive(deriver=first).status, READY)
        self.assertEqual(derive(deriver=second).status, READY)

    def test_59_caller_mutation_of_attempt_context_cannot_change_call_decision(self):
        ctx = attempt()
        result = derive(attempt_context=ctx)

        with self.assertRaises(FrozenInstanceError):
            ctx.attempt_reference = "attacker"
        self.assertEqual(result.status, READY)

    def test_60_output_setattr_attack_cannot_change_later_behavior(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        first = derive(deriver=deriver)
        object.__setattr__(first.binding, "engagement_reference", "attacker")
        replay = derive(deriver=deriver)

        self.assertEqual(replay.status, REPLAYED)

    def test_61_returned_binding_does_not_alias_internal_state(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        result = derive(deriver=deriver)
        object.__setattr__(result.binding, "principal_id", "attacker")
        rebinding = derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        )

        self.assertEqual(rebinding.status, REBINDING)

    def test_62_success_outputs_are_exact_expected_types(self):
        result = derive()

        self.assertIs(type(result), NonProductionAssessmentSubmissionAttemptBindingResult)
        self.assertIs(type(result.binding), NonProductionAssessmentSubmissionAttemptBinding)

    def test_63_hostile_principal_record_subclass_fails_closed(self):
        class PrincipalSubclass(PrincipalMapping):
            pass

        result = derive(
            principal_mapping_result=principal_result(
                PrincipalSubclass(
                    authority_reference="principal-authority",
                    state=AuthorityRecordState.ACTIVE,
                    subject_provider="provider-alpha",
                    subject="subject-alpha",
                    principal_id="principal-alpha",
                )
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_64_hostile_engagement_record_subclass_fails_closed(self):
        class EngagementSubclass(NonProductionAssessmentEngagementAuthorityEvidence):
            pass

        result = derive(
            engagement_lookup_result=engagement_result(
                records=(
                    EngagementSubclass(
                        authority_reference="engagement-authority",
                        state=AuthorityRecordState.ACTIVE,
                        engagement_reference="engagement-alpha",
                        business_entity_id="business-alpha",
                        lifecycle_state=(
                            NonProductionAssessmentEngagementLifecycleState.CURRENT
                        ),
                        establishment_provenance_reference="engagement-provenance",
                    ),
                )
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_65_hostile_participation_record_subclass_fails_closed(self):
        class ParticipationSubclass(
            NonProductionAssessmentEngagementParticipationAuthorityEvidence
        ):
            pass

        result = derive(
            participation_lookup_result=participation_result(
                records=(
                    ParticipationSubclass(
                        authority_reference="participation-authority",
                        state=AuthorityRecordState.ACTIVE,
                        principal_id="principal-alpha",
                        engagement_reference="engagement-alpha",
                        lifecycle_state=(
                            NonProductionAssessmentEngagementParticipationLifecycleState.
                            CURRENT
                        ),
                        participation_provenance_reference=(
                            "participation-provenance"
                        ),
                    ),
                )
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_66_decision_critical_provenance_strings_are_validated(self):
        cases = (
            principal_result(principal_record(authority_reference=" principal")),
            engagement_result(
                records=(
                    engagement_record(
                        establishment_provenance_reference="engagement-provenance "
                    ),
                )
            ),
            participation_result(
                records=(
                    participation_record(
                        participation_provenance_reference=" participation-provenance"
                    ),
                )
            ),
        )
        for index, value in enumerate(cases):
            with self.subTest(index=index):
                kwargs = {}
                if index == 0:
                    kwargs["principal_mapping_result"] = value
                elif index == 1:
                    kwargs["engagement_lookup_result"] = value
                else:
                    kwargs["participation_lookup_result"] = value
                self.assertEqual(derive(**kwargs).status, MALFORMED)

    def test_67_deterministic_equivalent_fresh_state_derivation(self):
        first = derive()
        second = derive()

        self.assertEqual(first.status, second.status)
        self.assertEqual(first.binding, second.binding)
        self.assertIsNot(first.binding, second.binding)

    def test_68_public_api_has_no_membership_input(self):
        parameters = inspect.signature(
            NonProductionAssessmentSubmissionAttemptBindingDeriver.
            derive_assessment_submission_attempt_binding
        ).parameters

        self.assertNotIn("membership", parameters)
        self.assertNotIn("membership_result", parameters)

    def test_69_public_api_has_no_entitlement_input(self):
        parameters = inspect.signature(
            NonProductionAssessmentSubmissionAttemptBindingDeriver.
            derive_assessment_submission_attempt_binding
        ).parameters

        self.assertNotIn("entitlement", parameters)
        self.assertNotIn("entitlement_result", parameters)

    def test_70_public_api_has_no_business_entity_input(self):
        parameters = inspect.signature(
            NonProductionAssessmentSubmissionAttemptBindingDeriver.
            derive_assessment_submission_attempt_binding
        ).parameters

        self.assertNotIn("business_entity_id", parameters)
        self.assertNotIn("business_entity", parameters)

    def test_71_public_api_has_no_resource_or_target_input(self):
        parameters = inspect.signature(
            NonProductionAssessmentSubmissionAttemptBindingDeriver.
            derive_assessment_submission_attempt_binding
        ).parameters

        self.assertNotIn("resource_reference", parameters)
        self.assertNotIn("target", parameters)

    def test_72_public_api_has_no_raw_authentication_input(self):
        parameters = inspect.signature(
            NonProductionAssessmentSubmissionAttemptBindingDeriver.
            derive_assessment_submission_attempt_binding
        ).parameters

        self.assertNotIn("token", parameters)
        self.assertNotIn("subject", parameters)
        self.assertNotIn("authenticated", parameters)

    def test_73_no_allow_deny_or_permission_output(self):
        result = derive()

        self.assertFalse(hasattr(result, "decision"))
        self.assertFalse(hasattr(result, "allowed"))
        self.assertFalse(hasattr(result.binding, "permission"))

    def test_74_ready_does_not_create_e_context_legitimacy(self):
        result = derive()

        self.assertFalse(hasattr(result, "e_context_legitimate"))
        self.assertFalse(hasattr(result.binding, "context_legitimate"))

    def test_75_ready_does_not_create_business_context_ready(self):
        result = derive()

        self.assertFalse(hasattr(result, "business_context_ready"))
        self.assertFalse(hasattr(result.binding, "business_entity_id"))

    def test_76_malformed_precedes_unsupported_operation(self):
        result = derive(
            attempt_context=attempt(
                attempt_reference="",
                protected_operation=object.__new__(
                    NonProductionProtectedApplicationOperation
                ),
            )
        )

        self.assertEqual(result.status, MALFORMED)

    def test_77_unsupported_operation_precedes_non_ready_engagement(self):
        result = derive(
            attempt_context=attempt(
                protected_operation=object.__new__(
                    NonProductionProtectedApplicationOperation
                ),
            ),
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.NOT_FOUND
            ),
        )

        self.assertEqual(result.status, UNSUPPORTED_OPERATION)

    def test_78_non_ready_engagement_precedes_non_ready_participation(self):
        result = derive(
            engagement_lookup_result=engagement_result(
                NonProductionAssessmentEngagementLookupStatus.NOT_FOUND
            ),
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.NOT_FOUND
            ),
        )

        self.assertEqual(result.status, ENGAGEMENT_NOT_READY)

    def test_79_ready_engagement_non_ready_participation(self):
        result = derive(
            participation_lookup_result=participation_result(
                NonProductionAssessmentEngagementParticipationLookupStatus.NOT_FOUND
            ),
        )

        self.assertEqual(result.status, PARTICIPATION_NOT_READY)

    def test_80_ready_upstream_mismatch_precedes_replay(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        result = derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
        )

        self.assertEqual(result.status, MISMATCH)

    def test_81_used_a_current_malformed_input_returns_malformed(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        self.assertEqual(
            derive(deriver=deriver, attempt_context=attempt(principal_id="")).status,
            MALFORMED,
        )

    def test_82_used_a_current_unsupported_operation_returns_unsupported(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        self.assertEqual(
            derive(
                deriver=deriver,
                attempt_context=attempt(
                    protected_operation=object.__new__(
                        NonProductionProtectedApplicationOperation
                    ),
                ),
            ).status,
            UNSUPPORTED_OPERATION,
        )

    def test_83_used_a_current_non_ready_engagement_returns_engagement_not_ready(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        self.assertEqual(
            derive(
                deriver=deriver,
                engagement_lookup_result=engagement_result(
                    NonProductionAssessmentEngagementLookupStatus.NOT_FOUND
                ),
            ).status,
            ENGAGEMENT_NOT_READY,
        )

    def test_84_used_a_current_non_ready_participation_returns_participation_not_ready(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        self.assertEqual(
            derive(
                deriver=deriver,
                participation_lookup_result=participation_result(
                    NonProductionAssessmentEngagementParticipationLookupStatus.NOT_FOUND
                ),
            ).status,
            PARTICIPATION_NOT_READY,
        )

    def test_85_only_otherwise_valid_used_attempt_reaches_replay(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        self.assertEqual(derive(deriver=deriver).status, REPLAYED)

    def test_86_only_otherwise_valid_used_attempt_reaches_rebinding(self):
        deriver = NonProductionAssessmentSubmissionAttemptBindingDeriver()
        derive(deriver=deriver)
        result = derive(
            deriver=deriver,
            attempt_context=attempt(candidate_engagement_reference="engagement-beta"),
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-beta"),)
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-beta"),)
            ),
        )

        self.assertEqual(result.status, REBINDING)

    def test_87_source_imports_do_not_include_disallowed_dependencies(self):
        source = inspect.getsource(binding_module)
        for forbidden in (
            "boto",
            "aws",
            "cognito",
            "requests",
            "urllib",
            "sqlite",
            "dynamodb",
            "openai",
            "bedrock",
        ):
            self.assertNotIn(forbidden, source.lower())

    def test_88_source_does_not_use_unsafe_reflection_helpers(self):
        source = inspect.getsource(binding_module)

        self.assertNotIn("vars(", source)
        self.assertNotIn(".__dict__", source)

    def test_89_public_status_members_are_exact(self):
        self.assertEqual(
            tuple(NonProductionAssessmentSubmissionAttemptBindingStatus),
            (
                READY,
                MALFORMED,
                ENGAGEMENT_NOT_READY,
                PARTICIPATION_NOT_READY,
                UNSUPPORTED_OPERATION,
                MISMATCH,
                REPLAYED,
                REBINDING,
            ),
        )

    def test_90_attempt_context_fields_are_exact(self):
        self.assertEqual(
            tuple(NonProductionAssessmentSubmissionAttemptContext.__dataclass_fields__),
            (
                "attempt_reference",
                "principal_id",
                "candidate_engagement_reference",
                "protected_operation",
            ),
        )

    def test_91_binding_fields_are_exact(self):
        self.assertEqual(
            tuple(NonProductionAssessmentSubmissionAttemptBinding.__dataclass_fields__),
            (
                "attempt_reference",
                "principal_id",
                "candidate_engagement_reference",
                "engagement_reference",
                "protected_operation",
                "principal_authority_reference",
                "engagement_authority_reference",
                "engagement_establishment_provenance_reference",
                "participation_authority_reference",
                "participation_provenance_reference",
            ),
        )

    def test_92_result_fields_are_exact(self):
        self.assertEqual(
            tuple(
                NonProductionAssessmentSubmissionAttemptBindingResult.
                __dataclass_fields__
            ),
            ("status", "binding"),
        )

    def test_93_deriver_has_no_authority_mutation_api(self):
        forbidden = {
            "add",
            "approve",
            "assign",
            "authorize",
            "create",
            "delete",
            "rebind",
            "revoke",
            "save",
            "update",
        }
        public = {
            name
            for name in dir(NonProductionAssessmentSubmissionAttemptBindingDeriver)
            if not name.startswith("_")
        }

        self.assertTrue(forbidden.isdisjoint(public))

    def test_94_no_dict_or_dynamic_registration_constructs(self):
        tree = ast.parse(inspect.getsource(binding_module))
        names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }

        self.assertNotIn("setattr", names)
        self.assertNotIn("getattr", names)


if __name__ == "__main__":
    unittest.main()
