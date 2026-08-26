import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trusted_authorization import (  # noqa: E402
    APPLICABILITY_GOVERNANCE_VERSION,
    AUTHORIZATION_SEMANTICS_VERSION,
    AuthorityLookupResult,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationDecision,
    AuthorizationRequest,
    BusinessEntity,
    Entitlement,
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
)
SUBJECT_B = TrustedSubjectEvidence(
    provider="fixture-idp",
    subject="subject-b",
)


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
        subject_provider="fixture-idp",
        subject="subject-a",
        principal_id="principal-a",
    )
    principal_b = PrincipalMapping(
        authority_reference="principal-map-b-v1",
        subject_provider="fixture-idp",
        subject="subject-b",
        principal_id="principal-b",
    )
    business_a = BusinessEntity(
        authority_reference="business-entity-a-v1",
        business_entity_id="business-a",
    )
    business_b = BusinessEntity(
        authority_reference="business-entity-b-v1",
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
        resource_id="report-a",
        resource_reference="report-ref-a",
        resource_class=ResourceClass.REPORT,
        business_entity_id="business-a",
    )
    resource_b = GovernedResource(
        authority_reference="resource-report-b-v1",
        resource_id="report-b",
        resource_reference="report-ref-b",
        resource_class=ResourceClass.REPORT,
        business_entity_id="business-b",
    )
    submission_a = GovernedResource(
        authority_reference="resource-submission-a-v1",
        resource_id="submission-a",
        resource_reference="submission-ref-a",
        resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
        business_entity_id="business-a",
    )
    dashboard_a = GovernedResource(
        authority_reference="resource-dashboard-a-v1",
        resource_id="dashboard-a",
        resource_reference="dashboard-ref-a",
        resource_class=ResourceClass.EXECUTIVE_DASHBOARD,
        business_entity_id="business-a",
    )
    entitlement_a = Entitlement(
        authority_reference="entitlement-principal-a-report-a-view-v1",
        state=entitlement_state,
        principal_id="principal-a",
        business_entity_id="business-a",
        resource_id="report-a",
        action=RequestedAction.VIEW,
    )

    entitlements = {}
    if include_entitlement:
        entitlements[
            (
                "principal-a",
                "business-a",
                "report-a",
                RequestedAction.VIEW,
            )
        ] = entitlement_a

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
        correlation_id="authz-test-001",
        evaluation_context="fixed-test-context",
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
                subject=TrustedSubjectEvidence("fixture-idp", "unknown")
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
            correlation_id = "authz-test-001"
            evaluation_context = "fixed-test-context"

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
        result = self.evaluate(authz_request=request(action=RequestedAction.DOWNLOAD))

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
                correlation_id="authz-test-001",
                evaluation_context="fixed-test-context",
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
