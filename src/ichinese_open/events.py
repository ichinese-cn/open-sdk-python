"""Event pushes and card callbacks from the platform to your request address: checking the signature,
decrypting, and answering the address check::

    X-Ich-Signature: v1=hex(HMAC-SHA256(signing secret, timestamp + "." + nonce + "." + raw body))
    encrypted body:  {"encrypt": base64(12-byte IV || AES-256-GCM ciphertext || 16-byte tag)},
                     key = SHA-256(encrypt key)

Always verify against the raw body bytes as received (not re-serialized JSON). Decrypting needs the
optional ``cryptography`` package (``pip install "ichinese-open-sdk[crypto]"``).
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import re
import time
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union, cast

from .errors import OpenApiError
from .types import CardAction, EventEnvelope, UrlVerification

#: Request headers: a dict (any case), ``http.client.HTTPMessage``, ``wsgiref``-style list of pairs, or
#: anything with ``items()``.
Headers = Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]
Body = Union[str, bytes, bytearray]

_DIGITS = re.compile(r"^\d+$")


def _bytes(body: Body) -> bytes:
    return body.encode("utf-8") if isinstance(body, str) else bytes(body)


def _header(headers: Headers, name: str) -> Optional[str]:
    items = headers.items() if hasattr(headers, "items") else headers  # type: ignore[union-attr]
    lname = name.lower()
    for k, v in items:  # type: ignore[misc]
        if str(k).lower() == lname:
            if isinstance(v, (list, tuple)):
                v = v[0] if v else None
            return None if v is None else str(v)
    return None


def sign(signing_secret: str, timestamp: str, nonce: str, body: Body) -> str:
    """The signature the platform puts in ``X-Ich-Signature`` for these values."""
    msg = f"{timestamp}.{nonce}.".encode("utf-8") + _bytes(body)
    return "v1=" + hmac.new(signing_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def verify_signature(
    headers: Headers,
    raw_body: Body,
    signing_secret: str,
    tolerance_seconds: float = 300,
    now: Optional[float] = None,
) -> None:
    """Checks a push's signature and age (default: at most 5 minutes off; ``now`` in Unix seconds).
    Raises ``OpenApiError`` with code ``INVALID_SIGNATURE`` otherwise."""

    def fail(message: str) -> None:
        raise OpenApiError(401, "INVALID_SIGNATURE", message)

    timestamp = _header(headers, "x-ich-timestamp")
    nonce = _header(headers, "x-ich-nonce")
    signature = _header(headers, "x-ich-signature")
    if not timestamp or not nonce or not signature:
        return fail("missing X-Ich-Timestamp, X-Ich-Nonce or X-Ich-Signature")
    current = int(time.time() if now is None else now)
    if not _DIGITS.match(timestamp) or abs(current - int(timestamp)) > tolerance_seconds:
        return fail("the timestamp is too far from now")
    expected = sign(signing_secret, timestamp, nonce, raw_body).encode("utf-8")
    if not hmac.compare_digest(expected, signature.encode("utf-8")):
        fail("the signature does not match")


def decrypt(encrypted: str, encrypt_key: str) -> str:
    """Decrypts an ``{"encrypt": …}`` body with the app's encrypt key (needs ``cryptography``)."""
    try:
        from cryptography.exceptions import InvalidTag
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as e:  # pragma: no cover - depends on the environment
        raise RuntimeError(
            'decrypting events needs the "cryptography" package: pip install "ichinese-open-sdk[crypto]"'
        ) from e
    try:
        data = base64.b64decode(encrypted, validate=False)
    except (binascii.Error, ValueError):
        raise OpenApiError(400, "INVALID_PAYLOAD", "not base64") from None
    if len(data) < 12 + 16:
        raise OpenApiError(400, "INVALID_PAYLOAD", "too short")
    key = hashlib.sha256(encrypt_key.encode("utf-8")).digest()
    try:
        # AESGCM takes ciphertext || tag, exactly what follows the IV.
        return AESGCM(key).decrypt(data[:12], data[12:], None).decode("utf-8")
    except (InvalidTag, UnicodeDecodeError):
        raise OpenApiError(400, "INVALID_PAYLOAD", "cannot decrypt (wrong encrypt key?)") from None


def parse_event(
    headers: Headers,
    raw_body: Body,
    signing_secret: str,
    encrypt_key: Optional[str] = None,
    tolerance_seconds: float = 300,
    now: Optional[float] = None,
) -> Union[EventEnvelope, UrlVerification]:
    """Verifies, decrypts and parses a push. Answer a ``url_verification`` with
    ``challenge_response(v)``, and an event with any 2xx within 5 seconds (dedupe by
    ``header["event_id"]``: retries keep it)."""
    verify_signature(headers, raw_body, signing_secret, tolerance_seconds, now)
    try:
        payload: Dict[str, Any] = json.loads(_bytes(raw_body).decode("utf-8"))
    except ValueError:
        raise OpenApiError(400, "INVALID_PAYLOAD", "the body is not JSON") from None
    if isinstance(payload, dict) and isinstance(payload.get("encrypt"), str):
        if not encrypt_key:
            raise OpenApiError(400, "INVALID_PAYLOAD", "encrypted push but no encrypt_key")
        payload = json.loads(decrypt(payload["encrypt"], encrypt_key))
    return cast(Union[EventEnvelope, UrlVerification], payload)


def parse_card_action(
    headers: Headers,
    raw_body: Body,
    signing_secret: str,
    encrypt_key: Optional[str] = None,
    tolerance_seconds: float = 300,
    now: Optional[float] = None,
) -> Union[CardAction, UrlVerification]:
    """A card callback (a button of a bot's card was clicked): same signature and encryption as events."""
    return cast(
        Union[CardAction, UrlVerification],
        parse_event(headers, raw_body, signing_secret, encrypt_key, tolerance_seconds, now),
    )


def is_url_verification(x: Any) -> bool:
    """Whether a parsed push is the address check."""
    return isinstance(x, dict) and x.get("type") == "url_verification"


def challenge_response(v: Mapping[str, Any]) -> Dict[str, str]:
    """The answer to the address check (send it as JSON)."""
    return {"challenge": v["challenge"]}
