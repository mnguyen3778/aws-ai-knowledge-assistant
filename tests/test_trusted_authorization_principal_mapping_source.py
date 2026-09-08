import sys
import unittest
from dataclasses import FrozenInstanceError, replace
from enum import Enum
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import trusted_authorization as trusted_authorization_package  # noqa: E402
import trusted_authorization.principal_mapping_source as principal_mapping_source_module  # noqa: E402
from trusted_authorization import (  # noqa: E402
    APPLICABILITY_GOVERNANCE_VERSION,
    AUTHORIZATION_SEMANTICS_VERSION,
    BOUNDED_EVALUATION_CONTEXT,
    AuthorityLookupStatus,
    AuthorityRecordState,
    AuthorizationDecision,
    AuthorizationRequest,
    GovernedVersionContext,
    ReasonCategory,
    RequestedAction,
    TrustedAuthorizationEvaluator,
    TrustedSubjectEvidence,
)
from trusted_authorization.models import PrincipalMapping  # noqa: E402
from trusted_authorization.principal_mapping_source import (  # noqa: E402
    NonProductionPrincipalMappingAuthoritySource,
)


SUBJECT = TrustedSubjectEvidence(
    provider="local-principal-source",
    subject="subject-alpha",
    verified=True,
)


def mapping(
    authority_reference="principal-map-alpha",
    state=AuthorityRecordState.ACTIVE,
    subject_provider="local-principal-source",
    subject="subject-alpha",
    principal_id="principal-alpha",
):
    return PrincipalMapping(
        authority_reference=authority_reference,
        state=state,
        subject_provider=subject_provider,
        subject=subject,
        principal_id=principal_id,
    )


def set_mapping_fields(record, **overrides):
    values = {
        "authority_reference": "principal-map-alpha",
        "state": AuthorityRecordState.ACTIVE,
        "subject_provider": "local-principal-source",
        "subject": "subject-alpha",
        "principal_id": "principal-alpha",
    }
    values.update(overrides)
    for name, value in values.items():
        object.__setattr__(record, name, value)
    return record


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
        correlation_id="principal-source-test",
        evaluation_context=BOUNDED_EVALUATION_CONTEXT,
    )


