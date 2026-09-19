import ast
import inspect
import sys
import unittest
from dataclasses import FrozenInstanceError, fields, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_business_context as business_context_module  # noqa: E402
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    BusinessEntity,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_engagement_context_legitimacy import (  # noqa: E402
    NonProductionAssessmentEngagementContextLegitimacy,
    NonProductionAssessmentEngagementContextLegitimacyResult,
    NonProductionAssessmentEngagementContextLegitimacyStatus,
)
from trusted_authorization.non_production_assessment_engagement_source import (  # noqa: E402
    NonProductionAssessmentEngagementAuthorityEvidence,
    NonProductionAssessmentEngagementLifecycleState,
    NonProductionAssessmentEngagementLookupResult,
    NonProductionAssessmentEngagementLookupStatus,
)
from trusted_authorization.non_production_assessment_submission_business_context import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus,
    resolve_non_production_assessment_submission_business_context,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionGovernedAssessmentSubmissionBusinessContext,
)


READY = NonProductionAssessmentSubmissionBusinessContextStatus.READY
MALFORMED = NonProductionAssessmentSubmissionBusinessContextStatus.MALFORMED
ENGAGEMENT_NOT_READY = (
    NonProductionAssessmentSubmissionBusinessContextStatus.ENGAGEMENT_NOT_READY
)
BUSINESS_ENTITY_NOT_READY = (
    NonProductionAssessmentSubmissionBusinessContextStatus.
    BUSINESS_ENTITY_NOT_READY
)
E_CONTEXT_NOT_READY = (
    NonProductionAssessmentSubmissionBusinessContextStatus.E_CONTEXT_NOT_READY
)
MISMATCH = NonProductionAssessmentSubmissionBusinessContextStatus.MISMATCH
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)


class StringSubclass(str):
    pass


class ForeignOperation(Enum):
    PROTECTED_ASSESSMENT_SUBMISSION = "PROTECTED_ASSESSMENT_SUBMISSION"


class ForeignStatus(Enum):
    FOUND = "FOUND"


class EngagementEvidenceSubclass(NonProductionAssessmentEngagementAuthorityEvidence):
    pass


class EngagementResultSubclass(NonProductionAssessmentEngagementLookupResult):
    pass


class BusinessEntitySubclass(BusinessEntity):
    pass


class AuthorityLookupResultSubclass(AuthorityLookupResult):
    pass


class ContextLegitimacySubclass(NonProductionAssessmentEngagementContextLegitimacy):
    pass


class ContextLegitimacyResultSubclass(
    NonProductionAssessmentEngagementContextLegitimacyResult
):
    pass


class HostileAttributeObject:
    reads = 0

    def __getattribute__(self, name):
        type(self).reads += 1
        raise AssertionError("foreign attributes must not be read")


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


def business_entity_record(
    authority_reference="business-entity-authority",
    state=AuthorityRecordState.ACTIVE,
    business_entity_id="business-alpha",
):
    return BusinessEntity(
        authority_reference=authority_reference,
        state=state,
        business_entity_id=business_entity_id,
    )


def business_entity_result(status=AuthorityLookupStatus.FOUND, records=None):
    if records is None:
        records = (
            (business_entity_record(),)
            if status is AuthorityLookupStatus.FOUND
            else ()
        )
    return AuthorityLookupResult(status=status, records=records)


