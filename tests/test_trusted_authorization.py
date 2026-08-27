import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trusted_authorization import (  # noqa: E402
    APPLICABILITY_GOVERNANCE_VERSION,
    AUTHORIZATION_SEMANTICS_VERSION,
    BOUNDED_EVALUATION_CONTEXT,
    AuthorityLookupResult,
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
    ResourceActionApplicability,
    ResourceClass,
    TrustedAuthorizationEvaluator,
    TrustedSubjectEvidence,
)


SUBJECT_A = TrustedSubjectEvidence(
    provider="fixture-idp",
    subject="subject-a",
    verified=True,
)
SUBJECT_B = TrustedSubjectEvidence(
    provider="fixture-idp",
    subject="subject-b",
    verified=True,
)


def governed_context(
    semantics_version=AUTHORIZATION_SEMANTICS_VERSION,
    applicability_version=APPLICABILITY_GOVERNANCE_VERSION,
    evaluation_context=BOUNDED_EVALUATION_CONTEXT,
):
    return GovernedVersionContext(
        authorization_semantics_version=semantics_version,
        applicability_governance_version=applicability_version,
        evaluation_context=evaluation_context,
    )


def instance_without(model_class, values, omitted_field):
    instance = object.__new__(model_class)
    for name, value in values.items():
        if name != omitted_field:
            object.__setattr__(instance, name, value)
    return instance


class FixtureAuthoritySource:
    def __init__(
        self,
        principal_mappings=None,
        business_entities=None,
        memberships=None,
        resources=None,
        entitlements=None,
        unavailable=None,
        stale=None,
        conflicting=None,
    ):
        self.principal_mappings = principal_mappings or {}
        self.business_entities = business_entities or {}
        self.memberships = memberships or {}
        self.resources = resources or {}
        self.entitlements = entitlements or {}
        self.unavailable = set(unavailable or ())
        self.stale = set(stale or ())
        self.conflicting = set(conflicting or ())

    def resolve_principal_mapping(self, subject_provider, subject):
        return self._result(
            "principal_mapping",
            self.principal_mappings.get((subject_provider, subject)),
        )

    def resolve_resource(self, resource_reference):
        return self._result(
            "resource",
            self.resources.get(resource_reference),
        )

    def resolve_business_entity(self, business_entity_id):
        return self._result(
            "business_entity",
            self.business_entities.get(business_entity_id),
        )

    def resolve_membership(self, principal_id, business_entity_id):
        return self._result(
            "membership",
            self.memberships.get((principal_id, business_entity_id)),
        )

    def resolve_entitlement(
        self,
        principal_id,
        business_entity_id,
        resource_id,
        action,
    ):
        return self._result(
            "entitlement",
            self.entitlements.get(
                (principal_id, business_entity_id, resource_id, action)
            ),
        )

    def _result(self, authority, record):
        if authority in self.unavailable:
            return AuthorityLookupResult.unavailable()
        if authority in self.stale:
            return AuthorityLookupResult.stale()
        if authority in self.conflicting:
            return AuthorityLookupResult.conflicting()
        if record is None:
            return AuthorityLookupResult.missing()
        return AuthorityLookupResult.found(record)


def base_authority(
    membership_state=AuthorityRecordState.ACTIVE,
    entitlement_state=AuthorityRecordState.ACTIVE,
    include_entitlement=True,
):
    principal_a = PrincipalMapping(
        authority_reference="principal-map-a-v1",
        state=AuthorityRecordState.ACTIVE,
        subject_provider="fixture-idp",
        subject="subject-a",
        principal_id="principal-a",
    )
    principal_b = PrincipalMapping(
        authority_reference="principal-map-b-v1",
        state=AuthorityRecordState.ACTIVE,
        subject_provider="fixture-idp",
        subject="subject-b",
        principal_id="principal-b",
    )
    business_a = BusinessEntity(
        authority_reference="business-entity-a-v1",
        state=AuthorityRecordState.ACTIVE,
        business_entity_id="business-a",
    )
    business_b = BusinessEntity(
        authority_reference="business-entity-b-v1",
        state=AuthorityRecordState.ACTIVE,
        business_entity_id="business-b",
    )
    membership_a = Membership(
        authority_reference="membership-a-business-a-v1",
        state=membership_state,
        principal_id="principal-a",
        business_entity_id="business-a",
    )
    resource_a = GovernedResource(
        authority_reference="resource-report-a-v1",
        state=AuthorityRecordState.ACTIVE,
        resource_id="report-a",
        resource_reference="report-ref-a",
        resource_class=ResourceClass.REPORT,
        business_entity_id="business-a",
    )
    resource_b = GovernedResource(
        authority_reference="resource-report-b-v1",
        state=AuthorityRecordState.ACTIVE,
        resource_id="report-b",
        resource_reference="report-ref-b",
        resource_class=ResourceClass.REPORT,
        business_entity_id="business-b",
    )
    submission_a = GovernedResource(
        authority_reference="resource-submission-a-v1",
        state=AuthorityRecordState.ACTIVE,
        resource_id="submission-a",
        resource_reference="submission-ref-a",
        resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
        business_entity_id="business-a",
    )
    dashboard_a = GovernedResource(
        authority_reference="resource-dashboard-a-v1",
        state=AuthorityRecordState.ACTIVE,
        resource_id="dashboard-a",
        resource_reference="dashboard-ref-a",
        resource_class=ResourceClass.EXECUTIVE_DASHBOARD,
        business_entity_id="business-a",
    )
    entitlements = {}
    if include_entitlement:
        for resource_id, action in (
            ("dashboard-a", RequestedAction.VIEW),
            ("dashboard-a", RequestedAction.EXPLAIN),
            ("report-a", RequestedAction.VIEW),
            ("report-a", RequestedAction.DOWNLOAD),
            ("report-a", RequestedAction.EXPLAIN),
            ("submission-a", RequestedAction.SUBMIT),
        ):
            entitlements[
                (
                    "principal-a",
                    "business-a",
                    resource_id,
                    action,
                )
            ] = Entitlement(
                authority_reference=(
                    "entitlement-principal-a-"
                    f"{resource_id}-{action.value.lower()}-v1"
                ),
                state=entitlement_state,
                principal_id="principal-a",
                business_entity_id="business-a",
                resource_id=resource_id,
                action=action,
            )

    return FixtureAuthoritySource(
        principal_mappings={
            ("fixture-idp", "subject-a"): principal_a,
            ("fixture-idp", "subject-b"): principal_b,
        },
        business_entities={
            "business-a": business_a,
            "business-b": business_b,
        },
        memberships={
            ("principal-a", "business-a"): membership_a,
        },
        resources={
            "report-ref-a": resource_a,
            "report-ref-b": resource_b,
            "submission-ref-a": submission_a,
            "dashboard-ref-a": dashboard_a,
        },
        entitlements=entitlements,
    )


