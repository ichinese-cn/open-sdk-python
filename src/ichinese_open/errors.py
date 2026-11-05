"""The open API's error type."""
from __future__ import annotations

from typing import Any, Dict, Optional

SCOPE_REASONS = ("scope_denied", "scope_pending", "scope_not_declared", "gold_only")


class OpenApiError(Exception):
    """An error answer of the open API (``{"error": {"code", "message", "request_id", "details"}}``),
    or a failure before one came (``code`` ``NETWORK`` / ``TIMEOUT`` / ``TOKEN_REQUIRED``, ``status`` 0).

    Attributes:
        status: HTTP status (0: no answer).
        code: stable error code: ``UNAUTHENTICATED``, ``FORBIDDEN``, ``NOT_FOUND``, ``VALIDATION_FAILED``,
            ``RATE_LIMITED``, … (``HTTP_<status>`` when the answer had no JSON error).
        message: human-readable message.
        request_id: the platform's request id (quote it when asking for support).
        reason: ``details.reason``, e.g. ``scope_denied``, ``token_expired``, ``code_used``.
        details: the error's ``details`` object.
        retry_after: seconds to wait (429), from ``Retry-After``.
    """

    def __init__(
        self,
        status: int,
        code: str,
        message: str = "",
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[float] = None,
    ) -> None:
        super().__init__(message or code)
        self.status = status
        self.code = code
        self.message = message or code
        self.request_id = request_id
        self.details: Dict[str, Any] = details if isinstance(details, dict) else {}
        reason = self.details.get("reason")
        self.reason: Optional[str] = reason if isinstance(reason, str) else None
        self.retry_after = retry_after

    @property
    def scope(self) -> Optional[str]:
        """The scope the user or institution refused (``scope_denied``): the app should do without it."""
        s = self.details.get("scope")
        return s if isinstance(s, str) else None

    @property
    def never_ask(self) -> bool:
        """The user chose「不再询问」(never ask) for the refused scope: do not ask again."""
        return self.details.get("never_ask") is True

    @property
    def is_scope_error(self) -> bool:
        """A refused, not yet asked or undeclared scope (403): degrade gracefully."""
        return self.status == 403 and self.reason in SCOPE_REASONS

    def __str__(self) -> str:
        rid = f" (request_id {self.request_id})" if self.request_id else ""
        return f"{self.status} {self.code}: {self.message}{rid}"

    def __repr__(self) -> str:
        return f"OpenApiError(status={self.status!r}, code={self.code!r}, reason={self.reason!r}, request_id={self.request_id!r})"