class NonProductionPrincipalMappingAuthoritySourceTests(unittest.TestCase):
    def test_known_subject_resolves_expected_stable_principal_mapping(self):
        expected = mapping()
        source = NonProductionPrincipalMappingAuthoritySource([expected])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records, (expected,))
        self.assertIs(type(result.records[0]), PrincipalMapping)
        self.assertIsNot(result.records[0], expected)
        self.assertEqual(result.records[0].authority_reference, "principal-map-alpha")
        self.assertEqual(result.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(result.records[0].subject_provider, "local-principal-source")
        self.assertEqual(result.records[0].subject, "subject-alpha")
        self.assertEqual(result.records[0].principal_id, "principal-alpha")

    def test_unknown_subject_and_empty_source_return_no_positive_mapping(self):
        populated = NonProductionPrincipalMappingAuthoritySource([mapping()])
        empty = NonProductionPrincipalMappingAuthoritySource()

        unknown = populated.resolve_principal_mapping(
            "local-principal-source",
            "unknown-subject",
        )
        absent = empty.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

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

        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        cases = (
            ("hostile provider", Hostile(), "subject-alpha"),
            ("hostile subject", "local-principal-source", Hostile()),
            ("empty provider", "", "subject-alpha"),
            ("whitespace provider", "   ", "subject-alpha"),
            ("empty subject", "local-principal-source", ""),
            ("whitespace subject", "local-principal-source", "   "),
        )

        for label, subject_provider, subject in cases:
            with self.subTest(case=label):
                Hostile.comparisons = 0

                result = source.resolve_principal_mapping(
                    subject_provider,
                    subject,
                )

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

        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        cases = (
            (
                "hostile str subclass provider",
                HostileStr("wrong-provider"),
                "subject-alpha",
                HostileStr,
                "comparisons",
            ),
            (
                "hostile str subclass subject",
                "local-principal-source",
                HostileStr("wrong-subject"),
                HostileStr,
                "comparisons",
            ),
            (
                "both hostile str subclass inputs",
                HostileStr("wrong-provider"),
                HostileStr("wrong-subject"),
                HostileStr,
                "comparisons",
            ),
            (
                "hostile strip provider",
                HostileStripStr("wrong-provider"),
                "subject-alpha",
                HostileStripStr,
                "strip_calls",
            ),
            (
                "raising strip provider",
                RaisingStripStr("local-principal-source"),
                "subject-alpha",
                RaisingStripStr,
                "strip_calls",
            ),
        )

        for label, subject_provider, subject, instrumented, counter in cases:
            with self.subTest(case=label):
                setattr(instrumented, counter, 0)

                result = source.resolve_principal_mapping(
                    subject_provider,
                    subject,
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(getattr(instrumented, counter), 0)

    def test_malformed_mapping_evidence_fails_closed(self):
        malformed = object.__new__(PrincipalMapping)
        object.__setattr__(malformed, "authority_reference", "bad-map")
        object.__setattr__(malformed, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(
            malformed,
            "subject_provider",
            "local-principal-source",
        )
        object.__setattr__(malformed, "subject", "subject-alpha")
        source = NonProductionPrincipalMappingAuthoritySource([malformed])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_non_current_mapping_states_return_no_positive_mapping(self):
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
                source = NonProductionPrincipalMappingAuthoritySource(
                    [mapping(state=state)]
                )

                result = source.resolve_principal_mapping(
                    "local-principal-source",
                    "subject-alpha",
                )

                self.assertEqual(result.status, expected_status)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)

    def test_conflicting_principal_mappings_fail_closed(self):
        cases = (
            ("authority_reference", {"authority_reference": "principal-map-beta"}),
            ("state", {"state": AuthorityRecordState.STALE}),
            ("principal_id", {"principal_id": "principal-beta"}),
        )

        for name, overrides in cases:
            with self.subTest(name=name):
                source = NonProductionPrincipalMappingAuthoritySource(
                    [
                        mapping(),
                        mapping(**overrides),
                    ]
                )

                result = source.resolve_principal_mapping(
                    "local-principal-source",
                    "subject-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.CONFLICTING)
                self.assertEqual(len(result.records), 2)

    def test_duplicate_applicable_mappings_fail_closed_without_deduplication(self):
        source = NonProductionPrincipalMappingAuthoritySource(
            [
                mapping(),
                mapping(),
            ]
        )

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(len(result.records), 2)

    def test_repeated_lookup_is_deterministic(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])

        first = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )
        second = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(first, second)

    def test_lookup_uses_captured_instance_identity_fields(self):
        class ConfusedPrincipalMapping(PrincipalMapping):
            def __getattribute__(self, name):
                if name == "subject_provider":
                    return "local-principal-source"
                if name == "subject":
                    return "subject-alpha"
                return object.__getattribute__(self, name)

        record = object.__new__(ConfusedPrincipalMapping)
        object.__setattr__(record, "authority_reference", "principal-map-spoof")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "subject_provider", "other-source")
        object.__setattr__(record, "subject", "other-subject")
        object.__setattr__(record, "principal_id", "principal-alpha")
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_benign_mapping_subclass_fails_closed(self):
        class BenignPrincipalMapping(PrincipalMapping):
            pass

        source = NonProductionPrincipalMappingAuthoritySource(
            [
                BenignPrincipalMapping(
                    "principal-map-alpha",
                    AuthorityRecordState.ACTIVE,
                    "local-principal-source",
                    "subject-alpha",
                    "principal-alpha",
                )
            ]
        )

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_mapping_subclass_field_spoofing_fails_closed_before_field_reads(self):
        class SpoofedPrincipalMapping(PrincipalMapping):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in (
                    "authority_reference",
                    "state",
                    "subject_provider",
                    "subject",
                    "principal_id",
                ):
                    type(self).authority_field_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-admin",
                    }[name]
                return object.__getattribute__(self, name)

        record = set_mapping_fields(
            object.__new__(SpoofedPrincipalMapping),
            state=AuthorityRecordState.REVOKED,
            subject_provider="wrong-provider",
            subject="wrong-subject",
            principal_id="wrong-principal",
        )
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(SpoofedPrincipalMapping.authority_field_reads, 0)

    def test_mapping_subclass_raising_getattribute_fails_closed_before_field_reads(self):
        class RaisingPrincipalMapping(PrincipalMapping):
            authority_field_reads = 0

            def __getattribute__(self, name):
                if name in (
                    "authority_reference",
                    "state",
                    "subject_provider",
                    "subject",
                    "principal_id",
                ):
                    type(self).authority_field_reads += 1
                    raise RuntimeError("field unavailable")
                return object.__getattribute__(self, name)

        record = set_mapping_fields(object.__new__(RaisingPrincipalMapping))
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(RaisingPrincipalMapping.authority_field_reads, 0)

    def test_getattr_subclass_fails_closed_before_dynamic_fallback(self):
        class GetattrPrincipalMapping(PrincipalMapping):
            getattr_calls = 0

            def __getattr__(self, name):
                type(self).getattr_calls += 1
                return "forged"

        record = set_mapping_fields(object.__new__(GetattrPrincipalMapping))
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(GetattrPrincipalMapping.getattr_calls, 0)

    def test_forged_dict_cannot_authorize_wrong_actual_provider(self):
        class ForgedDictPrincipalMapping(PrincipalMapping):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-admin",
                    }
                return object.__getattribute__(self, name)

        record = set_mapping_fields(
            object.__new__(ForgedDictPrincipalMapping),
            subject_provider="wrong-provider",
        )
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictPrincipalMapping.dict_reads, 0)

    def test_forged_dict_cannot_authorize_wrong_actual_subject(self):
        class ForgedDictPrincipalMapping(PrincipalMapping):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-admin",
                    }
                return object.__getattribute__(self, name)

        record = set_mapping_fields(
            object.__new__(ForgedDictPrincipalMapping),
            subject="wrong-subject",
        )
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictPrincipalMapping.dict_reads, 0)

    def test_forged_dict_cannot_repair_missing_principal_id(self):
        class ForgedDictPrincipalMapping(PrincipalMapping):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-admin",
                    }
                return object.__getattribute__(self, name)

        record = object.__new__(ForgedDictPrincipalMapping)
        object.__setattr__(record, "authority_reference", "actual-authority")
        object.__setattr__(record, "state", AuthorityRecordState.ACTIVE)
        object.__setattr__(record, "subject_provider", "local-principal-source")
        object.__setattr__(record, "subject", "subject-alpha")
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictPrincipalMapping.dict_reads, 0)

    def test_forged_dict_cannot_reactivate_revoked_or_stale_actual_evidence(self):
        class ForgedDictPrincipalMapping(PrincipalMapping):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "principal-map-alpha",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-alpha",
                    }
                return object.__getattribute__(self, name)

        for state in (AuthorityRecordState.REVOKED, AuthorityRecordState.STALE):
            with self.subTest(state=state):
                ForgedDictPrincipalMapping.dict_reads = 0
                record = set_mapping_fields(
                    object.__new__(ForgedDictPrincipalMapping),
                    state=state,
                )
                source = NonProductionPrincipalMappingAuthoritySource([record])

                result = source.resolve_principal_mapping(
                    "local-principal-source",
                    "subject-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertNotEqual(result.status, AuthorityLookupStatus.FOUND)
                self.assertEqual(result.records, ())
                self.assertEqual(ForgedDictPrincipalMapping.dict_reads, 0)

    def test_forged_dict_cannot_change_returned_authority_values(self):
        class ForgedDictPrincipalMapping(PrincipalMapping):
            dict_reads = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "attacker-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-admin",
                    }
                return object.__getattribute__(self, name)

        record = set_mapping_fields(object.__new__(ForgedDictPrincipalMapping))
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ForgedDictPrincipalMapping.dict_reads, 0)

    def test_dict_property_subclass_is_rejected_before_property_read(self):
        class DictPropertyPrincipalMapping(PrincipalMapping):
            dict_reads = 0

            @property
            def __dict__(self):
                type(self).dict_reads += 1
                return {
                    "authority_reference": "forged-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "subject_provider": "local-principal-source",
                    "subject": "subject-alpha",
                    "principal_id": "principal-admin",
                }

        record = set_mapping_fields(object.__new__(DictPropertyPrincipalMapping))
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictPropertyPrincipalMapping.dict_reads, 0)

    def test_dict_descriptor_subclass_is_rejected_before_descriptor_read(self):
        class DictDescriptor:
            reads = 0

            def __get__(self, instance, owner):
                type(self).reads += 1
                return {
                    "authority_reference": "forged-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "subject_provider": "local-principal-source",
                    "subject": "subject-alpha",
                    "principal_id": "principal-admin",
                }

        class DictDescriptorPrincipalMapping(PrincipalMapping):
            __dict__ = DictDescriptor()

        record = set_mapping_fields(object.__new__(DictDescriptorPrincipalMapping))
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(DictDescriptor.reads, 0)

    def test_combined_field_and_dict_spoofing_cannot_control_authority(self):
        class CombinedSpoofPrincipalMapping(PrincipalMapping):
            field_reads = 0
            dict_reads = 0
            getattr_calls = 0

            def __getattribute__(self, name):
                if name == "__dict__":
                    type(self).dict_reads += 1
                    return {
                        "authority_reference": "forged-authority",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-admin",
                    }
                if name in (
                    "authority_reference",
                    "state",
                    "subject_provider",
                    "subject",
                    "principal_id",
                ):
                    type(self).field_reads += 1
                    return "spoofed"
                return object.__getattribute__(self, name)

            def __getattr__(self, name):
                type(self).getattr_calls += 1
                return "spoofed"

        record = set_mapping_fields(object.__new__(CombinedSpoofPrincipalMapping))
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(CombinedSpoofPrincipalMapping.field_reads, 0)
        self.assertEqual(CombinedSpoofPrincipalMapping.dict_reads, 0)
        self.assertEqual(CombinedSpoofPrincipalMapping.getattr_calls, 0)

    def test_exact_mapping_with_dict_subclass_storage_fails_closed(self):
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
                    "subject_provider": "local-principal-source",
                    "subject": "subject-alpha",
                    "principal_id": "principal-admin",
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

        record = mapping(
            authority_reference="actual-authority",
            state=AuthorityRecordState.REVOKED,
            subject_provider="wrong-provider",
            subject="wrong-subject",
            principal_id="actual-principal",
        )
        object.__setattr__(record, "__dict__", HostileDict())
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(HostileDict.get_calls, 0)
        self.assertEqual(HostileDict.getitem_calls, 0)
        self.assertEqual(HostileDict.contains_calls, 0)
        self.assertEqual(HostileDict.iter_calls, 0)

    def test_validation_use_toctou_dict_subclass_fails_closed(self):
        class ToctouDict(dict):
            get_calls = 0

            def get(self, key, default=None):
                type(self).get_calls += 1
                phase = "validated" if type(self).get_calls <= 5 else "forged"
                if phase == "validated":
                    return {
                        "authority_reference": "principal-map-alpha",
                        "state": AuthorityRecordState.ACTIVE,
                        "subject_provider": "local-principal-source",
                        "subject": "subject-alpha",
                        "principal_id": "principal-alpha",
                    }.get(key, default)
                return {
                    "authority_reference": "attacker-authority",
                    "state": AuthorityRecordState.ACTIVE,
                    "subject_provider": "local-principal-source",
                    "subject": "subject-alpha",
                    "principal_id": "principal-admin",
                }.get(key, default)

        record = mapping()
        object.__setattr__(record, "__dict__", ToctouDict())
        source = NonProductionPrincipalMappingAuthoritySource([record])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())
        self.assertEqual(ToctouDict.get_calls, 0)

    def test_object_new_missing_instance_fields_fail_closed(self):
        required_fields = (
            "authority_reference",
            "state",
            "subject_provider",
            "subject",
            "principal_id",
        )
        values = {
            "authority_reference": "principal-map-alpha",
            "state": AuthorityRecordState.ACTIVE,
            "subject_provider": "local-principal-source",
            "subject": "subject-alpha",
            "principal_id": "principal-alpha",
        }

        for missing in required_fields:
            with self.subTest(missing=missing):
                malformed = object.__new__(PrincipalMapping)
                for name, value in values.items():
                    if name != missing:
                        object.__setattr__(malformed, name, value)
                source = NonProductionPrincipalMappingAuthoritySource([malformed])

                result = source.resolve_principal_mapping(
                    "local-principal-source",
                    "subject-alpha",
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
            ("authority_reference", "principal-map-alpha"),
            ("subject_provider", "local-principal-source"),
            ("subject", "subject-alpha"),
            ("principal_id", "principal-alpha"),
        )

        for field, value in cases:
            with self.subTest(field=field):
                HostileStoredStr.comparisons = 0
                HostileStoredStr.strip_calls = 0
                record = replace(mapping(), **{field: HostileStoredStr(value)})
                source = NonProductionPrincipalMappingAuthoritySource([record])

                result = source.resolve_principal_mapping(
                    "local-principal-source",
                    "subject-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())
                self.assertEqual(HostileStoredStr.comparisons, 0)
                self.assertEqual(HostileStoredStr.strip_calls, 0)

    def test_malformed_authority_fields_fail_closed(self):
        class OtherState(Enum):
            ACTIVE = "ACTIVE"

        cases = (
            ("authority_reference", ""),
            ("authority_reference", "   "),
            ("authority_reference", object()),
            ("state", None),
            ("state", "ACTIVE"),
            ("state", OtherState.ACTIVE),
            ("subject_provider", ""),
            ("subject_provider", "   "),
            ("subject_provider", object()),
            ("subject", ""),
            ("subject", "   "),
            ("subject", object()),
            ("principal_id", ""),
            ("principal_id", "   "),
            ("principal_id", object()),
        )

        for field, value in cases:
            with self.subTest(field=field, value=value):
                record = replace(mapping(), **{field: value})
                source = NonProductionPrincipalMappingAuthoritySource([record])

                result = source.resolve_principal_mapping(
                    "local-principal-source",
                    "subject-alpha",
                )

                self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
                self.assertEqual(result.records, ())

    def test_ambiguous_and_conflicting_outputs_use_safe_exact_records(self):
        duplicate_a = mapping()
        duplicate_b = mapping()
        conflict_a = mapping()
        conflict_b = replace(mapping(), principal_id="principal-beta")

        ambiguous = NonProductionPrincipalMappingAuthoritySource(
            [duplicate_a, duplicate_b]
        ).resolve_principal_mapping("local-principal-source", "subject-alpha")
        conflicting = NonProductionPrincipalMappingAuthoritySource(
            [conflict_a, conflict_b]
        ).resolve_principal_mapping("local-principal-source", "subject-alpha")

        self.assertEqual(ambiguous.status, AuthorityLookupStatus.AMBIGUOUS)
        self.assertEqual(conflicting.status, AuthorityLookupStatus.CONFLICTING)
        for result, originals in (
            (ambiguous, (duplicate_a, duplicate_b)),
            (conflicting, (conflict_a, conflict_b)),
        ):
            for returned in result.records:
                self.assertIs(type(returned), PrincipalMapping)
                for original in originals:
                    self.assertIsNot(returned, original)

    def test_record_order_cannot_create_positive_authority_from_multiple_records(self):
        duplicate_a = mapping()
        duplicate_b = mapping()
        conflict_a = mapping()
        conflict_b = replace(mapping(), principal_id="principal-beta")

        duplicate_forward = NonProductionPrincipalMappingAuthoritySource(
            [duplicate_a, duplicate_b]
        ).resolve_principal_mapping("local-principal-source", "subject-alpha")
        duplicate_reverse = NonProductionPrincipalMappingAuthoritySource(
            [duplicate_b, duplicate_a]
        ).resolve_principal_mapping("local-principal-source", "subject-alpha")
        conflict_forward = NonProductionPrincipalMappingAuthoritySource(
            [conflict_a, conflict_b]
        ).resolve_principal_mapping("local-principal-source", "subject-alpha")
        conflict_reverse = NonProductionPrincipalMappingAuthoritySource(
            [conflict_b, conflict_a]
        ).resolve_principal_mapping("local-principal-source", "subject-alpha")

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
        records = [mapping(subject="subject-original")]
        source = NonProductionPrincipalMappingAuthoritySource(records)
        records.append(mapping(subject="subject-added"))
        records.clear()

        original = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-original",
        )
        added = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-added",
        )

        self.assertEqual(original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(added.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(added.records, ())

    def test_source_consumes_generator_during_constructor_snapshot_creation(self):
        records = iter([mapping()])
        source = NonProductionPrincipalMappingAuthoritySource(records)

        first = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )
        second = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(first.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(second.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(first.records, second.records)

    def test_original_record_mutation_after_construction_cannot_change_authority(self):
        original = mapping()
        source = NonProductionPrincipalMappingAuthoritySource([original])
        before = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        with self.assertRaises(FrozenInstanceError):
            original.subject = "mutated-subject"
        object.__setattr__(original, "authority_reference", "mutated-authority")
        object.__setattr__(original, "state", AuthorityRecordState.REVOKED)
        object.__setattr__(original, "subject_provider", "mutated-provider")
        object.__setattr__(original, "subject", "mutated-subject")
        object.__setattr__(original, "principal_id", "principal-admin")

        after_original = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )
        after_mutated = source.resolve_principal_mapping(
            "mutated-provider",
            "mutated-subject",
        )

        self.assertEqual(before.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_original.status, AuthorityLookupStatus.FOUND)
        self.assertEqual(after_mutated.status, AuthorityLookupStatus.NOT_FOUND)
        self.assertEqual(after_original.records[0].authority_reference, "principal-map-alpha")
        self.assertEqual(after_original.records[0].state, AuthorityRecordState.ACTIVE)
        self.assertEqual(after_original.records[0].subject_provider, "local-principal-source")
        self.assertEqual(after_original.records[0].subject, "subject-alpha")
        self.assertEqual(after_original.records[0].principal_id, "principal-alpha")

    def test_valid_record_plus_malformed_evidence_fails_closed_globally(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping(), object()])

        result = source.resolve_principal_mapping(
            "local-principal-source",
            "subject-alpha",
        )

        self.assertEqual(result.status, AuthorityLookupStatus.MALFORMED)
        self.assertEqual(result.records, ())

    def test_verified_subject_evidence_does_not_create_mapping(self):
        source = NonProductionPrincipalMappingAuthoritySource()
        evaluator = TrustedAuthorizationEvaluator(source)

        result = evaluator.evaluate(request())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.PRINCIPAL_UNRESOLVED)

    def test_principal_mapping_alone_does_not_create_downstream_authority(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        evaluator = TrustedAuthorizationEvaluator(source)

        result = evaluator.evaluate(request())

        self.assertEqual(result.decision, AuthorizationDecision.DENY)
        self.assertEqual(result.reason, ReasonCategory.UNKNOWN_STATE)
        self.assertEqual(result.audit_evidence.principal_id, "principal-alpha")
        self.assertIn(
            "principal_mapping:principal-map-alpha",
            result.audit_evidence.authority_inputs,
        )
        self.assertIn(
            "resource_identity:UNSUPPORTED",
            result.audit_evidence.authority_inputs,
        )

    def test_unsupported_authority_categories_return_no_positive_authority(self):
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        lookups = (
            source.resolve_resource("resource-alpha"),
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
        source = NonProductionPrincipalMappingAuthoritySource([mapping()])
        forbidden_names = (
            "add_mapping",
            "create_mapping",
            "update_mapping",
            "delete_mapping",
            "remove_mapping",
            "revoke_mapping",
            "restore_mapping",
            "reactivate_mapping",
            "assign_principal",
            "mutate_mapping",
            "save_mapping",
            "write_mapping",
        )

        for name in forbidden_names:
            with self.subTest(name=name):
                self.assertFalse(hasattr(source, name))

    def test_source_module_exposes_no_final_decision_surface(self):
        forbidden_names = (
            "AuthorizationDecision",
            "AuthorizationResult",
            "ALLOW",
            "_allow",
            "_deny",
            "ReasonCategory",
        )

        for name in forbidden_names:
            with self.subTest(name=name):
                self.assertFalse(hasattr(principal_mapping_source_module, name))

    def test_source_is_not_exported_from_package_root(self):
        self.assertFalse(
            hasattr(
                trusted_authorization_package,
                "NonProductionPrincipalMappingAuthoritySource",
            )
        )

    def test_source_keeps_only_constructor_supplied_records(self):
        first = mapping()
        second = replace(first, authority_reference="principal-map-beta")
        source = NonProductionPrincipalMappingAuthoritySource([first, second])

        self.assertEqual(
            source.__slots__,
            ("_has_malformed_evidence", "_principal_mappings"),
        )
        self.assertEqual(source._principal_mappings, (first, second))
        self.assertIsNot(source._principal_mappings[0], first)
        self.assertIsNot(source._principal_mappings[1], second)


if __name__ == "__main__":
    unittest.main()