def request(
    subject=SUBJECT_A,
    resource_reference="report-ref-a",
    action=RequestedAction.VIEW,
):
    return AuthorizationRequest(
        subject_evidence=subject,
        resource_reference=resource_reference,
        requested_action=action,
        governed_version_context=governed_context(),
        correlation_id="authz-test-001",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


GOVERNED_APPLICABLE_ALLOW_CASES = (
    (
        ResourceClass.EXECUTIVE_DASHBOARD,
        RequestedAction.VIEW,
        "dashboard-ref-a",
        "dashboard-a",
    ),
    (
        ResourceClass.EXECUTIVE_DASHBOARD,
        RequestedAction.EXPLAIN,
        "dashboard-ref-a",
        "dashboard-a",
    ),
    (
        ResourceClass.REPORT,
        RequestedAction.VIEW,
        "report-ref-a",
        "report-a",
    ),
    (
        ResourceClass.REPORT,
        RequestedAction.DOWNLOAD,
        "report-ref-a",
        "report-a",
    ),
    (
        ResourceClass.REPORT,
        RequestedAction.EXPLAIN,
        "report-ref-a",
        "report-a",
    ),
    (
        ResourceClass.ASSESSMENT_SUBMISSION,
        RequestedAction.SUBMIT,
        "submission-ref-a",
        "submission-a",
    ),
)


GOVERNANCE_TRACEABILITY = (
    (
        "ALLOW/DENY-only decision semantics",
        "models.AuthorizationDecision",
        "evaluator._allow / evaluator._deny",
        "test_authorized_principal_resource_and_action_allows",
        "test_missing_authority_evidence_fails_closed",
    ),
    (
        "default-DENY and fail-closed behavior",
        "evaluator.TrustedAuthorizationEvaluator.evaluate",
        "test_missing_authority_evidence_fails_closed",
        "test_authority_lookup_exceptions_fail_closed",
    ),
    (
        "explicit lifecycle authority",
        "models.AuthorityRecord.state",
        "evaluator._authority_record_state",
        "test_authority_record_constructors_require_explicit_lifecycle_state",
        "test_missing_lifecycle_state_in_authority_record_fails_closed",
        "test_malformed_lifecycle_state_in_authority_record_fails_closed",
        "test_missing_lifecycle_state_on_each_authority_record_fails_closed",
        "test_missing_resource_class_instance_field_cannot_inherit_default",
        "test_missing_entitlement_action_instance_field_cannot_inherit_default",
        "test_missing_required_instance_fields_cannot_inherit_defaults",
    ),
    (
        "governed version/context validation",
        "models.GovernedVersionContext",
        "evaluator._governed_version_context_error",
        "test_missing_governed_version_context_fails_closed",
        "test_malformed_governed_version_context_fails_closed",
        "test_unsupported_governed_version_context_fails_closed",
        "test_conflicting_governed_evaluation_context_fails_closed",
    ),
    (
        "Business Entity isolation",
        "evaluator._validated_business_entity",
        "evaluator._validated_membership",
        "test_business_entity_a_principal_cannot_access_business_entity_b_resource",
    ),
    (
        "membership enforcement",
        "evaluator._validated_membership",
        "test_inactive_membership_denies",
        "test_revoked_membership_denies",
        "test_expired_membership_denies",
    ),
    (
        "entitlement enforcement",
        "evaluator._validated_entitlement",
        "test_missing_entitlement_denies",
        "test_revoked_entitlement_denies",
        "test_authorized_resource_with_unauthorized_action_denies",
        "test_entitlement_attribute_divergence_uses_instance_action",
    ),
    (
        "governed resource lookup",
        "evaluator.AuthorizationAuthoritySource.resolve_resource",
        "evaluator._validated_resource",
        "test_unknown_resource_denies",
        "test_resource_identity_must_match_requested_reference",
        "test_resource_attribute_divergence_uses_instance_resource_class",
    ),
    (
        "requested-action and applicability enforcement",
        "evaluator._canonical_action",
        "applicability.resolve_applicability",
        "test_unsupported_action_denies",
        "test_action_resource_mismatch_denies_before_entitlement",
    ),
    (
        "minimum necessary audit evidence",
        "models.AuthorizationAuditEvidence",
        "evaluator._audit_evidence",
        "test_audit_evidence_uses_minimum_necessary_disclosure",
        "test_invalid_governed_context_does_not_leak_raw_value",
    ),
    (
        "AI/LLM, Website/browser, production integration non-authority",
        "src/trusted_authorization package imports and code",
        "test_authorization_package_contains_no_prohibited_integration_terms",
    ),
    (
        "bounded v1 applicability positive evidence",
        "applicability._APPLICABILITY_MATRIX",
        "test_every_governed_applicable_resource_action_pair_allows",
    ),
    (
        "validated authority values are captured before use",
        "evaluator._required_instance_field",
        "evaluator._normalize_lookup_result",
        "test_authority_lookup_attribute_divergence_uses_instance_status",
        "test_required_authority_predicates_use_captured_instance_values",
    ),
)


PROHIBITED_AUTHORIZATION_INTEGRATION_TERMS = (
    "aws",
    "boto3",
    "bedrock",
    "cognito",
    "iam",
    "openai",
    "llm",
    "prompt",
    "agent",
    "mcp",
    "requests",
    "urllib",
    "socket",
    "subprocess",
    "pickle",
    "dynamodb",
    "s3",
)


class TrustedAuthorizationTests(unittest.TestCase):
    def evaluate(self, authority=None, authz_request=None):
        evaluator = TrustedAuthorizationEvaluator(authority or base_authority())
        return evaluator.evaluate(authz_request or request())

    def test_authorized_principal_resource_and_action_allows(self):
        result = self.evaluate()

        self.assertEqual(result.decision, AuthorizationDecision.ALLOW)
        self.assertIsNone(result.reason)
        self.assertEqual(result.audit_evidence.principal_id, "principal-a")
        self.assertEqual(result.audit_evidence.business_entity_id, "business-a")
        self.assertEqual(result.audit_evidence.resource_id, "report-a")
        self.assertEqual(
            result.audit_evidence.requested_action,
            RequestedAction.VIEW,
        )
        self.assertEqual(
            result.audit_evidence.applicability,
            ResourceActionApplicability.APPLICABLE,
        )
        self.assertEqual(
            result.audit_evidence.semantics_version,
            AUTHORIZATION_SEMANTICS_VERSION,
        )
        self.assertEqual(
            result.audit_evidence.applicability_version,
            APPLICABILITY_GOVERNANCE_VERSION,
        )

    def test_every_governed_applicable_resource_action_pair_allows(self):
        for (
            resource_class,
            action,
            resource_reference,
            resource_id,
        ) in GOVERNED_APPLICABLE_ALLOW_CASES:
            with self.subTest(resource_class=resource_class, action=action):
                result = self.evaluate(
                    authz_request=request(
                        resource_reference=resource_reference,
                        action=action,
                    )
                )

                self.assertEqual(result.decision, AuthorizationDecision.ALLOW)
                self.assertIsNone(result.reason)
                self.assertEqual(result.audit_evidence.resource_id, resource_id)
                self.assertEqual(result.audit_evidence.resource_class, resource_class)
                self.assertEqual(result.audit_evidence.requested_action, action)
                self.assertEqual(
                    result.audit_evidence.applicability,
                    ResourceActionApplicability.APPLICABLE,
                )

    def test_governance_traceability_matrix_covers_corrective_requirements(self):
        traceability = "\n".join(
            " -> ".join(item) for item in GOVERNANCE_TRACEABILITY
        )

        self.assertIn("ALLOW/DENY-only decision semantics", traceability)
        self.assertIn("default-DENY and fail-closed behavior", traceability)
        self.assertIn("explicit lifecycle authority", traceability)
        self.assertIn("governed version/context validation", traceability)
        self.assertIn("Business Entity isolation", traceability)
        self.assertIn("membership enforcement", traceability)
        self.assertIn("entitlement enforcement", traceability)
        self.assertIn("governed resource lookup", traceability)
        self.assertIn("requested-action and applicability enforcement", traceability)
        self.assertIn("minimum necessary audit evidence", traceability)
        self.assertIn("production integration non-authority", traceability)
        self.assertIn("bounded v1 applicability positive evidence", traceability)
        self.assertIn(
            "test_every_governed_applicable_resource_action_pair_allows",
            traceability,
        )
        for traceability_row in GOVERNANCE_TRACEABILITY:
            for reference in traceability_row:
                if reference.startswith("test_"):
                    self.assertTrue(
                        callable(getattr(self, reference, None)),
                        reference,
                    )

    def test_authorization_package_contains_no_prohibited_integration_terms(self):
        source_root = Path(__file__).resolve().parents[1] / "src"
        authorization_source = source_root / "trusted_authorization"
        text = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in authorization_source.glob("*.py")
        )

        for term in PROHIBITED_AUTHORIZATION_INTEGRATION_TERMS:
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_authority_record_constructors_require_explicit_lifecycle_state(self):
        with self.assertRaises(TypeError):
            PrincipalMapping(
                authority_reference="principal-map-a-v1",
                subject_provider="fixture-idp",
                subject="subject-a",
                principal_id="principal-a",
            )

    def test_missing_lifecycle_state_in_authority_record_fails_closed(self):
        authority = base_authority()
        principal_mapping = object.__new__(PrincipalMapping)
        object.__setattr__(
            principal_mapping,
            "authority_reference",
            "principal-map-a-missing-state-v1",
        )
        object.__setattr__(principal_mapping, "subject_provider", "fixture-idp")
        object.__setattr__(principal_mapping, "subject", "subject-a")
        object.__setattr__(principal_mapping, "principal_id", "principal-a")
        authority.principal_mappings[("fixture-idp", "subject-a")] = (
            principal_mapping
        )

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_malformed_lifecycle_state_in_authority_record_fails_closed(self):
        authority = base_authority()
        authority.resources["report-ref-a"] = replace(
            authority.resources["report-ref-a"],
            state="ACTIVE",
        )

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_missing_lifecycle_state_on_each_authority_record_fails_closed(self):
        cases = (
            (
                "principal_mapping",
                lambda authority: authority.principal_mappings.__setitem__(
                    ("fixture-idp", "subject-a"),
                    replace(
                        authority.principal_mappings[("fixture-idp", "subject-a")],
                        state=None,
                    ),
                ),
            ),
            (
                "resource",
                lambda authority: authority.resources.__setitem__(
                    "report-ref-a",
                    replace(authority.resources["report-ref-a"], state=None),
                ),
            ),
            (
                "business_entity",
                lambda authority: authority.business_entities.__setitem__(
                    "business-a",
                    replace(authority.business_entities["business-a"], state=None),
                ),
            ),
            (
                "membership",
                lambda authority: authority.memberships.__setitem__(
                    ("principal-a", "business-a"),
                    replace(
                        authority.memberships[("principal-a", "business-a")],
                        state=None,
                    ),
                ),
            ),
            (
                "entitlement",
                lambda authority: authority.entitlements.__setitem__(
                    (
                        "principal-a",
                        "business-a",
                        "report-a",
                        RequestedAction.VIEW,
                    ),
                    replace(
                        authority.entitlements[
                            (
                                "principal-a",
                                "business-a",
                                "report-a",
                                RequestedAction.VIEW,
                            )
                        ],
                        state=None,
                    ),
                ),
            ),
        )
        for label, mutate in cases:
            with self.subTest(authority=label):
                authority = base_authority()
                mutate(authority)

                result = self.evaluate(authority=authority)

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_missing_resource_class_instance_field_cannot_inherit_default(self):
        authority = base_authority()
        resource = object.__new__(GovernedResource)
        object.__setattr__(
            resource,
            "authority_reference",
            "resource-report-a-missing-class-v1",
        )
        object.__setattr__(resource, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(resource, "resource_id", "report-a")
        object.__setattr__(resource, "resource_reference", "report-ref-a")
        object.__setattr__(resource, "business_entity_id", "business-a")
        authority.resources["report-ref-a"] = resource

        self.assertFalse(hasattr(resource, "resource_class"))
        first = self.evaluate(authority=authority)
        second = self.evaluate(authority=authority)

        self.assertEqual(first.decision, AuthorizationDecision.DENY)
        self.assertEqual(first.reason, ReasonCategory.UNKNOWN_STATE)
        self.assertEqual(first, second)
        self.assertIsNone(first.audit_evidence.resource_class)
        self.assertNotEqual(first.decision, AuthorizationDecision.ALLOW)

    def test_missing_entitlement_action_instance_field_cannot_inherit_default(self):
        authority = base_authority()
        entitlement = object.__new__(Entitlement)
        object.__setattr__(
            entitlement,
            "authority_reference",
            "entitlement-principal-a-report-a-missing-action-v1",
        )
        object.__setattr__(entitlement, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(entitlement, "principal_id", "principal-a")
        object.__setattr__(entitlement, "business_entity_id", "business-a")
        object.__setattr__(entitlement, "resource_id", "report-a")
        authority.entitlements[
            (
                "principal-a",
                "business-a",
                "report-a",
                RequestedAction.VIEW,
            )
        ] = entitlement

        self.assertFalse(hasattr(entitlement, "action"))
        first = self.evaluate(authority=authority)
        second = self.evaluate(authority=authority)

        self.assertEqual(first.decision, AuthorizationDecision.DENY)
        self.assertEqual(first.reason, ReasonCategory.UNKNOWN_STATE)
        self.assertEqual(first, second)
        self.assertIn(
            "entitlement:entitlement-principal-a-report-a-missing-action-v1",
            first.audit_evidence.authority_inputs,
        )
        self.assertNotEqual(first.decision, AuthorizationDecision.ALLOW)

    def test_entitlement_attribute_divergence_uses_instance_action(self):
        class ConfusedEntitlement(Entitlement):
            def __getattribute__(self, name):
                if name == "action":
                    return RequestedAction.VIEW
                return object.__getattribute__(self, name)

        authority = base_authority()
        entitlement = object.__new__(ConfusedEntitlement)
        object.__setattr__(
            entitlement,
            "authority_reference",
            "entitlement-divergent-action-v1",
        )
        object.__setattr__(entitlement, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(entitlement, "principal_id", "principal-a")
        object.__setattr__(entitlement, "business_entity_id", "business-a")
        object.__setattr__(entitlement, "resource_id", "report-a")
        object.__setattr__(entitlement, "action", RequestedAction.DOWNLOAD)
        authority.entitlements[
            (
                "principal-a",
                "business-a",
                "report-a",
                RequestedAction.VIEW,
            )
        ] = entitlement

        self.assertEqual(vars(entitlement)["action"], RequestedAction.DOWNLOAD)
        self.assertEqual(entitlement.action, RequestedAction.VIEW)
        first = self.evaluate(authority=authority)
        second = self.evaluate(authority=authority)

        self.assertEqual(first.decision, AuthorizationDecision.DENY)
        self.assertEqual(first.reason, ReasonCategory.ENTITLEMENT_NOT_APPLICABLE)
        self.assertEqual(first, second)
        self.assertEqual(first.audit_evidence.requested_action, RequestedAction.VIEW)
        self.assertIn(
            "entitlement:entitlement-divergent-action-v1",
            first.audit_evidence.authority_inputs,
        )

    def test_resource_attribute_divergence_uses_instance_resource_class(self):
        class ConfusedResource(GovernedResource):
            def __getattribute__(self, name):
                if name == "resource_class":
                    return ResourceClass.REPORT
                return object.__getattribute__(self, name)

        authority = base_authority()
        resource = object.__new__(ConfusedResource)
        object.__setattr__(
            resource,
            "authority_reference",
            "resource-divergent-class-v1",
        )
        object.__setattr__(resource, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(resource, "resource_id", "report-a")
        object.__setattr__(resource, "resource_reference", "report-ref-a")
        object.__setattr__(
            resource,
            "resource_class",
            ResourceClass.ASSESSMENT_SUBMISSION,
        )
        object.__setattr__(resource, "business_entity_id", "business-a")
        authority.resources["report-ref-a"] = resource

        self.assertEqual(
            vars(resource)["resource_class"],
            ResourceClass.ASSESSMENT_SUBMISSION,
        )
        self.assertEqual(resource.resource_class, ResourceClass.REPORT)
        first = self.evaluate(authority=authority)
        second = self.evaluate(authority=authority)

        self.assertEqual(first.decision, AuthorizationDecision.DENY)
        self.assertEqual(first.reason, ReasonCategory.ACTION_NOT_APPLICABLE)
        self.assertEqual(first, second)
        self.assertEqual(
            first.audit_evidence.resource_class,
            ResourceClass.ASSESSMENT_SUBMISSION,
        )
        self.assertEqual(
            first.audit_evidence.applicability,
            ResourceActionApplicability.NOT_APPLICABLE,
        )

    def test_authority_lookup_attribute_divergence_uses_instance_status(self):
        class SpoofedLookup(AuthorityLookupResult):
            def __getattribute__(self, name):
                if name == "status":
                    return AuthorityLookupStatus.FOUND
                if name == "records":
                    return object.__getattribute__(self, "_spoofed_records")
                return object.__getattribute__(self, name)

        class SpoofedPrincipalAuthority:
            def __init__(self):
                self.delegate = base_authority()
                valid_record = self.delegate.principal_mappings[
                    ("fixture-idp", "subject-a")
                ]
                self.lookup = object.__new__(SpoofedLookup)
                object.__setattr__(
                    self.lookup,
                    "status",
                    AuthorityLookupStatus.UNAVAILABLE,
                )
                object.__setattr__(self.lookup, "records", ())
                object.__setattr__(self.lookup, "_spoofed_records", (valid_record,))

            def resolve_principal_mapping(self, subject_provider, subject):
                return self.lookup

            def resolve_resource(self, resource_reference):
                return self.delegate.resolve_resource(resource_reference)

            def resolve_business_entity(self, business_entity_id):
                return self.delegate.resolve_business_entity(business_entity_id)

            def resolve_membership(self, principal_id, business_entity_id):
                return self.delegate.resolve_membership(
                    principal_id,
                    business_entity_id,
                )

            def resolve_entitlement(
                self,
                principal_id,
                business_entity_id,
                resource_id,
                action,
            ):
                return self.delegate.resolve_entitlement(
                    principal_id,
                    business_entity_id,
                    resource_id,
                    action,
                )

        authority = SpoofedPrincipalAuthority()
        self.assertEqual(
            vars(authority.lookup)["status"],
            AuthorityLookupStatus.UNAVAILABLE,
        )
        self.assertEqual(authority.lookup.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(vars(authority.lookup)["records"], ())
        self.assertNotEqual(authority.lookup.records, ())
        first = self.evaluate(authority=authority)
        second = self.evaluate(authority=authority)

        self.assertEqual(first.decision, AuthorizationDecision.DENY)
        self.assertEqual(first.reason, ReasonCategory.AUTHORITY_UNAVAILABLE)
        self.assertEqual(first, second)
        self.assertEqual(
            first.audit_evidence.authority_inputs,
            (
                "authentication_evidence:verified",
                f"authorization_semantics:{AUTHORIZATION_SEMANTICS_VERSION}",
                f"resource_action_applicability:{APPLICABILITY_GOVERNANCE_VERSION}",
                f"evaluation_context:{BOUNDED_EVALUATION_CONTEXT}",
                "principal_mapping:UNAVAILABLE",
            ),
        )

    def test_required_authority_predicates_use_captured_instance_values(self):
        class ConfusedPrincipalMapping(PrincipalMapping):
            def __getattribute__(self, name):
                if name == "subject_provider":
                    return "fixture-idp"
                return object.__getattribute__(self, name)

        authority = base_authority()
        principal_mapping = object.__new__(ConfusedPrincipalMapping)
        object.__setattr__(
            principal_mapping,
            "authority_reference",
            "principal-map-divergent-provider-v1",
        )
        object.__setattr__(
            principal_mapping,
            "state",
            AuthorityRecordState.ACTIVE,
        )
        object.__setattr__(principal_mapping, "subject_provider", "other-idp")
        object.__setattr__(principal_mapping, "subject", "subject-a")
        object.__setattr__(principal_mapping, "principal_id", "principal-a")
        authority.principal_mappings[("fixture-idp", "subject-a")] = (
            principal_mapping
        )
        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)

        class ConfusedBusinessEntity(BusinessEntity):
            def __getattribute__(self, name):
                if name == "business_entity_id":
                    return "business-a"
                return object.__getattribute__(self, name)

        authority = base_authority()
        business_entity = object.__new__(ConfusedBusinessEntity)
        object.__setattr__(
            business_entity,
            "authority_reference",
            "business-entity-divergent-id-v1",
        )
        object.__setattr__(business_entity, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(business_entity, "business_entity_id", "business-b")
        authority.business_entities["business-a"] = business_entity
        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.BUSINESS_ENTITY_INVALID)
        self.assertEqual(result.audit_evidence.business_entity_id, "business-b")

        class ConfusedMembership(Membership):
            def __getattribute__(self, name):
                if name == "principal_id":
                    return "principal-a"
                return object.__getattribute__(self, name)

        authority = base_authority()
        membership = object.__new__(ConfusedMembership)
        object.__setattr__(
            membership,
            "authority_reference",
            "membership-divergent-principal-v1",
        )
        object.__setattr__(membership, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(membership, "principal_id", "principal-b")
        object.__setattr__(membership, "business_entity_id", "business-a")
        authority.memberships[("principal-a", "business-a")] = membership
        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)

    def test_missing_required_instance_fields_cannot_inherit_defaults(self):
        subject_values = {
            "provider": "fixture-idp",
            "subject": "subject-a",
            "verified": True,
        }
        for omitted_field in subject_values:
            with self.subTest(model="TrustedSubjectEvidence", field=omitted_field):
                result = self.evaluate(
                    authz_request=request(
                        subject=instance_without(
                            TrustedSubjectEvidence,
                            subject_values,
                            omitted_field,
                        )
                    )
                )

                self.assertEqual(result.decision, AuthorizationDecision.DENY)

        request_values = {
            "subject_evidence": SUBJECT_A,
            "resource_reference": "report-ref-a",
            "requested_action": RequestedAction.VIEW,
            "governed_version_context": governed_context(),
            "correlation_id": "authz-test-001",
            "evaluation_context": BOUNDED_EVALUATION_CONTEXT,
        }
        for omitted_field in (
            "subject_evidence",
            "resource_reference",
            "requested_action",
            "governed_version_context",
            "evaluation_context",
        ):
            with self.subTest(model="AuthorizationRequest", field=omitted_field):
                result = self.evaluate(
                    authz_request=instance_without(
                        AuthorizationRequest,
                        request_values,
                        omitted_field,
                    )
                )

                self.assertEqual(result.decision, AuthorizationDecision.DENY)

        context_values = {
            "authorization_semantics_version": AUTHORIZATION_SEMANTICS_VERSION,
            "applicability_governance_version": APPLICABILITY_GOVERNANCE_VERSION,
            "evaluation_context": BOUNDED_EVALUATION_CONTEXT,
        }
        for omitted_field in context_values:
            with self.subTest(model="GovernedVersionContext", field=omitted_field):
                result = self.evaluate(
                    authz_request=replace(
                        request(),
                        governed_version_context=instance_without(
                            GovernedVersionContext,
                            context_values,
                            omitted_field,
                        ),
                    )
                )

                self.assertEqual(result.decision, AuthorizationDecision.DENY)

        authority_record_cases = (
            (
                "PrincipalMapping",
                PrincipalMapping,
                {
                    "authority_reference": "principal-map-a-v1",
                    "state": AuthorityRecordState.ACTIVE,
                    "subject_provider": "fixture-idp",
                    "subject": "subject-a",
                    "principal_id": "principal-a",
                },
                lambda authority, record: authority.principal_mappings.__setitem__(
                    ("fixture-idp", "subject-a"),
                    record,
                ),
            ),
            (
                "BusinessEntity",
                BusinessEntity,
                {
                    "authority_reference": "business-entity-a-v1",
                    "state": AuthorityRecordState.ACTIVE,
                    "business_entity_id": "business-a",
                },
                lambda authority, record: authority.business_entities.__setitem__(
                    "business-a",
                    record,
                ),
            ),
            (
                "Membership",
                Membership,
                {
                    "authority_reference": "membership-a-business-a-v1",
                    "state": AuthorityRecordState.ACTIVE,
                    "principal_id": "principal-a",
                    "business_entity_id": "business-a",
                },
                lambda authority, record: authority.memberships.__setitem__(
                    ("principal-a", "business-a"),
                    record,
                ),
            ),
            (
                "GovernedResource",
                GovernedResource,
                {
                    "authority_reference": "resource-report-a-v1",
                    "state": AuthorityRecordState.ACTIVE,
                    "resource_id": "report-a",
                    "resource_reference": "report-ref-a",
                    "resource_class": ResourceClass.REPORT,
                    "business_entity_id": "business-a",
                },
                lambda authority, record: authority.resources.__setitem__(
                    "report-ref-a",
                    record,
                ),
            ),
            (
                "Entitlement",
                Entitlement,
                {
                    "authority_reference": "entitlement-principal-a-report-a-view-v1",
                    "state": AuthorityRecordState.ACTIVE,
                    "principal_id": "principal-a",
                    "business_entity_id": "business-a",
                    "resource_id": "report-a",
                    "action": RequestedAction.VIEW,
                },
                lambda authority, record: authority.entitlements.__setitem__(
                    (
                        "principal-a",
                        "business-a",
                        "report-a",
                        RequestedAction.VIEW,
                    ),
                    record,
                ),
            ),
        )
        for model_name, model_class, values, install in authority_record_cases:
            for omitted_field in values:
                with self.subTest(model=model_name, field=omitted_field):
                    authority = base_authority()
                    install(
                        authority,
                        instance_without(model_class, values, omitted_field),
                    )

                    result = self.evaluate(authority=authority)

                    self.assertEqual(result.decision, AuthorizationDecision.DENY)

    def test_missing_governed_version_context_fails_closed(self):
        result = self.evaluate(
            authz_request=replace(
                request(),
                governed_version_context=None,
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_incomplete_exact_governed_version_context_fails_closed(self):
        context = object.__new__(GovernedVersionContext)
        object.__setattr__(
            context,
            "authorization_semantics_version",
            "token-secret-version",
        )
        object.__setattr__(
            context,
            "evaluation_context",
            BOUNDED_EVALUATION_CONTEXT,
        )
        authz_request = replace(request(), governed_version_context=context)

        first = self.evaluate(authz_request=authz_request)
        second = self.evaluate(authz_request=authz_request)

        self.assertEqual(first.decision, AuthorizationDecision.DENY)
        self.assertEqual(first.reason, ReasonCategory.UNKNOWN_STATE)
        self.assertEqual(first, second)
        evidence = first.audit_evidence.to_dict()
        self.assertNotIn("token-secret-version", str(evidence))
        self.assertIn("governed_version_context:MALFORMED", str(evidence))

    def test_incomplete_exact_authorization_request_fails_closed(self):
        authz_request = object.__new__(AuthorizationRequest)
        object.__setattr__(authz_request, "subject_evidence", SUBJECT_A)
        object.__setattr__(
            authz_request,
            "resource_reference",
            "token-secret-resource",
        )
        object.__setattr__(
            authz_request,
            "requested_action",
            RequestedAction.VIEW,
        )
        object.__setattr__(
            authz_request,
            "correlation_id",
            "authz-test-incomplete-request",
        )
        object.__setattr__(
            authz_request,
            "evaluation_context",
            BOUNDED_EVALUATION_CONTEXT,
        )

        first = self.evaluate(authz_request=authz_request)
        second = self.evaluate(authz_request=authz_request)

        self.assertEqual(first.decision, AuthorizationDecision.DENY)
        self.assertEqual(first.reason, ReasonCategory.UNKNOWN_STATE)
        self.assertEqual(first, second)
        evidence = first.audit_evidence.to_dict()
        self.assertNotIn("token-secret-resource", str(evidence))
        self.assertIn("governed_version_context:MALFORMED", str(evidence))

    def test_malformed_governed_version_context_fails_closed(self):
        result = self.evaluate(
            authz_request=replace(
                request(),
                governed_version_context=governed_context(
                    applicability_version=""
                ),
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_unsupported_governed_version_context_fails_closed(self):
        result = self.evaluate(
            authz_request=replace(
                request(),
                governed_version_context=governed_context(
                    semantics_version="deterministic-authorization-v2"
                ),
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_conflicting_governed_evaluation_context_fails_closed(self):
        result = self.evaluate(
            authz_request=replace(
                request(),
                evaluation_context="conflicting-context",
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_invalid_governed_context_does_not_leak_raw_value(self):
        result = self.evaluate(
            authz_request=replace(
                request(),
                governed_version_context=governed_context(
                    semantics_version="token-secret-version"
                ),
            )
        )
        evidence = result.audit_evidence.to_dict()

        self.assertNotIn("token-secret-version", str(evidence))
        self.assertIn("governed_version_context:MALFORMED", str(evidence))

    def test_structurally_incomplete_exact_model_instances_fail_closed(self):
        subject = object.__new__(TrustedSubjectEvidence)
        object.__setattr__(subject, "subject", "subject-a")
        object.__setattr__(subject, "verified", True)
        auth_result = self.evaluate(authz_request=request(subject=subject))

        self.assertEqual(auth_result.decision, AuthorizationDecision.DENY)
        self.assertEqual(
            auth_result.reason,
            ReasonCategory.AUTHENTICATION_INVALID,
        )

        subject = object.__new__(TrustedSubjectEvidence)
        object.__setattr__(subject, "provider", "fixture-idp")
        object.__setattr__(subject, "subject", "subject-a")
        auth_result = self.evaluate(authz_request=request(subject=subject))

        self.assertEqual(auth_result.decision, AuthorizationDecision.DENY)
        self.assertEqual(
            auth_result.reason,
            ReasonCategory.AUTHENTICATION_INVALID,
        )

        authz_request = object.__new__(AuthorizationRequest)
        object.__setattr__(authz_request, "subject_evidence", SUBJECT_A)
        object.__setattr__(authz_request, "resource_reference", "report-ref-a")
        object.__setattr__(
            authz_request,
            "requested_action",
            RequestedAction.VIEW,
        )
        object.__setattr__(
            authz_request,
            "governed_version_context",
            governed_context(),
        )
        object.__setattr__(authz_request, "correlation_id", "authz-test-001")
        request_result = self.evaluate(authz_request=authz_request)

        self.assertEqual(request_result.decision, AuthorizationDecision.DENY)
        self.assertEqual(request_result.reason, ReasonCategory.UNKNOWN_STATE)

        authority = base_authority()
        principal_mapping = object.__new__(PrincipalMapping)
        object.__setattr__(
            principal_mapping,
            "authority_reference",
            "principal-map-a-missing-principal-v1",
        )
        object.__setattr__(principal_mapping, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(principal_mapping, "subject_provider", "fixture-idp")
        object.__setattr__(principal_mapping, "subject", "subject-a")
        authority.principal_mappings[("fixture-idp", "subject-a")] = (
            principal_mapping
        )
        principal_result = self.evaluate(authority=authority)

        self.assertEqual(principal_result.decision, AuthorizationDecision.DENY)
        self.assertEqual(principal_result.reason, ReasonCategory.UNKNOWN_STATE)

        authority = base_authority()
        resource = object.__new__(GovernedResource)
        object.__setattr__(
            resource,
            "authority_reference",
            "resource-report-a-missing-id-v1",
        )
        object.__setattr__(resource, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(resource, "resource_reference", "report-ref-a")
        object.__setattr__(resource, "resource_class", ResourceClass.REPORT)
        object.__setattr__(resource, "business_entity_id", "business-a")
        authority.resources["report-ref-a"] = resource
        resource_result = self.evaluate(authority=authority)

        self.assertEqual(resource_result.decision, AuthorizationDecision.DENY)
        self.assertEqual(resource_result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_equivalent_inputs_produce_equivalent_deterministic_output(self):
        first = self.evaluate()
        second = self.evaluate()

        self.assertEqual(first, second)
        self.assertEqual(
            first.audit_evidence.decision_id,
            second.audit_evidence.decision_id,
        )

    def test_authorization_result_is_immutable(self):
        result = self.evaluate()

        with self.assertRaises(FrozenInstanceError):
            result.decision = AuthorizationDecision.DENY

    def test_unknown_principal_denies(self):
        result = self.evaluate(
            authz_request=request(
                subject=TrustedSubjectEvidence("fixture-idp", "unknown", True)
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)

    def test_missing_principal_mapping_denies(self):
        authority = base_authority()
        authority.principal_mappings = {}

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)

    def test_invalid_authentication_evidence_denies_before_mapping(self):
        result = self.evaluate(
            authz_request=request(
                subject=TrustedSubjectEvidence("fixture-idp", "subject-a", False)
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHENTICATION_INVALID)

    def test_missing_authentication_evidence_denies(self):
        result = self.evaluate(authz_request=request(subject=None))

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHENTICATION_INVALID)

    def test_non_boolean_authentication_verified_value_denies(self):
        result = self.evaluate(
            authz_request=request(
                subject=TrustedSubjectEvidence("fixture-idp", "subject-a", 1)
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHENTICATION_INVALID)

    def test_caller_created_subject_object_cannot_masquerade_as_trusted(self):
        class SubjectLike:
            provider = "fixture-idp"
            subject = "subject-a"
            verified = True

        result = self.evaluate(authz_request=request(subject=SubjectLike()))

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHENTICATION_INVALID)

    def test_caller_created_request_object_cannot_masquerade_as_trusted(self):
        class RequestLike:
            subject_evidence = SUBJECT_A
            resource_reference = "report-ref-a"
            requested_action = RequestedAction.VIEW
            governed_version_context = governed_context()
            correlation_id = "authz-test-001"
            evaluation_context = BOUNDED_EVALUATION_CONTEXT

        result = self.evaluate(authz_request=RequestLike())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHENTICATION_INVALID)

    def test_authentication_failure_precedes_unsupported_action_detail(self):
        result = self.evaluate(
            authz_request=request(subject=None, action="UPDATE")
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHENTICATION_INVALID)

    def test_inactive_membership_denies(self):
        result = self.evaluate(
            authority=base_authority(membership_state=AuthorityRecordState.INACTIVE)
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)

    def test_revoked_membership_denies(self):
        result = self.evaluate(
            authority=base_authority(membership_state=AuthorityRecordState.REVOKED)
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)

    def test_expired_membership_denies(self):
        result = self.evaluate(
            authority=base_authority(membership_state=AuthorityRecordState.EXPIRED)
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)

    def test_missing_entitlement_denies(self):
        result = self.evaluate(authority=base_authority(include_entitlement=False))

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ENTITLEMENT_MISSING)

    def test_revoked_entitlement_denies(self):
        result = self.evaluate(
            authority=base_authority(entitlement_state=AuthorityRecordState.REVOKED)
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ENTITLEMENT_REVOKED)

    def test_expired_entitlement_denies(self):
        result = self.evaluate(
            authority=base_authority(entitlement_state=AuthorityRecordState.EXPIRED)
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ENTITLEMENT_REVOKED)

    def test_inactive_business_entity_denies(self):
        authority = base_authority()
        authority.business_entities["business-a"] = replace(
            authority.business_entities["business-a"],
            state=AuthorityRecordState.INACTIVE,
        )

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.BUSINESS_ENTITY_INVALID)

    def test_inactive_resource_denies(self):
        authority = base_authority()
        authority.resources["report-ref-a"] = replace(
            authority.resources["report-ref-a"],
            state=AuthorityRecordState.INACTIVE,
        )

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.RESOURCE_UNRESOLVED)

    def test_business_entity_a_principal_cannot_access_business_entity_b_resource(
        self,
    ):
        result = self.evaluate(
            authz_request=request(resource_reference="report-ref-b")
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)
        self.assertEqual(result.audit_evidence.business_entity_id, "business-b")
        self.assertEqual(result.audit_evidence.resource_id, "report-b")

    def test_manipulated_resource_identifier_is_not_authorization(self):
        authority = base_authority()
        resource_same_business = replace(
            authority.resources["report-ref-a"],
            authority_reference="resource-report-a-copy-v1",
            resource_id="report-a-copy",
            resource_reference="known-valid-report-a-copy",
        )
        authority.resources[
            "known-valid-report-a-copy"
        ] = resource_same_business

        result = self.evaluate(
            authority=authority,
            authz_request=request(resource_reference="known-valid-report-a-copy"),
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ENTITLEMENT_MISSING)
        self.assertEqual(result.audit_evidence.resource_id, "report-a-copy")

    def test_authorized_resource_with_unauthorized_action_denies(self):
        authority = base_authority(include_entitlement=False)
        authority.entitlements[
            (
                "principal-a",
                "business-a",
                "report-a",
                RequestedAction.VIEW,
            )
        ] = Entitlement(
            authority_reference="entitlement-principal-a-report-a-view-v1",
            state=AuthorityRecordState.ACTIVE,
            principal_id="principal-a",
            business_entity_id="business-a",
            resource_id="report-a",
            action=RequestedAction.VIEW,
        )

        result = self.evaluate(
            authority=authority,
            authz_request=request(action=RequestedAction.DOWNLOAD),
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ENTITLEMENT_MISSING)

    def test_unsupported_action_denies(self):
        result = self.evaluate(authz_request=request(action="UPDATE"))

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ACTION_UNSUPPORTED)

    def test_action_resource_mismatch_denies_before_entitlement(self):
        result = self.evaluate(
            authz_request=request(
                resource_reference="submission-ref-a",
                action=RequestedAction.VIEW,
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.ACTION_NOT_APPLICABLE)
        self.assertEqual(
            result.audit_evidence.applicability,
            ResourceActionApplicability.NOT_APPLICABLE,
        )

    def test_unknown_resource_denies(self):
        result = self.evaluate(
            authz_request=request(resource_reference="unknown-resource")
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.RESOURCE_UNRESOLVED)

    def test_malformed_authorization_request_denies(self):
        result = self.evaluate(
            authz_request=AuthorizationRequest(
                subject_evidence=SUBJECT_A,
                resource_reference=None,
                requested_action=RequestedAction.VIEW,
                governed_version_context=governed_context(),
                correlation_id="authz-test-001",
                evaluation_context=BOUNDED_EVALUATION_CONTEXT,
            )
        )

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.RESOURCE_UNRESOLVED)

    def test_missing_authority_evidence_fails_closed(self):
        authority = base_authority()
        authority.unavailable.add("entitlement")

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHORITY_UNAVAILABLE)

    def test_stale_authority_state_fails_closed(self):
        authority = base_authority()
        authority.stale.add("membership")

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.STATE_STALE)

    def test_conflicting_authority_state_fails_closed(self):
        authority = base_authority()
        authority.conflicting.add("resource")

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.AUTHORIZATION_CONFLICT)

    def test_user_b_cannot_use_user_a_entitlement(self):
        result = self.evaluate(authz_request=request(subject=SUBJECT_B))

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.MEMBERSHIP_INVALID)
        self.assertEqual(result.audit_evidence.principal_id, "principal-b")

    def test_audit_evidence_uses_minimum_necessary_disclosure(self):
        result = self.evaluate()
        evidence = result.audit_evidence.to_dict()

        self.assertNotIn("subject-a", str(evidence))
        self.assertNotIn("fixture-idp", str(evidence))
        self.assertNotIn("token", str(evidence).lower())
        self.assertIn("principal_mapping:principal-map-a-v1", str(evidence))
        self.assertIn(
            "entitlement:entitlement-principal-a-report-a-view-v1",
            str(evidence),
        )

    def test_malformed_authority_record_shape_cannot_allow(self):
        class MalformedRecord:
            def __init__(self, **values):
                self.__dict__.update(values)

        class MalformedAuthority:
            def resolve_principal_mapping(self, subject_provider, subject):
                return AuthorityLookupResult.found(
                    MalformedRecord(
                        authority_reference="malformed-principal",
                        state=AuthorityRecordState.ACTIVE,
                        subject_provider=subject_provider,
                        subject=subject,
                        principal_id="principal-a",
                    )
                )

            def resolve_resource(self, resource_reference):
                return AuthorityLookupResult.found(
                    MalformedRecord(
                        authority_reference="malformed-resource",
                        state=AuthorityRecordState.ACTIVE,
                        resource_id="report-a",
                        resource_reference=resource_reference,
                        resource_class=ResourceClass.REPORT,
                        business_entity_id="business-a",
                    )
                )

            def resolve_business_entity(self, business_entity_id):
                return AuthorityLookupResult.found(
                    MalformedRecord(
                        authority_reference="malformed-business-entity",
                        state=AuthorityRecordState.ACTIVE,
                        business_entity_id=business_entity_id,
                    )
                )

            def resolve_membership(self, principal_id, business_entity_id):
                return AuthorityLookupResult.found(
                    MalformedRecord(
                        authority_reference="malformed-membership",
                        state=AuthorityRecordState.ACTIVE,
                        principal_id=principal_id,
                        business_entity_id=business_entity_id,
                    )
                )

            def resolve_entitlement(
                self,
                principal_id,
                business_entity_id,
                resource_id,
                action,
            ):
                return AuthorityLookupResult.found(
                    MalformedRecord(
                        authority_reference="malformed-entitlement",
                        state=AuthorityRecordState.ACTIVE,
                        principal_id=principal_id,
                        business_entity_id=business_entity_id,
                        resource_id=resource_id,
                        action=action,
                    )
                )

        result = self.evaluate(authority=MalformedAuthority())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_principal_mapping_must_match_authenticated_subject(self):
        authority = base_authority()
        authority.principal_mappings[("fixture-idp", "subject-a")] = replace(
            authority.principal_mappings[("fixture-idp", "subject-a")],
            subject_provider="other-idp",
            subject="subject-b",
        )

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)

    def test_resource_identity_must_match_requested_reference(self):
        authority = base_authority()
        authority.resources["report-ref-a"] = replace(
            authority.resources["report-ref-a"],
            resource_reference="report-ref-b",
        )

        result = self.evaluate(authority=authority)

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.RESOURCE_MISMATCH)

    def test_malformed_lookup_records_collection_fails_closed(self):
        class MalformedLookupAuthority:
            def __init__(self):
                self.delegate = base_authority()

            def resolve_principal_mapping(self, subject_provider, subject):
                lookup = self.delegate.resolve_principal_mapping(
                    subject_provider, subject
                )
                return AuthorityLookupResult(
                    AuthorityLookupStatus.FOUND,
                    list(lookup.records),
                )

            def resolve_resource(self, resource_reference):
                return self.delegate.resolve_resource(resource_reference)

            def resolve_business_entity(self, business_entity_id):
                return self.delegate.resolve_business_entity(business_entity_id)

            def resolve_membership(self, principal_id, business_entity_id):
                return self.delegate.resolve_membership(
                    principal_id, business_entity_id
                )

            def resolve_entitlement(
                self,
                principal_id,
                business_entity_id,
                resource_id,
                action,
            ):
                return self.delegate.resolve_entitlement(
                    principal_id,
                    business_entity_id,
                    resource_id,
                    action,
                )

        result = self.evaluate(authority=MalformedLookupAuthority())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)

    def test_authority_lookup_exceptions_fail_closed(self):
        class ExplodingAuthority:
            def __init__(self, failing_method):
                self.delegate = base_authority()
                self.failing_method = failing_method

            def _fail_if_targeted(self, method_name):
                if method_name == self.failing_method:
                    raise RuntimeError("authority unavailable")

            def resolve_principal_mapping(self, subject_provider, subject):
                self._fail_if_targeted("resolve_principal_mapping")
                return self.delegate.resolve_principal_mapping(
                    subject_provider,
                    subject,
                )

            def resolve_resource(self, resource_reference):
                self._fail_if_targeted("resolve_resource")
                return self.delegate.resolve_resource(resource_reference)

            def resolve_business_entity(self, business_entity_id):
                self._fail_if_targeted("resolve_business_entity")
                return self.delegate.resolve_business_entity(business_entity_id)

            def resolve_membership(self, principal_id, business_entity_id):
                self._fail_if_targeted("resolve_membership")
                return self.delegate.resolve_membership(
                    principal_id, business_entity_id
                )

            def resolve_entitlement(
                self,
                principal_id,
                business_entity_id,
                resource_id,
                action,
            ):
                self._fail_if_targeted("resolve_entitlement")
                return self.delegate.resolve_entitlement(
                    principal_id,
                    business_entity_id,
                    resource_id,
                    action,
                )

        failing_methods = (
            "resolve_principal_mapping",
            "resolve_resource",
            "resolve_business_entity",
            "resolve_membership",
            "resolve_entitlement",
        )
        for method_name in failing_methods:
            with self.subTest(method_name=method_name):
                result = self.evaluate(
                    authority=ExplodingAuthority(method_name)
                )

                self.assertEqual(result.decision, AuthorizationDecision.DENY)
                self.assertEqual(
                    result.reason,
                    ReasonCategory.AUTHORITY_UNAVAILABLE,
                )


if __name__ == "__main__":
    unittest.main()
