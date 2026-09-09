import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization as trusted_authorization_package  # noqa: E402
import trusted_authorization.membership_source as membership_source_module  # noqa: E402
from trusted_authorization import (  # noqa: E402
    APPLICABILITY_GOVERNANCE_VERSION,
    AUTHORIZATION_SEMANTICS_VERSION,
    BOUNDED_EVALUATION_CONTEXT,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationDecision,
    AuthorizationRequest,
    GovernedVersionContext,
    RequestedAction,
    TrustedAuthorizationEvaluator,
    TrustedSubjectEvidence,
)
from trusted_authorization.membership_source import (  # noqa: E402
    NonProductionMembershipAuthoritySource,
)
from trusted_authorization.models import Membership  # noqa: E402


SUBJECT = TrustedSubjectEvidence(
    provider="membership-source-test",
    subject="subject-alpha",
    verified=True,
)


def membership(
    authority_reference="membership-alpha-authority",
    state=AuthorityRecordState.ACTIVE,
    principal_id="principal-alpha",
    business_entity_id="business-alpha",
):
    return Membership(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        business_entity_id=business_entity_id,
    )


def set_membership_fields(record, **overrides):
    values = {
        "authority_reference": "membership-alpha-authority",
        "state": AuthorityRecordState.ACTIVE,
        "principal_id": "principal-alpha",
        "business_entity_id": "business-alpha",
    }
    values.update(overrides)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def mutate_to_forged_membership(record):
    object.__setattr__(record, "authority_reference", "attacker-authority")
    object.__setattr__(record, "state", AuthorityRecordState.REVOKED)
    object.__setattr__(record, "principal_id", "principal-admin")
    object.__setattr__(record, "business_entity_id", "business-admin")


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


