import ast
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, fields, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_engagement_context_legitimacy as context_module  # noqa: E402
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    PrincipalMapping,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_engagement_context_legitimacy import (  # noqa: E402
    NonProductionAssessmentEngagementContextLegitimacy,
    NonProductionAssessmentEngagementContextLegitimacyResult,
    NonProductionAssessmentEngagementContextLegitimacyStatus,
    resolve_non_production_assessment_engagement_context_legitimacy,
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
    NonProductionAssessmentSubmissionAttemptBindingResult,
    NonProductionAssessmentSubmissionAttemptBindingStatus,
)


READY = NonProductionAssessmentEngagementContextLegitimacyStatus.READY
MALFORMED = NonProductionAssessmentEngagementContextLegitimacyStatus.MALFORMED
PRINCIPAL_NOT_READY = (
    NonProductionAssessmentEngagementContextLegitimacyStatus.PRINCIPAL_NOT_READY
)
ENGAGEMENT_NOT_READY = (
    NonProductionAssessmentEngagementContextLegitimacyStatus.ENGAGEMENT_NOT_READY
)
PARTICIPATION_NOT_READY = (
    NonProductionAssessmentEngagementContextLegitimacyStatus.PARTICIPATION_NOT_READY
)
BINDING_NOT_READY = (
    NonProductionAssessmentEngagementContextLegitimacyStatus.BINDING_NOT_READY
)
MISMATCH = NonProductionAssessmentEngagementContextLegitimacyStatus.MISMATCH
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)


class StringSubclass(str):
    pass


class ForeignOperation(Enum):
    PROTECTED_ASSESSMENT_SUBMISSION = "PROTECTED_ASSESSMENT_SUBMISSION"


class PrincipalMappingSubclass(PrincipalMapping):
    pass


class AuthorityLookupResultSubclass(AuthorityLookupResult):
    pass


class EngagementEvidenceSubclass(NonProductionAssessmentEngagementAuthorityEvidence):
    pass


class EngagementResultSubclass(NonProductionAssessmentEngagementLookupResult):
    pass


class ParticipationEvidenceSubclass(
    NonProductionAssessmentEngagementParticipationAuthorityEvidence
):
    pass


class ParticipationResultSubclass(
    NonProductionAssessmentEngagementParticipationLookupResult
):
    pass


class BindingSubclass(NonProductionAssessmentSubmissionAttemptBinding):
    pass


class BindingResultSubclass(NonProductionAssessmentSubmissionAttemptBindingResult):
    pass


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


def principal_result(status=AuthorityLookupStatus.FOUND, records=None):
    if records is None:
        records = (principal_record(),) if status is AuthorityLookupStatus.FOUND else ()
    return AuthorityLookupResult(status=status, records=records)


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
        records = (
            (engagement_record(),)
            if status is NonProductionAssessmentEngagementLookupStatus.FOUND
            else ()
        )
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
        records = (
            (participation_record(),)
            if status
            is NonProductionAssessmentEngagementParticipationLookupStatus.FOUND
            else ()
        )
    return NonProductionAssessmentEngagementParticipationLookupResult(
        status=status,
        records=records,
    )


def binding_record(
    attempt_reference="attempt-alpha",
    principal_id="principal-alpha",
    candidate_engagement_reference="engagement-alpha",
    engagement_reference="engagement-alpha",
    protected_operation=PROTECTED_ASSESSMENT,
    principal_authority_reference="principal-authority",
    engagement_authority_reference="engagement-authority",
    engagement_establishment_provenance_reference="engagement-provenance",
    participation_authority_reference="participation-authority",
    participation_provenance_reference="participation-provenance",
):
    return NonProductionAssessmentSubmissionAttemptBinding(
        attempt_reference=attempt_reference,
        principal_id=principal_id,
        candidate_engagement_reference=candidate_engagement_reference,
        engagement_reference=engagement_reference,
        protected_operation=protected_operation,
        principal_authority_reference=principal_authority_reference,
        engagement_authority_reference=engagement_authority_reference,
        engagement_establishment_provenance_reference=(
            engagement_establishment_provenance_reference
        ),
        participation_authority_reference=participation_authority_reference,
        participation_provenance_reference=participation_provenance_reference,
    )


