import json
import os
import unittest

from ichinese_open import OpenApiError, challenge_response, decrypt, is_url_verification, parse_event, sign, verify_signature

try:
    import cryptography  # noqa: F401

    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

# Beside this file in the SDK's own repository; in the monorepo, shared by every SDK.
VECTORS_PATH = os.path.join(os.path.dirname(__file__), "test-vectors.json")
if not os.path.exists(VECTORS_PATH):
    VECTORS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test-vectors.json")
try:
    with open(VECTORS_PATH, encoding="utf-8") as f:
        V = json.load(f)
except OSError:
    V = None

needs_vectors = unittest.skipIf(V is None, "test-vectors.json not found")
needs_crypto = unittest.skipUnless(HAS_CRYPTO, 'needs "cryptography" (pip install "ichinese-open-sdk[crypto]")')


def headers(signature, ts=None):
    return {"X-Ich-Timestamp": ts or V["timestamp"], "x-ich-nonce": V["nonce"], "X-ICH-SIGNATURE": signature}


@needs_vectors
class SignatureTest(unittest.TestCase):
    now = None

    def setUp(self):
        self.now = int(V["timestamp"]) + 10

    def test_sign_matches_vectors(self):
        self.assertEqual(sign(V["signing_secret"], V["timestamp"], V["nonce"], V["plain_body"]), V["plain_signature"])
        self.assertEqual(
            sign(V["signing_secret"], V["timestamp"], V["nonce"], V["encrypted_body"].encode()), V["encrypted_signature"]
        )

    def test_verify_plain_and_encrypted(self):
        verify_signature(headers(V["plain_signature"]), V["plain_body"].encode("utf-8"), V["signing_secret"], now=self.now)
        verify_signature(headers(V["encrypted_signature"]), V["encrypted_body"], V["signing_secret"], now=self.now)

    def test_header_pairs_are_accepted(self):
        pairs = list(headers(V["plain_signature"]).items())
        verify_signature(pairs, V["plain_body"], V["signing_secret"], now=self.now)

    def test_wrong_signature_is_rejected(self):
        with self.assertRaises(OpenApiError) as ctx:
            verify_signature(headers(V["plain_signature"]), V["plain_body"] + " ", V["signing_secret"], now=self.now)
        self.assertEqual(ctx.exception.code, "INVALID_SIGNATURE")
        with self.assertRaises(OpenApiError):
            verify_signature(headers(V["plain_signature"]), V["plain_body"], "other-secret", now=self.now)

    def test_old_timestamp_is_rejected(self):
        with self.assertRaises(OpenApiError) as ctx:
            verify_signature(headers(V["plain_signature"]), V["plain_body"], V["signing_secret"], now=self.now + 400)
        self.assertEqual(ctx.exception.code, "INVALID_SIGNATURE")
        verify_signature(
            headers(V["plain_signature"]), V["plain_body"], V["signing_secret"], tolerance_seconds=600, now=self.now + 400
        )

    def test_missing_headers_are_rejected(self):
        with self.assertRaises(OpenApiError) as ctx:
            verify_signature({}, V["plain_body"], V["signing_secret"], now=self.now)
        self.assertEqual(ctx.exception.code, "INVALID_SIGNATURE")

    def test_parse_plain_event(self):
        ev = parse_event(headers(V["plain_signature"]), V["plain_body"], V["signing_secret"], now=self.now)
        self.assertEqual(ev, json.loads(V["decrypted"]))
        self.assertEqual(ev["header"]["event_type"], "app.installed")
        self.assertEqual(ev["event"]["名称"], "演示")

    def test_url_verification(self):
        body = json.dumps({"type": "url_verification", "challenge": "ch-1"})
        h = {"X-Ich-Timestamp": V["timestamp"], "X-Ich-Nonce": "n", "X-Ich-Signature": sign("s", V["timestamp"], "n", body)}
        v = parse_event(h, body, "s", now=self.now)
        self.assertTrue(is_url_verification(v))
        self.assertEqual(challenge_response(v), {"challenge": "ch-1"})


@needs_vectors
@needs_crypto
class DecryptTest(unittest.TestCase):
    def test_decrypt_matches_vectors(self):
        enc = json.loads(V["encrypted_body"])["encrypt"]
        self.assertEqual(decrypt(enc, V["encrypt_key"]), V["decrypted"])

    def test_wrong_key(self):
        enc = json.loads(V["encrypted_body"])["encrypt"]
        with self.assertRaises(OpenApiError) as ctx:
            decrypt(enc, "wrong")
        self.assertEqual(ctx.exception.code, "INVALID_PAYLOAD")

    def test_parse_encrypted_event(self):
        now = int(V["timestamp"])
        ev = parse_event(headers(V["encrypted_signature"]), V["encrypted_body"], V["signing_secret"], V["encrypt_key"], now=now)
        self.assertEqual(ev, json.loads(V["decrypted"]))
        with self.assertRaises(OpenApiError) as ctx:
            parse_event(headers(V["encrypted_signature"]), V["encrypted_body"], V["signing_secret"], now=now)
        self.assertEqual(ctx.exception.code, "INVALID_PAYLOAD")


class MetaTest(unittest.TestCase):
    def test_constants(self):
        from ichinese_open import ERROR_REASONS, EVENT_TYPES, OPERATION_TOKENS, SCOPES, VERSION, Client

        self.assertIn("org:member:readonly", SCOPES)
        self.assertIn("app.installed", EVENT_TYPES)
        self.assertIn("scope_denied", ERROR_REASONS)
        self.assertEqual(OPERATION_TOKENS["get_tenant"], ("tenant",))
        self.assertRegex(VERSION, r"^\d+\.\d+\.\d+")
        for name in OPERATION_TOKENS:
            self.assertTrue(callable(getattr(Client, name)), name)


if __name__ == "__main__":
    unittest.main()
