import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization as trusted_authorization_package  # noqa: E402
import trusted_authorization.business_entity_source as business_entity_source_module  # noqa: E402
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
from trusted_authorization.business_entity_source import (  # noqa: E402
    NonProductionBusinessEntityAuthoritySource,
)
from trusted_authorization.models import BusinessEntity  # noqa: E402


SUBJECT = TrustedSubjectEvidence(
    provider="business-source-test",
    subject="subject-alpha",
    verified=True,
)


def business_entity(
    authority_reference="business-alpha-authority",
    state=AuthorityRecordState.ACTIVE,
    business_entity_id="business-alpha",
):
    return BusinessEntity(
        authority_reference=authority_reference,
        state=state,
        business_entity_id=business_entity_id,
    )


def set_business_entity_fields(record, **overrides):
    values = {
        "authority_reference": "business-alpha-authority",
        "state": AuthorityRecordState.ACTIVE,
        "business_entity_id": "business-alpha",
    }
    values.update(overrides)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


def mutate_to_forged_business_entity(record):
    object.__setattr__(record, "authority_reference", "attacker-authority")
    object.__setattr__(record, "state", AuthorityRecordState.REVOKED)
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
        correlation_id="business-entity-source-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


class NonProductionBusinessEntityAuthoritySourceTests(unittest.TestCase):
    def test_known_active_business_entity_resolves_expected_identity(self):
        expected = business_entity()
        source = NonProductionBusinessEntityAuthoritySource([expected])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records, (expected,))
        self.assertIs(type(result.records[0]), BusinessEntity)
        self.assertIsNot(result.records[0], expected)
        self.assertIsNot(result.records[0], source._business_entities[0])
        self.assertEqual(
            result.records[0].authority_reference,
            "business-alpha-authority",
        )
        self.assertEqual(result.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(result.records[0].business_entity_id, "business-alpha")

    def test_unknown_business_entity_and_empty_source_return_no_authority(self):
        populated = NonProductionBusinessEntityAuthoritySource([business_entity()])
        empty = NonProductionBusinessEntityAuthoritySource()

        unknown = populated.resolve_business_entity("business-missing")
        absent = empty.resolve_business_entity("business-alpha")

        self.assertEqual(unknown.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(unknown.records, ())
        self.assertEqual(absent.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(absent.records, ())

    def test_malformed_lookup_inputs_fail_closed_before_matching(self):
        class Hostile:
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        source = NonProductionBusinessEntityAuthoritySource([business_entity()])
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

                result = source.resolve_business_entity(lookup)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(Hostile.comparisons, 0)

    def test_str_subclass_lookup_inputs_fail_closed_before_behavior_invocation(self):
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

        source = NonProductionBusinessEntityAuthoritySource([business_entity()])
        cases = (
            (
                "hostile equality",
                HostileStr("business-alpha"),
                HostileStr,
                "comparisons",
            ),
            (
                "hostile strip",
                HostileStripStr("business-alpha"),
                HostileStripStr,
                "strip_calls",
            ),
            (
                "raising strip",
                RaisingStripStr("business-alpha"),
                RaisingStripStr,
                "strip_calls",
            ),
        )

        for label, lookup, instrumented, counter in cases:
            with self.subTest(case=label):
                setattr(instrumented, counter, 0)

                result = source.resolve_business_entity(lookup)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_business_entity_evidence_fails_closed(self):
        malformed = object.__new__(BusinessEntity)
        object.__setattr__(malformed, "authority_reference", "business-authority")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        source = NonProductionBusinessEntityAuthoritySource([malformed])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_non_current_business_entity_states_return_no_positive_authority(self):
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
                source = NonProductionBusinessEntityAuthoritySource(
                    [business_entity(state=state)]
                )

                result = source.resolve_business_entity("business-alpha")

                self.assertEqual(result.status, expected_status)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_conflicting_business_entities_fail_closed(self):
        cases = (
            ("authority_reference", {"authority_reference": "business-beta-authority"}),
            ("state", {"state": AuthorityRecordState.STALE}),
        )

        for name, overrides in cases:
            with self.subTest(name=name):
                source = NonProductionBusinessEntityAuthoritySource(
                    [
                        business_entity(),
                        business_entity(**overrides),
                    ]
                )

                result = source.resolve_business_entity("business-alpha")

                self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
                self.assertEqual(len(result.records), 2)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_duplicate_business_entities_fail_closed_without_deduplication(self):
        source = NonProductionBusinessEntityAuthoritySource(
            [
                business_entity(),
                business_entity(),
            ]
        )

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)

    def test_repeated_lookup_is_deterministic_and_output_isolated(self):
        source = NonProductionBusinessEntityAuthoritySource([business_entity()])

        first = source.resolve_business_entity("business-alpha")
        second = source.resolve_business_entity("business-alpha")

        self.assertEqual(first, second)
        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertIsNot(first.records[0], second.records[0])
        self.assertIsNot(first.records[0], source._business_entities[0])
        self.assertIsNot(second.records[0], source._business_entities[0])

    def test_lookup_uses_captured_instance_identity_field(self):
        class ConfusedBusinessEntity(BusinessEntity):
            def __getattribute__(self, name):
                if name == "business_entity_id":
                    return "business-alpha"
                return object.__getattribute__(self, name)

        record = object.__new__(ConfusedBusinessEntity)
        object.__setattr__(record, "authority_reference", "business-spoof")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "business_entity_id", "business-wrong")
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_benign_business_entity_subclass_fails_closed(self):
        class BenignBusinessEntity(BusinessEntity):
            pass

        source = NonProductionBusinessEntityAuthoritySource(
            [
                BenignBusinessEntity(
                    "business-alpha-authority",
                    AuthorityRecordState.ACTIVE,
                    "business-alpha",
                )
            ]
        )

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_business_entity_subclass_field_spoofing_fails_closed_before_reads(self):
        class SpoofedBusinessEntity(BusinessEntity):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in (
                    "authority_reference",
                    "state",
                    "business_entity_id",
                ):
                    type(self).authority_field_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "business_entity_id": "business-alpha",
                    }[name]
                return object.__getattribute__(self, name)

        record = set_business_entity_fields(
            object.__new__(SpoofedBusinessEntity),
            state=AuthorityRecordState.REVOKED,
            business_entity_id="business-wrong",
        )
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(SpoofedBusinessEntity.authority_field_reads, 0)

    def test_business_entity_subclass_raising_getattribute_fails_closed(self):
        class RaisingBusinessEntity(BusinessEntity):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in (
                    "authority_reference",
                    "state",
                    "business_entity_id",
                ):
                    type(self).authority_field_reads += 1
                    raise RuntimeError("field unavailable")
                return object.__getattribute__(self, name)

        record = set_business_entity_fields(object.__new__(RaisingBusinessEntity))
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(RaisingBusinessEntity.authority_field_reads, 0)

    def test_getattr_subclass_fails_closed_before_dynamic_fallback(self):
        class GetattrBusinessEntity(BusinessEntity):
            getattr_calls = 0

            def __getattr__(self, name):
                type(self).getattr_calls += 1
                return "forged"

        record = set_business_entity_fields(object.__new__(GetattrBusinessEntity))
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(GetattrBusinessEntity.getattr_calls, 0)

    def test_forged_dict_cannot_authorize_wrong_actual_business_entity_id(self):
        class ForgedDictBusinessEntity(BusinessEntity):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "business_entity_id": "business-alpha",
                    }
                return object.__getattribute__(self, name)

        record = set_business_entity_fields(
            object.__new__(ForgedDictBusinessEntity),
            business_entity_id="business-wrong",
        )
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictBusinessEntity.dict_reads, 0)

    def test_forged_dict_cannot_repair_missing_business_entity_id(self):
        class ForgedDictBusinessEntity(BusinessEntity):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "business_entity_id": "business-alpha",
                    }
                return object.__getattribute__(self, name)

        record = object.__new__(ForgedDictBusinessEntity)
        object.__setattr__(record, "authority_reference", "business-authority")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictBusinessEntity.dict_reads, 0)

    def test_forged_dict_cannot_reactivate_revoked_or_stale_evidence(self):
        class ForgedDictBusinessEntity(BusinessEntity):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "business-alpha-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "business_entity_id": "business-alpha",
                    }
                return object.__getattribute__(self, name)

        for state in (AuthorityRecordState.REVOKED, AuthorityRecordState.STALE):
            with self.subTest(state=state):
                ForgedDictBusinessEntity.dict_reads = 0
                record = set_business_entity_fields(
                    object.__new__(ForgedDictBusinessEntity),
                    state=state,
                )
                source = NonProductionBusinessEntityAuthoritySource([record])

                result = source.resolve_business_entity("business-alpha")

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(ForgedDictBusinessEntity.dict_reads, 0)

    def test_forged_dict_cannot_change_returned_authority_values(self):
        class ForgedDictBusinessEntity(BusinessEntity):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "business_entity_id": "business-admin",
                    }
                return object.__getattribute__(self, name)

        record = set_business_entity_fields(object.__new__(ForgedDictBusinessEntity))
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictBusinessEntity.dict_reads, 0)

    def test_dict_property_subclass_is_rejected_before_property_read(self):
        class DictPropertyBusinessEntity(BusinessEntity):
            dict_reads = 0

            @property
            def __dict__(self):
                type(self).dict_reads += 1
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "business_entity_id": "business-alpha",
                }

        record = set_business_entity_fields(object.__new__(DictPropertyBusinessEntity))
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictPropertyBusinessEntity.dict_reads, 0)

    def test_dict_descriptor_subclass_is_rejected_before_descriptor_read(self):
        class DictDescriptor:
            reads = 0

            def __get__(self, instance, owner):
                type(self).reads += 1
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "business_entity_id": "business-alpha",
                }

        class DictDescriptorBusinessEntity(BusinessEntity):
            __dict__ = DictDescriptor()

        record = set_business_entity_fields(object.__new__(DictDescriptorBusinessEntity))
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictDescriptor.reads, 0)

    def test_combined_field_and_dict_spoofing_cannot_control_authority(self):
        class CombinedSpoofBusinessEntity(BusinessEntity):
            field_reads = 0
            dict_reads = 0
            getattr_calls = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "business_entity_id": "business-alpha",
                    }
                if name in (
                    "authority_reference",
                    "state",
                    "business_entity_id",
                ):
                    type(self).field_reads += 1
                    return "spoofed"
                return object.__getattribute__(self, name)

            def __getattr__(self, name):
                type(self).getattr_calls += 1
                return "spoofed"

        record = set_business_entity_fields(object.__new__(CombinedSpoofBusinessEntity))
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(CombinedSpoofBusinessEntity.field_reads, 0)
        self.assertEqual(CombinedSpoofBusinessEntity.dict_reads, 0)
        self.assertEqual(CombinedSpoofBusinessEntity.getattr_calls, 0)

    def test_exact_business_entity_with_dict_subclass_storage_fails_closed(self):
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

        record = business_entity(
            authority_reference="actual-authority",
            state=AuthorityRecordState.REVOKED,
            business_entity_id="business-wrong",
        )
        object.__setattr__(record, "__dict__", HostileDict())
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

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
                phase = "validated" if type(self).get_calls <= 3 else "forged"
                if phase == "validated":
                    return {
                        "authority_reference": "business-alpha-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "business_entity_id": "business-alpha",
                    }.get(key, default)
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "business_entity_id": "business-admin",
                }.get(key, default)

        record = business_entity()
        object.__setattr__(record, "__dict__", ToctouDict())
        source = NonProductionBusinessEntityAuthoritySource([record])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ToctouDict.get_calls, 0)

    def test_object_new_missing_instance_fields_fail_closed(self):
        required_fields = (
            "authority_reference",
            "state",
            "business_entity_id",
        )
        values = {
            "authority_reference": "business-alpha-authority",
            "state": AuthorityRecordState.ACTIVE,
            "business_entity_id": "business-alpha",
        }

        for missing in required_fields:
            with self.subTest(missing=missing):
                malformed = object.__new__(BusinessEntity)
                for name, value in values.items():
                    if name != missing:
                        object.__setattr__(malformed, name, value)
                source = NonProductionBusinessEntityAuthoritySource([malformed])

                result = source.resolve_business_entity("business-alpha")

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
            ("authority_reference", "business-alpha-authority"),
            ("business_entity_id", "business-alpha"),
        )

        for field, value in cases:
            with self.subTest(field=field):
                HostileStoredStr.comparisons = 0
                HostileStoredStr.strip_calls = 0
                record = replace(business_entity(), **{field: HostileStoredStr(value)})
                source = NonProductionBusinessEntityAuthoritySource([record])

                result = source.resolve_business_entity("business-alpha")

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
            ("business_entity_id", None),
            ("business_entity_id", ""),
            ("business_entity_id", "   "),
            ("business_entity_id", object()),
        )

        for field, value in cases:
            with self.subTest(field=field, value=value):
                record = replace(business_entity(), **{field: value})
                source = NonProductionBusinessEntityAuthoritySource([record])

                result = source.resolve_business_entity("business-alpha")

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_wrong_requested_id_cannot_create_authority(self):
        source = NonProductionBusinessEntityAuthoritySource([business_entity()])

        result = source.resolve_business_entity("business-admin")

        self.assertEqual(result.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(result.records, ())

    def test_ambiguous_output_materializes_safe_exact_records(self):
        first = business_entity()
        second = business_entity()
        source = NonProductionBusinessEntityAuthoritySource([first, second])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)
        for returned in result.records:
            self.assertIs(type(returned), BusinessEntity)
            self.assertIsNot(returned, first)
            self.assertIsNot(returned, second)
            self.assertEqual(
                returned.authority_reference,
                "business-alpha-authority",
            )
            self.assertEqual(returned.business_entity_id, "business-alpha")

    def test_conflicting_output_materializes_safe_exact_records(self):
        original = business_entity()
        conflict = replace(
            business_entity(),
            authority_reference="business-beta-authority",
        )
        source = NonProductionBusinessEntityAuthoritySource([original, conflict])

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(len(result.records), 2)
        for returned in result.records:
            self.assertIs(type(returned), BusinessEntity)
            self.assertIsNot(returned, original)
            self.assertIsNot(returned, conflict)

    def test_record_order_cannot_create_positive_authority_from_multiple_records(self):
        duplicate_a = business_entity()
        duplicate_b = business_entity()
        conflict_a = business_entity()
        conflict_b = replace(
            business_entity(),
            authority_reference="business-beta-authority",
        )

        duplicate_forward = NonProductionBusinessEntityAuthoritySource(
            [duplicate_a, duplicate_b]
        ).resolve_business_entity("business-alpha")
        duplicate_reverse = NonProductionBusinessEntityAuthoritySource(
            [duplicate_b, duplicate_a]
        ).resolve_business_entity("business-alpha")
        conflict_forward = NonProductionBusinessEntityAuthoritySource(
            [conflict_a, conflict_b]
        ).resolve_business_entity("business-alpha")
        conflict_reverse = NonProductionBusinessEntityAuthoritySource(
            [conflict_b, conflict_a]
        ).resolve_business_entity("business-alpha")

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
        records = [business_entity(business_entity_id="business-original")]
        source = NonProductionBusinessEntityAuthoritySource(records)
        records.append(business_entity(business_entity_id="business-added"))
        records.clear()

        original = source.resolve_business_entity("business-original")
        added = source.resolve_business_entity("business-added")

        self.assertEqual(original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(added.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(added.records, ())

    def test_source_consumes_generator_during_constructor_snapshot_creation(self):
        records = iter([business_entity()])
        source = NonProductionBusinessEntityAuthoritySource(records)

        first = source.resolve_business_entity("business-alpha")
        second = source.resolve_business_entity("business-alpha")

        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(second.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(first.records, second.records)
        self.assertIsNot(first.records[0], second.records[0])

    def test_original_record_mutation_after_construction_cannot_change_authority(self):
        original = business_entity()
        source = NonProductionBusinessEntityAuthoritySource([original])
        before = source.resolve_business_entity("business-alpha")

        with self.assertRaises(FrozenInstanceError):
            original.business_entity_id = "business-admin"
        object.__setattr__(original, "authority_reference", "attacker-authority")
        object.__setattr__(original, "state", AuthorityRecordState.REVOKED)
        object.__setattr__(original, "business_entity_id", "business-admin")

        after_original = source.resolve_business_entity("business-alpha")
        after_mutated = source.resolve_business_entity("business-admin")

        self.assertEqual(before.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_mutated.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(
            after_original.records[0].authority_reference,
            "business-alpha-authority",
        )
        self.assertEqual(after_original.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(after_original.records[0].business_entity_id, "business-alpha")

    def test_found_output_does_not_alias_internal_snapshot(self):
        original = business_entity()
        source = NonProductionBusinessEntityAuthoritySource([original])

        first = source.resolve_business_entity("business-alpha")
        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        returned = first.records[0]
        self.assertIs(type(returned), BusinessEntity)
        self.assertIsNot(returned, original)
        self.assertIsNot(returned, source._business_entities[0])

        mutate_to_forged_business_entity(returned)

        original_id = source.resolve_business_entity("business-alpha")
        forged_id = source.resolve_business_entity("business-admin")

        self.assertEqual(original_id.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(forged_id.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(
            original_id.records[0].authority_reference,
            "business-alpha-authority",
        )
        self.assertEqual(original_id.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(original_id.records[0].business_entity_id, "business-alpha")

    def test_ambiguous_output_does_not_alias_internal_snapshots(self):
        source = NonProductionBusinessEntityAuthoritySource(
            [business_entity(), business_entity()]
        )

        first = source.resolve_business_entity("business-alpha")
        self.assertEqual(first.status, AuthorityLookupStatus.AMBIGUOUS)

        for returned, internal in zip(first.records, source._business_entities):
            self.assertIs(type(returned), BusinessEntity)
            self.assertIsNot(returned, internal)
            mutate_to_forged_business_entity(returned)

        second = source.resolve_business_entity("business-alpha")
        forged = source.resolve_business_entity("business-admin")

        self.assertEqual(second.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(forged.status, AuthorityLookupStatus.NOT_FOUND)
        for returned, internal in zip(second.records, source._business_entities):
            self.assertEqual(returned, business_entity())
            self.assertIsNot(returned, internal)

    def test_conflicting_output_does_not_alias_internal_snapshots(self):
        conflict = replace(
            business_entity(),
            authority_reference="business-beta-authority",
        )
        source = NonProductionBusinessEntityAuthoritySource(
            [business_entity(), conflict]
        )

        first = source.resolve_business_entity("business-alpha")
        self.assertEqual(first.status, AuthorityLookupStatus.CONFLICTING)

        for returned, internal in zip(first.records, source._business_entities):
            self.assertIs(type(returned), BusinessEntity)
            self.assertIsNot(returned, internal)
            mutate_to_forged_business_entity(returned)

        second = source.resolve_business_entity("business-alpha")
        forged = source.resolve_business_entity("business-admin")

        self.assertEqual(second.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(forged.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(
            {record.authority_reference for record in second.records},
            {"business-alpha-authority", "business-beta-authority"},
        )
        for returned, internal in zip(second.records, source._business_entities):
            self.assertIsNot(returned, internal)

    def test_valid_record_plus_malformed_evidence_fails_closed_globally(self):
        source = NonProductionBusinessEntityAuthoritySource(
            [business_entity(), object()]
        )

        result = source.resolve_business_entity("business-alpha")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_business_entity_alone_does_not_create_downstream_authority(self):
        source = NonProductionBusinessEntityAuthoritySource([business_entity()])
        evaluator = TrustedAuthorizationEvaluator(source)

        result = evaluator.evaluate(request())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertIn(
            "principal_mapping:UNSUPPORTED",
            result.audit_evidence.authority_inputs,
        )

    def test_unsupported_authority_categories_return_no_positive_authority(self):
        source = NonProductionBusinessEntityAuthoritySource([business_entity()])
        lookups = (
            source.resolve_principal_mapping("business-source-test", "subject-alpha"),
            source.resolve_resource("resource-alpha"),
            source.resolve_membership("principal-alpha", "business-alpha"),
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
        source = NonProductionBusinessEntityAuthoritySource([business_entity()])
        forbidden_names = (
            "add_business_entity",
            "create_business_entity",
            "update_business_entity",
            "delete_business_entity",
            "remove_business_entity",
            "revoke_business_entity",
            "restore_business_entity",
            "reactivate_business_entity",
            "assign_business_entity",
            "mutate_business_entity",
            "save_business_entity",
            "write_business_entity",
            "upsert_business_entity",
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
                self.assertFalse(hasattr(business_entity_source_module, name))

    def test_source_is_not_exported_from_package_root(self):
        self.assertFalse(
            hasattr(
                trusted_authorization_package,
                "NonProductionBusinessEntityAuthoritySource",
            )
        )

    def test_source_keeps_only_constructor_supplied_snapshots(self):
        first = business_entity()
        second = replace(first, authority_reference="business-beta-authority")
        source = NonProductionBusinessEntityAuthoritySource([first, second])

        self.assertEqual(
            source.__slots__,
            ("_business_entities", "_has_malformed_evidence"),
        )
        self.assertEqual(source._business_entities, (first, second))
        self.assertIsNot(source._business_entities[0], first)
        self.assertIsNot(source._business_entities[1], second)


if __name__ == "__main__":
    unittest.main()
