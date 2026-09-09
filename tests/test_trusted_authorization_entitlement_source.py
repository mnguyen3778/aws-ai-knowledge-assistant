import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization as trusted_authorization_package  # noqa: E402
import trusted_authorization.entitlement_source as entitlement_source_module  # noqa: E402
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
from trusted_authorization.entitlement_source import (  # noqa: E402
    NonProductionEntitlementAuthoritySource,
)
from trusted_authorization.models import Entitlement  # noqa: E402


P1 = "principal-alpha"
P2 = "principal-beta"
B1 = "business-alpha"
B2 = "business-beta"
R1 = "resource-alpha"
R2 = "resource-beta"
A1 = RequestedAction.VIEW
A2 = RequestedAction.DOWNLOAD

SUBJECT = TrustedSubjectEvidence(
    provider="entitlement-source-test",
    subject="subject-alpha",
    verified=True,
)


def entitlement(
    authority_reference="entitlement-alpha-authority",
    state=AuthorityRecordState.ACTIVE,
    principal_id=P1,
    business_entity_id=B1,
    resource_id=R1,
    action=A1,
):
    return Entitlement(
        authority_reference=authority_reference,
        state=state,
        principal_id=principal_id,
        business_entity_id=business_entity_id,
        resource_id=resource_id,
        action=action,
    )


def set_entitlement_fields(record, **overrides):
    values = {
        "authority_reference": "entitlement-alpha-authority",
        "state": AuthorityRecordState.ACTIVE,
        "principal_id": P1,
        "business_entity_id": B1,
        "resource_id": R1,
        "action": A1,
    }
    values.update(overrides)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def mutate_to_forged_entitlement(record):
    object.__setattr__(record, "authority_reference", "attacker-authority")
    object.__setattr__(record, "state", AuthorityRecordState.REVOKED)
    object.__setattr__(record, "principal_id", "principal-admin")
    object.__setattr__(record, "business_entity_id", "business-admin")
    object.__setattr__(record, "resource_id", "resource-admin")
    object.__setattr__(record, "action", RequestedAction.SUBMIT)


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
        resource_reference=R1,
        requested_action=A1,
        governed_version_context=governed_context(),
        correlation_id="entitlement-source-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


