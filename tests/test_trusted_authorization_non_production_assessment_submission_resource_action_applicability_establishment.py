import dataclasses
import inspect
import sys
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_resource_action_applicability_establishment as applicability_module  # noqa: E402
from trusted_authorization.applicability import (  # noqa: E402
    resolve_applicability,
)
from trusted_authorization.models import (  # noqa: E402
    AuthorityRecordState,
    AuthorizationRequest,
    BusinessEntity,
    Entitlement,
    GovernedResource,
    Membership,
    RequestedAction,
    ResourceActionApplicability,
    ResourceClass,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionApplicationOperationSelectionResult,
    NonProductionApplicationOperationSelectionStatus,
    NonProductionProtectedApplicationOperation,
    resolve_non_production_application_operation_selection,
)
from trusted_authorization.non_production_assessment_submission_business_context import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_action_applicability_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority,
    NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence,
    NonProductionAssessmentSubmissionResourceActionApplicabilityFact,
    NonProductionAssessmentSubmissionResourceActionApplicabilityResult,
    NonProductionAssessmentSubmissionResourceActionApplicabilityStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_identity_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionResourceIdentityAuthority,
    NonProductionAssessmentSubmissionResourceIdentityResult,
    NonProductionAssessmentSubmissionResourceIdentityStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_lifecycle import (  # noqa: E402
    NonProductionAssessmentSubmissionLifecycleState,
)
from trusted_authorization.non_production_resource_action_handoff import (  # noqa: E402
    NonProductionApplicationOperation,
    NonProductionResourceActionHandoffResult,
    NonProductionResourceActionHandoffStatus,
    resolve_non_production_resource_action_handoff,
)


STATUS = NonProductionAssessmentSubmissionResourceActionApplicabilityStatus
ESTABLISHED = STATUS.ESTABLISHED
REUSED = STATUS.REUSED
MALFORMED = STATUS.MALFORMED
MISMATCH = STATUS.MISMATCH
COLLISION = STATUS.COLLISION
NOT_APPLICABLE = STATUS.APPLICABILITY_NOT_APPLICABLE
UNRESOLVED = STATUS.APPLICABILITY_UNRESOLVED
BC_READY = NonProductionAssessmentSubmissionBusinessContextStatus.READY
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)
_DEFAULT = object()


RI_FIELDS = (
    "attempt_reference",
    "resource_reference",
    "resource_id",
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
    "resource_lifecycle_state",
    "lifecycle_authority_reference",
    "lifecycle_provenance_reference",
    "target_authority_reference",
    "target_provenance_reference",
    "target_governance_reference",
    "resource_identity_state",
    "resource_identity_authority_reference",
    "resource_identity_provenance_reference",
    "resource_identity_governance_reference",
)


class StringSubclass(str):
    pass


class BusinessContextResultSubclass(
    NonProductionAssessmentSubmissionBusinessContextResult
):
    pass


class BusinessContextSubclass(NonProductionAssessmentSubmissionBusinessContext):
    pass


class ForeignStatus(Enum):
    READY = "READY"


class ForeignApplicability(Enum):
    APPLICABLE = "APPLICABLE"


class ForeignLifecycle(Enum):
    SUBMITTED = "SUBMITTED"


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
    return NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority(
        candidate_resource_references=tuple(candidates),
    )


def establish(auth=None, *, context_result=_DEFAULT):
    if auth is None:
        auth = authority("resource-alpha")
    if context_result is _DEFAULT:
        context_result = business_context_result()
    return auth.establish_assessment_submission_resource_action_applicability(
        business_context_result=context_result,
    )


def owned_identity_authority(auth):
    return object.__getattribute__(auth, "_resource_identity_authority")


def identity_result(resource_reference="resource-alpha", context_result=None):
    if context_result is None:
        context_result = business_context_result()
    source = NonProductionAssessmentSubmissionResourceIdentityAuthority(
        candidate_resource_references=(resource_reference,),
    )
    return source.establish_assessment_submission_resource_identity(
        business_context_result=context_result,
    )


def replaced_identity_result(result, *, fact=None, evidence=None, **evidence_changes):
    if fact is None:
        fact = result.resource_identity_fact
    if evidence is None:
        evidence = dataclasses.replace(
            result.establishment_evidence,
            **evidence_changes,
        )
    return NonProductionAssessmentSubmissionResourceIdentityResult(
        status=result.status,
        resource_identity_fact=fact,
        establishment_evidence=evidence,
    )


