import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trusted_authorization import (  # noqa: E402
    AuthorityLookupStatus,
    AuthorityRecordState,
    RequestedAction,
    ResourceClass,
)
from trusted_authorization.models import GovernedResource  # noqa: E402
from trusted_authorization.resource_identity_source import (  # noqa: E402
    NonProductionResourceIdentityAuthoritySource,
)


def resource(
    authority_reference="resource-alpha-authority",
    state=AuthorityRecordState.ACTIVE,
    resource_id="resource-alpha",
    resource_reference="resource-alpha-ref",
    resource_class=ResourceClass.REPORT,
    business_entity_id="business-alpha",
):
    return GovernedResource(
        authority_reference=authority_reference,
        state=state,
        resource_id=resource_id,
        resource_reference=resource_reference,
        resource_class=resource_class,
        business_entity_id=business_entity_id,
    )


def set_resource_fields(record, **overrides):
    values = {
        "authority_reference": "resource-alpha-authority",
        "state": AuthorityRecordState.ACTIVE,
        "resource_id": "resource-alpha",
        "resource_reference": "resource-alpha-ref",
        "resource_class": ResourceClass.REPORT,
        "business_entity_id": "business-alpha",
    }
    values.update(overrides)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


class NonProductionResourceIdentityAuthoritySourceTests(unittest.TestCase):
    def test_known_active_resource_resolves_expected_governed_identity(self):
        expected = resource()
        source = NonProductionResourceIdentityAuthoritySource([expected])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(result.records, (expected,))
        self.assertIs(type(result.records[0]), GovernedResource)
        self.assertIsNot(result.records[0], expected)
        self.assertEqual(result.records[0].resource_id, "resource-alpha")
        self.assertEqual(result.records[0].resource_reference, "resource-alpha-ref")
        self.assertEqual(result.records[0].resource_class, ResourceClass.REPORT)
        self.assertEqual(result.records[0].business_entity_id, "business-alpha")
        self.assertEqual(
            result.records[0].authority_reference,
            "resource-alpha-authority",
        )

    def test_unknown_resource_and_empty_source_return_no_positive_authority(self):
        populated = NonProductionResourceIdentityAuthoritySource([resource()])
        empty = NonProductionResourceIdentityAuthoritySource()

        unknown = populated.resolve_resource("unknown-resource-ref")
        absent = empty.resolve_resource("resource-alpha-ref")

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

        source = NonProductionResourceIdentityAuthoritySource([resource()])
        cases = (
            ("none", None),
            ("integer", 7),
            ("hostile object", Hostile()),
            ("empty", ""),
            ("space", " "),
            ("spaces", "   "),
            ("tab", "\t"),
            ("newline", "\n"),
            ("mixed whitespace", " \t\n "),
        )

        for label, resource_reference in cases:
            with self.subTest(case=label):
                Hostile.comparisons = 0

                result = source.resolve_resource(resource_reference)

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
                return object()

        class RaisingStripStr(str):
            strip_calls = 0

            def strip(self):
                type(self).strip_calls += 1
                raise RuntimeError("strip unavailable")

        source = NonProductionResourceIdentityAuthoritySource([resource()])
        cases = (
            ("hostile str subclass", HostileStr("wrong-resource-ref"), HostileStr, "comparisons"),
            ("hostile strip", HostileStripStr("wrong-resource-ref"), HostileStripStr, "strip_calls"),
            ("raising strip", RaisingStripStr("resource-alpha-ref"), RaisingStripStr, "strip_calls"),
        )

        for label, resource_reference, instrumented, counter in cases:
            with self.subTest(case=label):
                setattr(instrumented, counter, 0)

                result = source.resolve_resource(resource_reference)

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_record_evidence_fails_closed(self):
        malformed = object.__new__(GovernedResource)
        object.__setattr__(malformed, "authority_reference", "bad-resource")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(malformed, "resource_id", "resource-alpha")
        object.__setattr__(malformed, "resource_reference", "resource-alpha-ref")
        object.__setattr__(malformed, "business_entity_id", "business-alpha")
        source = NonProductionResourceIdentityAuthoritySource([malformed])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_wrong_record_type_fails_closed(self):
        source = NonProductionResourceIdentityAuthoritySource([object()])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_object_new_missing_instance_fields_fail_closed(self):
        required_fields = (
            "authority_reference",
            "state",
            "resource_id",
            "resource_reference",
            "resource_class",
            "business_entity_id",
        )
        values = {
            "authority_reference": "resource-alpha-authority",
            "state": AuthorityRecordState.ACTIVE,
            "resource_id": "resource-alpha",
            "resource_reference": "resource-alpha-ref",
            "resource_class": ResourceClass.REPORT,
            "business_entity_id": "business-alpha",
        }

        for missing in required_fields:
            with self.subTest(missing=missing):
                malformed = object.__new__(GovernedResource)
                for name, value in values.items():
                    if name != missing:
                        object.__setattr__(malformed, name, value)
                source = NonProductionResourceIdentityAuthoritySource([malformed])

                result = source.resolve_resource("resource-alpha-ref")

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_record_subclass_getattribute_spoofing_fails_closed(self):
        class ConfusedResource(GovernedResource):
            field_reads = 0

            def __getattribute__(self, name):
                if name == "resource_reference":
                    type(self).field_reads += 1
                    return "resource-alpha-ref"
                if name == "resource_id":
                    type(self).field_reads += 1
                    return "resource-alpha"
                if name == "business_entity_id":
                    type(self).field_reads += 1
                    return "business-alpha"
                return object.__getattribute__(self, name)

        record = object.__new__(ConfusedResource)
        object.__setattr__(record, "authority_reference", "resource-spoof")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "resource_id", "other-resource")
        object.__setattr__(record, "resource_reference", "other-resource-ref")
        object.__setattr__(record, "resource_class", ResourceClass.REPORT)
        object.__setattr__(record, "business_entity_id", "other-business")
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ConfusedResource.field_reads, 0)

    def test_record_subclass_field_spoofing_fails_closed_before_field_reads(self):
        class SpoofedResource(GovernedResource):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in (
                    "authority_reference",
                    "state",
                    "resource_id",
                    "resource_reference",
                    "resource_class",
                    "business_entity_id",
                ):
                    type(self).authority_field_reads += 1
                    return {
                        "authority_reference": "spoofed-authority",
                        "state": AuthorityRecordState.REVOKED,
                        "resource_id": "spoofed-resource",
                        "resource_reference": "spoofed-reference",
                        "resource_class": ResourceClass.EXECUTIVE_DASHBOARD,
                        "business_entity_id": "spoofed-business",
                    }[name]
                return object.__getattribute__(self, name)

        original = object.__new__(SpoofedResource)
        object.__setattr__(original, "authority_reference", "resource-alpha-authority")
        object.__setattr__(original, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(original, "resource_id", "resource-alpha")
        object.__setattr__(original, "resource_reference", "resource-alpha-ref")
        object.__setattr__(original, "resource_class", ResourceClass.REPORT)
        object.__setattr__(original, "business_entity_id", "business-alpha")
        source = NonProductionResourceIdentityAuthoritySource([original])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(SpoofedResource.authority_field_reads, 0)

    def test_forged_dict_cannot_authorize_wrong_actual_resource_reference(self):
        class ForgedDictResource(GovernedResource):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "resource_id": "forged-resource",
                        "resource_reference": "resource-alpha-ref",
                        "resource_class": ResourceClass.REPORT,
                        "business_entity_id": "forged-business",
                    }
                return object.__getattribute__(self, name)

        record = set_resource_fields(
            object.__new__(ForgedDictResource),
            authority_reference="actual-authority",
            resource_id="actual-resource",
            resource_reference="wrong-resource-ref",
            business_entity_id="actual-business",
        )
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictResource.dict_reads, 0)

    def test_forged_dict_cannot_repair_malformed_actual_evidence(self):
        class ForgedDictResource(GovernedResource):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "resource_id": "forged-resource",
                        "resource_reference": "resource-alpha-ref",
                        "resource_class": ResourceClass.REPORT,
                        "business_entity_id": "forged-business",
                    }
                return object.__getattribute__(self, name)

        record = object.__new__(ForgedDictResource)
        object.__setattr__(record, "authority_reference", "actual-authority")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "resource_id", "actual-resource")
        object.__setattr__(record, "resource_reference", "resource-alpha-ref")
        object.__setattr__(record, "resource_class", ResourceClass.REPORT)
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictResource.dict_reads, 0)

    def test_forged_dict_cannot_reactivate_revoked_actual_evidence(self):
        class ForgedDictResource(GovernedResource):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "resource-alpha-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "resource_id": "resource-alpha",
                        "resource_reference": "resource-alpha-ref",
                        "resource_class": ResourceClass.REPORT,
                        "business_entity_id": "business-alpha",
                    }
                return object.__getattribute__(self, name)

        record = set_resource_fields(
            object.__new__(ForgedDictResource),
            state=AuthorityRecordState.REVOKED,
        )
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictResource.dict_reads, 0)

    def test_forged_dict_cannot_change_returned_authority_values(self):
        class ForgedDictResource(GovernedResource):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "resource_id": "resource-admin",
                        "resource_reference": "wrong-resource-ref",
                        "resource_class": ResourceClass.EXECUTIVE_DASHBOARD,
                        "business_entity_id": "business-beta",
                    }
                return object.__getattribute__(self, name)

        record = set_resource_fields(object.__new__(ForgedDictResource))
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictResource.dict_reads, 0)

    def test_combined_field_and_dict_spoofing_cannot_control_authority(self):
        class CombinedSpoofResource(GovernedResource):
            field_reads = 0
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "resource_id": "forged-resource",
                        "resource_reference": "forged-reference",
                        "resource_class": ResourceClass.EXECUTIVE_DASHBOARD,
                        "business_entity_id": "forged-business",
                    }
                if name in (
                    "authority_reference",
                    "state",
                    "resource_id",
                    "resource_reference",
                    "resource_class",
                    "business_entity_id",
                ):
                    type(self).field_reads += 1
                    return "spoofed"
                return object.__getattribute__(self, name)

        record = set_resource_fields(object.__new__(CombinedSpoofResource))
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(CombinedSpoofResource.field_reads, 0)
        self.assertEqual(CombinedSpoofResource.dict_reads, 0)

    def test_raising_dict_subclass_is_rejected_before_dict_override(self):
        class RaisingDictResource(GovernedResource):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    raise RuntimeError("forged dict unavailable")
                return object.__getattribute__(self, name)

        record = set_resource_fields(object.__new__(RaisingDictResource))
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(RaisingDictResource.dict_reads, 0)

    def test_forged_dict_cannot_change_duplicate_or_conflict_classification(self):
        class ForgedClassificationResource(GovernedResource):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return object.__getattribute__(self, "_forged_fields")
                return object.__getattribute__(self, name)

        duplicate_a = set_resource_fields(object.__new__(ForgedClassificationResource))
        duplicate_b = set_resource_fields(object.__new__(ForgedClassificationResource))
        object.__setattr__(
            duplicate_a,
            "_forged_fields",
            {
                "authority_reference": "resource-alpha-authority",
                "state": AuthorityRecordState.ACTIVE,
                "resource_id": "forged-a",
                "resource_reference": "resource-alpha-ref",
                "resource_class": ResourceClass.REPORT,
                "business_entity_id": "business-alpha",
            },
        )
        object.__setattr__(
            duplicate_b,
            "_forged_fields",
            {
                "authority_reference": "resource-alpha-authority",
                "state": AuthorityRecordState.ACTIVE,
                "resource_id": "forged-b",
                "resource_reference": "resource-alpha-ref",
                "resource_class": ResourceClass.REPORT,
                "business_entity_id": "business-alpha",
            },
        )

        duplicate_result = NonProductionResourceIdentityAuthoritySource(
            [duplicate_a, duplicate_b]
        ).resolve_resource("resource-alpha-ref")

        conflict_a = set_resource_fields(object.__new__(ForgedClassificationResource))
        conflict_b = set_resource_fields(
            object.__new__(ForgedClassificationResource),
            resource_id="resource-beta",
        )
        for record in (conflict_a, conflict_b):
            object.__setattr__(
                record,
                "_forged_fields",
                {
                    "authority_reference": "resource-alpha-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "resource_id": "resource-alpha",
                    "resource_reference": "resource-alpha-ref",
                    "resource_class": ResourceClass.REPORT,
                    "business_entity_id": "business-alpha",
                },
            )

        conflict_result = NonProductionResourceIdentityAuthoritySource(
            [conflict_a, conflict_b]
        ).resolve_resource("resource-alpha-ref")

        self.assertEqual(duplicate_result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(duplicate_result.records, ())
        self.assertEqual(conflict_result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(conflict_result.records, ())
        self.assertEqual(ForgedClassificationResource.dict_reads, 0)

    def test_dict_property_subclass_is_rejected_before_property_read(self):
        class DictPropertyResource(GovernedResource):
            dict_reads = 0

            @property
            def __dict__(self):
                type(self).dict_reads += 1
                return {
                    "authority_reference": "forged-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "resource_id": "forged-resource",
                    "resource_reference": "resource-alpha-ref",
                    "resource_class": ResourceClass.EXECUTIVE_DASHBOARD,
                    "business_entity_id": "forged-business",
                }

        record = set_resource_fields(object.__new__(DictPropertyResource))
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictPropertyResource.dict_reads, 0)

    def test_dict_descriptor_subclass_is_rejected_before_descriptor_read(self):
        class DictDescriptor:
            reads = 0

            def __get__(self, instance, owner):
                type(self).reads += 1
                return {
                    "authority_reference": "forged-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "resource_id": "forged-resource",
                    "resource_reference": "resource-alpha-ref",
                    "resource_class": ResourceClass.EXECUTIVE_DASHBOARD,
                    "business_entity_id": "forged-business",
                }

        class DictDescriptorResource(GovernedResource):
            __dict__ = DictDescriptor()

        record = set_resource_fields(object.__new__(DictDescriptorResource))
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictDescriptor.reads, 0)

    def test_exact_record_with_dict_subclass_storage_fails_closed(self):
        class HostileDict(dict):
            get_calls = 0
            getitem_calls = 0
            contains_calls = 0
            iter_calls = 0

            def get(self, key, default=None):
                type(self).get_calls += 1
                return {
                    "authority_reference": "forged-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "resource_id": "forged-resource",
                    "resource_reference": "resource-alpha-ref",
                    "resource_class": ResourceClass.EXECUTIVE_DASHBOARD,
                    "business_entity_id": "forged-business",
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

        record = resource()
        object.__setattr__(
            record,
            "__dict__",
            HostileDict(
                {
                    "authority_reference": "actual-authority",
                    "state": AuthorityRecordState.REVOKED,
                    "resource_id": "actual-resource",
                    "resource_reference": "wrong-resource-ref",
                    "resource_class": ResourceClass.REPORT,
                    "business_entity_id": "actual-business",
                }
            ),
        )
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(HostileDict.get_calls, 0)
        self.assertEqual(HostileDict.getitem_calls, 0)
        self.assertEqual(HostileDict.contains_calls, 0)
        self.assertEqual(HostileDict.iter_calls, 0)

    def test_validation_materialization_toctou_dict_subclass_fails_closed(self):
        class ToctouDict(dict):
            get_calls = 0

            def get(self, key, default=None):
                type(self).get_calls += 1
                phase = "validated" if type(self).get_calls <= 6 else "forged"
                if phase == "validated":
                    return {
                        "authority_reference": "resource-alpha-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "resource_id": "resource-alpha",
                        "resource_reference": "resource-alpha-ref",
                        "resource_class": ResourceClass.REPORT,
                        "business_entity_id": "business-alpha",
                    }.get(key, default)
                return {
                    "authority_reference": "forged-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "resource_id": "forged-resource",
                    "resource_reference": "resource-alpha-ref",
                    "resource_class": ResourceClass.EXECUTIVE_DASHBOARD,
                    "business_entity_id": "forged-business",
                }.get(key, default)

        record = resource()
        object.__setattr__(record, "__dict__", ToctouDict())
        source = NonProductionResourceIdentityAuthoritySource([record])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ToctouDict.get_calls, 0)

    def test_hostile_stored_string_subclasses_fail_closed(self):
        class HostileStoredStr(str):
            comparisons = 0

            def __eq__(self, other):
                type(self).comparisons += 1
                return True

        cases = (
            ("authority_reference", "resource-alpha-authority"),
            ("resource_id", "resource-alpha"),
            ("resource_reference", "wrong-resource-ref"),
            ("business_entity_id", "business-alpha"),
        )

        for field, value in cases:
            with self.subTest(field=field):
                HostileStoredStr.comparisons = 0
                record = replace(resource(), **{field: HostileStoredStr(value)})
                source = NonProductionResourceIdentityAuthoritySource([record])

                result = source.resolve_resource("resource-alpha-ref")

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(HostileStoredStr.comparisons, 0)

    def test_malformed_authority_fields_fail_closed(self):
        cases = (
            ("authority_reference", ""),
            ("authority_reference", "   "),
            ("authority_reference", object()),
            ("state", None),
            ("state", "ACTIVE"),
            ("resource_id", ""),
            ("resource_id", "   "),
            ("resource_id", object()),
            ("resource_reference", ""),
            ("resource_reference", "   "),
            ("resource_reference", object()),
            ("resource_class", None),
            ("resource_class", "REPORT"),
            ("business_entity_id", ""),
            ("business_entity_id", "   "),
            ("business_entity_id", object()),
        )

        for field, value in cases:
            with self.subTest(field=field, value=value):
                record = replace(resource(), **{field: value})
                source = NonProductionResourceIdentityAuthoritySource([record])

                result = source.resolve_resource("resource-alpha-ref")

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_non_current_resource_states_return_no_positive_authority(self):
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
                source = NonProductionResourceIdentityAuthoritySource(
                    [resource(state=state)]
                )

                result = source.resolve_resource("resource-alpha-ref")

                self.assertEqual(result.status, expected_status)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_duplicate_resources_fail_closed_without_deduplication(self):
        source = NonProductionResourceIdentityAuthoritySource(
            [resource(), resource()]
        )

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)

    def test_ambiguous_output_materializes_safe_exact_records(self):
        first = resource()
        second = resource()
        source = NonProductionResourceIdentityAuthoritySource([first, second])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)
        for returned in result.records:
            self.assertIs(type(returned), GovernedResource)
            self.assertIsNot(returned, first)
            self.assertIsNot(returned, second)
            self.assertEqual(returned.authority_reference, "resource-alpha-authority")
            self.assertEqual(returned.resource_id, "resource-alpha")
            self.assertEqual(returned.business_entity_id, "business-alpha")

    def test_conflicting_resources_fail_closed(self):
        cases = (
            ("authority_reference", "resource-beta-authority"),
            ("state", AuthorityRecordState.REVOKED),
            ("resource_id", "resource-beta"),
            ("resource_class", ResourceClass.EXECUTIVE_DASHBOARD),
            ("business_entity_id", "business-beta"),
        )

        for field, value in cases:
            with self.subTest(field=field):
                source = NonProductionResourceIdentityAuthoritySource(
                    [resource(), replace(resource(), **{field: value})]
                )

                result = source.resolve_resource("resource-alpha-ref")

                self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
                self.assertEqual(len(result.records), 2)

    def test_conflicting_output_materializes_safe_exact_records(self):
        original = resource()
        conflicting = replace(resource(), resource_id="resource-beta")
        source = NonProductionResourceIdentityAuthoritySource([original, conflicting])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(len(result.records), 2)
        for returned in result.records:
            self.assertIs(type(returned), GovernedResource)
            self.assertIsNot(returned, original)
            self.assertIsNot(returned, conflicting)
        self.assertEqual(
            {record.resource_id for record in result.records},
            {"resource-alpha", "resource-beta"},
        )

    def test_record_order_cannot_create_positive_authority_from_multiple_records(self):
        first = resource()
        second = replace(first, resource_id="resource-beta")

        forward = NonProductionResourceIdentityAuthoritySource(
            [first, second]
        ).resolve_resource("resource-alpha-ref")
        reverse = NonProductionResourceIdentityAuthoritySource(
            [second, first]
        ).resolve_resource("resource-alpha-ref")

        self.assertEqual(forward.status, AuthorityLookupStatus.CONFLICTING)
        self.assertEqual(reverse.status, AuthorityLookupStatus.CONFLICTING)
        self.assertNotEqual(forward.status, AuthorityLookupStatus.FOUND)
        self.assertNotEqual(reverse.status, AuthorityLookupStatus.FOUND)

    def test_repeated_lookup_is_deterministic(self):
        source = NonProductionResourceIdentityAuthoritySource([resource()])

        first = source.resolve_resource("resource-alpha-ref")
        second = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(first, second)

    def test_source_captures_constructor_records_against_caller_list_mutation(self):
        records = [resource()]
        source = NonProductionResourceIdentityAuthoritySource(records)
        records.append(replace(resource(), resource_reference="resource-beta-ref"))

        result = source.resolve_resource("resource-beta-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(result.records, ())
        self.assertEqual(source._resources, (resource(),))
        self.assertIsNot(source._resources[0], records[0])

    def test_source_consumes_generator_during_constructor_snapshot_creation(self):
        records = iter([resource()])
        source = NonProductionResourceIdentityAuthoritySource(records)

        first = source.resolve_resource("resource-alpha-ref")
        second = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(second.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(first.records, second.records)

    def test_original_record_mutation_after_construction_cannot_change_authority(self):
        original = resource()
        source = NonProductionResourceIdentityAuthoritySource([original])
        before = source.resolve_resource("resource-alpha-ref")

        with self.assertRaises(FrozenInstanceError):
            original.resource_reference = "mutated-resource-ref"
        object.__setattr__(original, "resource_reference", "mutated-resource-ref")
        object.__setattr__(original, "business_entity_id", "mutated-business")
        object.__setattr__(original, "resource_id", "mutated-resource")
        object.__setattr__(original, "state", AuthorityRecordState.REVOKED)

        after_original_ref = source.resolve_resource("resource-alpha-ref")
        after_mutated_ref = source.resolve_resource("mutated-resource-ref")

        self.assertEqual(before.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_original_ref.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_mutated_ref.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(after_original_ref.records[0].resource_reference, "resource-alpha-ref")
        self.assertEqual(after_original_ref.records[0].business_entity_id, "business-alpha")
        self.assertEqual(after_original_ref.records[0].resource_id, "resource-alpha")
        self.assertEqual(after_original_ref.records[0].state, AuthorityRecordState.ACTIVE)

    def test_valid_record_plus_malformed_evidence_fails_closed_globally(self):
        source = NonProductionResourceIdentityAuthoritySource([resource(), object()])

        result = source.resolve_resource("resource-alpha-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_unsupported_authority_categories_return_no_positive_authority(self):
        source = NonProductionResourceIdentityAuthoritySource([resource()])
        lookups = (
            source.resolve_principal_mapping("provider-alpha", "subject-alpha"),
            source.resolve_business_entity("business-alpha"),
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
        source = NonProductionResourceIdentityAuthoritySource([resource()])
        forbidden_names = (
            "add_resource",
            "create_resource",
            "update_resource",
            "delete_resource",
            "remove_resource",
            "revoke_resource",
            "restore_resource",
            "reactivate_resource",
            "assign_resource",
            "mutate_resource",
            "save_resource",
            "write_resource",
        )

        for name in forbidden_names:
            with self.subTest(name=name):
                self.assertFalse(hasattr(source, name))

    def test_source_module_exposes_only_expected_model_dependencies(self):
        import trusted_authorization.resource_identity_source as module

        expected_public_names = {
            "AuthorityLookupResult",
            "AuthorityLookupStatus",
            "AuthorityRecordState",
            "BusinessEntity",
            "Entitlement",
            "GovernedResource",
            "Iterable",
            "Membership",
            "NonProductionResourceIdentityAuthoritySource",
            "PrincipalMapping",
            "RequestedAction",
            "ResourceClass",
        }

        actual_public_names = {
            name
            for name in vars(module)
            if not name.startswith("_") and name != "annotations"
        }

        self.assertEqual(actual_public_names, expected_public_names)

    def test_source_has_no_final_decision_authority_surface(self):
        import trusted_authorization.resource_identity_source as module

        self.assertFalse(hasattr(module, "AuthorizationDecision"))
        self.assertFalse(hasattr(module, "AuthorizationResult"))
        self.assertFalse(hasattr(module, "ReasonCategory"))

    def test_cross_business_entity_resource_lookup_preserves_binding(self):
        business_b_resource = resource(
            authority_reference="resource-beta-authority",
            resource_id="resource-beta",
            resource_reference="resource-beta-ref",
            business_entity_id="business-beta",
        )
        source = NonProductionResourceIdentityAuthoritySource(
            [resource(), business_b_resource]
        )

        result = source.resolve_resource("resource-beta-ref")

        self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(result.records, (business_b_resource,))
        self.assertEqual(result.records[0].business_entity_id, "business-beta")


if __name__ == "__main__":
    unittest.main()