def binding_result(
    status=NonProductionAssessmentSubmissionAttemptBindingStatus.READY,
    binding=None,
):
    if binding is None and status is NonProductionAssessmentSubmissionAttemptBindingStatus.READY:
        binding = binding_record()
    return NonProductionAssessmentSubmissionAttemptBindingResult(
        status=status,
        binding=binding,
    )


def resolve(
    *,
    principal_mapping_result=None,
    engagement_lookup_result=None,
    participation_lookup_result=None,
    attempt_binding_result=None,
):
    if principal_mapping_result is None:
        principal_mapping_result = principal_result()
    if engagement_lookup_result is None:
        engagement_lookup_result = engagement_result()
    if participation_lookup_result is None:
        participation_lookup_result = participation_result()
    if attempt_binding_result is None:
        attempt_binding_result = binding_result()
    return resolve_non_production_assessment_engagement_context_legitimacy(
        principal_mapping_result=principal_mapping_result,
        engagement_result=engagement_lookup_result,
        participation_result=participation_lookup_result,
        attempt_binding_result=attempt_binding_result,
    )


def assert_status(testcase, expected_status, **kwargs):
    result = resolve(**kwargs)
    testcase.assertEqual(result.status, expected_status)
    if expected_status is READY:
        testcase.assertIs(
            type(result.context_legitimacy),
            NonProductionAssessmentEngagementContextLegitimacy,
        )
    else:
        testcase.assertIsNone(result.context_legitimacy)
    return result