def context_legitimacy_record(
    attempt_reference="attempt-alpha",
    principal_id="principal-alpha",
    engagement_reference="engagement-alpha",
    protected_operation=PROTECTED_ASSESSMENT,
    principal_authority_reference="principal-authority",
    engagement_authority_reference="engagement-authority",
    engagement_establishment_provenance_reference="engagement-provenance",
    participation_authority_reference="participation-authority",
    participation_provenance_reference="participation-provenance",
):
    return NonProductionAssessmentEngagementContextLegitimacy(
        attempt_reference=attempt_reference,
        principal_id=principal_id,
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


def context_legitimacy_result(
    status=NonProductionAssessmentEngagementContextLegitimacyStatus.READY,
    context_legitimacy=None,
):
    if (
        context_legitimacy is None
        and status is NonProductionAssessmentEngagementContextLegitimacyStatus.READY
    ):
        context_legitimacy = context_legitimacy_record()
    return NonProductionAssessmentEngagementContextLegitimacyResult(
        status=status,
        context_legitimacy=context_legitimacy,
    )


def resolve(
    *,
    engagement_lookup_result=None,
    business_entity_lookup_result=None,
    context_result=None,
):
    if engagement_lookup_result is None:
        engagement_lookup_result = engagement_result()
    if business_entity_lookup_result is None:
        business_entity_lookup_result = business_entity_result()
    if context_result is None:
        context_result = context_legitimacy_result()
    return resolve_non_production_assessment_submission_business_context(
        engagement_result=engagement_lookup_result,
        business_entity_result=business_entity_lookup_result,
        engagement_context_legitimacy_result=context_result,
    )


def assert_status(testcase, expected_status, **kwargs):
    result = resolve(**kwargs)
    testcase.assertEqual(result.status, expected_status)
    if expected_status is READY:
        testcase.assertIs(
            type(result.business_context),
            NonProductionAssessmentSubmissionBusinessContext,
        )
    else:
        testcase.assertIsNone(result.business_context)
    return result


class NonProductionAssessmentSubmissionBusinessContextTests(unittest.TestCase):
    def test_01_valid_captured_inputs_return_ready(self):
        result = assert_status(self, READY)

        self.assertIs(type(result), NonProductionAssessmentSubmissionBusinessContextResult)

    def test_02_ready_output_contains_exact_eleven_fields(self):
        context = resolve().business_context

        self.assertEqual(
            tuple(field.name for field in fields(context)),
            (
                "attempt_reference",
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
            ),
        )
        self.assertEqual(context.attempt_reference, "attempt-alpha")
        self.assertEqual(context.principal_id, "principal-alpha")
        self.assertEqual(context.engagement_reference, "engagement-alpha")
        self.assertEqual(context.business_entity_id, "business-alpha")
        self.assertIs(context.protected_operation, PROTECTED_ASSESSMENT)
        self.assertEqual(context.principal_authority_reference, "principal-authority")
        self.assertEqual(
            context.engagement_authority_reference,
            "engagement-authority",
        )
        self.assertEqual(
            context.engagement_establishment_provenance_reference,
            "engagement-provenance",
        )
        self.assertEqual(
            context.participation_authority_reference,
            "participation-authority",
        )
        self.assertEqual(
            context.participation_provenance_reference,
            "participation-provenance",
        )
        self.assertEqual(
            context.business_entity_authority_reference,
            "business-entity-authority",
        )
        self.assertFalse(hasattr(context, "resource_reference"))
        self.assertFalse(hasattr(context, "permission"))
        self.assertFalse(hasattr(context, "allow"))
        self.assertFalse(hasattr(context, "deny"))

    def test_03_status_members_are_exact(self):
        self.assertEqual(
            {status.name for status in NonProductionAssessmentSubmissionBusinessContextStatus},
            {
                "READY",
                "MALFORMED",
                "ENGAGEMENT_NOT_READY",
                "BUSINESS_ENTITY_NOT_READY",
                "E_CONTEXT_NOT_READY",
                "MISMATCH",
            },
        )

    def test_04_result_contract_only_ready_carries_record(self):
        self.assertIsNotNone(resolve().business_context)
        for status in NonProductionAssessmentSubmissionBusinessContextStatus:
            if status is READY:
                continue
            result = NonProductionAssessmentSubmissionBusinessContextResult(
                status=status,
                business_context=None,
            )
            self.assertIsNone(result.business_context)

    def test_05_repeated_ready_composition_is_deterministic_and_fresh(self):
        first = resolve()
        second = resolve()

        self.assertEqual(first.status, READY)
        self.assertEqual(second.status, READY)
        self.assertIsNot(first, second)
        self.assertIsNot(first.business_context, second.business_context)
        self.assertEqual(first.business_context, second.business_context)

    def test_06_output_is_frozen_and_mutation_does_not_affect_later_calls(self):
        first = resolve()

        with self.assertRaises(FrozenInstanceError):
            first.business_context.business_entity_id = "business-evil"
        object.__setattr__(first.business_context, "business_entity_id", "business-evil")

        second = resolve()
        self.assertEqual(second.business_context.business_entity_id, "business-alpha")

    def test_07_no_mutable_composer_state_exists(self):
        self.assertFalse(
            any(
                name
                for name in dir(business_context_module)
                if name.startswith("_") and name.endswith("registry")
            )
        )
        self.assertFalse(hasattr(business_context_module, "_attempts"))
        self.assertFalse(hasattr(business_context_module, "_cache"))

    def test_08_engagement_non_found_statuses_are_not_ready(self):
        for status in NonProductionAssessmentEngagementLookupStatus:
            if status is NonProductionAssessmentEngagementLookupStatus.FOUND:
                continue
            with self.subTest(status=status):
                assert_status(
                    self,
                    ENGAGEMENT_NOT_READY,
                    engagement_lookup_result=engagement_result(status=status),
                )

    def test_09_engagement_zero_record_success_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(records=()),
        )

    def test_10_engagement_multi_record_success_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(),
                    engagement_record(authority_reference="engagement-authority-2"),
                ),
            ),
        )

    def test_11_engagement_wrong_record_type_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(records=(object(),)),
        )

    def test_12_engagement_record_subclass_is_malformed(self):
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

    def test_13_engagement_result_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=EngagementResultSubclass(
                NonProductionAssessmentEngagementLookupStatus.FOUND,
                (engagement_record(),),
            ),
        )

    def test_14_engagement_non_current_success_is_malformed(self):
        for record in (
            engagement_record(state=AuthorityRecordState.STALE),
            engagement_record(
                lifecycle_state=NonProductionAssessmentEngagementLifecycleState.
                NON_CURRENT
            ),
        ):
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    engagement_lookup_result=engagement_result(records=(record,)),
                )

    def test_15_engagement_strings_are_strict(self):
        cases = (
            engagement_record(engagement_reference=""),
            engagement_record(engagement_reference=" engagement-alpha"),
            engagement_record(engagement_reference=StringSubclass("engagement-alpha")),
            engagement_record(business_entity_id="business-alpha "),
            engagement_record(business_entity_id=StringSubclass("business-alpha")),
            engagement_record(authority_reference=""),
            engagement_record(
                establishment_provenance_reference=StringSubclass(
                    "engagement-provenance"
                ),
            ),
        )
        for record in cases:
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    engagement_lookup_result=engagement_result(records=(record,)),
                )

    def test_16_business_entity_non_success_statuses_are_not_ready(self):
        for status in AuthorityLookupStatus:
            if status is AuthorityLookupStatus.FOUND:
                continue
            with self.subTest(status=status):
                assert_status(
                    self,
                    BUSINESS_ENTITY_NOT_READY,
                    business_entity_lookup_result=business_entity_result(status=status),
                )

    def test_17_business_entity_zero_record_success_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=business_entity_result(records=()),
        )

    def test_18_business_entity_multi_record_success_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=business_entity_result(
                records=(
                    business_entity_record(),
                    business_entity_record(authority_reference="business-authority-2"),
                ),
            ),
        )

    def test_19_business_entity_wrong_record_type_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=business_entity_result(records=(object(),)),
        )

    def test_20_business_entity_record_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=business_entity_result(
                records=(
                    BusinessEntitySubclass(
                        "business-entity-authority",
                        AuthorityRecordState.ACTIVE,
                        "business-alpha",
                    ),
                ),
            ),
        )

    def test_21_business_entity_result_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=AuthorityLookupResultSubclass(
                AuthorityLookupStatus.FOUND,
                (business_entity_record(),),
            ),
        )

    def test_22_business_entity_non_active_success_is_malformed(self):
        for state in AuthorityRecordState:
            if state is AuthorityRecordState.ACTIVE:
                continue
            with self.subTest(state=state):
                assert_status(
                    self,
                    MALFORMED,
                    business_entity_lookup_result=business_entity_result(
                        records=(business_entity_record(state=state),),
                    ),
                )

    def test_23_business_entity_strings_are_strict(self):
        cases = (
            business_entity_record(business_entity_id=""),
            business_entity_record(business_entity_id=" business-alpha"),
            business_entity_record(business_entity_id=StringSubclass("business-alpha")),
            business_entity_record(authority_reference="business-authority "),
            business_entity_record(
                authority_reference=StringSubclass("business-entity-authority")
            ),
        )
        for record in cases:
            with self.subTest(record=record):
                assert_status(
                    self,
                    MALFORMED,
                    business_entity_lookup_result=business_entity_result(
                        records=(record,),
                    ),
                )

    def test_24_e_context_non_ready_statuses_are_not_ready(self):
        for status in NonProductionAssessmentEngagementContextLegitimacyStatus:
            if status is NonProductionAssessmentEngagementContextLegitimacyStatus.READY:
                continue
            with self.subTest(status=status):
                assert_status(
                    self,
                    E_CONTEXT_NOT_READY,
                    context_result=context_legitimacy_result(status=status),
                )

    def test_25_e_context_ready_without_record_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            context_result=NonProductionAssessmentEngagementContextLegitimacyResult(
                status=NonProductionAssessmentEngagementContextLegitimacyStatus.READY,
                context_legitimacy=None,
            ),
        )

    def test_26_e_context_non_ready_with_record_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            context_result=NonProductionAssessmentEngagementContextLegitimacyResult(
                status=(
                    NonProductionAssessmentEngagementContextLegitimacyStatus.
                    MISMATCH
                ),
                context_legitimacy=context_legitimacy_record(),
            ),
        )

    def test_27_e_context_record_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            context_result=context_legitimacy_result(
                context_legitimacy=ContextLegitimacySubclass(
                    "attempt-alpha",
                    "principal-alpha",
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

    def test_28_e_context_result_subclass_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            context_result=ContextLegitimacyResultSubclass(
                NonProductionAssessmentEngagementContextLegitimacyStatus.READY,
                context_legitimacy_record(),
            ),
        )

    def test_29_e_context_strings_are_strict(self):
        cases = (
            context_legitimacy_record(attempt_reference=""),
            context_legitimacy_record(attempt_reference=" attempt-alpha"),
            context_legitimacy_record(attempt_reference=StringSubclass("attempt-alpha")),
            context_legitimacy_record(principal_id="principal-alpha "),
            context_legitimacy_record(principal_id=StringSubclass("principal-alpha")),
            context_legitimacy_record(engagement_reference=""),
            context_legitimacy_record(
                principal_authority_reference=StringSubclass("principal-authority")
            ),
            context_legitimacy_record(engagement_authority_reference=" "),
            context_legitimacy_record(
                engagement_establishment_provenance_reference=StringSubclass(
                    "engagement-provenance"
                )
            ),
            context_legitimacy_record(participation_authority_reference="x "),
            context_legitimacy_record(
                participation_provenance_reference=StringSubclass(
                    "participation-provenance"
                )
            ),
        )
        for context in cases:
            with self.subTest(context=context):
                assert_status(
                    self,
                    MALFORMED,
                    context_result=context_legitimacy_result(
                        context_legitimacy=context,
                    ),
                )

    def test_30_e_context_foreign_operation_is_malformed(self):
        assert_status(
            self,
            MALFORMED,
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    protected_operation=ForeignOperation.PROTECTED_ASSESSMENT_SUBMISSION
                ),
            ),
        )

    def test_31_exact_e_mismatch_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    engagement_reference="engagement-beta",
                ),
            ),
        )

    def test_32_same_b_different_e_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        engagement_reference="engagement-alpha",
                        business_entity_id="business-alpha",
                    ),
                ),
            ),
            business_entity_lookup_result=business_entity_result(
                records=(business_entity_record(business_entity_id="business-alpha"),),
            ),
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    engagement_reference="engagement-beta",
                ),
            ),
        )

    def test_33_exact_b_mismatch_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            business_entity_lookup_result=business_entity_result(
                records=(business_entity_record(business_entity_id="business-beta"),),
            ),
        )

    def test_34_cross_b_substitution_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            engagement_lookup_result=engagement_result(
                records=(engagement_record(business_entity_id="business-alpha"),),
            ),
            business_entity_lookup_result=business_entity_result(
                records=(business_entity_record(business_entity_id="business-beta"),),
            ),
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    engagement_reference="engagement-alpha",
                ),
            ),
        )

    def test_35_engagement_authority_provenance_mismatch_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    engagement_authority_reference="engagement-authority-old",
                ),
            ),
        )

    def test_36_engagement_establishment_provenance_mismatch_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    engagement_establishment_provenance_reference=(
                        "engagement-provenance-old"
                    ),
                ),
            ),
        )

    def test_37_engagement_authority_rotation_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        authority_reference="engagement-authority-rotated",
                    ),
                ),
            ),
        )

    def test_38_engagement_establishment_provenance_rotation_is_mismatch(self):
        assert_status(
            self,
            MISMATCH,
            engagement_lookup_result=engagement_result(
                records=(
                    engagement_record(
                        establishment_provenance_reference=(
                            "engagement-provenance-rotated"
                        ),
                    ),
                ),
            ),
        )

    def test_39_attempt_scope_is_preserved_from_e_context(self):
        result = resolve(
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    attempt_reference="attempt-beta",
                ),
            ),
        )

        self.assertEqual(result.status, READY)
        self.assertEqual(result.business_context.attempt_reference, "attempt-beta")

    def test_40_principal_is_preserved_but_does_not_select_b(self):
        result = resolve(
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    principal_id="principal-beta",
                ),
            ),
        )

        self.assertEqual(result.status, READY)
        self.assertEqual(result.business_context.principal_id, "principal-beta")
        self.assertEqual(result.business_context.business_entity_id, "business-alpha")

    def test_41_business_entity_authority_is_preserved(self):
        result = resolve(
            business_entity_lookup_result=business_entity_result(
                records=(
                    business_entity_record(
                        authority_reference="business-entity-authority-beta",
                    ),
                ),
            ),
        )

        self.assertEqual(result.status, READY)
        self.assertEqual(
            result.business_context.business_entity_authority_reference,
            "business-entity-authority-beta",
        )

    def test_42_operation_is_preserved_and_exact(self):
        result = resolve()

        self.assertIs(result.business_context.protected_operation, PROTECTED_ASSESSMENT)

    def test_43_malformed_dominates_all_not_ready(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=object(),
            business_entity_lookup_result=business_entity_result(
                status=AuthorityLookupStatus.NOT_FOUND,
            ),
            context_result=context_legitimacy_result(
                status=(
                    NonProductionAssessmentEngagementContextLegitimacyStatus.
                    MISMATCH
                ),
            ),
        )

    def test_44_malformed_business_entity_dominates_engagement_not_ready(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(
                status=NonProductionAssessmentEngagementLookupStatus.NOT_FOUND,
            ),
            business_entity_lookup_result=object(),
        )

    def test_45_malformed_e_context_dominates_business_entity_not_ready(self):
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=business_entity_result(
                status=AuthorityLookupStatus.NOT_FOUND,
            ),
            context_result=object(),
        )

    def test_46_engagement_not_ready_precedes_business_entity_not_ready(self):
        assert_status(
            self,
            ENGAGEMENT_NOT_READY,
            engagement_lookup_result=engagement_result(
                status=NonProductionAssessmentEngagementLookupStatus.NOT_FOUND,
            ),
            business_entity_lookup_result=business_entity_result(
                status=AuthorityLookupStatus.NOT_FOUND,
            ),
        )

    def test_47_business_entity_not_ready_precedes_e_context_not_ready(self):
        assert_status(
            self,
            BUSINESS_ENTITY_NOT_READY,
            business_entity_lookup_result=business_entity_result(
                status=AuthorityLookupStatus.NOT_FOUND,
            ),
            context_result=context_legitimacy_result(
                status=(
                    NonProductionAssessmentEngagementContextLegitimacyStatus.
                    BINDING_NOT_READY
                ),
            ),
        )

    def test_48_e_context_not_ready_precedes_mismatch(self):
        assert_status(
            self,
            E_CONTEXT_NOT_READY,
            context_result=context_legitimacy_result(
                status=(
                    NonProductionAssessmentEngagementContextLegitimacyStatus.
                    BINDING_NOT_READY
                ),
            ),
            business_entity_lookup_result=business_entity_result(
                records=(business_entity_record(business_entity_id="business-beta"),),
            ),
        )

    def test_49_mismatch_precedes_ready(self):
        assert_status(
            self,
            MISMATCH,
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    engagement_authority_reference="wrong-authority",
                ),
            ),
        )

    def test_50_forged_engagement_success_with_malformed_evidence_is_malformed(self):
        malformed = object.__new__(NonProductionAssessmentEngagementAuthorityEvidence)
        object.__setattr__(malformed, "authority_reference", "engagement-authority")

        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=engagement_result(records=(malformed,)),
        )

    def test_51_forged_business_entity_success_with_malformed_record_is_malformed(self):
        malformed = object.__new__(BusinessEntity)
        object.__setattr__(malformed, "authority_reference", "business-authority")

        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=business_entity_result(records=(malformed,)),
        )

    def test_52_forged_ready_e_context_malformed_record_is_malformed(self):
        malformed = object.__new__(NonProductionAssessmentEngagementContextLegitimacy)
        object.__setattr__(malformed, "attempt_reference", "attempt-alpha")

        assert_status(
            self,
            MALFORMED,
            context_result=context_legitimacy_result(context_legitimacy=malformed),
        )

    def test_53_forged_ready_e_context_exact_but_mismatched_fails(self):
        assert_status(
            self,
            MISMATCH,
            context_result=context_legitimacy_result(
                context_legitimacy=context_legitimacy_record(
                    engagement_reference="engagement-forged",
                ),
            ),
        )

    def test_54_forged_ready_e_context_exact_matching_is_bounded_ready(self):
        result = resolve(
            context_result=NonProductionAssessmentEngagementContextLegitimacyResult(
                NonProductionAssessmentEngagementContextLegitimacyStatus.READY,
                NonProductionAssessmentEngagementContextLegitimacy(
                    "attempt-alpha",
                    "principal-alpha",
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

        self.assertEqual(result.status, READY)

    def test_55_placeholder_cannot_be_supplied_as_proof(self):
        placeholder = NonProductionGovernedAssessmentSubmissionBusinessContext(
            business_entity_id="business-alpha",
        )

        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=placeholder,
        )
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=placeholder,
        )
        assert_status(
            self,
            MALFORMED,
            context_result=placeholder,
        )

    def test_56_public_api_accepts_no_raw_business_entity_argument(self):
        signature = inspect.signature(
            resolve_non_production_assessment_submission_business_context
        )

        self.assertEqual(
            tuple(signature.parameters),
            (
                "engagement_result",
                "business_entity_result",
                "engagement_context_legitimacy_result",
            ),
        )
        self.assertNotIn("business_entity_id", signature.parameters)

    def test_57_hostile_and_mapping_like_objects_are_rejected_without_reads(self):
        hostile = HostileAttributeObject()
        HostileAttributeObject.reads = 0

        assert_status(self, MALFORMED, engagement_lookup_result=hostile)
        self.assertEqual(HostileAttributeObject.reads, 0)
        assert_status(self, MALFORMED, business_entity_lookup_result={"records": ()})
        assert_status(self, MALFORMED, context_result={"context_legitimacy": None})

    def test_58_foreign_status_enums_are_malformed(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=NonProductionAssessmentEngagementLookupResult(
                status=ForeignStatus.FOUND,
                records=(engagement_record(),),
            ),
        )
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=AuthorityLookupResult(
                status=ForeignStatus.FOUND,
                records=(business_entity_record(),),
            ),
        )
        assert_status(
            self,
            MALFORMED,
            context_result=NonProductionAssessmentEngagementContextLegitimacyResult(
                status=ForeignStatus.FOUND,
                context_legitimacy=context_legitimacy_record(),
            ),
        )

    def test_59_records_tuple_is_required(self):
        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=NonProductionAssessmentEngagementLookupResult(
                NonProductionAssessmentEngagementLookupStatus.FOUND,
                [engagement_record()],
            ),
        )
        assert_status(
            self,
            MALFORMED,
            business_entity_lookup_result=AuthorityLookupResult(
                AuthorityLookupStatus.FOUND,
                [business_entity_record()],
            ),
        )

    def test_60_structurally_valid_non_success_records_do_not_launder_ready(self):
        assert_status(
            self,
            ENGAGEMENT_NOT_READY,
            engagement_lookup_result=engagement_result(
                status=NonProductionAssessmentEngagementLookupStatus.AMBIGUOUS,
                records=(engagement_record(),),
            ),
        )
        assert_status(
            self,
            BUSINESS_ENTITY_NOT_READY,
            business_entity_lookup_result=business_entity_result(
                status=AuthorityLookupStatus.AMBIGUOUS,
                records=(business_entity_record(),),
            ),
        )

    def test_61_existing_result_constructor_can_make_non_ready_only_without_record(self):
        for status in NonProductionAssessmentSubmissionBusinessContextStatus:
            if status is READY:
                continue
            result = NonProductionAssessmentSubmissionBusinessContextResult(status)
            self.assertIsNone(result.business_context)

    def test_62_source_import_boundary_excludes_downstream_and_runtime_modules(self):
        source = inspect.getsource(business_context_module)

        forbidden_terms = (
            "membership",
            "entitlement",
            "resource_identity",
            "target_handoff",
            "runtime",
            "evaluator",
            "boto3",
            "cognito",
            "jwt",
            "requests",
        )
        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, source.lower())

    def test_63_source_avoids_vars_and_dunder_dict_authority_reads(self):
        tree = ast.parse(inspect.getsource(business_context_module))
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("vars", called_names)
        self.assertNotIn("__dict__", inspect.getsource(business_context_module))

    def test_64_source_does_not_invoke_authority_sources_or_e_context_composer(self):
        source = inspect.getsource(business_context_module)

        self.assertNotIn("NonProductionAssessmentEngagementAuthoritySource", source)
        self.assertNotIn("NonProductionBusinessEntityAuthoritySource", source)
        self.assertNotIn(
            "resolve_non_production_assessment_engagement_context_legitimacy(",
            source,
        )
        self.assertNotIn("AttemptBindingDeriver", source)

    def test_65_no_lifecycle_or_authority_source_class_is_introduced(self):
        public_classes = {
            name
            for name, value in vars(business_context_module).items()
            if inspect.isclass(value) and value.__module__ == business_context_module.__name__
        }

        self.assertEqual(
            {
                name
                for name in public_classes
                if not name.startswith("_")
            },
            {
                "NonProductionAssessmentSubmissionBusinessContext",
                "NonProductionAssessmentSubmissionBusinessContextStatus",
                "NonProductionAssessmentSubmissionBusinessContextResult",
            },
        )
        self.assertFalse(any("Source" in name for name in public_classes))
        self.assertFalse(any("Lifecycle" in name for name in public_classes))

    def test_66_ready_context_is_not_existing_lifecycle_placeholder(self):
        result = resolve()

        self.assertIs(
            type(result.business_context),
            NonProductionAssessmentSubmissionBusinessContext,
        )
        self.assertIsNot(
            type(result.business_context),
            NonProductionGovernedAssessmentSubmissionBusinessContext,
        )

    def test_67_no_output_aliasing_to_upstream_records(self):
        engagement = engagement_record()
        entity = business_entity_record()
        legitimacy = context_legitimacy_record()
        result = resolve(
            engagement_lookup_result=engagement_result(records=(engagement,)),
            business_entity_lookup_result=business_entity_result(records=(entity,)),
            context_result=context_legitimacy_result(context_legitimacy=legitimacy),
        )

        self.assertIsNot(result.business_context, engagement)
        self.assertIsNot(result.business_context, entity)
        self.assertIsNot(result.business_context, legitimacy)

    def test_68_repeated_composition_with_same_inputs_may_return_ready(self):
        engagement = engagement_result()
        entity = business_entity_result()
        legitimacy = context_legitimacy_result()

        self.assertEqual(
            resolve(
                engagement_lookup_result=engagement,
                business_entity_lookup_result=entity,
                context_result=legitimacy,
            ).status,
            READY,
        )
        self.assertEqual(
            resolve(
                engagement_lookup_result=engagement,
                business_entity_lookup_result=entity,
                context_result=legitimacy,
            ).status,
            READY,
        )

    def test_69_business_context_result_subclass_is_not_input_authority(self):
        class BusinessContextResultSubclass(
            NonProductionAssessmentSubmissionBusinessContextResult
        ):
            pass

        assert_status(
            self,
            MALFORMED,
            engagement_lookup_result=BusinessContextResultSubclass(READY),
        )

    def test_70_wrong_operation_value_under_exact_type_is_mismatch_when_possible(self):
        operation_members = tuple(NonProductionProtectedApplicationOperation)
        self.assertEqual(operation_members, (PROTECTED_ASSESSMENT,))

    def test_71_replace_can_construct_mismatched_e_context_but_it_fails_closed(self):
        legitimacy = replace(
            context_legitimacy_record(),
            engagement_establishment_provenance_reference="other-provenance",
        )

        assert_status(
            self,
            MISMATCH,
            context_result=context_legitimacy_result(context_legitimacy=legitimacy),
        )

    def test_72_direct_business_context_construction_is_not_composer_input(self):
        constructed = NonProductionAssessmentSubmissionBusinessContext(
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
        )

        assert_status(self, MALFORMED, context_result=constructed)

    def test_73_raw_caller_principal_or_business_entity_cannot_be_supplied(self):
        assert_status(self, MALFORMED, engagement_lookup_result="engagement-alpha")
        assert_status(self, MALFORMED, business_entity_lookup_result="business-alpha")
        assert_status(self, MALFORMED, context_result="attempt-alpha")

    def test_74_no_permission_or_allow_deny_surface_exists(self):
        public_names = {
            name
            for name in vars(business_context_module)
            if not name.startswith("_")
        }

        for forbidden in (
            "Membership",
            "Entitlement",
            "ResourceIdentity",
            "Target",
            "Permission",
            "ALLOW",
            "DENY",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertFalse(any(forbidden in name for name in public_names))

    def test_75_output_mutation_does_not_create_hidden_state(self):
        first = resolve()
        second = resolve()
        object.__setattr__(
            first,
            "business_context",
            NonProductionAssessmentSubmissionBusinessContext(
                attempt_reference="attempt-evil",
                principal_id="principal-evil",
                engagement_reference="engagement-evil",
                business_entity_id="business-evil",
                protected_operation=PROTECTED_ASSESSMENT,
                principal_authority_reference="principal-evil",
                engagement_authority_reference="engagement-evil",
                engagement_establishment_provenance_reference="provenance-evil",
                participation_authority_reference="participation-evil",
                participation_provenance_reference="participation-provenance-evil",
                business_entity_authority_reference="business-entity-evil",
            ),
        )

        third = resolve()
        self.assertEqual(second.business_context.business_entity_id, "business-alpha")
        self.assertEqual(third.business_context.business_entity_id, "business-alpha")