class NonProductionEntitlementAuthoritySourceTests(unittest.TestCase):
    def test_known_active_entitlement_resolves_expected_tuple(self):
        expected = entitlement()
        source = NonProductionEntitlementAuthoritySource([expected])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records, (expected,))
        self.assertIs(type(result.records[0]), Entitlement)
        self.assertIsNot(result.records[0], expected)
        self.assertIsNot(result.records[0], source._entitlements[0])
        self.assertEqual(
            result.records[0].authority_reference,
            "entitlement-alpha-authority",
        )
        self.assertEqual(result.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(result.records[0].principal_id, P1)
        self.assertEqual(result.records[0].business_entity_id, B1)
        self.assertEqual(result.records[0].resource_id, R1)
        self.assertIs(result.records[0].action, A1)

    def test_unknown_tuple_and_empty_source_return_no_authority(self):
        populated = NonProductionEntitlementAuthoritySource([entitlement()])
        empty = NonProductionEntitlementAuthoritySource()
        cases = (
            populated.resolve_entitlement(P2, B1, R1, A1),
            populated.resolve_entitlement(P1, B2, R1, A1),
            populated.resolve_entitlement(P1, B1, R2, A1),
            populated.resolve_entitlement(P1, B1, R1, A2),
            empty.resolve_entitlement(P1, B1, R1, A1),
        )

        for result in cases:
            with self.subTest(result=result):
                self.assertEqual(result.status, AuthorityLookupStatus.NOT_FOUND)
                self.assertEqual(result.records, ())

    def test_malformed_principal_lookup_inputs_fail_closed_before_matching(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        for label, lookup, instrumented, counter in _hostile_identifier_inputs(P1):
            with self.subTest(case=label):
                if instrumented is not None:
                    setattr(instrumented, counter, 0)

                result = source.resolve_entitlement(lookup, B1, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                if instrumented is not None:
                    self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_business_entity_lookup_inputs_fail_closed_before_matching(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        for label, lookup, instrumented, counter in _hostile_identifier_inputs(B1):
            with self.subTest(case=label):
                if instrumented is not None:
                    setattr(instrumented, counter, 0)

                result = source.resolve_entitlement(P1, lookup, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                if instrumented is not None:
                    self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_resource_lookup_inputs_fail_closed_before_matching(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        for label, lookup, instrumented, counter in _hostile_identifier_inputs(R1):
            with self.subTest(case=label):
                if instrumented is not None:
                    setattr(instrumented, counter, 0)

                result = source.resolve_entitlement(P1, B1, lookup, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                if instrumented is not None:
                    self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_action_lookup_inputs_fail_closed_before_matching(self):
        class OtherAction(Enum):
            VIEW = "VIEW"

        class HostileAction:
            comparisons = 0
            string_conversions = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

            def __str__(self):
                type(self).string_conversions += 1
                return "VIEW"

        source = NonProductionEntitlementAuthoritySource([entitlement()])
        cases = (
            None,
            "VIEW",
            "view",
            "*",
            "ALL",
            1,
            object(),
            OtherAction.VIEW,
            HostileAction(),
        )

        for lookup in cases:
            with self.subTest(lookup=lookup):
                HostileAction.comparisons = 0
                HostileAction.string_conversions = 0

                result = source.resolve_entitlement(P1, B1, R1, lookup)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(HostileAction.comparisons, 0)
                self.assertEqual(HostileAction.string_conversions, 0)

    def test_multiple_malformed_lookup_dimensions_fail_closed(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        cases = (
            (None, None, R1, A1),
            (P1, None, None, A1),
            (P1, B1, None, None),
            (None, None, None, A1),
            (None, None, None, None),
        )

        for lookup in cases:
            with self.subTest(lookup=lookup):
                result = source.resolve_entitlement(*lookup)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_exact_tuple_matching_prevents_single_dimension_forgery(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        cases = (
            (P1, B1, R1, A1, AuthorityLookupStatus.FOUND),
            (P2, B1, R1, A1, AuthorityLookupStatus.NOT_FOUND),
            (P1, B2, R1, A1, AuthorityLookupStatus.NOT_FOUND),
            (P1, B1, R2, A1, AuthorityLookupStatus.NOT_FOUND),
            (P1, B1, R1, A2, AuthorityLookupStatus.NOT_FOUND),
        )

        for principal_id, business_id, resource_id, action, expected in cases:
            with self.subTest(
                principal_id=principal_id,
                business_id=business_id,
                resource_id=resource_id,
                action=action,
            ):
                result = source.resolve_entitlement(
                    principal_id,
                    business_id,
                    resource_id,
                    action,
                )

                self.assertEqual(result.status, expected)

    def test_multi_dimensional_substitutions_cannot_forge_permission(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        forged = (
            (P2, B2, R1, A1),
            (P2, B1, R2, A1),
            (P2, B1, R1, A2),
            (P1, B2, R2, A1),
            (P1, B2, R1, A2),
            (P1, B1, R2, A2),
            (P2, B2, R2, A2),
        )

        for lookup in forged:
            with self.subTest(lookup=lookup):
                result = source.resolve_entitlement(*lookup)

                self.assertEqual(result.status, AuthorityLookupStatus.NOT_FOUND)
                self.assertEqual(result.records, ())

    def test_complete_action_isolation_matrix_has_no_action_inheritance(self):
        for source_action in RequestedAction:
            with self.subTest(source_action=source_action):
                source = NonProductionEntitlementAuthoritySource(
                    [entitlement(action=source_action)]
                )
                found = source.resolve_entitlement(P1, B1, R1, source_action)
                self.assertEqual(found.status, AuthorityLookupStatus.FOUND)

                for lookup_action in RequestedAction:
                    if lookup_action is source_action:
                        continue

                    result = source.resolve_entitlement(P1, B1, R1, lookup_action)

                    self.assertEqual(result.status, AuthorityLookupStatus.NOT_FOUND)
                    self.assertEqual(result.records, ())

    def test_unrelated_tuples_do_not_contaminate_exact_tuple_classification(self):
        records = (
            entitlement(),
            entitlement(action=RequestedAction.DOWNLOAD),
            entitlement(resource_id=R2),
            entitlement(business_entity_id=B2),
            entitlement(principal_id=P2),
        )
        source = NonProductionEntitlementAuthoritySource(records)

        original = source.resolve_entitlement(P1, B1, R1, A1)
        download = source.resolve_entitlement(P1, B1, R1, RequestedAction.DOWNLOAD)
        other_resource = source.resolve_entitlement(P1, B1, R2, A1)
        other_business = source.resolve_entitlement(P1, B2, R1, A1)
        other_principal = source.resolve_entitlement(P2, B1, R1, A1)

        for result in (
            original,
            download,
            other_resource,
            other_business,
            other_principal,
        ):
            with self.subTest(result=result):
                self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(len(result.records), 1)

        removed_original = NonProductionEntitlementAuthoritySource(records[1:])
        self.assertEqual(
            removed_original.resolve_entitlement(P1, B1, R1, A1).status,
            AuthorityLookupStatus.NOT_FOUND,
        )
        self.assertEqual(
            removed_original.resolve_entitlement(
                P1,
                B1,
                R1,
                RequestedAction.DOWNLOAD,
            ).status,
            AuthorityLookupStatus.FOUND,
        )

    def test_non_current_entitlement_states_return_no_positive_authority(self):
        cases = (
            (AuthorityRecordState.ACTIVE, AuthorityLookupStatus.FOUND),
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
                source = NonProductionEntitlementAuthoritySource(
                    [entitlement(state=state)]
                )

                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, expected_status)
                if state is not AuthorityRecordState.ACTIVE:
                    self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_conflicting_entitlements_fail_closed(self):
        cases = (
            (
                "authority_reference",
                {"authority_reference": "entitlement-beta-authority"},
            ),
            ("state", {"state": AuthorityRecordState.STALE}),
        )

        for name, overrides in cases:
            with self.subTest(name=name):
                source = NonProductionEntitlementAuthoritySource(
                    [entitlement(), entitlement(**overrides)]
                )

                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
                self.assertEqual(len(result.records), 2)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_duplicate_entitlements_fail_closed_without_deduplication(self):
        source = NonProductionEntitlementAuthoritySource(
            [entitlement(), entitlement()]
        )

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)
        self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_record_order_cannot_create_positive_authority_from_multiple_records(self):
        duplicate_a = entitlement()
        duplicate_b = entitlement()
        conflict_a = entitlement()
        conflict_b = replace(
            entitlement(),
            authority_reference="entitlement-beta-authority",
        )

        duplicate_forward = NonProductionEntitlementAuthoritySource(
            [duplicate_a, duplicate_b]
        ).resolve_entitlement(P1, B1, R1, A1)
        duplicate_reverse = NonProductionEntitlementAuthoritySource(
            [duplicate_b, duplicate_a]
        ).resolve_entitlement(P1, B1, R1, A1)
        conflict_forward = NonProductionEntitlementAuthoritySource(
            [conflict_a, conflict_b]
        ).resolve_entitlement(P1, B1, R1, A1)
        conflict_reverse = NonProductionEntitlementAuthoritySource(
            [conflict_b, conflict_a]
        ).resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(duplicate_forward.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(duplicate_reverse.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(conflict_forward.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(conflict_reverse.status, AuthorityLookupStatus.CONFLICTING)

    def test_source_captures_constructor_records_against_caller_list_mutation(self):
        records = [entitlement()]
        source = NonProductionEntitlementAuthoritySource(records)
        records.append(
            entitlement(
                principal_id=P2,
                business_entity_id=B2,
                resource_id=R2,
                action=A2,
            )
        )
        records.reverse()
        records[0] = entitlement(resource_id="resource-replaced")
        records.clear()

        original = source.resolve_entitlement(P1, B1, R1, A1)
        forged = source.resolve_entitlement(P2, B2, R2, A2)

        self.assertEqual(original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(forged.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(forged.records, ())

    def test_source_consumes_generator_during_constructor_snapshot_creation(self):
        source = NonProductionEntitlementAuthoritySource(iter([entitlement()]))

        first = source.resolve_entitlement(P1, B1, R1, A1)
        second = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(second.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(first.records, second.records)
        self.assertIsNot(first.records[0], second.records[0])

    def test_original_record_mutation_after_construction_cannot_change_authority(self):
        original = entitlement()
        source = NonProductionEntitlementAuthoritySource([original])
        before = source.resolve_entitlement(P1, B1, R1, A1)

        with self.assertRaises(FrozenInstanceError):
            original.resource_id = "resource-admin"
        mutate_to_forged_entitlement(original)

        after_original = source.resolve_entitlement(P1, B1, R1, A1)
        forged = source.resolve_entitlement(
            "principal-admin",
            "business-admin",
            "resource-admin",
            RequestedAction.SUBMIT,
        )

        self.assertEqual(before.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(forged.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(after_original.records[0], entitlement())

    def test_original_revoked_or_stale_mutation_cannot_reactivate_authority(self):
        cases = (
            (AuthorityRecordState.REVOKED, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.INACTIVE, AuthorityLookupStatus.NOT_FOUND),
            (AuthorityRecordState.STALE, AuthorityLookupStatus.STALE),
        )

        for original_state, expected_status in cases:
            with self.subTest(original_state=original_state):
                original = entitlement(state=original_state)
                source = NonProductionEntitlementAuthoritySource([original])
                object.__setattr__(original, "state", AuthorityRecordState.ACTIVE)

                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, expected_status)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_found_output_does_not_alias_internal_snapshot(self):
        original = entitlement()
        source = NonProductionEntitlementAuthoritySource([original])

        first = source.resolve_entitlement(P1, B1, R1, A1)
        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        returned = first.records[0]
        self.assertIs(type(returned), Entitlement)
        self.assertIsNot(returned, original)
        self.assertIsNot(returned, source._entitlements[0])

        mutate_to_forged_entitlement(returned)

        original_tuple = source.resolve_entitlement(P1, B1, R1, A1)
        forged_tuple = source.resolve_entitlement(
            "principal-admin",
            "business-admin",
            "resource-admin",
            RequestedAction.SUBMIT,
        )

        self.assertEqual(original_tuple.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(original_tuple.records[0], entitlement())
        self.assertEqual(forged_tuple.status, AuthorityLookupStatus.NOT_FOUND)

    def test_repeated_found_output_isolated_from_returned_mutation(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        first = source.resolve_entitlement(P1, B1, R1, A1)
        second = source.resolve_entitlement(P1, B1, R1, A1)
        third = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertIsNot(first.records[0], second.records[0])
        self.assertIsNot(second.records[0], third.records[0])

        mutate_to_forged_entitlement(first.records[0])

        after = source.resolve_entitlement(P1, B1, R1, A1)
        self.assertEqual(after.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after.records[0], entitlement())
        self.assertEqual(second.records[0], entitlement())
        self.assertEqual(third.records[0], entitlement())

    def test_ambiguous_output_does_not_alias_internal_snapshots(self):
        source = NonProductionEntitlementAuthoritySource(
            [entitlement(), entitlement()]
        )

        first = source.resolve_entitlement(P1, B1, R1, A1)
        self.assertEqual(first.status, AuthorityLookupStatus.AMBIGUOUS)

        for returned, internal in zip(first.records, source._entitlements):
            self.assertIs(type(returned), Entitlement)
            self.assertIsNot(returned, internal)
            mutate_to_forged_entitlement(returned)

        second = source.resolve_entitlement(P1, B1, R1, A1)
        forged = source.resolve_entitlement(
            "principal-admin",
            "business-admin",
            "resource-admin",
            RequestedAction.SUBMIT,
        )

        self.assertEqual(second.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(forged.status, AuthorityLookupStatus.NOT_FOUND)
        for returned, internal in zip(second.records, source._entitlements):
            self.assertEqual(returned, entitlement())
            self.assertIsNot(returned, internal)

    def test_repeated_ambiguous_outputs_are_distinct(self):
        source = NonProductionEntitlementAuthoritySource(
            [entitlement(), entitlement()]
        )

        first = source.resolve_entitlement(P1, B1, R1, A1)
        second = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(first.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(second.status, AuthorityLookupStatus.AMBIGUOUS)
        for first_record, second_record in zip(first.records, second.records):
            self.assertIsNot(first_record, second_record)

    def test_conflicting_output_does_not_alias_internal_snapshots(self):
        conflict = replace(
            entitlement(),
            authority_reference="entitlement-beta-authority",
        )
        source = NonProductionEntitlementAuthoritySource([entitlement(), conflict])

        first = source.resolve_entitlement(P1, B1, R1, A1)
        self.assertEqual(first.status, AuthorityLookupStatus.CONFLICTING)

        for returned, internal in zip(first.records, source._entitlements):
            self.assertIs(type(returned), Entitlement)
            self.assertIsNot(returned, internal)
            object.__setattr__(returned, "authority_reference", "equivalent")

        second = source.resolve_entitlement(P1, B1, R1, A1)
        self.assertEqual(second.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(
            {record.authority_reference for record in second.records},
            {"entitlement-alpha-authority", "entitlement-beta-authority"},
        )

    def test_repeated_conflicting_outputs_are_distinct(self):
        conflict = replace(
            entitlement(),
            authority_reference="entitlement-beta-authority",
        )
        source = NonProductionEntitlementAuthoritySource([entitlement(), conflict])

        first = source.resolve_entitlement(P1, B1, R1, A1)
        second = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(first.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(second.status, AuthorityLookupStatus.CONFLICTING)
        for first_record, second_record in zip(first.records, second.records):
            self.assertIsNot(first_record, second_record)

    def test_malformed_entitlement_evidence_fails_closed(self):
        malformed = object.__new__(Entitlement)
        object.__setattr__(malformed, "authority_reference", "entitlement-authority")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(malformed, "principal_id", P1)
        object.__setattr__(malformed, "business_entity_id", B1)
        object.__setattr__(malformed, "resource_id", R1)
        source = NonProductionEntitlementAuthoritySource([malformed])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_object_new_missing_instance_fields_fail_closed(self):
        required_fields = (
            "authority_reference",
            "state",
            "principal_id",
            "business_entity_id",
            "resource_id",
            "action",
        )
        values = {
            "authority_reference": "entitlement-alpha-authority",
            "state": AuthorityRecordState.ACTIVE,
            "principal_id": P1,
            "business_entity_id": B1,
            "resource_id": R1,
            "action": A1,
        }

        for missing in required_fields:
            with self.subTest(missing=missing):
                malformed = object.__new__(Entitlement)
                for name, value in values.items():
                    if name != missing:
                        object.__setattr__(malformed, name, value)
                source = NonProductionEntitlementAuthoritySource([malformed])

                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_empty_and_multi_missing_partial_instances_fail_closed(self):
        empty = object.__new__(Entitlement)
        partial = object.__new__(Entitlement)
        object.__setattr__(partial, "authority_reference", "entitlement")
        object.__setattr__(partial, "principal_id", P1)

        for record in (empty, partial):
            with self.subTest(record=record):
                source = NonProductionEntitlementAuthoritySource([record])
                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_malformed_authority_fields_fail_closed(self):
        class OtherState(Enum):
            ACTIVE = "ACTIVE"

        class OtherAction(Enum):
            VIEW = "VIEW"

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
            ("resource_id", None),
            ("resource_id", ""),
            ("resource_id", "   "),
            ("resource_id", object()),
            ("action", None),
            ("action", "VIEW"),
            ("action", OtherAction.VIEW),
            ("action", object()),
        )

        for field, value in cases:
            with self.subTest(field=field, value=value):
                record = replace(entitlement(), **{field: value})
                source = NonProductionEntitlementAuthoritySource([record])

                result = source.resolve_entitlement(P1, B1, R1, A1)

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
            ("authority_reference", "entitlement-alpha-authority"),
            ("principal_id", P1),
            ("business_entity_id", B1),
            ("resource_id", R1),
        )

        for field, value in cases:
            with self.subTest(field=field):
                HostileStoredStr.comparisons = 0
                HostileStoredStr.strip_calls = 0
                record = replace(entitlement(), **{field: HostileStoredStr(value)})
                source = NonProductionEntitlementAuthoritySource([record])

                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(HostileStoredStr.comparisons, 0)
                self.assertEqual(HostileStoredStr.strip_calls, 0)

    def test_benign_entitlement_subclass_fails_closed(self):
        class BenignEntitlement(Entitlement):
            pass

        source = NonProductionEntitlementAuthoritySource(
            [
                BenignEntitlement(
                    "entitlement-alpha-authority",
                    AuthorityRecordState.ACTIVE,
                    P1,
                    B1,
                    R1,
                    A1,
                )
            ]
        )

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_entitlement_subclass_field_spoofing_fails_before_reads(self):
        class SpoofedEntitlement(Entitlement):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in _AUTHORITY_FIELDS:
                    type(self).authority_field_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "principal_id": P1,
                        "business_entity_id": B1,
                        "resource_id": R1,
                        "action": A1,
                    }[name]
                return object.__getattribute__(self, name)

        record = set_entitlement_fields(
            object.__new__(SpoofedEntitlement),
            state=AuthorityRecordState.REVOKED,
            principal_id=P2,
            business_entity_id=B2,
            resource_id=R2,
            action=A2,
        )
        source = NonProductionEntitlementAuthoritySource([record])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(SpoofedEntitlement.authority_field_reads, 0)

    def test_entitlement_subclass_raising_getattribute_fails_closed(self):
        class RaisingEntitlement(Entitlement):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in _AUTHORITY_FIELDS:
                    type(self).authority_field_reads += 1
                    raise RuntimeError("field unavailable")
                return object.__getattribute__(self, name)

        record = set_entitlement_fields(object.__new__(RaisingEntitlement))
        source = NonProductionEntitlementAuthoritySource([record])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(RaisingEntitlement.authority_field_reads, 0)

    def test_getattr_subclass_fails_closed_before_dynamic_fallback(self):
        class GetattrEntitlement(Entitlement):
            getattr_calls = 0

            def __getattr__(self, name):
                type(self).getattr_calls += 1
                return "forged"

        record = set_entitlement_fields(object.__new__(GetattrEntitlement))
        source = NonProductionEntitlementAuthoritySource([record])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(GetattrEntitlement.getattr_calls, 0)

    def test_property_and_descriptor_subclasses_fail_closed_before_reads(self):
        class PropertyEntitlement(Entitlement):
            property_reads = 0

            @property
            def resource_id(self):
                type(self).property_reads += 1
                return R1

        class Descriptor:
            reads = 0

            def __get__(self, instance, owner):
                type(self).reads += 1
                return A1

        class DescriptorEntitlement(Entitlement):
            action = Descriptor()

        for cls, counter_owner, counter in (
            (PropertyEntitlement, PropertyEntitlement, "property_reads"),
            (DescriptorEntitlement, Descriptor, "reads"),
        ):
            with self.subTest(cls=cls):
                setattr(counter_owner, counter, 0)
                record = object.__new__(cls)
                source = NonProductionEntitlementAuthoritySource([record])

                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(counter_owner, counter), 0)

    def test_hostile_dict_subclasses_fail_closed_without_mapping_callbacks(self):
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
                return super().get(key, default)

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

        record = object.__new__(Entitlement)
        object.__setattr__(
            record,
            "__dict__",
            HostileDict(
                {
                    "authority_reference": "entitlement-alpha-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "principal_id": P1,
                    "business_entity_id": B1,
                    "resource_id": R1,
                    "action": A1,
                }
            ),
        )
        source = NonProductionEntitlementAuthoritySource([record])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(HostileDict.get_calls, 0)
        self.assertEqual(HostileDict.getitem_calls, 0)
        self.assertEqual(HostileDict.contains_calls, 0)
        self.assertEqual(HostileDict.iter_calls, 0)
        self.assertEqual(HostileDict.keys_calls, 0)
        self.assertEqual(HostileDict.items_calls, 0)
        self.assertEqual(HostileDict.values_calls, 0)

    def test_subclass_dict_property_descriptor_and_override_fail_closed(self):
        class DictPropertyEntitlement(Entitlement):
            dict_reads = 0

            @property
            def __dict__(self):
                type(self).dict_reads += 1
                return {}

        class DictDescriptor:
            reads = 0

            def __get__(self, instance, owner):
                type(self).reads += 1
                return {}

        class DictDescriptorEntitlement(Entitlement):
            __dict__ = DictDescriptor()

        class DictGetattributeEntitlement(Entitlement):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {}
                return object.__getattribute__(self, name)

        cases = (
            (DictPropertyEntitlement, DictPropertyEntitlement, "dict_reads"),
            (DictDescriptorEntitlement, DictDescriptor, "reads"),
            (DictGetattributeEntitlement, DictGetattributeEntitlement, "dict_reads"),
        )
        for cls, counter_owner, counter in cases:
            with self.subTest(cls=cls):
                setattr(counter_owner, counter, 0)
                record = set_entitlement_fields(object.__new__(cls))
                source = NonProductionEntitlementAuthoritySource([record])

                result = source.resolve_entitlement(P1, B1, R1, A1)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(counter_owner, counter), 0)

    def test_toctou_mapping_storage_is_rejected_before_mutating_reads(self):
        class ToctouDict(dict):
            getitem_calls = 0

            def __getitem__(self, key):
                type(self).getitem_calls += 1
                if key == "state":
                    return AuthorityRecordState.ACTIVE
                return super().__getitem__(key)

        record = object.__new__(Entitlement)
        object.__setattr__(
            record,
            "__dict__",
            ToctouDict(
                {
                    "authority_reference": "entitlement-alpha-authority",
                    "state": AuthorityRecordState.REVOKED,
                    "principal_id": P1,
                    "business_entity_id": B1,
                    "resource_id": R1,
                    "action": A1,
                }
            ),
        )
        source = NonProductionEntitlementAuthoritySource([record])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ToctouDict.getitem_calls, 0)

    def test_valid_record_plus_malformed_evidence_fails_closed_globally(self):
        malformed = object.__new__(Entitlement)
        object.__setattr__(malformed, "authority_reference", "malformed")
        source = NonProductionEntitlementAuthoritySource(
            [entitlement(), malformed]
        )
        reverse = NonProductionEntitlementAuthoritySource(
            [malformed, entitlement()]
        )

        result = source.resolve_entitlement(P1, B1, R1, A1)
        reverse_result = reverse.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(reverse_result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(reverse_result.records, ())

    def test_malformed_unrelated_evidence_still_globally_poisons_source(self):
        malformed = object.__new__(Entitlement)
        object.__setattr__(malformed, "authority_reference", "malformed")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(malformed, "principal_id", P2)
        object.__setattr__(malformed, "business_entity_id", B2)
        object.__setattr__(malformed, "resource_id", R2)
        source = NonProductionEntitlementAuthoritySource([entitlement(), malformed])

        result = source.resolve_entitlement(P1, B1, R1, A1)

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_entitlement_source_alone_does_not_create_upstream_authority(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        evaluator = TrustedAuthorizationEvaluator(source)

        result = evaluator.evaluate(request())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertIn(
            "principal_mapping:UNSUPPORTED",
            result.audit_evidence.authority_inputs,
        )

    def test_unsupported_authority_categories_return_no_positive_authority(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        lookups = (
            source.resolve_principal_mapping("provider", "subject"),
            source.resolve_resource("resource-ref"),
            source.resolve_business_entity(B1),
            source.resolve_membership(P1, B1),
        )

        for lookup in lookups:
            with self.subTest(lookup=lookup):
                self.assertEqual(lookup.status, AuthorityLookupStatus.UNSUPPORTED)
                self.assertEqual(lookup.records, ())

    def test_source_exposes_no_authority_management_surface(self):
        source = NonProductionEntitlementAuthoritySource([entitlement()])
        forbidden_names = (
            "add_entitlement",
            "create_entitlement",
            "update_entitlement",
            "delete_entitlement",
            "remove_entitlement",
            "revoke_entitlement",
            "restore_entitlement",
            "reactivate_entitlement",
            "assign_entitlement",
            "mutate_entitlement",
            "save_entitlement",
            "write_entitlement",
            "upsert_entitlement",
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
                self.assertFalse(hasattr(entitlement_source_module, name))

    def test_source_is_not_exported_from_package_root(self):
        self.assertFalse(
            hasattr(
                trusted_authorization_package,
                "NonProductionEntitlementAuthoritySource",
            )
        )

    def test_source_keeps_only_constructor_supplied_snapshots(self):
        first = entitlement()
        second = replace(first, authority_reference="entitlement-beta-authority")
        source = NonProductionEntitlementAuthoritySource([first, second])

        self.assertEqual(
            source.__slots__,
            ("_entitlements", "_has_malformed_evidence"),
        )
        self.assertEqual(source._entitlements, (first, second))
        self.assertIsNot(source._entitlements[0], first)
        self.assertIsNot(source._entitlements[1], second)


_AUTHORITY_FIELDS = (
    "authority_reference",
    "state",
    "principal_id",
    "business_entity_id",
    "resource_id",
    "action",
)


def _hostile_identifier_inputs(valid_text):
    class Hostile:
        comparisons = 0
        string_conversions = 0

        def __eq__(self, other):
            type(self).comparisons += 1
            return True

        def __str__(self):
            type(self).string_conversions += 1
            return valid_text

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

    return (
        ("none", None, None, None),
        ("integer", 1, None, None),
        ("object", object(), None, None),
        ("hostile object", Hostile(), Hostile, "comparisons"),
        ("empty", "", None, None),
        ("whitespace", "   ", None, None),
        ("str subclass", HostileStr(valid_text), HostileStr, "comparisons"),
        (
            "hostile strip",
            HostileStripStr(valid_text),
            HostileStripStr,
            "strip_calls",
        ),
        (
            "raising strip",
            RaisingStripStr(valid_text),
            RaisingStripStr,
            "strip_calls",
        ),
    )


if __name__ == "__main__":
    unittest.main()