class NonProductionAssessmentEngagementContextLegitimacyTests(unittest.TestCase):
    def test_01_valid_captured_inputs_return_ready(self):
        result = assert_status(self, READY)

        self.assertIs(
            type(result),
            NonProductionAssessmentEngagementContextLegitimacyResult,
        )

    def test_02_ready_output_contains_exact_nine_fields(self):
        legitimacy = resolve().context_legitimacy

        self.assertEqual(
            tuple(field.name for field in fields(legitimacy)),
            (
                "attempt_reference",
                "principal_id",
                "engagement_reference",
                "protected_operation",
                "principal_authority_reference",
                "engagement_authority_reference",
                "engagement_establishment_provenance_reference",
                "participation_authority_reference",
                "participation_provenance_reference",
            ),
        )
        self.assertEqual(legitimacy.attempt_reference, "attempt-alpha")
        self.assertEqual(legitimacy.principal_id, "principal-alpha")
        self.assertEqual(legitimacy.engagement_reference, "engagement-alpha")
        self.assertIs(legitimacy.protected_operation, PROTECTED_ASSESSMENT)
        self.assertEqual(
            legitimacy.principal_authority_reference,
            "principal-authority",
        )
        self.assertEqual(
            legitimacy.engagement_authority_reference,
            "engagement-authority",
        )
        self.assertEqual(
            legitimacy.engagement_establishment_provenance_reference,
            "engagement-provenance",
        )
        self.assertEqual(
            legitimacy.participation_authority_reference,
            "participation-authority",
        )
        self.assertEqual(
            legitimacy.participation_provenance_reference,
            "participation-provenance",
        )
        self.assertFalse(hasattr(legitimacy, "business_entity_id"))
        self.assertFalse(hasattr(legitimacy, "permission"))
        self.assertFalse(hasattr(legitimacy, "business_context_ready"))

    def test_03_status_members_are_exact(self):
        self.assertEqual(
            {status.name for status in NonProductionAssessmentEngagementContextLegitimacyStatus},
            {
                "READY",
                "MALFORMED",
                "PRINCIPAL_NOT_READY",
                "ENGAGEMENT_NOT_READY",
                "PARTICIPATION_NOT_READY",
                "BINDING_NOT_READY",
                "MISMATCH",
            },
        )

    def test_04_result_contract_only_ready_carries_record(self):
        self.assertIsNotNone(resolve().context_legitimacy)
        for status in NonProductionAssessmentEngagementContextLegitimacyStatus:
            if status is READY:
                continue
            result = NonProductionAssessmentEngagementContextLegitimacyResult(
                status=status,
                context_legitimacy=None,
            )
            self.assertIsNone(result.context_legitimacy)

    def test_05_repeated_ready_composition_is_deterministic_and_fresh(self):
        first = resolve()
        second = resolve()

        self.assertEqual(first.status, READY)
        self.assertEqual(second.status, READY)
        self.assertIsNot(first, second)
        self.assertIsNot(first.context_legitimacy, second.context_legitimacy)
        self.assertEqual(first.context_legitimacy, second.context_legitimacy)

    def test_06_output_is_frozen_and_mutation_does_not_affect_later_calls(self):
        first = resolve()

        with self.assertRaises(FrozenInstanceError):
            first.context_legitimacy.principal_id = "evil"
        object.__setattr__(first.context_legitimacy, "principal_id", "evil")

        second = resolve()
        self.assertEqual(second.context_legitimacy.principal_id, "principal-alpha")

    def test_07_same_ready_binding_may_compose_ready_repeatedly(self):
        ready_binding = binding_result()

        self.assertEqual(
            resolve(attempt_binding_result=ready_binding).status,
            READY,
        )
        self.assertEqual(
            resolve(attempt_binding_result=ready_binding).status,
            READY,
        )

    def test_08_no_mutable_composer_state_exists(self):
        self.assertFalse(
            any(
                name
                for name in dir(context_module)
                if name.startswith("_") and name.endswith("registry")
            )
        )
        self.assertFalse(hasattr(context_module, "_bound_attempts"))

    def test_09_principal_non_success_statuses_are_not_ready(self):
        for status in AuthorityLookupStatus:
            if status is AuthorityLookupStatus.FOUND:
                continue
            with self.subTest(status=status):
                assert_status(
                    self,
                    PRINCIPAL_NOT_READY,
                    principal_mapping_result=principal_result(status=status),
                )

    def test_10_principal_zero_record_success_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            principal_mapping_result=principal_result(records=()),
        )

    def test_11_principal_multi_record_success_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            principal_mapping_result=principal_result(
                records=(principal_record(), principal_record("other-authority")),
            ),
        )

    def test_12_principal_wrong_record_type_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            principal_mapping_result=principal_result(records=(object(),)),
        )

    def test_13_principal_record_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            principal_mapping_result=principal_result(
                records=(
                    PrincipalMappingSubclass(
                        "principal-authority",
                        AuthorityRecordState.ACTIVE,
                        "provider-alpha",
                        "subject-alpha",
                        "principal-alpha",
                    ),
                ),
            ),
        )

    def test_14_principal_result_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            principal_mapping_result=AuthorityLookupResultSubclass(
                AuthorityLookupStatus.FOUND,
                (principal_record(),),
            ),
        )

    def test_15_principal_inactive_success_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            principal_mapping_result=principal_result(
                records=(principal_record(state=AuthorityRecordState.REVOKED),),
            ),
        )

    def test_16_principal_strings_are_strict(self):
        for record in (
            principal_record(principal_id=""),
            principal_record(principal_id=" principal-alpha"),
            principal_record(principal_id=StringSubclass("principal-alpha")),
            principal_record(authority_reference=""),
            principal_record(authority_reference=StringSubclass("principal-authority")),
        ):
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    principal_mapping_result=principal_result(records=(record,)),
                )

    def test_17_principal_p_mismatch_with_participation_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            participation_lookup_result=participation_result(
                records=(participation_record(principal_id="principal-other"),),
            ),
        )

    def test_18_principal_p_mismatch_with_binding_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(
                binding=binding_record(principal_id="principal-other"),
            ),
        )

    def test_19_principal_authority_reference_mismatch_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(
                binding=binding_record(
                    principal_authority_reference="principal-authority-old",
                ),
            ),
        )

    def test_20_engagement_non_found_statuses_are_not_ready(self):
        for status in NonProductionAssessmentEngagementLookupStatus:
            if status is NonProductionAssessmentEngagementLookupStatus.FOUND:
                continue
            with self.subTest(status=status):
                assert_status(
                    self,
                    ENGAGEMENT_NOT_READY,
                    engagement_lookup_result=engagement_result(status=status),
                )

    def test_21_engagement_zero_record_found_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(records=()),
        )

    def test_22_engagement_multi_record_found_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(
                records=(engagement_record(), engagement_record("other-authority")),
            ),
        )

    def test_23_engagement_wrong_evidence_type_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(records=(object(),)),
        )

    def test_24_engagement_evidence_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(
                records=(
                    EngagementEvidenceSubclass(
                        "engagement-authority",
                        AuthorityRecordState.ACTIVE,
                        "engagement-alpha",
                        "business-alpha",
                        NonProductionAssessmentEngagementLifecycleState.CURRENT,
                        "engagement-provenance",
                    ),
                ),
            ),
        )

    def test_25_engagement_result_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=EngagementResultSubclass(
                NonProductionAssessmentEngagementLookupStatus.FOUND,
                (engagement_record(),),
            ),
        )

    def test_26_engagement_non_active_or_non_current_found_is_malformed(self):
        for record in (
            engagement_record(state=AuthorityRecordState.EXPIRED),
            engagement_record(
                lifecycle_state=(
                    NonProductionAssessmentEngagementLifecycleState.NON_CURRENT
                ),
            ),
        ):
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    engagement_lookup_result=engagement_result(records=(record,)),
                )

    def test_27_engagement_strings_are_strict(self):
        for record in (
            engagement_record(engagement_reference=""),
            engagement_record(engagement_reference="engagement-alpha "),
            engagement_record(engagement_reference=StringSubclass("engagement-alpha")),
            engagement_record(business_entity_id=""),
            engagement_record(authority_reference=StringSubclass("engagement-authority")),
            engagement_record(establishment_provenance_reference=" provenance"),
        ):
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    engagement_lookup_result=engagement_result(records=(record,)),
                )

    def test_28_engagement_e_mismatch_with_participation_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-other"),),
            ),
        )

    def test_29_engagement_e_mismatch_with_binding_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(
                binding=binding_record(engagement_reference="engagement-other"),
            ),
        )

    def test_30_engagement_e_mismatch_with_binding_candidate_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(
                binding=binding_record(
                    candidate_engagement_reference="engagement-other",
                ),
            ),
        )

    def test_31_engagement_provenance_mismatches_are_mismatch(self):
        for binding in (
            binding_record(engagement_authority_reference="engagement-authority-old"),
            binding_record(
                engagement_establishment_provenance_reference=(
                    "engagement-provenance-old"
                ),
            ),
        ):
            with self.subTest(binding=binding):
                assert_status(
                    self,
                    MISMATCH,
                    attempt_binding_result=binding_result(binding=binding),
                )

    def test_32_participation_non_found_statuses_are_not_ready(self):
        for status in NonProductionAssessmentEngagementParticipationLookupStatus:
            if status is NonProductionAssessmentEngagementParticipationLookupStatus.FOUND:
                continue
            with self.subTest(status=status):
                assert_status(
                    self,
                    PARTICIPATION_NOT_READY,
                    participation_lookup_result=participation_result(status=status),
                )

    def test_33_participation_zero_record_found_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            participation_lookup_result=participation_result(records=()),
        )

    def test_34_participation_multi_record_found_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            participation_lookup_result=participation_result(
                records=(participation_record(), participation_record("other-authority")),
            ),
        )

    def test_35_participation_wrong_evidence_type_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            participation_lookup_result=participation_result(records=(object(),)),
        )

    def test_36_participation_evidence_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            participation_lookup_result=participation_result(
                records=(
                    ParticipationEvidenceSubclass(
                        "participation-authority",
                        AuthorityRecordState.ACTIVE,
                        "principal-alpha",
                        "engagement-alpha",
                        (
                            NonProductionAssessmentEngagementParticipationLifecycleState.
                            CURRENT
                        ),
                        "participation-provenance",
                    ),
                ),
            ),
        )

    def test_37_participation_result_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            participation_lookup_result=ParticipationResultSubclass(
                NonProductionAssessmentEngagementParticipationLookupStatus.FOUND,
                (participation_record(),),
            ),
        )

    def test_38_participation_non_active_or_non_current_found_is_malformed(self):
        for record in (
            participation_record(state=AuthorityRecordState.DISABLED),
            participation_record(
                lifecycle_state=(
                    NonProductionAssessmentEngagementParticipationLifecycleState.
                    NON_CURRENT
                ),
            ),
        ):
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    participation_lookup_result=participation_result(records=(record,)),
                )

    def test_39_participation_strings_are_strict(self):
        for record in (
            participation_record(principal_id=""),
            participation_record(principal_id="principal-alpha "),
            participation_record(principal_id=StringSubclass("principal-alpha")),
            participation_record(engagement_reference=" engagement-alpha"),
            participation_record(authority_reference=StringSubclass("participation-authority")),
            participation_record(participation_provenance_reference=""),
        ):
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    participation_lookup_result=participation_result(records=(record,)),
                )

    def test_40_participation_p_mismatch_with_binding_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(
                binding=binding_record(principal_id="principal-other"),
            ),
        )

    def test_41_participation_e_mismatch_with_binding_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(
                binding=binding_record(engagement_reference="engagement-other"),
            ),
        )

    def test_42_participation_provenance_mismatches_are_mismatch(self):
        for binding in (
            binding_record(participation_authority_reference="participation-old"),
            binding_record(participation_provenance_reference="participation-old"),
        ):
            with self.subTest(binding=binding):
                assert_status(
                    self,
                    MISMATCH,
                    attempt_binding_result=binding_result(binding=binding),
                )

    def test_43_every_non_ready_binding_status_is_binding_not_ready(self):
        for status in NonProductionAssessmentSubmissionAttemptBindingStatus:
            if status is NonProductionAssessmentSubmissionAttemptBindingStatus.READY:
                continue
            with self.subTest(status=status):
                assert_status(
                    self,
                    BINDING_NOT_READY,
                    attempt_binding_result=binding_result(status=status),
                )

    def test_44_binding_ready_without_binding_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            attempt_binding_result=NonProductionAssessmentSubmissionAttemptBindingResult(
                status=NonProductionAssessmentSubmissionAttemptBindingStatus.READY,
                binding=None,
            ),
        )

    def test_45_binding_wrong_type_or_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            attempt_binding_result=binding_result(binding=object()),
        )
        assert_status(
            self,
            MALFORMED,
            attempt_binding_result=binding_result(
                binding=BindingSubclass(
                    "attempt-alpha",
                    "principal-alpha",
                    "engagement-alpha",
                    "engagement-alpha",
                    PROTECTED_ASSESSMENT,
                    "principal-authority",
                    "engagement-authority",
                    "engagement-provenance",
                    "participation-authority",
                    "participation-provenance",
                ),
            ),
        )

    def test_46_binding_result_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            attempt_binding_result=BindingResultSubclass(
                NonProductionAssessmentSubmissionAttemptBindingStatus.READY,
                binding_record(),
            ),
        )

    def test_47_binding_strings_are_strict(self):
        for binding in (
            binding_record(attempt_reference=""),
            binding_record(attempt_reference=" attempt-alpha"),
            binding_record(attempt_reference=StringSubclass("attempt-alpha")),
            binding_record(principal_id=""),
            binding_record(principal_id=StringSubclass("principal-alpha")),
            binding_record(engagement_reference="engagement-alpha "),
            binding_record(candidate_engagement_reference=""),
            binding_record(candidate_engagement_reference=StringSubclass("engagement-alpha")),
            binding_record(principal_authority_reference=""),
            binding_record(engagement_authority_reference=" "),
            binding_record(engagement_establishment_provenance_reference=" x"),
            binding_record(participation_authority_reference=StringSubclass("participation-authority")),
            binding_record(participation_provenance_reference="x "),
        ):
            with self.subTest(binding=binding):
                assert_status(
                    self,
                    MALFORMED,
                    attempt_binding_result=binding_result(binding=binding),
                )

    def test_48_binding_foreign_operation_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            attempt_binding_result=binding_result(
                binding=binding_record(
                    protected_operation=(
                        ForeignOperation.PROTECTED_ASSESSMENT_SUBMISSION
                    ),
                ),
            ),
        )

    def test_49_binding_candidate_mismatch_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(
                binding=binding_record(
                    candidate_engagement_reference="engagement-other",
                ),
            ),
        )

    def test_50_same_b_different_e_cannot_substitute(self):
        assert_status(
            self,
            MISMATCH,
            engagement_lookup_result=engagement_result(
                records=(engagement_record(engagement_reference="engagement-two"),),
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-two"),),
            ),
            attempt_binding_result=binding_result(
                binding=binding_record(engagement_reference="engagement-one"),
            ),
        )

    def test_51_cross_b_substitution_fails_by_exact_e(self):
        assert_status(
            self,
            MISMATCH,
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        engagement_reference="engagement-two",
                        business_entity_id="business-two",
                    ),
                ),
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(engagement_reference="engagement-two"),),
            ),
            attempt_binding_result=binding_result(
                binding=binding_record(engagement_reference="engagement-one"),
            ),
        )

    def test_52_principal_substitution_fails(self):
        assert_status(
            self,
            MISMATCH,
            principal_mapping_result=principal_result(
                records=(principal_record(principal_id="principal-one"),),
            ),
            participation_lookup_result=participation_result(
                records=(participation_record(principal_id="principal-one"),),
            ),
            attempt_binding_result=binding_result(
                binding=binding_record(principal_id="principal-two"),
            ),
        )

    def test_53_attempt_reference_is_preserved_only_from_binding(self):
        result = resolve(
            attempt_binding_result=binding_result(
                binding=binding_record(attempt_reference="attempt-beta"),
            ),
        )

        self.assertEqual(result.status, READY)
        self.assertEqual(result.context_legitimacy.attempt_reference, "attempt-beta")

    def test_54_provenance_rotation_for_same_p_e_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        authority_reference="engagement-authority-new",
                        establishment_provenance_reference="engagement-provenance-new",
                    ),
                ),
            ),
        )

    def test_55_snapshot_mixing_is_blocked_by_provenance_conjunction(self):
        assert_status(
            self,
            MISMATCH,
            principal_mapping_result=principal_result(
                records=(
                    principal_record(authority_reference="principal-authority-t2"),
                ),
            ),
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        authority_reference="engagement-authority-t2",
                    ),
                ),
            ),
            participation_lookup_result=participation_result(
                records=(
                    participation_record(
                        authority_reference="participation-authority-t2",
                    ),
                ),
            ),
        )

    def test_56_structurally_invalid_forged_ready_binding_is_malformed(self):
        forged = replace(binding_record(), participation_provenance_reference="")

        assert_status(
            self,
            MALFORMED,
            attempt_binding_result=binding_result(binding=forged),
        )

    def test_57_structurally_valid_mismatched_forged_binding_is_mismatch(self):
        forged = binding_record(principal_id="principal-forged")

        assert_status(
            self,
            MISMATCH,
            attempt_binding_result=binding_result(binding=forged),
        )

    def test_58_structurally_valid_fully_matching_forged_binding_can_compose(self):
        forged = binding_record()

        assert_status(
            self,
            READY,
            attempt_binding_result=NonProductionAssessmentSubmissionAttemptBindingResult(
                status=NonProductionAssessmentSubmissionAttemptBindingStatus.READY,
                binding=forged,
            ),
        )

    def test_59_structurally_valid_exact_constructed_upstreams_can_compose(self):
        assert_status(
            self,
            READY,
            principal_mapping_result=AuthorityLookupResult(
                status=AuthorityLookupStatus.FOUND,
                records=(principal_record(),),
            ),
            engagement_lookup_result=NonProductionAssessmentEngagementLookupResult(
                status=NonProductionAssessmentEngagementLookupStatus.FOUND,
                records=(engagement_record(),),
            ),
            participation_lookup_result=(
                NonProductionAssessmentEngagementParticipationLookupResult(
                    status=(
                        NonProductionAssessmentEngagementParticipationLookupStatus.
                        FOUND
                    ),
                    records=(participation_record(),),
                )
            ),
        )

    def test_60_malformed_beats_principal_not_ready(self):
        assert_status(
            self,
            MALFORMED,
            principal_mapping_result=object(),
            engagement_lookup_result=engagement_result(
                status=NonProductionAssessmentEngagementLookupStatus.NOT_FOUND,
            ),
        )

    def test_61_principal_not_ready_beats_engagement_not_ready(self):
        assert_status(
            self,
            PRINCIPAL_NOT_READY,
            principal_mapping_result=principal_result(
                status=AuthorityLookupStatus.NOT_FOUND,
            ),
            engagement_lookup_result=engagement_result(
                status=NonProductionAssessmentEngagementLookupStatus.NOT_FOUND,
            ),
        )

    def test_62_engagement_not_ready_beats_participation_not_ready(self):
        assert_status(
            self,
            ENGAGEMENT_NOT_READY,
            engagement_lookup_result=engagement_result(
                status=NonProductionAssessmentEngagementLookupStatus.NOT_FOUND,
            ),
            participation_lookup_result=participation_result(
                status=(
                    NonProductionAssessmentEngagementParticipationLookupStatus.
                    NOT_FOUND
                ),
            ),
        )

    def test_63_participation_not_ready_beats_binding_not_ready(self):
        assert_status(
            self,
            PARTICIPATION_NOT_READY,
            participation_lookup_result=participation_result(
                status=(
                    NonProductionAssessmentEngagementParticipationLookupStatus.
                    NOT_FOUND
                ),
            ),
            attempt_binding_result=binding_result(
                status=NonProductionAssessmentSubmissionAttemptBindingStatus.REPLAYED,
            ),
        )

    def test_64_binding_not_ready_beats_mismatch(self):
        assert_status(
            self,
            BINDING_NOT_READY,
            participation_lookup_result=participation_result(
                records=(participation_record(principal_id="principal-other"),),
            ),
            attempt_binding_result=binding_result(
                status=NonProductionAssessmentSubmissionAttemptBindingStatus.REPLAYED,
            ),
        )

    def test_65_mismatch_is_after_all_ready_prerequisites(self):
        assert_status(
            self,
            MISMATCH,
            participation_lookup_result=participation_result(
                records=(participation_record(principal_id="principal-other"),),
            ),
        )

    def test_66_malformed_current_inputs_are_not_masked_by_binding_not_ready(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=object(),
            attempt_binding_result=binding_result(
                status=NonProductionAssessmentSubmissionAttemptBindingStatus.REPLAYED,
            ),
        )

    def test_67_dicts_booleans_and_hostile_objects_are_malformed(self):
        for kwargs in (
            {"principal_mapping_result": {"status": AuthorityLookupStatus.FOUND}},
            {"engagement_lookup_result": {"status": "FOUND"}},
            {"participation_lookup_result": True},
            {"attempt_binding_result": object()},
        ):
            with self.subTest(kwargs=kwargs):
                assert_status(self, MALFORMED, **kwargs)

    def test_68_source_avoids_vars_dict_and_authority_bools(self):
        source = inspect.getsource(context_module)

        self.assertNotIn("vars(", source)
        self.assertNotIn("__dict__", source)
        for disallowed in (
            "authenticated",
            "authorized",
            "allowed",
            "participates",
            "permission",
        ):
            self.assertNotIn(disallowed, source)

    def test_69_function_signature_has_only_captured_result_inputs(self):
        signature = inspect.signature(
            resolve_non_production_assessment_engagement_context_legitimacy
        )

        self.assertEqual(
            tuple(signature.parameters),
            (
                "principal_mapping_result",
                "engagement_result",
                "participation_result",
                "attempt_binding_result",
            ),
        )
        self.assertTrue(
            all(
                parameter.kind is inspect.Parameter.KEYWORD_ONLY
                for parameter in signature.parameters.values()
            )
        )

    def test_70_public_authority_surface_is_exact(self):
        public_names = {
            name
            for name in dir(context_module)
            if not name.startswith("_")
            and getattr(getattr(context_module, name), "__module__", None)
            == context_module.__name__
        }

        self.assertEqual(
            public_names,
            {
                "NonProductionAssessmentEngagementContextLegitimacy",
                "NonProductionAssessmentEngagementContextLegitimacyStatus",
                "NonProductionAssessmentEngagementContextLegitimacyResult",
                "resolve_non_production_assessment_engagement_context_legitimacy",
            },
        )

    def test_71_source_imports_no_downstream_or_runtime_authority(self):
        source = inspect.getsource(context_module)
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }

        for forbidden in (
            "trusted_authorization.membership_source",
            "trusted_authorization.entitlement_source",
            "trusted_authorization.business_entity_source",
            "trusted_authorization.resource_identity_source",
            "trusted_authorization.evaluator",
            "trusted_authorization.non_production_runtime_composition",
            "boto3",
        ):
            self.assertNotIn(forbidden, imported_modules)

    def test_72_output_contains_no_business_context_or_allow_deny(self):
        source = inspect.getsource(context_module)

        self.assertNotIn("BUSINESS_CONTEXT_READY", source)
        self.assertNotIn("ALLOW", source)
        self.assertNotIn("DENY", source)
        self.assertNotIn("AuthorizationDecision", source)

    def test_73_result_mutation_does_not_affect_later_calls(self):
        first = resolve()
        object.__setattr__(first, "context_legitimacy", None)

        second = resolve()
        self.assertEqual(second.status, READY)
        self.assertIsNotNone(second.context_legitimacy)

    def test_74_operation_scope_is_not_permission(self):
        result = resolve()

        self.assertEqual(result.status, READY)
        self.assertFalse(hasattr(result.context_legitimacy, "permission"))

    def test_75_all_non_ready_results_have_no_context_legitimacy(self):
        scenarios = (
            {"principal_mapping_result": object()},
            {
                "principal_mapping_result": principal_result(
                    status=AuthorityLookupStatus.NOT_FOUND,
                ),
            },
            {
                "engagement_lookup_result": engagement_result(
                    status=NonProductionAssessmentEngagementLookupStatus.NOT_FOUND,
                ),
            },
            {
                "participation_lookup_result": participation_result(
                    status=(
                        NonProductionAssessmentEngagementParticipationLookupStatus.
                        NOT_FOUND
                    ),
                ),
            },
            {
                "attempt_binding_result": binding_result(
                    status=(
                        NonProductionAssessmentSubmissionAttemptBindingStatus.
                        REPLAYED
                    ),
                ),
            },
            {
                "attempt_binding_result": binding_result(
                    binding=binding_record(principal_id="principal-other"),
                ),
            },
        )
        for kwargs in scenarios:
            with self.subTest(kwargs=kwargs):
                self.assertIsNone(resolve(**kwargs).context_legitimacy)


if __name__ == "__main__":
    unittest.main()