def request(subject=SUBJECT):
    return AuthorizationRequest(
        subject_evidence=subject,
        resource_reference="resource-alpha",
        requested_action=RequestedAction.VIEW,
        governed_version_context=governed_context(),
        correlation_id="membership-source-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


class NonProductionMembershipAuthoritySourceTests(unittest.TestCase):
    def test_known_active_membership_resolves_expected_relationship(self):
        expected = membership()
        source = NonProductionMembershipAuthoritySource([expected])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records, (expected,))
        self.assertIs(type(result.records[0]), Membership)
        self.assertIsNot(result.records[0], expected)
        self.assertIsNot(result.records[0], source._memberships[0])
        self.assertEqual(
            result.records[0].authority_reference,
            "membership-alpha-authority",
        )
        self.assertEqual(result.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(result.records[0].principal_id, "principal-alpha")
        self.assertEqual(result.records[0].business_entity_id, "business-alpha")

    def test_unknown_pair_and_empty_source_return_no_authority(self):
        populated = NonProductionMembershipAuthoritySource([membership()])
        empty = NonProductionMembershipAuthoritySource()

        wrong_principal = populated.resolve_membership(
            "principal-beta",
            "business-alpha",
        )
        wrong_business = populated.resolve_membership(
            "principal-alpha",
            "business-beta",
        )
        absent = empty.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(wrong_principal.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(wrong_principal.records, ())
        self.assertEqual(wrong_business.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(wrong_business.records, ())
        self.assertEqual(absent.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(absent.records, ())

    def test_malformed_principal_lookup_inputs_fail_closed_before_matching(self):
        class Hostile:
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        source = NonProductionMembershipAuthoritySource([membership()])
        cases = (
            ("none", None),
            ("integer", 1),
            ("hostile object", Hostile()),
            ("empty", ""),
            ("whitespace", "   "),
        )

        for label, lookup in cases:
            with self.subTest(case=label):
                Hostile.comparisons = 0

                result = source.resolve_membership(lookup, "business-alpha")

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(Hostile.comparisons, 0)

    def test_malformed_business_entity_lookup_inputs_fail_closed_before_matching(self):
        class Hostile:
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        source = NonProductionMembershipAuthoritySource([membership()])
        cases = (
            ("none", None),
            ("integer", 1),
            ("hostile object", Hostile()),
            ("empty", ""),
            ("whitespace", "   "),
        )

        for label, lookup in cases:
            with self.subTest(case=label):
                Hostile.comparisons = 0

                result = source.resolve_membership("principal-alpha", lookup)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(Hostile.comparisons, 0)

    def test_both_lookup_dimensions_malformed_fail_closed(self):
        source = NonProductionMembershipAuthoritySource([membership()])

        result = source.resolve_membership(None, object())

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_principal_str_subclass_lookup_fails_before_behavior_invocation(self):
        class HostileStr(str):
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        class HostileStripStr(str):
            strip_calls = 0

            def strip(self):
                type(self).strip_calls += 1
                return self

        class RaisingStripStr(str):
            strip_calls = 0

            def strip(self):
                type(self).strip_calls += 1
                raise RuntimeError("strip unavailable")

        source = NonProductionMembershipAuthoritySource([membership()])
        cases = (
            ("hostile equality", HostileStr("principal-alpha"), HostileStr, "comparisons"),
            ("hostile strip", HostileStripStr("principal-alpha"), HostileStripStr, "strip_calls"),
            ("raising strip", RaisingStripStr("principal-alpha"), RaisingStripStr, "strip_calls"),
        )

        for label, lookup, instrumented, counter in cases:
            with self.subTest(case=label):
                setattr(instrumented, counter, 0)

                result = source.resolve_membership(lookup, "business-alpha")

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(instrumented, counter), 0)

    def test_business_entity_str_subclass_lookup_fails_before_behavior_invocation(self):
        class HostileStr(str):
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        class HostileStripStr(str):
            strip_calls = 0

            def strip(self):
                type(self).strip_calls += 1
                return self

        class RaisingStripStr(str):
            strip_calls = 0

            def strip(self):
                type(self).strip_calls += 1
                raise RuntimeError("strip unavailable")

        source = NonProductionMembershipAuthoritySource([membership()])
        cases = (
            ("hostile equality", HostileStr("business-alpha"), HostileStr, "comparisons"),
            ("hostile strip", HostileStripStr("business-alpha"), HostileStripStr, "strip_calls"),
            ("raising strip", RaisingStripStr("business-alpha"), RaisingStripStr, "strip_calls"),
        )

        for label, lookup, instrumented, counter in cases:
            with self.subTest(case=label):
                setattr(instrumented, counter, 0)

                result = source.resolve_membership("principal-alpha", lookup)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_membership_evidence_fails_closed(self):
        malformed = object.__new__(Membership)
        object.__setattr__(malformed, "authority_reference", "membership-authority")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(malformed, "principal_id", "principal-alpha")
        source = NonProductionMembershipAuthoritySource([malformed])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_non_current_membership_states_return_no_positive_authority(self):
        cases = (
            (AuthorityRecordState.INACTIVE, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.DISABLED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.REVOKED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.EXPIRED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.TERMINATED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.UNKNOWN, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.STALE, AuthorityLookupStatus.STALE),
        )
        for state, expected_status in cases:
            with self.subTest(state=state):
                source = NonProductionMembershipAuthoritySource(
                    [membership(state=state)]
                )

                result = source.resolve_membership(
                    "principal-alpha",
                    "business-alpha",
                )

                self.assertEqual(result.status, expected_status)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_conflicting_memberships_fail_closed(self):
        cases = (
            ("authority_reference", {"authority_reference": "membership-beta-authority"}),
            ("state", {"state": AuthorityRecordState.STALE}),
        )

        for name, overrides in cases:
            with self.subTest(name=name):
                source = NonProductionMembershipAuthoritySource(
                    [
                        membership(),
                        membership(**overrides),
                    ]
                )

                result = source.resolve_membership(
                    "principal-alpha",
                    "business-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
                self.assertEqual(len(result.records), 2)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_duplicate_memberships_fail_closed_without_deduplication(self):
        source = NonProductionMembershipAuthoritySource([membership(), membership()])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)

    def test_repeated_lookup_is_deterministic_and_output_isolated(self):
        source = NonProductionMembershipAuthoritySource([membership()])

        first = source.resolve_membership("principal-alpha", "business-alpha")
        second = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(first, second)
        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertIsNot(first.records[0], second.records[0])
        self.assertIsNot(first.records[0], source._memberships[0])
        self.assertIsNot(second.records[0], source._memberships[0])

    def test_exact_pair_matching_prevents_relationship_forgery(self):
        source = NonProductionMembershipAuthoritySource([membership()])

        cases = (
            ("principal-alpha", "business-alpha", AuthorityLookupStatus.FOUND),
            ("principal-beta", "business-alpha", AuthorityLookupStatus.NOT_FOUND),
            ("principal-alpha", "business-beta", AuthorityLookupStatus.NOT_FOUND),
            ("principal-beta", "business-beta", AuthorityLookupStatus.NOT_FOUND),
        )

        for principal_id, business_entity_id, expected in cases:
            with self.subTest(principal_id=principal_id, business_entity_id=business_entity_id):
                result = source.resolve_membership(principal_id, business_entity_id)

                self.assertEqual(result.status, expected)

    def test_membership_does_not_support_partial_principal_or_be_lookup(self):
        source = NonProductionMembershipAuthoritySource(
            [
                membership(principal_id="principal-alpha", business_entity_id="business-alpha"),
                membership(principal_id="principal-alpha", business_entity_id="business-beta"),
                membership(principal_id="principal-beta", business_entity_id="business-alpha"),
            ]
        )

        wrong_pair = source.resolve_membership("principal-beta", "business-beta")

        self.assertEqual(wrong_pair.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(wrong_pair.records, ())

    def test_lookup_uses_captured_instance_relationship_fields(self):
        class ConfusedMembership(Membership):
            def __getattribute__(self, name):
                if name == "principal_id":
                    return "principal-alpha"
                if name == "business_entity_id":
                    return "business-alpha"
                return object.__getattribute__(self, name)

        record = object.__new__(ConfusedMembership)
        object.__setattr__(record, "authority_reference", "membership-spoof")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "principal_id", "principal-wrong")
        object.__setattr__(record, "business_entity_id", "business-wrong")
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_benign_membership_subclass_fails_closed(self):
        class BenignMembership(Membership):
            pass

        source = NonProductionMembershipAuthoritySource(
            [
                BenignMembership(
                    "membership-alpha-authority",
                    AuthorityRecordState.ACTIVE,
                    "principal-alpha",
                    "business-alpha",
                )
            ]
        )

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_membership_subclass_field_spoofing_fails_closed_before_reads(self):
        class SpoofedMembership(Membership):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in (
                    "authority_reference",
                    "state",
                    "principal_id",
                    "business_entity_id",
                ):
                    type(self).authority_field_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": "principal-alpha",
                        "business_entity_id": "business-alpha",
                    }[name]
                return object.__getattribute__(self, name)

        record = set_membership_fields(
            object.__new__(SpoofedMembership),
            state=AuthorityRecordState.REVOKED,
            principal_id="principal-wrong",
            business_entity_id="business-wrong",
        )
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(SpoofedMembership.authority_field_reads, 0)

    def test_membership_subclass_raising_getattribute_fails_closed(self):
        class RaisingMembership(Membership):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in (
                    "authority_reference",
                    "state",
                    "principal_id",
                    "business_entity_id",
                ):
                    type(self).authority_field_reads += 1
                    raise RuntimeError("field unavailable")
                return object.__getattribute__(self, name)

        record = set_membership_fields(object.__new__(RaisingMembership))
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(RaisingMembership.authority_field_reads, 0)

    def test_getattr_subclass_fails_closed_before_dynamic_fallback(self):
        class GetattrMembership(Membership):
            getattr_calls = 0

            def __getattr__(self, name):
                type(self).getattr_calls += 1
                return "forged"

        record = set_membership_fields(object.__new__(GetattrMembership))
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(GetattrMembership.getattr_calls, 0)

    def test_forged_dict_cannot_authorize_wrong_actual_relationship(self):
        class ForgedDictMembership(Membership):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": "principal-alpha",
                        "business_entity_id": "business-alpha",
                    }
                return object.__getattribute__(self, name)

        record = set_membership_fields(
            object.__new__(ForgedDictMembership),
            principal_id="principal-wrong",
            business_entity_id="business-wrong",
        )
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictMembership.dict_reads, 0)

    def test_forged_dict_cannot_repair_missing_relationship_field(self):
        class ForgedDictMembership(Membership):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": "principal-alpha",
                        "business_entity_id": "business-alpha",
                    }
                return object.__getattribute__(self, name)

        record = object.__new__(ForgedDictMembership)
        object.__setattr__(record, "authority_reference", "membership-authority")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "principal_id", "principal-alpha")
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictMembership.dict_reads, 0)

    def test_forged_dict_cannot_reactivate_revoked_or_stale_evidence(self):
        class ForgedDictMembership(Membership):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "membership-alpha-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": "principal-alpha",
                        "business_entity_id": "business-alpha",
                    }
                return object.__getattribute__(self, name)

        for state in (AuthorityRecordState.REVOKED, AuthorityRecordState.STALE):
            with self.subTest(state=state):
                ForgedDictMembership.dict_reads = 0
                record = set_membership_fields(
                    object.__new__(ForgedDictMembership),
                    state=state,
                )
                source = NonProductionMembershipAuthoritySource([record])

                result = source.resolve_membership(
                    "principal-alpha",
                    "business-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(ForgedDictMembership.dict_reads, 0)

    def test_forged_dict_cannot_change_returned_authority_values(self):
        class ForgedDictMembership(Membership):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": "principal-admin",
                        "business_entity_id": "business-admin",
                    }
                return object.__getattribute__(self, name)

        record = set_membership_fields(object.__new__(ForgedDictMembership))
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictMembership.dict_reads, 0)

    def test_dict_property_subclass_is_rejected_before_property_read(self):
        class DictPropertyMembership(Membership):
            dict_reads = 0

            @property
            def __dict__(self):
                type(self).dict_reads += 1
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "principal_id": "principal-alpha",
                    "business_entity_id": "business-alpha",
                }

        record = set_membership_fields(object.__new__(DictPropertyMembership))
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictPropertyMembership.dict_reads, 0)

    def test_dict_descriptor_subclass_is_rejected_before_descriptor_read(self):
        class DictDescriptor:
            reads = 0

            def __get__(self, instance, owner):
                type(self).reads += 1
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "principal_id": "principal-alpha",
                    "business_entity_id": "business-alpha",
                }

        class DictDescriptorMembership(Membership):
            __dict__ = DictDescriptor()

        record = set_membership_fields(object.__new__(DictDescriptorMembership))
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictDescriptor.reads, 0)

    def test_combined_field_and_dict_spoofing_cannot_control_authority(self):
        class CombinedSpoofMembership(Membership):
            field_reads = 0
            dict_reads = 0
            getattr_calls = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": "principal-alpha",
                        "business_entity_id": "business-alpha",
                    }
                if name in (
                    "authority_reference",
                    "state",
                    "principal_id",
                    "business_entity_id",
                ):
                    type(self).field_reads += 1
                    return "spoofed"
                return object.__getattribute__(self, name)

            def __getattr__(self, name):
                type(self).getattr_calls += 1
                return "spoofed"

        record = set_membership_fields(object.__new__(CombinedSpoofMembership))
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(CombinedSpoofMembership.field_reads, 0)
        self.assertEqual(CombinedSpoofMembership.dict_reads, 0)
        self.assertEqual(CombinedSpoofMembership.getattr_calls, 0)

    def test_exact_membership_with_dict_subclass_storage_fails_closed(self):
        class HostileDict(dict):
            get_calls = 0
            getitem_calls = 0
            contains_calls = 0
            iter_calls = 0
            keys_calls = 0
            items_calls = 0
            values_calls = 0

            def get(self, key, default=None):
                type(self).get_calls += 1
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "principal_id": "principal-alpha",
                    "business_entity_id": "business-alpha",
                }.get(key, default)

            def __getitem__(self, key):
                type(self).getitem_calls += 1
                return super().__getitem__(key)

            def __contains__(self, key):
                type(self).contains_calls += 1
                return True

            def __iter__(self):
                type(self).iter_calls += 1
                return super().__iter__()

            def keys(self):
                type(self).keys_calls += 1
                return super().keys()

            def items(self):
                type(self).items_calls += 1
                return super().items()

            def values(self):
                type(self).values_calls += 1
                return super().values()

        record = membership(
            authority_reference="actual-authority",
            state=AuthorityRecordState.REVOKED,
            principal_id="principal-wrong",
            business_entity_id="business-wrong",
        )
        object.__setattr__(record, "__dict__", HostileDict())
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(HostileDict.get_calls, 0)
        self.assertEqual(HostileDict.getitem_calls, 0)
        self.assertEqual(HostileDict.contains_calls, 0)
        self.assertEqual(HostileDict.iter_calls, 0)
        self.assertEqual(HostileDict.keys_calls, 0)
        self.assertEqual(HostileDict.items_calls, 0)
        self.assertEqual(HostileDict.values_calls, 0)

    def test_validation_use_toctou_dict_subclass_fails_closed(self):
        class ToctouDict(dict):
            get_calls = 0

            def get(self, key, default=None):
                type(self).get_calls += 1
                if type(self).get_calls <= 4:
                    return {
                        "authority_reference": "membership-alpha-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": "principal-alpha",
                        "business_entity_id": "business-alpha",
                    }.get(key, default)
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "principal_id": "principal-admin",
                    "business_entity_id": "business-admin",
                }.get(key, default)

        record = membership()
        object.__setattr__(record, "__dict__", ToctouDict())
        source = NonProductionMembershipAuthoritySource([record])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ToctouDict.get_calls, 0)

    def test_object_new_missing_instance_fields_fail_closed(self):
        required_fields = (
            "authority_reference",
            "state",
            "principal_id",
            "business_entity_id",
        )
        values = {
            "authority_reference": "membership-alpha-authority",
            "state": AuthorityRecordState.ACTIVE,
            "principal_id": "principal-alpha",
            "business_entity_id": "business-alpha",
        }

        for missing in required_fields:
            with self.subTest(missing=missing):
                malformed = object.__new__(Membership)
                for name, value in values.items():
                    if name != missing:
                        object.__setattr__(malformed, name, value)
                source = NonProductionMembershipAuthoritySource([malformed])

                result = source.resolve_membership(
                    "principal-alpha",
                    "business-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_hostile_stored_string_subclasses_fail_closed(self):
        class HostileStoredStr(str):
            comparisons = 0
            strip_calls = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

            def strip(self):
                type(self).strip_calls += 1
                return self

        cases = (
            ("authority_reference", "membership-alpha-authority"),
            ("principal_id", "principal-alpha"),
            ("business_entity_id", "business-alpha"),
        )

        for field, value in cases:
            with self.subTest(field=field):
                HostileStoredStr.comparisons = 0
                HostileStoredStr.strip_calls = 0
                record = replace(membership(), **{field: HostileStoredStr(value)})
                source = NonProductionMembershipAuthoritySource([record])

                result = source.resolve_membership(
                    "principal-alpha",
                    "business-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(HostileStoredStr.comparisons, 0)
                self.assertEqual(HostileStoredStr.strip_calls, 0)

    def test_malformed_authority_fields_fail_closed(self):
        class OtherState(Enum):
            ACTIVE = "ACTIVE"

        cases = (
            ("authority_reference", None),
            ("authority_reference", ""),
            ("authority_reference", "   "),
            ("authority_reference", object()),
            ("state", None),
            ("state", "ACTIVE"),
            ("state", OtherState.ACTIVE),
            ("principal_id", None),
            ("principal_id", ""),
            ("principal_id", "   "),
            ("principal_id", object()),
            ("business_entity_id", None),
            ("business_entity_id", ""),
            ("business_entity_id", "   "),
            ("business_entity_id", object()),
        )

        for field, value in cases:
            with self.subTest(field=field, value=value):
                record = replace(membership(), **{field: value})
                source = NonProductionMembershipAuthoritySource([record])

                result = source.resolve_membership(
                    "principal-alpha",
                    "business-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_ambiguous_output_materializes_safe_exact_records(self):
        first = membership()
        second = membership()
        source = NonProductionMembershipAuthoritySource([first, second])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)
        for returned in result.records:
            self.assertIs(type(returned), Membership)
            self.assertIsNot(returned, first)
            self.assertIsNot(returned, second)
            self.assertEqual(
                returned.authority_reference,
                "membership-alpha-authority",
            )
            self.assertEqual(returned.principal_id, "principal-alpha")
            self.assertEqual(returned.business_entity_id, "business-alpha")

    def test_conflicting_output_materializes_safe_exact_records(self):
        original = membership()
        conflict = replace(
            membership(),
            authority_reference="membership-beta-authority",
        )
        source = NonProductionMembershipAuthoritySource([original, conflict])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(len(result.records), 2)
        for returned in result.records:
            self.assertIs(type(returned), Membership)
            self.assertIsNot(returned, original)
            self.assertIsNot(returned, conflict)

    def test_record_order_cannot_create_positive_authority_from_multiple_records(self):
        duplicate_a = membership()
        duplicate_b = membership()
        conflict_a = membership()
        conflict_b = replace(
            membership(),
            authority_reference="membership-beta-authority",
        )

        duplicate_forward = NonProductionMembershipAuthoritySource(
            [duplicate_a, duplicate_b]
        ).resolve_membership("principal-alpha", "business-alpha")
        duplicate_reverse = NonProductionMembershipAuthoritySource(
            [duplicate_b, duplicate_a]
        ).resolve_membership("principal-alpha", "business-alpha")
        conflict_forward = NonProductionMembershipAuthoritySource(
            [conflict_a, conflict_b]
        ).resolve_membership("principal-alpha", "business-alpha")
        conflict_reverse = NonProductionMembershipAuthoritySource(
            [conflict_b, conflict_a]
        ).resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(duplicate_forward.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(duplicate_reverse.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(conflict_forward.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(conflict_reverse.status, AuthorityLookupStatus.CONFLICTING)
        for result in (
            duplicate_forward,
            duplicate_reverse,
            conflict_forward,
            conflict_reverse,
        ):
            self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_source_captures_constructor_records_against_caller_list_mutation(self):
        records = [
            membership(
                principal_id="principal-original",
                business_entity_id="business-original",
            )
        ]
        source = NonProductionMembershipAuthoritySource(records)
        records.append(
            membership(
                principal_id="principal-original",
                business_entity_id="business-added",
            )
        )
        records.reverse()
        records.clear()

        original = source.resolve_membership(
            "principal-original",
            "business-original",
        )
        added = source.resolve_membership("principal-original", "business-added")

        self.assertEqual(original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(added.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(added.records, ())

    def test_source_consumes_generator_during_constructor_snapshot_creation(self):
        records = iter([membership()])
        source = NonProductionMembershipAuthoritySource(records)

        first = source.resolve_membership("principal-alpha", "business-alpha")
        second = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(second.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(first.records, second.records)
        self.assertIsNot(first.records[0], second.records[0])

    def test_original_record_mutation_after_construction_cannot_change_authority(self):
        original = membership()
        source = NonProductionMembershipAuthoritySource([original])
        before = source.resolve_membership("principal-alpha", "business-alpha")

        with self.assertRaises(FrozenInstanceError):
            original.principal_id = "principal-admin"
        object.__setattr__(original, "authority_reference", "attacker-authority")
        object.__setattr__(original, "state", AuthorityRecordState.REVOKED)
        object.__setattr__(original, "principal_id", "principal-admin")
        object.__setattr__(original, "business_entity_id", "business-admin")

        after_original = source.resolve_membership("principal-alpha", "business-alpha")
        after_principal = source.resolve_membership("principal-admin", "business-alpha")
        after_business = source.resolve_membership("principal-alpha", "business-admin")
        after_combined = source.resolve_membership("principal-admin", "business-admin")

        self.assertEqual(before.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_principal.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(after_business.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(after_combined.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(
            after_original.records[0].authority_reference,
            "membership-alpha-authority",
        )
        self.assertEqual(after_original.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(after_original.records[0].principal_id, "principal-alpha")
        self.assertEqual(after_original.records[0].business_entity_id, "business-alpha")

    def test_original_revoked_or_stale_mutation_cannot_reactivate_authority(self):
        cases = (
            (AuthorityRecordState.REVOKED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.STALE, AuthorityLookupStatus.STALE),
        )

        for original_state, expected_status in cases:
            with self.subTest(original_state=original_state):
                original = membership(state=original_state)
                source = NonProductionMembershipAuthoritySource([original])
                object.__setattr__(original, "state", AuthorityRecordState.ACTIVE)

                result = source.resolve_membership("principal-alpha", "business-alpha")

                self.assertEqual(result.status, expected_status)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_found_output_does_not_alias_internal_snapshot(self):
        original = membership()
        source = NonProductionMembershipAuthoritySource([original])

        first = source.resolve_membership("principal-alpha", "business-alpha")
        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        returned = first.records[0]
        self.assertIs(type(returned), Membership)
        self.assertIsNot(returned, original)
        self.assertIsNot(returned, source._memberships[0])

        mutate_to_forged_membership(returned)

        original_pair = source.resolve_membership("principal-alpha", "business-alpha")
        forged_principal = source.resolve_membership("principal-admin", "business-alpha")
        forged_business = source.resolve_membership("principal-alpha", "business-admin")
        forged_pair = source.resolve_membership("principal-admin", "business-admin")

        self.assertEqual(original_pair.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(forged_principal.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(forged_business.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(forged_pair.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(
            original_pair.records[0].authority_reference,
            "membership-alpha-authority",
        )
        self.assertEqual(original_pair.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(original_pair.records[0].principal_id, "principal-alpha")
        self.assertEqual(original_pair.records[0].business_entity_id, "business-alpha")

    def test_ambiguous_output_does_not_alias_internal_snapshots(self):
        source = NonProductionMembershipAuthoritySource([membership(), membership()])

        first = source.resolve_membership("principal-alpha", "business-alpha")
        self.assertEqual(first.status, AuthorityLookupStatus.AMBIGUOUS)

        for returned, internal in zip(first.records, source._memberships):
            self.assertIs(type(returned), Membership)
            self.assertIsNot(returned, internal)
            mutate_to_forged_membership(returned)

        second = source.resolve_membership("principal-alpha", "business-alpha")
        forged = source.resolve_membership("principal-admin", "business-admin")

        self.assertEqual(second.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(forged.status, AuthorityLookupStatus.NOT_FOUND)
        for returned, internal in zip(second.records, source._memberships):
            self.assertEqual(returned, membership())
            self.assertIsNot(returned, internal)

    def test_conflicting_output_does_not_alias_internal_snapshots(self):
        conflict = replace(
            membership(),
            authority_reference="membership-beta-authority",
        )
        source = NonProductionMembershipAuthoritySource([membership(), conflict])

        first = source.resolve_membership("principal-alpha", "business-alpha")
        self.assertEqual(first.status, AuthorityLookupStatus.CONFLICTING)

        for returned, internal in zip(first.records, source._memberships):
            self.assertIs(type(returned), Membership)
            self.assertIsNot(returned, internal)
            mutate_to_forged_membership(returned)

        second = source.resolve_membership("principal-alpha", "business-alpha")
        forged = source.resolve_membership("principal-admin", "business-admin")

        self.assertEqual(second.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(forged.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(
            {record.authority_reference for record in second.records},
            {"membership-alpha-authority", "membership-beta-authority"},
        )
        for returned, internal in zip(second.records, source._memberships):
            self.assertIsNot(returned, internal)

    def test_valid_record_plus_malformed_evidence_fails_closed_globally(self):
        malformed = object.__new__(Membership)
        object.__setattr__(malformed, "authority_reference", "malformed")
        source = NonProductionMembershipAuthoritySource([membership(), malformed])
        reverse_source = NonProductionMembershipAuthoritySource([malformed, membership()])

        result = source.resolve_membership("principal-alpha", "business-alpha")
        reverse = reverse_source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(reverse.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(reverse.records, ())

    def test_malformed_unrelated_evidence_still_globally_poisons_source(self):
        malformed = object.__new__(Membership)
        object.__setattr__(malformed, "authority_reference", "malformed")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(malformed, "principal_id", "principal-unrelated")
        source = NonProductionMembershipAuthoritySource([membership(), malformed])

        result = source.resolve_membership("principal-alpha", "business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_membership_alone_does_not_create_downstream_authority(self):
        source = NonProductionMembershipAuthoritySource([membership()])
        evaluator = TrustedAuthorizationEvaluator(source)

        result = evaluator.evaluate(request())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertIn(
            "principal_mapping:UNSUPPORTED",
            result.audit_evidence.authority_inputs,
        )

    def test_unsupported_authority_categories_return_no_positive_authority(self):
        source = NonProductionMembershipAuthoritySource([membership()])
        lookups = (
            source.resolve_principal_mapping("membership-source-test", "subject-alpha"),
            source.resolve_resource("resource-alpha"),
            source.resolve_business_entity("business-alpha"),
            source.resolve_entitlement(
                "principal-alpha",
                "business-alpha",
                "resource-alpha",
                RequestedAction.VIEW,
            ),
        )

        for lookup in lookups:
            with self.subTest(lookup=lookup):
                self.assertEqual(lookup.status, AuthorityLookupStatus.UNSUPPORTED)
                self.assertEqual(lookup.records, ())

    def test_source_exposes_no_authority_management_surface(self):
        source = NonProductionMembershipAuthoritySource([membership()])
        forbidden_names = (
            "add_membership",
            "create_membership",
            "update_membership",
            "delete_membership",
            "remove_membership",
            "revoke_membership",
            "restore_membership",
            "reactivate_membership",
            "assign_membership",
            "mutate_membership",
            "save_membership",
            "write_membership",
            "upsert_membership",
        )

        for name in forbidden_names:
            with self.subTest(name=name):
                self.assertFalse(hasattr(source, name))

    def test_source_module_exposes_no_final_decision_surface(self):
        forbidden_names = (
            "AuthorizationDecision",
            "AuthorizationResult",
            "ALLOW",
            "DENY",
            "_allow",
            "_deny",
            "ReasonCategory",
        )

        for name in forbidden_names:
            with self.subTest(name=name):
                self.assertFalse(hasattr(membership_source_module, name))

    def test_source_is_not_exported_from_package_root(self):
        self.assertFalse(
            hasattr(
                trusted_authorization_package,
                "NonProductionMembershipAuthoritySource",
            )
        )

    def test_source_keeps_only_constructor_supplied_snapshots(self):
        first = membership()
        second = replace(first, authority_reference="membership-beta-authority")
        source = NonProductionMembershipAuthoritySource([first, second])

        self.assertEqual(
            source.__slots__,
            ("_has_malformed_evidence", "_memberships"),
        )
        self.assertEqual(source._memberships, (first, second))
        self.assertIsNot(source._memberships[0], first)
        self.assertIsNot(source._memberships[1], second)


if __name__ == "__main__":
    unittest.main()
