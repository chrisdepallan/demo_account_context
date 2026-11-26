"""Tests for HMAC-SHA256 signing and verification of webhook deliveries."""

import hashlib
import hmac
import unittest

from acme_webhooks import (
    DEFAULT_TOLERANCE_SECONDS,
    SIGNATURE_HEADER,
    SignatureVerificationError,
    build_signature_header,
    compute_signature,
    generate_secret,
    is_valid_signature,
    parse_signature_header,
    verify_signature,
)

SECRET = "whsec_EXAMPLE_NOT_A_REAL_SECRET"
OLD_SECRET = "whsec_EXAMPLE_OLD_NOT_A_REAL_SECRET"
TIMESTAMP = 1795701780
BODY = b'{"id":"evt_3N7Q1Z8K4B","type":"task.completed"}'


class ComputeTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(SIGNATURE_HEADER, "Acme-Signature")
        self.assertEqual(DEFAULT_TOLERANCE_SECONDS, 300)

    def test_signature_is_hmac_sha256_of_timestamp_dot_body(self):
        expected = hmac.new(
            SECRET.encode(), b"1795701780." + BODY, hashlib.sha256
        ).hexdigest()
        self.assertEqual(compute_signature(SECRET, TIMESTAMP, BODY), expected)
        self.assertEqual(len(expected), 64)

    def test_str_and_bytes_payloads_sign_the_same(self):
        self.assertEqual(
            compute_signature(SECRET, TIMESTAMP, BODY),
            compute_signature(SECRET, TIMESTAMP, BODY.decode()),
        )

    def test_empty_secret_is_rejected(self):
        with self.assertRaises(ValueError):
            compute_signature("", TIMESTAMP, BODY)

    def test_generated_secret_format(self):
        secret = generate_secret()
        self.assertTrue(secret.startswith("whsec_"))
        self.assertEqual(len(secret), len("whsec_") + 32)
        self.assertNotEqual(secret, generate_secret())


class HeaderTests(unittest.TestCase):
    def test_header_format(self):
        header = build_signature_header(SECRET, BODY, TIMESTAMP)
        self.assertEqual(header, f"t={TIMESTAMP},v1={compute_signature(SECRET, TIMESTAMP, BODY)}")

    def test_parse_round_trip(self):
        timestamp, signatures = parse_signature_header(
            build_signature_header([SECRET, OLD_SECRET], BODY, TIMESTAMP)
        )
        self.assertEqual(timestamp, TIMESTAMP)
        self.assertEqual(len(signatures), 2)

    def test_parse_ignores_unknown_keys_and_spaces(self):
        timestamp, signatures = parse_signature_header("t=10, v2=zzz, v1=abc")
        self.assertEqual((timestamp, signatures), (10, ["abc"]))

    def test_parse_rejects_malformed_headers(self):
        for header in ("", "v1=abc", "t=10", "t=soon,v1=abc", "garbage"):
            with self.assertRaises(SignatureVerificationError, msg=header):
                parse_signature_header(header)


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.header = build_signature_header(SECRET, BODY, TIMESTAMP)

    def test_valid_signature_returns_timestamp(self):
        self.assertEqual(verify_signature(SECRET, BODY, self.header, now=TIMESTAMP + 5), TIMESTAMP)

    def test_wrong_secret_fails(self):
        with self.assertRaises(SignatureVerificationError):
            verify_signature(OLD_SECRET, BODY, self.header, now=TIMESTAMP)

    def test_modified_body_fails(self):
        self.assertFalse(is_valid_signature(SECRET, BODY + b" ", self.header, now=TIMESTAMP))

    def test_tolerance_is_five_minutes_both_ways(self):
        self.assertTrue(is_valid_signature(SECRET, BODY, self.header, now=TIMESTAMP + 300))
        self.assertFalse(is_valid_signature(SECRET, BODY, self.header, now=TIMESTAMP + 301))
        self.assertTrue(is_valid_signature(SECRET, BODY, self.header, now=TIMESTAMP - 300))
        self.assertFalse(is_valid_signature(SECRET, BODY, self.header, now=TIMESTAMP - 301))

    def test_custom_tolerance(self):
        self.assertTrue(
            is_valid_signature(SECRET, BODY, self.header, tolerance=3600, now=TIMESTAMP + 900)
        )

    def test_rotation_overlap_accepts_old_and_new_secret(self):
        header = build_signature_header([SECRET, OLD_SECRET], BODY, TIMESTAMP)
        self.assertTrue(is_valid_signature(SECRET, BODY, header, now=TIMESTAMP))
        self.assertTrue(is_valid_signature(OLD_SECRET, BODY, header, now=TIMESTAMP))
        self.assertFalse(is_valid_signature("whsec_EXAMPLE_OTHER", BODY, header, now=TIMESTAMP))

    def test_is_valid_signature_never_raises(self):
        self.assertFalse(is_valid_signature(SECRET, BODY, "", now=TIMESTAMP))
        self.assertFalse(is_valid_signature(SECRET, BODY, "t=1,v1=é", now=1))
        self.assertFalse(is_valid_signature("", BODY, self.header, now=TIMESTAMP))


if __name__ == "__main__":
    unittest.main()
