import ast
import dataclasses
import hashlib
import inspect
import sys
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization.non_production_assessment_submission_resource_identity_establishment as identity_module  # noqa: E402
from trusted_authorization.models import (  # noqa: E402
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    BusinessEntity,
    Entitlement,
    GovernedResource,
    Membership,
    RequestedAction,
    ResourceClass,
)
from trusted_authorization.non_production_application_operation_selection import (  # noqa: E402
    NonProductionProtectedApplicationOperation,
)
from trusted_authorization.non_production_assessment_submission_business_context import (  # noqa: E402
    NonProductionAssessmentSubmissionBusinessContext,
    NonProductionAssessmentSubmissionBusinessContextResult,
    NonProductionAssessmentSubmissionBusinessContextStatus,
)
from trusted_authorization.non_production_assessment_submission_resource_identity_establishment import (  # noqa: E402
    NonProductionAssessmentSubmissionResourceIdentityAuthority,
    NonProductionAssessmentSubmissionResourceIdentityEvidence,
    NonProductionAssessmentSubmissionResourceIdentityFact,
    NonProductionAssessmentSubmissionResourceIdentityResult,
    NonProductionAssessmentSubmissionResourceIdentityStatus,
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
from trusted_authorization.resource_identity_source import (  # noqa: E402
    NonProductionResourceIdentityAuthoritySource,
)


ESTABLISHED = NonProductionAssessmentSubmissionResourceIdentityStatus.ESTABLISHED
REUSED = NonProductionAssessmentSubmissionResourceIdentityStatus.REUSED
MALFORMED = NonProductionAssessmentSubmissionResourceIdentityStatus.MALFORMED
BUSINESS_CONTEXT_NOT_READY = (
    NonProductionAssessmentSubmissionResourceIdentityStatus.
    BUSINESS_CONTEXT_NOT_READY
)
UNSUPPORTED_OPERATION = (
    NonProductionAssessmentSubmissionResourceIdentityStatus.UNSUPPORTED_OPERATION
)
MISMATCH = NonProductionAssessmentSubmissionResourceIdentityStatus.MISMATCH
COLLISION = NonProductionAssessmentSubmissionResourceIdentityStatus.COLLISION
ALLOCATION_UNAVAILABLE = (
    NonProductionAssessmentSubmissionResourceIdentityStatus.ALLOCATION_UNAVAILABLE
)
PROTECTED_ASSESSMENT = (
    NonProductionProtectedApplicationOperation.PROTECTED_ASSESSMENT_SUBMISSION
)
BC_READY = NonProductionAssessmentSubmissionBusinessContextStatus.READY
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
    return NonProductionAssessmentSubmissionResourceIdentityAuthority(
        candidate_resource_references=tuple(candidates),
    )


def establish(auth=None, *, context_result=_DEFAULT):
    if auth is None:
        auth = authority("resource-alpha")
    if context_result is _DEFAULT:
        context_result = business_context_result()
    return auth.establish_assessment_submission_resource_identity(
        business_context_result=context_result,
    )


def target_authority(auth):
    return object.__getattribute__(auth, "_target_establishment_authority")


def target_result_for(context_result, resource_reference):
    target = NonProductionAssessmentSubmissionTargetEstablishmentAuthority(
        candidate_resource_references=(resource_reference,),
    )
    return target.establish_assessment_submission_target(
        business_context_result=context_result,
    )


def dataclass_values(value):
    return {field.name: getattr(value, field.name) for field in dataclasses.fields(value)}


def governed_resource(**overrides):
    values = {
        "authority_reference": (
            "non-production-assessment-submission-resource-identity-authority"
        ),
        "state": AuthorityRecordState.ACTIVE,
        "resource_id": "resource-alpha",
        "resource_reference": "resource-alpha",
        "resource_class": ResourceClass.ASSESSMENT_SUBMISSION,
        "business_entity_id": "business-alpha",
    }
    values.update(overrides)
    return GovernedResource(**values)


class ResourceIdentityEstablishmentTests(unittest.TestCase):
    def assert_failure(self, result, status):
        self.assertIs(type(result), NonProductionAssessmentSubmissionResourceIdentityResult)
        self.assertIs(result.status, status)
        self.assertIsNone(result.resource_identity_fact)
        self.assertIsNone(result.establishment_evidence)

    def test_01_frozen_source_identity(self):
        source_path = Path(identity_module.__file__)
        content = source_path.read_bytes()
        self.assertEqual(len(content), 41938)
        self.assertEqual(content.count(b"\n"), 1025)
        self.assertEqual(
            hashlib.sha256(content).hexdigest(),
            "a3f72be828a1611a5f9a9eb2aae7cb22a9926c45f2592d9845dfe83de5e949af",
        )

    def test_02_public_surface_is_exactly_five_types(self):
        public_types = {
            name
            for name, value in vars(identity_module).items()
            if not name.startswith("_") and inspect.isclass(value)
        }
        self.assertEqual(
            public_types,
            {
                "NonProductionAssessmentSubmissionResourceIdentityAuthority",
                "NonProductionAssessmentSubmissionResourceIdentityFact",
                "NonProductionAssessmentSubmissionResourceIdentityEvidence",
                "NonProductionAssessmentSubmissionResourceIdentityStatus",
                "NonProductionAssessmentSubmissionResourceIdentityResult",
            },
        )

    def test_03_constructor_and_method_signatures_are_exact(self):
        self.assertEqual(
            str(inspect.signature(
                NonProductionAssessmentSubmissionResourceIdentityAuthority
            )),
            "(*, candidate_resource_references: 'tuple[str, ...] | None' = None) -> 'None'",
        )
        self.assertEqual(
            str(inspect.signature(
                NonProductionAssessmentSubmissionResourceIdentityAuthority.
                establish_assessment_submission_resource_identity
            )),
            "(self, *, business_context_result: 'object') -> "
            "'NonProductionAssessmentSubmissionResourceIdentityResult'",
        )

    def test_04_public_api_has_no_authority_or_dependency_injection(self):
        constructor = inspect.signature(
            NonProductionAssessmentSubmissionResourceIdentityAuthority
        )
        method = inspect.signature(
            NonProductionAssessmentSubmissionResourceIdentityAuthority.
            establish_assessment_submission_resource_identity
        )
        self.assertEqual(tuple(constructor.parameters), ("candidate_resource_references",))
        self.assertEqual(tuple(method.parameters), ("self", "business_context_result"))
        public_methods = {
            name
            for name, value in inspect.getmembers(
                NonProductionAssessmentSubmissionResourceIdentityAuthority
            )
            if not name.startswith("_") and callable(value)
        }
        self.assertEqual(
            public_methods,
            {"establish_assessment_submission_resource_identity"},
        )

    def test_05_exact_private_target_authority_is_retained(self):
        auth = authority("resource-alpha")
        owned = target_authority(auth)
        self.assertIs(type(owned), NonProductionAssessmentSubmissionTargetEstablishmentAuthority)
        self.assertIs(target_authority(auth), owned)

    def test_06_generic_source_is_reused_unchanged(self):
        self.assertIs(
            identity_module._ResourceIdentitySource,
            NonProductionResourceIdentityAuthoritySource,
        )
        source_path = Path(inspect.getfile(NonProductionResourceIdentityAuthoritySource))
        self.assertEqual(
            hashlib.sha256(source_path.read_bytes()).hexdigest(),
            "da419ec5f6ab011153d6cd5f786b6e2f2d2ca704bbb641a9dda3fb797177bb85",
        )

    def test_07_governed_resource_is_private_exact_projection(self):
        seen = []
        original = NonProductionResourceIdentityAuthoritySource.resolve_resource

        def capture(source, reference):
            seen.append(object.__getattribute__(source, "_resources")[0])
            return original(source, reference)

        with patch.object(
            NonProductionResourceIdentityAuthoritySource,
            "resolve_resource",
            side_effect=capture,
        ):
            result = establish()
        self.assertIs(result.status, ESTABLISHED)
        self.assertEqual(len(seen), 1)
        projection = seen[0]
        self.assertIs(type(projection), GovernedResource)
        self.assertEqual(projection.resource_reference, "resource-alpha")
        self.assertEqual(projection.resource_id, "resource-alpha")
        self.assertEqual(projection.business_entity_id, "business-alpha")
        self.assertIs(projection.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(projection.state, AuthorityRecordState.ACTIVE)

    def test_08_first_success_returns_exact_output_types(self):
        result = establish()
        self.assertIs(result.status, ESTABLISHED)
        self.assertIs(type(result), NonProductionAssessmentSubmissionResourceIdentityResult)
        self.assertIs(type(result.resource_identity_fact), NonProductionAssessmentSubmissionResourceIdentityFact)
        self.assertIs(type(result.establishment_evidence), NonProductionAssessmentSubmissionResourceIdentityEvidence)

    def test_09_fact_fields_and_values_are_exact(self):
        fact = establish().resource_identity_fact
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(fact))),
            (
                "resource_reference",
                "resource_id",
                "business_entity_id",
                "resource_class",
                "resource_lifecycle_state",
            ),
        )
        self.assertEqual(fact.resource_reference, "resource-alpha")
        self.assertEqual(fact.resource_id, "resource-alpha")
        self.assertEqual(fact.business_entity_id, "business-alpha")
        self.assertIs(fact.resource_class, ResourceClass.ASSESSMENT_SUBMISSION)
        self.assertIs(
            fact.resource_lifecycle_state,
            NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL,
        )

    def test_10_evidence_fields_are_exact_and_complete(self):
        evidence = establish().establishment_evidence
        self.assertEqual(
            tuple(field.name for field in dataclasses.fields(type(evidence))),
            (
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
            ),
        )
        self.assertEqual(evidence.attempt_reference, "attempt-alpha")
        self.assertEqual(evidence.principal_id, "principal-alpha")
        self.assertEqual(evidence.engagement_reference, "engagement-alpha")
        self.assertEqual(evidence.business_entity_id, "business-alpha")
        self.assertIs(evidence.protected_operation, PROTECTED_ASSESSMENT)

    def test_11_result_fields_and_payload_invariant(self):
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(
                    NonProductionAssessmentSubmissionResourceIdentityResult
                )
            ),
            ("status", "resource_identity_fact", "establishment_evidence"),
        )
        success = establish()
        self.assertIsNotNone(success.resource_identity_fact)
        self.assertIsNotNone(success.establishment_evidence)
        failure = establish(authority(), context_result=business_context_result())
        self.assert_failure(failure, ALLOCATION_UNAVAILABLE)

    def test_12_fixed_references_and_provenance_are_exact(self):
        evidence = establish().establishment_evidence
        self.assertEqual(
            evidence.resource_identity_authority_reference,
            "non-production-assessment-submission-resource-identity-authority",
        )
        self.assertEqual(
            evidence.resource_identity_governance_reference,
            "resource-identity-authority-source-governance-v1",
        )
        self.assertEqual(
            evidence.resource_identity_provenance_reference,
            "non-production-assessment-submission-resource-identity-"
            "establishment-provenance-1",
        )

    def test_13_status_enum_is_exactly_thirteen_members(self):
        self.assertEqual(
            tuple(member.name for member in NonProductionAssessmentSubmissionResourceIdentityStatus),
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
            ),
        )

    def test_14_exact_retry_reuses_semantics_with_fresh_outputs(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        retry = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(first.resource_identity_fact, retry.resource_identity_fact)
        self.assertEqual(first.establishment_evidence, retry.establishment_evidence)
        self.assertIsNot(first, retry)
        self.assertIsNot(first.resource_identity_fact, retry.resource_identity_fact)
        self.assertIsNot(first.establishment_evidence, retry.establishment_evidence)

    def test_15_retry_preserves_r_identity_and_provenance(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        retry = establish(auth)
        for name in (
            "resource_reference",
            "resource_id",
            "business_entity_id",
            "resource_class",
            "resource_lifecycle_state",
        ):
            self.assertEqual(
                getattr(first.resource_identity_fact, name),
                getattr(retry.resource_identity_fact, name),
            )
        self.assertEqual(
            first.establishment_evidence.target_provenance_reference,
            retry.establishment_evidence.target_provenance_reference,
        )
        self.assertEqual(
            first.establishment_evidence.resource_identity_provenance_reference,
            retry.establishment_evidence.resource_identity_provenance_reference,
        )

    def test_16_three_indexes_reference_one_immutable_snapshot(self):
        auth = authority("resource-alpha")
        establish(auth)
        by_attempt = object.__getattribute__(auth, "_identities_by_attempt")
        by_reference = object.__getattribute__(auth, "_identities_by_resource_reference")
        by_id = object.__getattribute__(auth, "_identities_by_resource_id")
        snapshot = by_attempt["attempt-alpha"]
        self.assertIs(snapshot, by_reference["resource-alpha"])
        self.assertIs(snapshot, by_id["resource-alpha"])
        self.assertTrue(type(snapshot).__dataclass_params__.frozen)
        self.assertFalse(hasattr(snapshot, "__dict__"))

    def test_17_returned_object_mutation_is_isolated(self):
        auth = authority("resource-alpha")
        first = establish(auth)
        object.__setattr__(first.resource_identity_fact, "resource_id", "attacker")
        object.__setattr__(first.establishment_evidence, "business_entity_id", "attacker")
        object.__setattr__(
            first.establishment_evidence,
            "target_provenance_reference",
            "attacker",
        )
        object.__setattr__(
            first.establishment_evidence,
            "resource_identity_provenance_reference",
            "attacker",
        )
        object.__setattr__(first, "status", MALFORMED)
        retry = establish(auth)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(retry.resource_identity_fact.resource_id, "resource-alpha")
        self.assertEqual(retry.establishment_evidence.business_entity_id, "business-alpha")
        self.assertEqual(
            retry.establishment_evidence.target_provenance_reference,
            "non-production-assessment-submission-target-establishment-provenance-1",
        )
        self.assertEqual(
            retry.establishment_evidence.resource_identity_provenance_reference,
            "non-production-assessment-submission-resource-identity-"
            "establishment-provenance-1",
        )

    def test_18_distinct_events_receive_distinct_instance_local_provenance(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        beta = business_context_result(
            context=business_context(
                attempt_reference="attempt-beta",
                principal_id="principal-beta",
                engagement_reference="engagement-beta",
            )
        )
        second = establish(auth, context_result=beta)
        self.assertIs(second.status, ESTABLISHED)
        self.assertNotEqual(
            first.establishment_evidence.resource_identity_provenance_reference,
            second.establishment_evidence.resource_identity_provenance_reference,
        )
        other = establish(authority("resource-alpha"))
        self.assertEqual(
            other.establishment_evidence.resource_identity_provenance_reference,
            first.establishment_evidence.resource_identity_provenance_reference,
        )

    def test_19_malformed_foreign_input_is_rejected_without_attribute_reads(self):
        HostileObject.reads = 0
        result = establish(context_result=HostileObject())
        self.assert_failure(result, MALFORMED)
        self.assertEqual(HostileObject.reads, 0)

    def test_20_result_and_context_subclasses_are_rejected(self):
        subclass_result = ResultSubclass(
            status=BC_READY,
            business_context=business_context(),
        )
        self.assert_failure(establish(context_result=subclass_result), MALFORMED)
        subclass_context = ContextSubclass(**dataclass_values(business_context()))
        self.assert_failure(
            establish(
                context_result=NonProductionAssessmentSubmissionBusinessContextResult(
                    status=BC_READY,
                    business_context=subclass_context,
                )
            ),
            MALFORMED,
        )

    def test_21_every_authority_string_rejects_subclass_blank_and_whitespace(self):
        names = tuple(
            field.name
            for field in dataclasses.fields(NonProductionAssessmentSubmissionBusinessContext)
            if field.name != "protected_operation"
        )
        for name in names:
            for value in (StringSubclass("value"), "", " value", "value ", 7):
                with self.subTest(name=name, value=repr(value)):
                    context = business_context(**{name: value})
                    self.assert_failure(
                        establish(context_result=business_context_result(context=context)),
                        MALFORMED,
                    )

    def test_22_non_ready_and_malformed_status_structures_fail_closed(self):
        for status in NonProductionAssessmentSubmissionBusinessContextStatus:
            if status is BC_READY:
                continue
            with self.subTest(status=status):
                self.assert_failure(
                    establish(context_result=business_context_result(status=status)),
                    BUSINESS_CONTEXT_NOT_READY,
                )
        malformed = NonProductionAssessmentSubmissionBusinessContextResult(
            status=ForeignStatus.READY,
            business_context=business_context(),
        )
        self.assert_failure(establish(context_result=malformed), MALFORMED)

    def test_23_public_validation_precedes_private_target_invocation(self):
        auth = authority("resource-alpha")
        with patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            side_effect=AssertionError("must not be called"),
        ) as target_call:
            self.assert_failure(establish(auth, context_result=object()), MALFORMED)
            target_call.assert_not_called()

    def test_24_business_context_not_ready_precedes_private_target(self):
        auth = authority("resource-alpha")
        with patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            side_effect=AssertionError("must not be called"),
        ) as target_call:
            self.assert_failure(
                establish(
                    auth,
                    context_result=business_context_result(
                        status=(
                            NonProductionAssessmentSubmissionBusinessContextStatus.
                            ENGAGEMENT_NOT_READY
                        )
                    ),
                ),
                BUSINESS_CONTEXT_NOT_READY,
            )
            target_call.assert_not_called()

    def test_25_unsupported_operation_precedes_private_target(self):
        _, snapshot = identity_module._business_context_snapshot(
            business_context_result()
        )
        unsupported = dataclasses.replace(snapshot, protected_operation=object())
        auth = authority("resource-alpha")
        with patch.object(
            identity_module,
            "_business_context_snapshot",
            return_value=(identity_module._CapturedStatus.READY, unsupported),
        ), patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            side_effect=AssertionError("must not be called"),
        ) as target_call:
            self.assert_failure(establish(auth), UNSUPPORTED_OPERATION)
            target_call.assert_not_called()

    def test_26_all_upstream_failure_statuses_map_without_payload(self):
        mapping = {
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.MALFORMED: MALFORMED,
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.BUSINESS_CONTEXT_NOT_READY: BUSINESS_CONTEXT_NOT_READY,
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.UNSUPPORTED_OPERATION: UNSUPPORTED_OPERATION,
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.MISMATCH: MISMATCH,
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.COLLISION: COLLISION,
            NonProductionAssessmentSubmissionTargetEstablishmentStatus.ALLOCATION_UNAVAILABLE: ALLOCATION_UNAVAILABLE,
        }
        for target_status, expected in mapping.items():
            with self.subTest(target_status=target_status):
                target_result = NonProductionAssessmentSubmissionTargetEstablishmentResult(
                    status=target_status
                )
                with patch.object(
                    NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
                    "establish_assessment_submission_target",
                    return_value=target_result,
                ), patch.object(
                    identity_module,
                    "_resolve_projected_resource",
                    side_effect=AssertionError("RI lookup must not run"),
                ):
                    self.assert_failure(establish(), expected)

    def test_27_target_success_requires_exact_result_fact_and_evidence_types(self):
        context_result = business_context_result()
        valid = target_result_for(context_result, "resource-alpha")

        class TargetResultSubclass(NonProductionAssessmentSubmissionTargetEstablishmentResult):
            pass

        class TargetFactSubclass(NonProductionAssessmentSubmissionTargetLegitimacyFact):
            pass

        class TargetEvidenceSubclass(NonProductionAssessmentSubmissionTargetEstablishmentEvidence):
            pass

        variants = (
            object(),
            TargetResultSubclass(**dataclass_values(valid)),
            dataclasses.replace(
                valid,
                target_fact=TargetFactSubclass(**dataclass_values(valid.target_fact)),
            ),
            dataclasses.replace(
                valid,
                establishment_evidence=TargetEvidenceSubclass(
                    **dataclass_values(valid.establishment_evidence)
                ),
            ),
        )
        for target_result in variants:
            with self.subTest(target_result=type(target_result)):
                with patch.object(
                    NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
                    "establish_assessment_submission_target",
                    return_value=target_result,
                ):
                    self.assert_failure(establish(), MALFORMED)

    def test_28_target_fact_and_evidence_must_converge(self):
        context_result = business_context_result()
        valid = target_result_for(context_result, "resource-alpha")
        bad_fact = dataclasses.replace(
            valid.target_fact,
            resource_reference="resource-other",
        )
        with patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            return_value=dataclasses.replace(valid, target_fact=bad_fact),
        ):
            self.assert_failure(establish(context_result=context_result), MALFORMED)

    def test_29_complete_target_lineage_is_validated(self):
        context_result = business_context_result()
        valid = target_result_for(context_result, "resource-alpha")
        evidence = valid.establishment_evidence
        string_fields = (
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
            "lifecycle_authority_reference",
            "lifecycle_provenance_reference",
            "target_authority_reference",
            "target_provenance_reference",
            "target_governance_reference",
        )
        for name in string_fields:
            with self.subTest(name=name):
                changed = dataclasses.replace(evidence, **{name: ""})
                with patch.object(
                    NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
                    "establish_assessment_submission_target",
                    return_value=dataclasses.replace(
                        valid,
                        establishment_evidence=changed,
                    ),
                ):
                    self.assert_failure(
                        establish(context_result=context_result),
                        MALFORMED,
                    )

    def test_30_generic_ri_failure_statuses_map_exactly(self):
        mapping = {
            AuthorityLookupStatus.NOT_FOUND: NonProductionAssessmentSubmissionResourceIdentityStatus.RESOURCE_IDENTITY_NOT_FOUND,
            AuthorityLookupStatus.AMBIGUOUS: NonProductionAssessmentSubmissionResourceIdentityStatus.RESOURCE_IDENTITY_AMBIGUOUS,
            AuthorityLookupStatus.CONFLICTING: NonProductionAssessmentSubmissionResourceIdentityStatus.RESOURCE_IDENTITY_CONFLICTING,
            AuthorityLookupStatus.STALE: NonProductionAssessmentSubmissionResourceIdentityStatus.RESOURCE_IDENTITY_STALE,
            AuthorityLookupStatus.UNAVAILABLE: NonProductionAssessmentSubmissionResourceIdentityStatus.RESOURCE_IDENTITY_UNAVAILABLE,
            AuthorityLookupStatus.MALFORMED: MALFORMED,
            AuthorityLookupStatus.UNSUPPORTED: MALFORMED,
        }
        for lookup_status, expected in mapping.items():
            with self.subTest(lookup_status=lookup_status):
                lookup_result = AuthorityLookupResult(lookup_status)
                with patch.object(
                    NonProductionResourceIdentityAuthoritySource,
                    "resolve_resource",
                    return_value=lookup_result,
                ):
                    self.assert_failure(establish(), expected)

    def test_31_generic_ri_result_and_record_require_exact_types(self):
        class LookupResultSubclass(AuthorityLookupResult):
            pass

        class ResourceSubclass(GovernedResource):
            pass

        variants = (
            object(),
            LookupResultSubclass(
                AuthorityLookupStatus.FOUND,
                (governed_resource(),),
            ),
            AuthorityLookupResult.found(
                ResourceSubclass(**dataclass_values(governed_resource()))
            ),
        )
        for lookup_result in variants:
            with self.subTest(lookup_result=type(lookup_result)):
                with patch.object(
                    NonProductionResourceIdentityAuthoritySource,
                    "resolve_resource",
                    return_value=lookup_result,
                ):
                    self.assert_failure(establish(), MALFORMED)

    def test_32_resolved_resource_requires_exact_authority_active_state_and_class(self):
        variants = (
            governed_resource(authority_reference="wrong-authority"),
            governed_resource(state=AuthorityRecordState.STALE),
            governed_resource(resource_class=ResourceClass.REPORT),
            governed_resource(resource_id=StringSubclass("resource-alpha")),
        )
        for record in variants:
            with self.subTest(record=record):
                with patch.object(
                    NonProductionResourceIdentityAuthoritySource,
                    "resolve_resource",
                    return_value=AuthorityLookupResult.found(record),
                ):
                    self.assert_failure(establish(), MALFORMED)

    def test_33_resource_id_substitution_fails_closed(self):
        record = governed_resource(resource_id="resource-other")
        with patch.object(
            NonProductionResourceIdentityAuthoritySource,
            "resolve_resource",
            return_value=AuthorityLookupResult.found(record),
        ):
            self.assert_failure(establish(), MISMATCH)

    def test_34_business_entity_substitution_fails_closed(self):
        record = governed_resource(business_entity_id="business-other")
        with patch.object(
            NonProductionResourceIdentityAuthoritySource,
            "resolve_resource",
            return_value=AuthorityLookupResult.found(record),
        ):
            self.assert_failure(establish(), MISMATCH)

    def test_35_resource_reference_substitution_fails_closed(self):
        record = governed_resource(resource_reference="resource-other")
        with patch.object(
            NonProductionResourceIdentityAuthoritySource,
            "resolve_resource",
            return_value=AuthorityLookupResult.found(record),
        ):
            self.assert_failure(establish(), MISMATCH)

    def test_36_target_class_and_lifecycle_substitution_fail_closed(self):
        context_result = business_context_result()
        valid = target_result_for(context_result, "resource-alpha")
        variants = (
            dataclasses.replace(
                valid.establishment_evidence,
                resource_class=ResourceClass.REPORT,
            ),
            dataclasses.replace(
                valid.establishment_evidence,
                resource_lifecycle_state=object(),
            ),
        )
        for evidence in variants:
            with self.subTest(evidence=evidence):
                fact = dataclasses.replace(
                    valid.target_fact,
                    resource_class=evidence.resource_class,
                )
                target_result = dataclasses.replace(
                    valid,
                    target_fact=fact,
                    establishment_evidence=evidence,
                )
                with patch.object(
                    NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
                    "establish_assessment_submission_target",
                    return_value=target_result,
                ):
                    self.assert_failure(
                        establish(context_result=context_result),
                        MALFORMED,
                    )

    def test_37_same_attempt_cannot_move_to_r2(self):
        auth = authority("resource-alpha", "resource-beta")
        context_result = business_context_result()
        self.assertIs(establish(auth, context_result=context_result).status, ESTABLISHED)
        r2 = target_result_for(context_result, "resource-beta")
        with patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            return_value=r2,
        ):
            self.assert_failure(
                establish(auth, context_result=context_result),
                MISMATCH,
            )
        self.assertEqual(len(object.__getattribute__(auth, "_identities_by_attempt")), 1)

    def test_38_same_resource_cannot_move_to_conflicting_attempt_or_business(self):
        auth = authority("resource-alpha", "resource-beta")
        self.assertIs(establish(auth).status, ESTABLISHED)
        other_context = business_context_result(
            context=business_context(
                attempt_reference="attempt-beta",
                principal_id="principal-beta",
                engagement_reference="engagement-beta",
                business_entity_id="business-beta",
            )
        )
        conflicting = target_result_for(other_context, "resource-alpha")
        with patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            return_value=conflicting,
        ):
            self.assert_failure(
                establish(auth, context_result=other_context),
                COLLISION,
            )

    def test_39_resource_id_index_collision_fails_without_consumption(self):
        auth = authority("resource-alpha", "resource-beta")
        first = establish(auth)
        snapshot = object.__getattribute__(auth, "_identities_by_attempt")[
            "attempt-alpha"
        ]
        object.__getattribute__(auth, "_identities_by_resource_id")[
            "resource-beta"
        ] = snapshot
        beta = business_context_result(
            context=business_context(
                attempt_reference="attempt-beta",
                principal_id="principal-beta",
                engagement_reference="engagement-beta",
            )
        )
        result = establish(auth, context_result=beta)
        self.assert_failure(result, COLLISION)
        self.assertEqual(
            object.__getattribute__(auth, "_next_resource_identity_provenance_index"),
            2,
        )
        self.assertEqual(
            first.establishment_evidence.resource_identity_provenance_reference,
            "non-production-assessment-submission-resource-identity-"
            "establishment-provenance-1",
        )

    def test_40_changed_same_attempt_lineage_returns_mismatch(self):
        auth = authority("resource-alpha")
        self.assertIs(establish(auth).status, ESTABLISHED)
        changed = business_context_result(
            context=business_context(engagement_reference="engagement-other")
        )
        self.assert_failure(establish(auth, context_result=changed), MISMATCH)

    def test_41_ri_failure_precedes_existing_attempt_reuse(self):
        auth = authority("resource-alpha")
        self.assertIs(establish(auth).status, ESTABLISHED)
        with patch.object(
            NonProductionResourceIdentityAuthoritySource,
            "resolve_resource",
            return_value=AuthorityLookupResult.missing(),
        ):
            result = establish(auth)
        self.assert_failure(
            result,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_NOT_FOUND,
        )

    def test_42_attempt_mismatch_precedes_resource_collision(self):
        auth = authority("resource-alpha", "resource-beta")
        context_result = business_context_result()
        establish(auth, context_result=context_result)
        snapshot = object.__getattribute__(auth, "_identities_by_attempt")[
            "attempt-alpha"
        ]
        object.__getattribute__(auth, "_identities_by_resource_reference")[
            "resource-beta"
        ] = snapshot
        r2 = target_result_for(context_result, "resource-beta")
        with patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            return_value=r2,
        ):
            self.assert_failure(
                establish(auth, context_result=context_result),
                MISMATCH,
            )

    def test_43_failures_consume_no_ri_state_or_provenance(self):
        failures = (
            AuthorityLookupStatus.NOT_FOUND,
            AuthorityLookupStatus.AMBIGUOUS,
            AuthorityLookupStatus.CONFLICTING,
            AuthorityLookupStatus.STALE,
            AuthorityLookupStatus.UNAVAILABLE,
            AuthorityLookupStatus.MALFORMED,
        )
        for lookup_status in failures:
            with self.subTest(lookup_status=lookup_status):
                auth = authority("resource-alpha")
                with patch.object(
                    NonProductionResourceIdentityAuthoritySource,
                    "resolve_resource",
                    return_value=AuthorityLookupResult(lookup_status),
                ):
                    result = establish(auth)
                self.assertIsNone(result.resource_identity_fact)
                self.assertEqual(
                    len(object.__getattribute__(auth, "_identities_by_attempt")),
                    0,
                )
                self.assertEqual(
                    len(object.__getattribute__(auth, "_identities_by_resource_reference")),
                    0,
                )
                self.assertEqual(
                    len(object.__getattribute__(auth, "_identities_by_resource_id")),
                    0,
                )
                self.assertEqual(
                    object.__getattribute__(
                        auth,
                        "_next_resource_identity_provenance_index",
                    ),
                    1,
                )

    def test_44_partial_failure_preserves_target_and_retry_recovers_same_r(self):
        auth = authority("resource-alpha", "resource-beta")
        with patch.object(
            NonProductionResourceIdentityAuthoritySource,
            "resolve_resource",
            return_value=AuthorityLookupResult.missing(),
        ):
            failed = establish(auth)
        self.assert_failure(
            failed,
            NonProductionAssessmentSubmissionResourceIdentityStatus.
            RESOURCE_IDENTITY_NOT_FOUND,
        )
        target = target_authority(auth)
        targets = object.__getattribute__(target, "_targets_by_attempt")
        self.assertEqual(len(targets), 1)
        target_snapshot = targets["attempt-alpha"]
        retry = establish(auth)
        self.assertIs(retry.status, ESTABLISHED)
        self.assertEqual(retry.resource_identity_fact.resource_reference, "resource-alpha")
        self.assertEqual(
            retry.establishment_evidence.target_provenance_reference,
            target_snapshot.target_provenance_reference,
        )
        self.assertEqual(len(targets), 1)
        self.assertEqual(
            object.__getattribute__(target, "_next_target_provenance_index"),
            2,
        )

    def test_45_each_call_reenters_target_and_performs_ri_lookup(self):
        auth = authority("resource-alpha")
        original_target = (
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority.
            establish_assessment_submission_target
        )
        original_lookup = NonProductionResourceIdentityAuthoritySource.resolve_resource
        target_calls = []
        lookup_calls = []

        def call_target(instance, *, business_context_result):
            target_calls.append(instance)
            return original_target(
                instance,
                business_context_result=business_context_result,
            )

        def call_lookup(source, reference):
            lookup_calls.append(reference)
            return original_lookup(source, reference)

        with patch.object(
            NonProductionAssessmentSubmissionTargetEstablishmentAuthority,
            "establish_assessment_submission_target",
            side_effect=call_target,
        ), patch.object(
            NonProductionResourceIdentityAuthoritySource,
            "resolve_resource",
            side_effect=call_lookup,
        ):
            first = establish(auth)
            retry = establish(auth)
        self.assertIs(first.status, ESTABLISHED)
        self.assertIs(retry.status, REUSED)
        self.assertEqual(target_calls, [target_authority(auth), target_authority(auth)])
        self.assertEqual(lookup_calls, ["resource-alpha", "resource-alpha"])

    def test_46_active_identity_and_provisional_lifecycle_remain_distinct(self):
        result = establish()
        evidence = result.establishment_evidence
        self.assertIs(evidence.resource_identity_state, AuthorityRecordState.ACTIVE)
        self.assertIs(
            evidence.resource_lifecycle_state,
            NonProductionAssessmentSubmissionLifecycleState.PROVISIONAL,
        )
        self.assertIsNot(
            type(evidence.resource_identity_state),
            type(evidence.resource_lifecycle_state),
        )

    def test_47_operation_is_preserved_as_lineage_not_permission(self):
        result = establish()
        self.assertIs(
            result.establishment_evidence.protected_operation,
            PROTECTED_ASSESSMENT,
        )
        fact_fields = {field.name for field in dataclasses.fields(type(result.resource_identity_fact))}
        evidence_fields = {field.name for field in dataclasses.fields(type(result.establishment_evidence))}
        for forbidden in ("permission", "decision", "allow", "deny", "entitlement"):
            self.assertNotIn(forbidden, fact_fields)
            self.assertNotIn(forbidden, evidence_fields)

    def test_48_candidate_references_create_no_authority_by_themselves(self):
        auth = authority("resource-alpha", "resource-beta")
        self.assertEqual(object.__getattribute__(auth, "_identities_by_attempt"), {})
        self.assertEqual(
            object.__getattribute__(auth, "_identities_by_resource_reference"),
            {},
        )
        self.assertEqual(object.__getattribute__(auth, "_identities_by_resource_id"), {})
        target = target_authority(auth)
        self.assertEqual(object.__getattribute__(target, "_targets_by_attempt"), {})

    def test_49_caller_created_authority_payloads_are_not_public_inputs(self):
        established = establish()
        target = target_result_for(business_context_result(), "resource-alpha")
        values = (
            "resource-alpha",
            governed_resource(),
            target,
            target.target_fact,
            target.establishment_evidence,
            established,
            established.resource_identity_fact,
            established.establishment_evidence,
            {"resource_reference": "resource-alpha"},
            BusinessEntity(
                authority_reference="business-authority",
                state=AuthorityRecordState.ACTIVE,
                business_entity_id="business-alpha",
            ),
            Membership(
                authority_reference="membership-authority",
                state=AuthorityRecordState.ACTIVE,
                principal_id="principal-alpha",
                business_entity_id="business-alpha",
            ),
            Entitlement(
                authority_reference="entitlement-authority",
                state=AuthorityRecordState.ACTIVE,
                principal_id="principal-alpha",
                business_entity_id="business-alpha",
                resource_id="resource-alpha",
                action=RequestedAction.SUBMIT,
            ),
        )
        for value in values:
            with self.subTest(value=type(value)):
                self.assert_failure(establish(context_result=value), MALFORMED)

    def test_50_no_coercion_or_boundary_dict_inference(self):
        tree = ast.parse(Path(identity_module.__file__).read_text())
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("str", calls)
        self.assertNotIn("vars", calls)
        self.assertNotIn("dict", calls)
        self.assertNotIn("eval", calls)
        self.assertNotIn("exec", calls)

    def test_51_no_authority_expansion_or_lifecycle_transition(self):
        source = Path(identity_module.__file__).read_text()
        for forbidden in (
            "Membership",
            "Entitlement",
            "AuthorizationDecision",
            "AuthorizationRequest",
            "ResourceActionApplicability",
            "_LifecycleState.SUBMITTED",
            "_LifecycleState.ABANDONED",
            "sqlite",
            "boto",
            "requests",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_52_outputs_are_slotted_and_have_no_mutable_nested_payload(self):
        result = establish()
        for value in (
            result,
            result.resource_identity_fact,
            result.establishment_evidence,
        ):
            with self.subTest(value=type(value)):
                self.assertFalse(hasattr(value, "__dict__"))
        for field in dataclasses.fields(type(result.establishment_evidence)):
            self.assertNotIsInstance(
                getattr(result.establishment_evidence, field.name),
                (dict, list, set),
            )


if __name__ == "__main__":
    unittest.main()