class ResourceActionApplicabilityEstablishmentTests(unittest.TestCase):
    def assert_failure(self, result, status):
        self.assertIs(
            type(result),
            NonProductionAssessmentSubmissionResourceActionApplicabilityResult,
        )
        self.assertIs(result.status, status)
        self.assertIsNone(result.applicability_fact)
        self.assertIsNone(result.establishment_evidence)

    def test_01_public_surface_is_exactly_five_types(self):
        public_types = {
            name
            for name, value in vars(applicability_module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(
            public_types,
            {
                "NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority",
                "NonProductionAssessmentSubmissionResourceActionApplicabilityFact",
                "NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence",
                "NonProductionAssessmentSubmissionResourceActionApplicabilityStatus",
                "NonProductionAssessmentSubmissionResourceActionApplicabilityResult",
            },
        )

    def test_02_constructor_and_method_signatures_are_exact(self):
        self.assertEqual(
            str(inspect.signature(
                NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority
            )),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) "
            "-> 'None'",
        )
        self.assertEqual(
            str(inspect.signature(
                NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority.
                establish_assessment_submission_resource_action_applicability
            )),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionResourceActionApplicabilityResult'",
        )

    def test_03_public_api_has_no_dependency_or_authority_injection(self):
        constructor = inspect.signature(
            NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority
        )
        method = inspect.signature(
            NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority.
            establish_assessment_submission_resource_action_applicability
        )
        self.assertEqual(tuple(constructor.parameters), ("candidate_resource_references",))
        self.assertEqual(tuple(method.parameters), ("self", "business_context_result"))
        public_methods = {
            name
            for name, value in inspect.getmembers(
                NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority
            )
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(
            public_methods,
            {"establish_assessment_submission_resource_action_applicability"},
        )
        with self.assertRaises(TypeError):
            NonProductionAssessmentSubmissionResourceActionApplicabilityAuthority(
                resource_identity_authority=object()
            )

    def test_04_one_exact_private_resource_identity_authority_is_retained(self):
        auth = authority("resource-alpha")
        owned = owned_identity_authority(auth)
        self.assertIs(type(owned), NonProductionAssessmentSubmissionResourceIdentityAuthority)
        self.assertIs(owned_identity_authority(auth), owned)

    def test_05_first_success_returns_exact_types_and_established(self):
        result = establish()
        self.assertIs(result.status, ESTABLISHED)
        self.assertIs(
            type(result),
            NonProductionAssessmentSubmissionResourceActionApplicabilityResult,
        )
        self.assertIs(
            type(result.applicability_fact),
            NonProductionAssessmentSubmissionResourceActionApplicabilityFact,
        )
        self.assertIs(
            type(result.establishment_evidence),
            NonProductionAssessmentSubmissionResourceActionApplicabilityEvidence,
        )

    def test_06_fact_fields_and_values_are_exact(self):
        fact = establish().applicability_fact
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(fact))),
            (
                "resource_reference",
                "resource_id",
                "resource_class",
                "requested_action",
                "applicability",
            ),
        )
        self.assertEqual(fact.resource_reference, "resource-alpha")
        self.assertEqual(fact.resource_id, "resource-alpha")
        self.assertIs(fact.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(fact.requested_action, RequestedAction.SUBMIT)
        self.assertIs(fact.applicability, ResourceActionApplicability.APPLICABLE)

    def test_07_evidence_fields_are_exact_and_preserve_all_ri_lineage(self):
        evidence = establish().establishment_evidence
        actual_fields = tuple(field.name for field in dataclasses.fields(type(evidence)))
        self.assertEqual(
            actual_fields,
            RI_FIELDS
            + (
                "requested_action",
                "applicability",
                "applicability_authority_reference",
                "applicability_provenance_reference",
                "applicability_governance_reference",
            ),
        )
        self.assertEqual(len(actual_fields), 33)
        upstream = identity_result().establishment_evidence
        for name in RI_FIELDS:
            self.assertEqual(getattr(evidence, name), getattr(upstream, name), name)

    def test_08_result_fields_and_payload_invariant_are_exact(self):
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionResourceActionApplicabilityResult
                )
            ),
            ("status", "applicability_fact", "establishment_evidence"),
        )
        success = establish()
        self.assertIsNotNone(success.applicability_fact)
        self.assertIsNotNone(success.establishment_evidence)
        self.assert_failure(establish(authority()), STATUS.ALLOCATION_UNAVAILABLE)

    def test_09_status_enum_is_exactly_fifteen_members(self):
        self.assertEqual(
            tuple(
                member.name
                for member in NonProductionAssessmentSubmissionResourceActionApplicabilityStatus
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
                "RESOURCE_IDENTITY_NOT_FOUND",
                "RESOURCE_IDENTITY_AMBIGUOUS",
                "RESOURCE_IDENTITY_CONFLICTING",
                "RESOURCE_IDENTITY_STALE",
                "RESOURCE_IDENTITY_UNAVAILABLE",
                "APPLICABILITY_NOT_APPLICABLE",
                "APPLICABILITY_UNRESOLVED",
            ),
        )

    def test_10_fixed_references_and_provenance_are_exact(self):
        evidence = establish().establishment_evidence
        self.assertEqual(
            evidence.applicability_authority_reference,
            "non-production-assessment-submission-resource-action-"
            "applicability-authority",
        )
        self.assertEqual(
            evidence.applicability_governance_reference,
            "resource-action-applicability-governance-v1",
        )
        self.assertEqual(
            evidence.applicability_provenance_reference,
            "non-production-assessment-submission-resource-action-"
            "applicability-establishment-provenance-1",
        )

    def test_11_operation_and_action_are_privately_derived(self):
        selections = []
        handoffs = []
        resolutions = []

        def select(*, protected_operation):
            selections.append(protected_operation)
            return resolve_non_production_application_operation_selection(
                protected_operation=protected_operation
            )

        def handoff(*, resource_reference, operation):
            handoffs.append((resource_reference, operation))
            return resolve_non_production_resource_action_handoff(
                resource_reference=resource_reference,
                operation=operation,
            )

        def resolve(resource_class, action):
            resolutions.append((resource_class, action))
            return resolve_applicability(resource_class, action)

        with patch.object(applicability_module, "_select_operation", side_effect=select):
            with patch.object(
                applicability_module, "_resolve_resource_action", side_effect=handoff
            ):
                with patch.object(
                    applicability_module, "_resolve_applicability", side_effect=resolve
                ):
                    result = establish()
        self.assertIs(result.status, ESTABLISHED)
        self.assertEqual(selections, [PROTECTED_ASSESSMENT])
        self.assertEqual(
            handoffs,
            [("resource-alpha", NonProductionApplicationOperation.SUBMIT_ASSESSMENT)],
        )
        self.assertEqual(
            resolutions,
            [(ResourceClass.ASSESSMENT_SUBMISSION, RequestedAction.SUBMIT)],
        )

    def test_12_exact_retry_reuses_event_and_returns_fresh_outputs(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        retry = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(first.applicability_fact, retry.applicability_fact)
        self.assertEqual(first.establishment_evidence, retry.establishment_evidence)
        self.assertIsNot(first, retry)
        self.assertIsNot(first.applicability_fact, retry.applicability_fact)
        self.assertIsNot(first.establishment_evidence, retry.establishment_evidence)

    def test_13_retry_preserves_all_provenance_and_identity(self):
        auth = authority("resource-alpha")
        first = establish(auth).establishment_evidence
        retry = establish(auth).establishment_evidence
        for name in (
            "resource_reference",
            "resource_id",
            "target_provenance_reference",
            "resource_identity_provenance_reference",
            "applicability_provenance_reference",
            "applicability_governance_reference",
        ):
            self.assertEqual(getattr(first, name), getattr(retry, name), name)

    def test_14_three_indexes_reference_one_immutable_event(self):
        auth = authority("resource-alpha")
        establish(auth)
        by_attempt = object.__getattribute__(auth, "_applicabilities_by_attempt")
        by_resource = object.__getattribute__(
            auth, "_applicabilities_by_resource_reference"
        )
        by_id = object.__getattribute__(auth, "_applicabilities_by_resource_id")
        self.assertEqual(len(by_attempt), 1)
        self.assertEqual(len(by_resource), 1)
        self.assertEqual(len(by_id), 1)
        snapshot = by_attempt["attempt-alpha"]
        self.assertIs(by_resource["resource-alpha"], snapshot)
        self.assertIs(by_id["resource-alpha"], snapshot)
        self.assertTrue(dataclasses.is_dataclass(snapshot))
        self.assertEqual(snapshot.__dataclass_params__.frozen, True)

    def test_15_no_fourth_resource_action_index_exists(self):
        auth = authority("resource-alpha")
        self.assertFalse(hasattr(auth, "_applicabilities_by_resource_action"))
        self.assertEqual(
            set(auth.__slots__),
            {
                "_resource_identity_authority",
                "_applicabilities_by_attempt",
                "_applicabilities_by_resource_reference",
                "_applicabilities_by_resource_id",
                "_next_applicability_provenance_index",
            },
        )

    def test_16_every_call_reenters_same_retained_ri_authority(self):
        auth = authority("resource-alpha")
        owned = owned_identity_authority(auth)
        calls = []
        original = (
            NonProductionAssessmentSubmissionResourceIdentityAuthority.
            establish_assessment_submission_resource_identity
        )

        def invoke(instance, *, business_context_result):
            calls.append(instance)
            return original(instance, business_context_result=business_context_result)

        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            side_effect=invoke,
        ):
            establish(auth)
            establish(auth)
        self.assertEqual(calls, [owned, owned])

    def test_17_not_applicable_is_failure_without_state_or_decision(self):
        auth = authority("resource-alpha")
        with patch.object(
            applicability_module,
            "_resolve_applicability",
            return_value=ResourceActionApplicability.NOT_APPLICABLE,
        ):
            result = establish(auth)
        self.assert_failure(result, NOT_APPLICABLE)
        self.assertEqual(object.__getattribute__(auth, "_applicabilities_by_attempt"), {})
        self.assertEqual(
            object.__getattribute__(auth, "_next_applicability_provenance_index"), 1
        )
        self.assertFalse(hasattr(result, "authorization_decision"))

    def test_18_unresolved_and_resolver_exception_fail_without_state(self):
        for side_effect, expected in (
            (None, ResourceActionApplicability.UNRESOLVED),
            (RuntimeError("unavailable"), None),
        ):
            auth = authority("resource-alpha")
            kwargs = (
                {"return_value": expected}
                if side_effect is None
                else {"side_effect": side_effect}
            )
            with patch.object(
                applicability_module, "_resolve_applicability", **kwargs
            ):
                result = establish(auth)
            self.assert_failure(result, UNRESOLVED)
            self.assertEqual(
                object.__getattribute__(auth, "_applicabilities_by_attempt"), {}
            )
            self.assertEqual(
                object.__getattribute__(auth, "_next_applicability_provenance_index"),
                1,
            )

    def test_19_malformed_generic_results_fail_closed(self):
        for value in (ForeignApplicability.APPLICABLE, "APPLICABLE", None, object()):
            with self.subTest(value=value):
                with patch.object(
                    applicability_module, "_resolve_applicability", return_value=value
                ):
                    self.assert_failure(establish(), MALFORMED)

    def test_20_all_ri_failure_statuses_map_one_to_one(self):
        mappings = {
            NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED: (
                STATUS.MALFORMED
            ),
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            BUSINESS_CONTEXT_NOT_READY: STATUS.BUSINESS_CONTEXT_NOT_READY,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            UNSUPPORTED_OPERATION: STATUS.UNSUPPORTED_OPERATION,
            NonProductionAssessmentSubmissionResourceIdentityStatus.MISMATCH: (
                STATUS.MISMATCH
            ),
            NonProductionAssessmentSubmissionResourceIdentityStatus.COLLISION: (
                STATUS.COLLISION
            ),
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            ALLOCATION_UNAVAILABLE: STATUS.ALLOCATION_UNAVAILABLE,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_NOT_FOUND: STATUS.RESOURCE_IDENTITY_NOT_FOUND,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_AMBIGUOUS: STATUS.RESOURCE_IDENTITY_AMBIGUOUS,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_CONFLICTING: STATUS.RESOURCE_IDENTITY_CONFLICTING,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_STALE: STATUS.RESOURCE_IDENTITY_STALE,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_UNAVAILABLE: STATUS.RESOURCE_IDENTITY_UNAVAILABLE,
        }
        for source_status, output_status in mappings.items():
            with self.subTest(source_status=source_status):
                result = NonProductionAssessmentSubmissionResourceIdentityResult(
                    status=source_status
                )
                with patch.object(
                    NonProductionAssessmentSubmissionResourceIdentityAuthority,
                    "establish_assessment_submission_resource_identity",
                    return_value=result,
                ):
                    self.assert_failure(establish(), output_status)

    def test_21_ri_failure_with_payload_is_malformed(self):
        success = identity_result()
        malformed_failure = NonProductionAssessmentSubmissionResourceIdentityResult(
            status=NonProductionAssessmentSubmissionResourceIdentityStatus.MISMATCH,
            resource_identity_fact=success.resource_identity_fact,
            establishment_evidence=success.establishment_evidence,
        )
        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            return_value=malformed_failure,
        ):
            self.assert_failure(establish(), MALFORMED)

    def test_22_bc_types_readiness_and_subclasses_are_hardened(self):
        not_ready_statuses = tuple(
            status
            for status in NonProductionAssessmentSubmissionBusinessContextStatus
            if status is not BC_READY
        )
        for status in not_ready_statuses:
            with self.subTest(status=status):
                self.assert_failure(
                    establish(context_result=business_context_result(status=status)),
                    STATUS.BUSINESS_CONTEXT_NOT_READY,
                )
        bad_inputs = (
            None,
            {},
            HostileObject(),
            BusinessContextResultSubclass(
                status=BC_READY,
                business_context=business_context(),
            ),
            NonProductionAssessmentSubmissionBusinessContextResult(
                status=ForeignStatus.READY,
                business_context=business_context(),
            ),
            business_context_result(
                context=BusinessContextSubclass(
                    **{
                        field.name: getattr(business_context(), field.name)
                        for field in dataclasses.fields(
                            NonProductionAssessmentSubmissionBusinessContext
                        )
                    }
                )
            ),
        )
        for value in bad_inputs:
            with self.subTest(value=type(value)):
                self.assert_failure(establish(context_result=value), MALFORMED)
        self.assertEqual(HostileObject.reads, 0)

    def test_23_all_business_context_strings_are_exact_trimmed_nonblank(self):
        fields = tuple(
            field.name
            for field in dataclasses.fields(
                NonProductionAssessmentSubmissionBusinessContext
            )
            if field.name != "protected_operation"
        )
        for field in fields:
            for value in ("", " ", " value", "value ", StringSubclass("value")):
                with self.subTest(field=field, value=repr(value)):
                    self.assert_failure(
                        establish(
                            context_result=business_context_result(
                                context=business_context(**{field: value})
                            )
                        ),
                        MALFORMED,
                    )

    def test_24_unsupported_operation_precedes_private_ri_invocation(self):
        foreign_operation = object()
        context = business_context(protected_operation=foreign_operation)
        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
        ) as private_ri:
            result = establish(context_result=business_context_result(context=context))
        self.assert_failure(result, MALFORMED)
        private_ri.assert_not_called()

    def test_25_bc_and_ri_lineage_mismatch_fails_closed(self):
        original = identity_result()
        for field, value in (
            ("attempt_reference", "attempt-other"),
            ("principal_id", "principal-other"),
            ("engagement_reference", "engagement-other"),
            ("business_entity_id", "business-other"),
            ("principal_authority_reference", "principal-authority-other"),
            ("engagement_authority_reference", "engagement-authority-other"),
            (
                "engagement_establishment_provenance_reference",
                "engagement-provenance-other",
            ),
            ("participation_authority_reference", "participation-authority-other"),
            (
                "participation_provenance_reference",
                "participation-provenance-other",
            ),
            ("business_entity_authority_reference", "business-authority-other"),
        ):
            with self.subTest(field=field):
                changed = replaced_identity_result(original, **{field: value})
                with patch.object(
                    NonProductionAssessmentSubmissionResourceIdentityAuthority,
                    "establish_assessment_submission_resource_identity",
                    return_value=changed,
                ):
                    self.assert_failure(establish(), MISMATCH)

    def test_26_ri_fact_and_evidence_mismatch_fails_closed(self):
        original = identity_result()
        changed_fact = dataclasses.replace(
            original.resource_identity_fact,
            resource_id="resource-other",
        )
        changed = replaced_identity_result(original, fact=changed_fact)
        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            return_value=changed,
        ):
            self.assert_failure(establish(), MISMATCH)

    def test_27_resource_identity_exact_invariants_are_enforced(self):
        original = identity_result()
        cases = (
            {"resource_id": "resource-other"},
            {"resource_class": ResourceClass.REPORT},
            {"resource_lifecycle_state": ForeignLifecycle.SUBMITTED},
            {"resource_identity_state": AuthorityRecordState.STALE},
            {"target_authority_reference": "target-other"},
            {"target_governance_reference": "target-governance-other"},
            {"resource_identity_authority_reference": "ri-authority-other"},
            {"resource_identity_governance_reference": "ri-governance-other"},
        )
        for changes in cases:
            with self.subTest(changes=changes):
                changed = replaced_identity_result(original, **changes)
                with patch.object(
                    NonProductionAssessmentSubmissionResourceIdentityAuthority,
                    "establish_assessment_submission_resource_identity",
                    return_value=changed,
                ):
                    self.assert_failure(establish(), MALFORMED)

    def test_28_operation_selector_conflicts_fail_closed(self):
        invalid = NonProductionApplicationOperationSelectionResult(
            status=NonProductionApplicationOperationSelectionStatus.INVALID,
            selected_application_operation=None,
        )
        wrong = NonProductionApplicationOperationSelectionResult(
            status=NonProductionApplicationOperationSelectionStatus.READY,
            selected_application_operation=NonProductionApplicationOperation.VIEW_RESOURCE,
        )
        for result, status in ((invalid, MALFORMED), (wrong, MISMATCH)):
            with self.subTest(result=result):
                with patch.object(
                    applicability_module, "_select_operation", return_value=result
                ):
                    self.assert_failure(establish(), status)

    def test_29_resource_action_handoff_conflicts_fail_closed(self):
        cases = (
            (
                NonProductionResourceActionHandoffResult(
                    status=NonProductionResourceActionHandoffStatus.INVALID
                ),
                MALFORMED,
            ),
            (
                NonProductionResourceActionHandoffResult(
                    status=NonProductionResourceActionHandoffStatus.READY,
                    resource_reference="resource-other",
                    requested_action=RequestedAction.SUBMIT,
                ),
                MISMATCH,
            ),
            (
                NonProductionResourceActionHandoffResult(
                    status=NonProductionResourceActionHandoffStatus.READY,
                    resource_reference="resource-alpha",
                    requested_action=RequestedAction.VIEW,
                ),
                MISMATCH,
            ),
        )
        for result, status in cases:
            with self.subTest(result=result):
                with patch.object(
                    applicability_module,
                    "_resolve_resource_action",
                    return_value=result,
                ):
                    self.assert_failure(establish(), status)

    def test_30_changed_upstream_lineage_on_retry_is_mismatch(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        current = identity_result()
        for field in (
            "target_provenance_reference",
            "resource_identity_provenance_reference",
        ):
            with self.subTest(field=field):
                changed = replaced_identity_result(
                    current, **{field: f"{field}-other"}
                )
                with patch.object(
                    NonProductionAssessmentSubmissionResourceIdentityAuthority,
                    "establish_assessment_submission_resource_identity",
                    return_value=changed,
                ):
                    self.assert_failure(establish(auth), MISMATCH)

    def test_31_changed_applicability_governance_fails_without_mutation(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        before = dict(object.__getattribute__(auth, "_applicabilities_by_attempt"))
        with patch.object(
            applicability_module,
            "_GENERIC_APPLICABILITY_GOVERNANCE_REFERENCE",
            "resource-action-applicability-governance-v2",
        ):
            result = establish(auth)
        self.assert_failure(result, UNRESOLVED)
        self.assertEqual(
            object.__getattribute__(auth, "_applicabilities_by_attempt"), before
        )
        self.assertEqual(
            first.establishment_evidence.applicability_provenance_reference,
            "non-production-assessment-submission-resource-action-"
            "applicability-establishment-provenance-1",
        )

    def test_32_existing_attempt_conflict_precedes_collision(self):
        auth = authority("resource-alpha")
        establish(auth)
        by_attempt = object.__getattribute__(auth, "_applicabilities_by_attempt")
        stored = by_attempt["attempt-alpha"]
        object.__getattribute__(auth, "_applicabilities_by_resource_reference").clear()
        result = establish(auth)
        self.assert_failure(result, MISMATCH)
        self.assertIs(by_attempt["attempt-alpha"], stored)

    def test_33_resource_and_resource_id_collisions_fail_closed(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        snapshot = object.__getattribute__(
            auth, "_applicabilities_by_attempt"
        )["attempt-alpha"]
        object.__getattribute__(auth, "_applicabilities_by_attempt").clear()
        for index_name in (
            "_applicabilities_by_resource_reference",
            "_applicabilities_by_resource_id",
        ):
            by_resource = object.__getattribute__(auth, index_name)
            by_resource["resource-alpha"] = snapshot
            self.assert_failure(establish(auth), COLLISION)
            by_resource.clear()
        self.assertIs(first.status, ESTABLISHED)

    def test_34_failure_non_consumption_and_recovery_preserve_upstream_ri(self):
        auth = authority("resource-alpha")
        with patch.object(
            applicability_module,
            "_resolve_applicability",
            side_effect=(
                ResourceActionApplicability.UNRESOLVED,
                ResourceActionApplicability.APPLICABLE,
            ),
        ):
            failed = establish(auth)
            recovered = establish(auth)
        self.assert_failure(failed, UNRESOLVED)
        self.assertIs(recovered.status, ESTABLISHED)
        self.assertEqual(recovered.applicability_fact.resource_reference, "resource-alpha")
        ri = owned_identity_authority(auth)
        identities = object.__getattribute__(ri, "_identities_by_attempt")
        self.assertEqual(len(identities), 1)
        self.assertEqual(
            recovered.establishment_evidence.resource_identity_provenance_reference,
            identities["attempt-alpha"].resource_identity_provenance_reference,
        )
        self.assertEqual(
            object.__getattribute__(auth, "_next_applicability_provenance_index"), 2
        )

    def test_35_different_successful_events_get_distinct_provenance(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        second_context = business_context_result(
            context=business_context(
                attempt_reference="attempt-beta",
                principal_id="principal-beta",
            )
        )
        second = establish(auth, context_result=second_context)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(second.status, ESTABLISHED)
        self.assertEqual(first.applicability_fact.resource_reference, "resource-alpha")
        self.assertEqual(second.applicability_fact.resource_reference, "resource-beta")
        self.assertNotEqual(
            first.establishment_evidence.applicability_provenance_reference,
            second.establishment_evidence.applicability_provenance_reference,
        )

    def test_36_returned_fact_mutation_is_isolated(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        object.__setattr__(first.applicability_fact, "resource_id", "forged")
        object.__setattr__(first.applicability_fact, "requested_action", RequestedAction.VIEW)
        retry = establish(auth)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(retry.applicability_fact.resource_id, "resource-alpha")
        self.assertIs(retry.applicability_fact.requested_action, RequestedAction.SUBMIT)

    def test_37_returned_evidence_and_result_mutation_are_isolated(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        object.__setattr__(first.establishment_evidence, "business_entity_id", "forged")
        object.__setattr__(
            first.establishment_evidence,
            "applicability_provenance_reference",
            "forged",
        )
        object.__setattr__(first, "status", MALFORMED)
        retry = establish(auth)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(retry.establishment_evidence.business_entity_id, "business-alpha")
        self.assertEqual(
            retry.establishment_evidence.applicability_provenance_reference,
            "non-production-assessment-submission-resource-action-"
            "applicability-establishment-provenance-1",
        )

    def test_38_public_payload_construction_cannot_enter_authority(self):
        success = establish()
        candidates = (
            success.applicability_fact,
            success.establishment_evidence,
            success,
            identity_result().resource_identity_fact,
            identity_result().establishment_evidence,
            identity_result(),
            ResourceClass.ASSESSMENT_SUBMISSION,
            RequestedAction.SUBMIT,
            ResourceActionApplicability.APPLICABLE,
        )
        for candidate in candidates:
            with self.subTest(candidate=type(candidate)):
                self.assert_failure(
                    establish(context_result=candidate),
                    MALFORMED,
                )

    def test_39_raw_and_unrelated_authority_objects_are_rejected(self):
        objects = (
            "resource-alpha",
            ("attempt-alpha", "resource-alpha"),
            GovernedResource(
                authority_reference="authority",
                state=AuthorityRecordState.ACTIVE,
                resource_id="resource-alpha",
                resource_reference="resource-alpha",
                resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
                business_entity_id="business-alpha",
            ),
            BusinessEntity("authority", AuthorityRecordState.ACTIVE, "business-alpha"),
            Membership(
                "authority",
                AuthorityRecordState.ACTIVE,
                "principal-alpha",
                "business-alpha",
            ),
            Entitlement(
                "authority",
                AuthorityRecordState.ACTIVE,
                "principal-alpha",
                "business-alpha",
                "resource-alpha",
                RequestedAction.SUBMIT,
            ),
            AuthorizationRequest(None, None, None, None, "correlation", "context"),
            {"root": True, "admin": True, "owner": True},
            {"aws": "identity", "iam": "role", "cognito": "subject"},
            {"ai": "assertion", "llm": "assertion", "mcp": "assertion"},
        )
        for value in objects:
            with self.subTest(value=type(value)):
                self.assert_failure(establish(context_result=value), MALFORMED)

    def test_40_candidate_references_do_not_create_authority_without_ready_bc(self):
        auth = authority("resource-alpha", "resource-beta")
        self.assert_failure(
            establish(auth, context_result=None),
            MALFORMED,
        )
        self.assertEqual(object.__getattribute__(auth, "_applicabilities_by_attempt"), {})
        ri = owned_identity_authority(auth)
        self.assertEqual(object.__getattribute__(ri, "_identities_by_attempt"), {})

    def test_41_snapshot_once_isolated_from_mid_call_public_mutation(self):
        context_result = business_context_result()
        private_result = identity_result(context_result=context_result)

        def mutate_then_return(instance, *, business_context_result):
            context = object.__getattribute__(business_context_result, "business_context")
            object.__setattr__(context, "business_entity_id", "mutated-after-capture")
            return private_result

        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            side_effect=mutate_then_return,
        ):
            result = establish(context_result=context_result)
        self.assertIs(result.status, ESTABLISHED)
        self.assertEqual(
            result.establishment_evidence.business_entity_id,
            "business-alpha",
        )

    def test_42_no_coercion_or_vars_dict_authority_inference(self):
        class Coercible:
            def __str__(self):
                return "attempt-alpha"

            def __iter__(self):
                return iter(("attempt-alpha",))

        context = business_context(attempt_reference=Coercible())
        self.assert_failure(
            establish(context_result=business_context_result(context=context)),
            MALFORMED,
        )
        source = inspect.getsource(applicability_module)
        self.assertNotIn("vars(", source)
        self.assertNotIn(".__dict__", source)
        self.assertNotIn("str(value)", source)

    def test_43_result_type_and_nested_type_substitution_fail_closed(self):
        original = identity_result()

        class ForeignResult:
            status = original.status
            resource_identity_fact = original.resource_identity_fact
            establishment_evidence = original.establishment_evidence

        for result in (ForeignResult(), object(), None):
            with self.subTest(result=type(result)):
                with patch.object(
                    NonProductionAssessmentSubmissionResourceIdentityAuthority,
                    "establish_assessment_submission_resource_identity",
                    return_value=result,
                ):
                    self.assert_failure(establish(), MALFORMED)

    def test_44_malformed_selector_handoff_and_resolver_types_fail_closed(self):
        probes = (
            ("_select_operation", object()),
            ("_resolve_resource_action", object()),
            ("_resolve_applicability", ForeignApplicability.APPLICABLE),
        )
        for name, value in probes:
            with self.subTest(name=name):
                with patch.object(applicability_module, name, return_value=value):
                    self.assert_failure(establish(), MALFORMED)

    def test_45_authority_separation_is_structural_and_behavioral(self):
        result = establish()
        fact_fields = {field.name for field in dataclasses.fields(type(result.applicability_fact))}
        evidence_fields = {
            field.name for field in dataclasses.fields(type(result.establishment_evidence))
        }
        prohibited = {
            "authentication",
            "membership",
            "entitlement",
            "permission",
            "authorization_decision",
            "allow",
            "deny",
            "submitted",
            "abandoned",
            "runtime",
            "persistence",
            "deployment",
            "production_authority",
        }
        self.assertTrue(prohibited.isdisjoint(fact_fields))
        self.assertTrue(prohibited.isdisjoint(evidence_fields))
        self.assertIs(
            result.establishment_evidence.resource_lifecycle_state,
            NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL,
        )

    def test_46_instance_state_and_provenance_are_isolated(self):
        first_auth = authority("resource-alpha")
        second_auth = authority("resource-alpha")
        first = establish(first_auth)
        second = establish(second_auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(second.status, ESTABLISHED)
        self.assertEqual(
            first.establishment_evidence.applicability_provenance_reference,
            second.establishment_evidence.applicability_provenance_reference,
        )
        self.assertIsNot(
            object.__getattribute__(first_auth, "_applicabilities_by_attempt"),
            object.__getattribute__(second_auth, "_applicabilities_by_attempt"),
        )

    def test_47_all_controlled_failures_leave_payloads_absent(self):
        failures = []
        failures.append(establish(context_result=None))
        failures.append(establish(authority()))
        with patch.object(
            applicability_module,
            "_resolve_applicability",
            return_value=ResourceActionApplicability.NOT_APPLICABLE,
        ):
            failures.append(establish())
        with patch.object(
            applicability_module,
            "_resolve_applicability",
            return_value=ResourceActionApplicability.UNRESOLVED,
        ):
            failures.append(establish())
        for result in failures:
            self.assertNotIn(result.status, (ESTABLISHED, REUSED))
            self.assertIsNone(result.applicability_fact)
            self.assertIsNone(result.establishment_evidence)

    def test_48_status_precedence_public_validation_before_private_ri(self):
        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            side_effect=AssertionError("must not run"),
        ):
            self.assert_failure(establish(context_result=None), MALFORMED)
            self.assert_failure(
                establish(
                    context_result=business_context_result(
                        status=(
                            NonProductionAssessmentSubmissionBusinessContextStatus.
                            E_CONTEXT_NOT_READY
                        )
                    )
                ),
                STATUS.BUSINESS_CONTEXT_NOT_READY,
            )

    def test_49_status_precedence_ri_failure_before_action_or_applicability(self):
        ri_failure = NonProductionAssessmentSubmissionResourceIdentityResult(
            status=NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_STALE
        )
        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            return_value=ri_failure,
        ):
            with patch.object(
                applicability_module,
                "_select_operation",
                side_effect=AssertionError("must not run"),
            ):
                with patch.object(
                    applicability_module,
                    "_resolve_applicability",
                    side_effect=AssertionError("must not run"),
                ):
                    self.assert_failure(
                        establish(),
                        STATUS.RESOURCE_IDENTITY_STALE,
                    )

    def test_50_status_precedence_generic_failure_before_retry_reuse(self):
        auth = authority("resource-alpha")
        self.assertIs(establish(auth).status, ESTABLISHED)
        with patch.object(
            applicability_module,
            "_resolve_applicability",
            return_value=ResourceActionApplicability.UNRESOLVED,
        ):
            self.assert_failure(establish(auth), UNRESOLVED)
        self.assertIs(establish(auth).status, REUSED)

    def test_51_provenance_allocates_only_after_complete_success(self):
        auth = authority("resource-alpha")
        with patch.object(
            applicability_module,
            "_resolve_applicability",
            return_value=ResourceActionApplicability.NOT_APPLICABLE,
        ):
            self.assert_failure(establish(auth), NOT_APPLICABLE)
        self.assertEqual(
            object.__getattribute__(auth, "_next_applicability_provenance_index"), 1
        )
        success = establish(auth)
        self.assertEqual(
            success.establishment_evidence.applicability_provenance_reference,
            "non-production-assessment-submission-resource-action-"
            "applicability-establishment-provenance-1",
        )
        self.assertEqual(
            object.__getattribute__(auth, "_next_applicability_provenance_index"), 2
        )

    def test_52_canonical_commit_occurs_after_output_validation(self):
        auth = authority("resource-alpha")
        with patch.object(
            applicability_module,
            "_outputs_converge",
            return_value=False,
        ):
            self.assert_failure(establish(auth), MALFORMED)
        self.assertEqual(object.__getattribute__(auth, "_applicabilities_by_attempt"), {})
        self.assertEqual(
            object.__getattribute__(auth, "_applicabilities_by_resource_reference"),
            {},
        )
        self.assertEqual(
            object.__getattribute__(auth, "_applicabilities_by_resource_id"), {}
        )
        self.assertEqual(
            object.__getattribute__(auth, "_next_applicability_provenance_index"), 1
        )

    def test_53_no_runtime_persistence_or_evaluator_dependencies(self):
        source = inspect.getsource(applicability_module)
        for forbidden in (
            "AuthorizationEvaluator",
            "AuthorizationDecision",
            "resolve_membership",
            "resolve_entitlement",
            "resolve_business_entity",
            "boto3",
            "sqlite",
            "requests.",
        ):
            self.assertNotIn(forbidden, source)

    def test_54_generic_components_are_reused_unchanged(self):
        self.assertIs(applicability_module._resolve_applicability, resolve_applicability)
        self.assertIs(
            applicability_module._select_operation,
            resolve_non_production_application_operation_selection,
        )
        self.assertIs(
            applicability_module._resolve_resource_action,
            resolve_non_production_resource_action_handoff,
        )

    def test_55_public_method_rejects_all_extra_authority_keywords(self):
        auth = authority("resource-alpha")
        method = auth.establish_assessment_submission_resource_action_applicability
        for name in (
            "attempt_reference",
            "principal_id",
            "engagement_reference",
            "business_entity_id",
            "resource_reference",
            "resource_id",
            "resource_class",
            "protected_operation",
            "application_operation",
            "requested_action",
            "resource_identity_result",
            "applicability_result",
            "governed_resource",
        ):
            with self.subTest(name=name):
                with self.assertRaises(TypeError):
                    method(
                        business_context_result=business_context_result(),
                        **{name: object()},
                    )

    def test_56_ri_fact_string_subclass_is_rejected(self):
        original = identity_result()
        changed_fact = dataclasses.replace(
            original.resource_identity_fact,
            resource_reference=StringSubclass("resource-alpha"),
        )
        changed = replaced_identity_result(original, fact=changed_fact)
        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            return_value=changed,
        ):
            self.assert_failure(establish(), MALFORMED)

    def test_57_same_attempt_cannot_change_resource(self):
        auth = authority("resource-alpha")
        self.assertIs(establish(auth).status, ESTABLISHED)
        original = identity_result()
        changed_fact = dataclasses.replace(
            original.resource_identity_fact,
            resource_reference="resource-beta",
            resource_id="resource-beta",
        )
        changed = replaced_identity_result(
            original,
            fact=changed_fact,
            resource_reference="resource-beta",
            resource_id="resource-beta",
        )
        with patch.object(
            NonProductionAssessmentSubmissionResourceIdentityAuthority,
            "establish_assessment_submission_resource_identity",
            return_value=changed,
        ):
            self.assert_failure(establish(auth), MISMATCH)


if __name__ == "__main__":
    unittest.main()
