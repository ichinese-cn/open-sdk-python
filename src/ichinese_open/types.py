"""Typed shapes of the answers the hand-written part returns (``TypedDict``, so they stay plain dicts)."""
from __future__ import annotations

import sys
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Literal, NotRequired, TypedDict
else:  # pragma: no cover
    from typing import Literal, TypedDict

    try:
        from typing_extensions import NotRequired
    except ImportError:  # typing_extensions is optional; fall back to a plain alias
        NotRequired = Optional  # type: ignore[assignment,misc]

TokenType = Literal["app", "tenant", "user"]


class UserAccessToken(TypedDict):
    """What ``exchange_auth_code`` and ``refresh_user_token`` return."""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    open_id: str
    scopes: List[str]
    denied_scopes: List[str]
    tenant_key: NotRequired[Optional[str]]


class TenantAccessToken(TypedDict):
    tenant_access_token: str
    expires_in: int
    tenant_key: str
    scopes: List[str]


class EventHeader(TypedDict):
    event_id: str
    event_type: str
    create_time: str
    app_id: str
    tenant_key: NotRequired[Optional[str]]


class EventEnvelope(TypedDict):
    """An event push (``schema`` ``"1.0"``); dedupe by ``header["event_id"]``: retries keep it."""

    schema: str
    header: EventHeader
    event: Dict[str, Any]


class UrlVerification(TypedDict):
    """The address check: answer with ``challenge_response(v)``."""

    type: Literal["url_verification"]
    challenge: str


class CardAction(TypedDict):
    """A card callback (a button of a bot's card was clicked)."""

    schema: str
    header: Dict[str, Any]
    operator: NotRequired[Dict[str, Any]]
    action: Dict[str, Any]
    message_id: NotRequired[str]


class Page(TypedDict):
    """One page of a cursor-paged list."""

    items: List[Dict[str, Any]]
    has_more: bool
    page_token: NotRequired[Optional[str]]


#: An HTTP transport: ``(method, url, headers, body or None, timeout seconds) -> (status, headers, body)``.
#: Raise ``TimeoutError`` for a timeout and ``OSError`` for other network failures.
Transport = Callable[[str, str, Mapping[str, str], Optional[bytes], float], Tuple[int, Mapping[str, str], bytes]]
