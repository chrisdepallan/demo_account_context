"""Tests for acme_audit_log.entries and acme_audit_log.hash_chain."""

import dataclasses
import re
import unittest
from datetime import datetime, timedelta, timezone

from acme_audit_log import (
    GENESIS_HASH,
    AuditEntry,
    EntryValidationError,
    EventCategory,
    HashChain,
    canonical_json,
    category_for,
    compute_hash,
    is_recorded,
    new_entry_id,
    validate_entry,
    verify_chain,
)

T0 = datetime(2026, 11, 26, 9, 30, tzinfo=timezone.utc)


def make_entry(n=0, **overrides):
    values = dict(
        id=f"aud_7H2KQ9M4{n:02d}",
        account_id="acc_7F3K9Q2M",
        occurred_at=T0 + timedelta(minutes=n),
        event_type="member.invited",
        actor_type="user",
        actor_id="admin@customer.example",
        workspace_id="ws_4H8P2L",
        ip_address="203.0.113.10",
        metadata={"role": "Member"},
    )
    values.update(overrides)
    return AuditEntry(**values)


class EntryTests(unittest.TestCase):
    def test_valid_entry_passes_and_has_category(self):
        entry = validate_entry(make_entry())
        self.assertIs(entry.category, EventCategory.MEMBERS)

    def test_new_entry_id_format(self):
        ids = {new_entry_id() for _ in range(50)}
        self.assertEqual(len(ids), 50)
        self.assertTrue(all(re.match(r"^aud_[A-Z0-9]{10}$", value) for value in ids))

    def test_categories(self):
        self.assertIs(category_for("login.failed"), EventCategory.AUTHENTICATION)
        self.assertIs(category_for("api_key.revoked"), EventCategory.SECURITY)
        self.assertIs(category_for("file.deleted"), EventCategory.DATA)
        self.assertIs(category_for("invoice.paid"), EventCategory.BILLING)
        self.assertIs(category_for("account.closed"), EventCategory.ACCOUNT)
        self.assertIs(category_for("audit_log.exported"), EventCategory.AUDIT)

    def test_bad_event_types_are_rejected(self):
        for event_type in ("MemberInvited", "member", "member.", "comment.created"):
            with self.assertRaises(EntryValidationError, msg=event_type):
                category_for(event_type)

    def test_bad_ids_are_rejected(self):
        for overrides in (
            {"id": "aud_short"},
            {"account_id": "acc_lowercase"},
            {"workspace_id": "ws_TOOLONG99"},
            {"region": "eu-west"},
            {"ip_address": "999.1.1.1"},
            {"actor_type": "robot"},
            {"actor_id": ""},
        ):
            with self.assertRaises(EntryValidationError, msg=str(overrides)):
                validate_entry(make_entry(**overrides))

    def test_timestamp_must_be_timezone_aware(self):
        with self.assertRaises(EntryValidationError):
            validate_entry(make_entry(occurred_at=datetime(2026, 11, 26, 9, 30)))

    def test_support_actor_needs_ticket(self):
        with self.assertRaises(EntryValidationError):
            validate_entry(make_entry(actor_type="support", actor_id="agent"))
        validate_entry(make_entry(actor_type="support", actor_id="SUP-48213"))

    def test_metadata_rules(self):
        for metadata in (
            {"new_password": "x"},
            {"nested": {"a": 1}},
            {f"k{i}": i for i in range(21)},
            {"note": "x" * 5000},
        ):
            with self.assertRaises(EntryValidationError):
                validate_entry(make_entry(metadata=metadata))

    def test_is_recorded_by_plan(self):
        self.assertFalse(is_recorded("member.invited", "Free"))
        self.assertFalse(is_recorded("member.invited", "Starter"))
        self.assertTrue(is_recorded("member.invited", "Pro"))
        self.assertFalse(is_recorded("file.downloaded", "Business"))
        self.assertTrue(is_recorded("file.downloaded", "Enterprise"))
        self.assertFalse(is_recorded("comment.created", "Enterprise"))

    def test_entry_is_immutable(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            make_entry().event_type = "member.removed"


class HashChainTests(unittest.TestCase):
    def build(self, count=5):
        chain = HashChain()
        for n in range(count):
            chain.append(make_entry(n))
        return chain

    def test_first_entry_links_to_genesis(self):
        chain = self.build(1)
        first = chain.entries[0]
        self.assertEqual(first.prev_hash, GENESIS_HASH)
        self.assertEqual(first.sequence, 1)
        self.assertEqual(first.hash, compute_hash(GENESIS_HASH, 1, first.entry))
        self.assertRegex(first.hash, r"^[0-9a-f]{64}$")

    def test_entries_are_linked_and_head_moves(self):
        chain = self.build(3)
        items = chain.entries
        self.assertEqual(items[1].prev_hash, items[0].hash)
        self.assertEqual(items[2].prev_hash, items[1].hash)
        self.assertEqual(chain.head, items[2].hash)
        self.assertEqual(len(chain), 3)

    def test_empty_and_intact_chains_verify(self):
        self.assertTrue(HashChain().verify().valid)
        result = self.build().verify()
        self.assertTrue(result.valid)
        self.assertEqual(result.checked, 5)

    def test_canonical_json_is_timezone_independent(self):
        utc = make_entry()
        shifted = make_entry(occurred_at=T0.astimezone(timezone(timedelta(hours=5, minutes=30))))
        self.assertEqual(canonical_json(utc), canonical_json(shifted))

    def test_modified_entry_is_detected(self):
        items = list(self.build().entries)
        tampered = dataclasses.replace(items[2].entry, actor_id="intruder@customer.example")
        items[2] = dataclasses.replace(items[2], entry=tampered)
        result = verify_chain(items)
        self.assertFalse(result.valid)
        self.assertEqual((result.first_invalid_sequence, result.reason), (3, "hash_mismatch"))
        self.assertEqual(result.checked, 2)

    def test_removed_entry_is_detected(self):
        items = list(self.build().entries)
        del items[1]
        result = verify_chain(items)
        self.assertEqual((result.valid, result.first_invalid_sequence), (False, 3))
        self.assertEqual(result.reason, "prev_hash_mismatch")

    def test_reordered_entries_are_detected(self):
        items = list(self.build().entries)
        items[1], items[2] = items[2], items[1]
        self.assertFalse(verify_chain(items).valid)

    def test_verification_after_purge_uses_checkpoint(self):
        items = list(self.build().entries)
        kept = items[2:]
        self.assertFalse(verify_chain(kept).valid)
        self.assertTrue(verify_chain(kept, start_hash=items[1].hash).valid)

    def test_append_rejects_invalid_and_foreign_entries(self):
        chain = self.build(1)
        with self.assertRaises(EntryValidationError):
            chain.append(make_entry(1, event_type="comment.created"))
        with self.assertRaises(ValueError):
            chain.append(make_entry(1, account_id="acc_9Z8Y7X6W"))
        self.assertEqual(len(chain), 1)


if __name__ == "__main__":
    unittest.main()
