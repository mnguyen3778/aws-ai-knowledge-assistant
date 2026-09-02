import sys
import unittest
from dataclasses import replace
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
    provider="local-proof-provider",
    subject="subject-a",
    verified=True,
)

SUBJECT_B = TrustedSubjectEvidence(
    provider="local-proof-provider",
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


def authorization_request(
    subject=SUBJECT_A,
    resource_reference="report-a-ref",
    action=RequestedAction.VIEW,
    version_context=None,
    evaluation_context=BOUNDED_EVALUATION_CONTEXT,
):
    return AuthorizationRequest(
        subject_evidence=subject,
        resource_reference=resource_reference,
        requested_action=action,
        governed_version_context=(
            version_context if version_context is not None else governed_context()
        ),
        correlation_id="local-proof-correlation",
        evaluation_context=evaluation_context,
    )


class LocalCompositionAuthoritySource:
    def __init__(
        self,
        principal_mappings,
        business_entities,
        memberships,
        resources,
        entitlements,
        statuses=None,
        failures=None,
    ):
        self.principal_mappings = principal_mappings
        self.business_entities = business_entities
        self.memberships = memberships
        self.resources = resources
        self.entitlements = entitlements
        self.statuses = statuses or {}
        self.failures = set(failures or ())

    def resolve_principal_mapping(self, subject_provider, subject):
        self._raise_if_configured("principal_mapping")
        return self._result(
            "principal_mapping",
            self.principal_mappings.get((subject_provider, subject)),
        )

    def resolve_resource(self, resource_reference):
        self._raise_if_configured("resource")
        return self._result("resource", self.resources.get(resource_reference))

    def resolve_business_entity(self, business_entity_id):
        self._raise_if_configured("business_entity")
        return self._result(
            "business_entity",
            self.business_entities.get(business_entity_id),
        )

    def resolve_membership(self, principal_id, business_entity_id):
        self._raise_if_configured("membership")
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
        self._raise_if_configured("entitlement")
        return self._result(
            "entitlement",
            self.entitlements.get(
                (principal_id, business_entity_id, resource_id, action)
            ),
        )

    def _raise_if_configured(self, label):
        if label in self.failures:
            raise ValueError(f"{label} unavailable")

    def _result(self, label, record):
        status = self.statuses.get(label)
        if status is AuthorityLookupStatus.UNAVAILABLE:
            return AuthorityLookupResult.unavailable()
        if status is AuthorityLookupStatus.STALE:
            return AuthorityLookupResult.stale()
        if status is AuthorityLookupStatus.CONFLICTING:
            return AuthorityLookupResult.conflicting()
        if status is AuthorityLookupStatus.AMBIGUOUS:
            return AuthorityLookupResult.ambiguous()
        if status is AuthorityLookupStatus.MALFORMED:
            return AuthorityLookupResult(AuthorityLookupStatus.MALFORMED)
        if status is AuthorityLookupStatus.UNSUPPORTED:
            return AuthorityLookupResult(AuthorityLookupStatus.UNSUPPORTED)
        if record is None:
            return AuthorityLookupResult.missing()
        return AuthorityLookupResult.found(record)


def local_authority_source():
    principal_a = PrincipalMapping(
        authority_reference="principal-map-a",
        state=AuthorityRecordState.ACTIVE,
        subject_provider="local-proof-provider",
        subject="subject-a",
        principal_id="principal-a",
    )
    principal_b = PrincipalMapping(
        authority_reference="principal-map-b",
        state=AuthorityRecordState.ACTIVE,
        subject_provider="local-proof-provider",
        subject="subject-b",
        principal_id="principal-b",
    )
    business_a = BusinessEntity(
        authority_reference="business-a",
        state=AuthorityRecordState.ACTIVE,
        business_entity_id="business-a",
    )
    business_b = BusinessEntity(
        authority_reference="business-b",
        state=AuthorityRecordState.ACTIVE,
        business_entity_id="business-b",
    )
    membership_a = Membership(
        authority_reference="membership-principal-a-business-a",
        state=AuthorityRecordState.ACTIVE,
        principal_id="principal-a",
        business_entity_id="business-a",
    )
    report_a = GovernedResource(
        authority_reference="resource-report-a",
        state=AuthorityRecordState.ACTIVE,
        resource_id="report-a",
        resource_reference="report-a-ref",
        resource_class=ResourceClass.REPORT,
        business_entity_id="business-a",
    )
    report_b = GovernedResource(
        authority_reference="resource-report-b",
        state=AuthorityRecordState.ACTIVE,
        resource_id="report-b",
        resource_reference="report-b-ref",
        resource_class=ResourceClass.REPORT,
        business_entity_id="business-b",
    )
    report_copy = GovernedResource(
        authority_reference="resource-report-copy",
        state=AuthorityRecordState.ACTIVE,
        resource_id="report-copy",
        resource_reference="report-copy-ref",
        resource_class=ResourceClass.REPORT,
        business_entity_id="business-a",
    )
    submission_a = GovernedResource(
        authority_reference="resource-submission-a",
        state=AuthorityRecordState.ACTIVE,
        resource_id="submission-a",
        resource_reference="submission-a-ref",
        resource_class=ResourceClass.ASSESSMENT_SUBMISSION,
        business_entity_id="business-a",
    )
    entitlement_view = Entitlement(
        authority_reference="entitlement-principal-a-report-a-view",
        state=AuthorityRecordState.ACTIVE,
        principal_id="principal-a",
        business_entity_id="business-a",
        resource_id="report-a",
        action=RequestedAction.VIEW,
    )
    entitlement_download = Entitlement(
        authority_reference="entitlement-principal-a-report-a-download",
        state=AuthorityRecordState.ACTIVE,
        principal_id="principal-a",
        business_entity_id="business-a",
        resource_id="report-a",
        action=RequestedAction.DOWNLOAD,
    )

    return LocalCompositionAuthoritySource(
        principal_mappings={
            ("local-proof-provider", "subject-a"): principal_a,
            ("local-proof-provider", "subject-b"): principal_b,
        },
        business_entities={
            "business-a": business_a,
            "business-b": business_b,
        },
        memberships={
            ("principal-a", "business-a"): membership_a,
        },
        resources={
            "report-a-ref": report_a,
            "report-b-ref": report_b,
            "report-copy-ref": report_copy,
            "submission-a-ref": submission_a,
        },
        entitlements={
            (
                "principal-a",
                "business-a",
                "report-a",
                RequestedAction.VIEW,
            ): entitlement_view,
            (
                "principal-a",
                "business-a",
                "report-a",
                RequestedAction.DOWNLOAD,
            ): entitlement_download,
        },
    )


def evaluate(authority_source=None, request=None):
    evaluator = TrustedAuthorizationEvaluator(
        authority_source or local_authority_source()
    )
    return evaluator.evaluate(request or authorization_request())


class MalformedRecord:
    def __init__(self, **values):
        self.__dict__.update(values)


class TrustedAuthorizationLocalIntegrationHarnessTests(unittest.TestCase):
    def test_valid_local_composition_allows_and_preserves_audit(self):
        first = evaluate()
        second = evaluate()

        self.assertEqual(first.decision, AuthorizationDecision.ALLOW)
        self.assertIsNone(first.reason)
        self.assertEqual(first, second)
        self.assertEqual(
            first.audit_evidence.decision_id,
            second.audit_evidence.decision_id,
        )
        self.assertEqual(first.audit_evidence.principal_id, "principal-a")
        self.assertEqual(first.audit_evidence.business_entity_id, "business-a")
        self.assertEqual(first.audit_evidence.resource_id, "report-a")
        self.assertEqual(
            first.audit_evidence.requested_action,
            RequestedAction.VIEW,
        )
        self.assertEqual(
            first.audit_evidence.applicability,
            ResourceActionApplicability.APPLICABLE,
        )
        self.assertEqual(
            first.audit_evidence.semantics_version,
            AUTHORIZATION_SEMANTICS_VERSION,
        )
        self.assertEqual(
            first.audit_evidence.applicability_version,
            APPLICABILITY_GOVERNANCE_VERSION,
        )
        self.assertEqual(
            first.audit_evidence.authority_inputs,
            (
                "authentication_evidence:verified",
                f"authorization_semantics:{AUTHORIZATION_SEMANTICS_VERSION}",
                f"resource_action_applicability:{APPLICABILITY_GOVERNANCE_VERSION}",
                f"evaluation_context:{BOUNDED_EVALUATION_CONTEXT}",
                "principal_mapping:principal-map-a",
                "resource_identity:resource-report-a",
                f"resource_action_applicability:{APPLICABILITY_GOVERNANCE_VERSION}",
                "business_entity:business-a",
                "membership:membership-principal-a-business-a",
                "entitlement:entitlement-principal-a-report-a-view",
            ),
        )

    def test_local_composition_negative_cases_fail_closed(self):
        cases = (
            (
                "unknown principal",
                local_authority_source(),
                authorization_request(
                    subject=TrustedSubjectEvidence(
                        "local-proof-provider",
                        "unknown-subject",
                        True,
                    )
                ),
                ReasonCategory.PRINCIPAL_UNRESOLVED,
            ),
            (
                "missing principal mapping",
                self._without("principal_mapping"),
                authorization_request(),
                ReasonCategory.PRINCIPAL_UNRESOLVED,
            ),
            (
                "invalid principal mapping",
                self._with_principal_state(AuthorityRecordState.REVOKED),
                authorization_request(),
                ReasonCategory.PRINCIPAL_UNRESOLVED,
            ),
            (
                "wrong business entity",
                local_authority_source(),
                authorization_request(resource_reference="report-b-ref"),
                ReasonCategory.MEMBERSHIP_INVALID,
            ),
            (
                "missing membership",
                self._without("membership"),
                authorization_request(),
                ReasonCategory.MEMBERSHIP_INVALID,
            ),
            (
                "inactive membership",
                self._with_membership_state(AuthorityRecordState.INACTIVE),
                authorization_request(),
                ReasonCategory.MEMBERSHIP_INVALID,
            ),
            (
                "disabled membership",
                self._with_membership_state(AuthorityRecordState.DISABLED),
                authorization_request(),
                ReasonCategory.MEMBERSHIP_INVALID,
            ),
            (
                "missing entitlement",
                self._without("entitlement"),
                authorization_request(),
                ReasonCategory.ENTITLEMENT_MISSING,
            ),
            (
                "revoked entitlement",
                self._with_entitlement_state(AuthorityRecordState.REVOKED),
                authorization_request(),
                ReasonCategory.ENTITLEMENT_REVOKED,
            ),
            (
                "missing resource",
                local_authority_source(),
                authorization_request(resource_reference="missing-resource"),
                ReasonCategory.RESOURCE_UNRESOLVED,
            ),
            (
                "wrong resource business entity",
                local_authority_source(),
                authorization_request(resource_reference="report-b-ref"),
                ReasonCategory.MEMBERSHIP_INVALID,
            ),
            (
                "wrong requested action",
                self._without("download_entitlement"),
                authorization_request(action=RequestedAction.DOWNLOAD),
                ReasonCategory.ENTITLEMENT_MISSING,
            ),
            (
                "unsupported action",
                local_authority_source(),
                authorization_request(action="UPDATE"),
                ReasonCategory.ACTION_UNSUPPORTED,
            ),
            (
                "inapplicable action",
                local_authority_source(),
                authorization_request(
                    resource_reference="submission-a-ref",
                    action=RequestedAction.VIEW,
                ),
                ReasonCategory.ACTION_NOT_APPLICABLE,
            ),
            (
                "stale membership lookup",
                self._with_status("membership", AuthorityLookupStatus.STALE),
                authorization_request(),
                ReasonCategory.STATE_STALE,
            ),
            (
                "resource lookup failure",
                self._with_status("resource", AuthorityLookupStatus.UNAVAILABLE),
                authorization_request(),
                ReasonCategory.AUTHORITY_UNAVAILABLE,
            ),
            (
                "authority source exception",
                self._with_failure("entitlement"),
                authorization_request(),
                ReasonCategory.AUTHORITY_UNAVAILABLE,
            ),
            (
                "unsupported governance version",
                local_authority_source(),
                authorization_request(
                    version_context=governed_context(
                        semantics_version="unsupported-version"
                    )
                ),
                ReasonCategory.UNKNOWN_STATE,
            ),
            (
                "context mismatch",
                local_authority_source(),
                authorization_request(evaluation_context="wrong-context"),
                ReasonCategory.UNKNOWN_STATE,
            ),
            (
                "idor bola attempt",
                local_authority_source(),
                authorization_request(resource_reference="report-copy-ref"),
                ReasonCategory.ENTITLEMENT_MISSING,
            ),
        )

        for label, authority_source, request, expected_reason in cases:
            with self.subTest(case=label):
                first = evaluate(authority_source=authority_source, request=request)
                second = evaluate(authority_source=authority_source, request=request)

                self.assertEqual(first.decision, AuthorizationDecision.DENY)
                self.assertEqual(first.reason, expected_reason)
                self.assertEqual(first, second)

    def test_malformed_and_contradictory_local_evidence_fails_closed(self):
        malformed = local_authority_source()
        malformed.resources["report-a-ref"] = MalformedRecord(
            authority_reference="malformed-resource",
            state=AuthorityRecordState.ACTIVE,
            resource_id="report-a",
            resource_reference="report-a-ref",
            resource_class=ResourceClass.REPORT,
            business_entity_id="business-a",
        )
        malformed_result = evaluate(authority_source=malformed)

        conflicting_result = evaluate(
            authority_source=self._with_status(
                "resource",
                AuthorityLookupStatus.CONFLICTING,
            )
        )

        self.assertEqual(malformed_result.decision, AuthorizationDecision.DENY)
        self.assertEqual(malformed_result.reason, ReasonCategory.UNKNOWN_STATE)
        self.assertEqual(conflicting_result.decision, AuthorizationDecision.DENY)
        self.assertEqual(
            conflicting_result.reason,
            ReasonCategory.AUTHORIZATION_CONFLICT,
        )

    def test_local_composition_does_not_reclassify_failed_lookup_as_revocation(self):
        unavailable = evaluate(
            authority_source=self._with_status(
                "entitlement",
                AuthorityLookupStatus.UNAVAILABLE,
            )
        )
        revoked = evaluate(
            authority_source=self._with_entitlement_state(
                AuthorityRecordState.REVOKED
            )
        )

        self.assertEqual(unavailable.decision, AuthorizationDecision.DENY)
        self.assertEqual(unavailable.reason, ReasonCategory.AUTHORITY_UNAVAILABLE)
        self.assertEqual(revoked.decision, AuthorizationDecision.DENY)
        self.assertEqual(revoked.reason, ReasonCategory.ENTITLEMENT_REVOKED)
        self.assertNotEqual(unavailable.reason, revoked.reason)

    def test_local_composition_keeps_authentication_separate_from_authorization(self):
        invalid_authentication = evaluate(
            request=authorization_request(
                subject=TrustedSubjectEvidence(
                    "local-proof-provider",
                    "subject-a",
                    False,
                )
            )
        )
        missing_membership = evaluate(authority_source=self._without("membership"))

        self.assertEqual(
            invalid_authentication.decision,
            AuthorizationDecision.DENY,
        )
        self.assertEqual(
            invalid_authentication.reason,
            ReasonCategory.AUTHENTICATION_INVALID,
        )
        self.assertEqual(missing_membership.decision, AuthorizationDecision.DENY)
        self.assertEqual(missing_membership.reason, ReasonCategory.MEMBERSHIP_INVALID)

    def _without(self, evidence_name):
        authority = local_authority_source()
        if evidence_name == "principal_mapping":
            authority.principal_mappings = {}
        elif evidence_name == "membership":
            authority.memberships = {}
        elif evidence_name == "entitlement":
            authority.entitlements = {}
        elif evidence_name == "download_entitlement":
            authority.entitlements.pop(
                (
                    "principal-a",
                    "business-a",
                    "report-a",
                    RequestedAction.DOWNLOAD,
                )
            )
        return authority

    def _with_principal_state(self, state):
        authority = local_authority_source()
        authority.principal_mappings[("local-proof-provider", "subject-a")] = replace(
            authority.principal_mappings[("local-proof-provider", "subject-a")],
            state=state,
        )
        return authority

    def _with_membership_state(self, state):
        authority = local_authority_source()
        authority.memberships[("principal-a", "business-a")] = replace(
            authority.memberships[("principal-a", "business-a")],
            state=state,
        )
        return authority

    def _with_entitlement_state(self, state):
        authority = local_authority_source()
        authority.entitlements[
            (
                "principal-a",
                "business-a",
                "report-a",
                RequestedAction.VIEW,
            )
        ] = replace(
            authority.entitlements[
                (
                    "principal-a",
                    "business-a",
                    "report-a",
                    RequestedAction.VIEW,
                )
            ],
            state=state,
        )
        return authority

    def _with_status(self, label, status):
        authority = local_authority_source()
        authority.statuses[label] = status
        return authority

    def _with_failure(self, label):
        authority = local_authority_source()
        authority.failures.add(label)
        return authority


if __name__ == "__main__":
    unittest.main()
