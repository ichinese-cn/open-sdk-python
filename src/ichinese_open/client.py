"""The open platform's server SDK for Python (M4.85).

Every operation of the open API as a method (generated from docs/api/open-api.yaml), plus what each app
would otherwise write itself: getting the app and tenant tokens and renewing them before they expire,
retrying after rate limits and server errors with backoff, paging through lists, typed errors, and
exchanging the web login's codes::

    client = Client(os.environ["APP_ID"], os.environ["APP_SECRET"])
    for m in client.iter_list_tenant_members(tenant_key=tenant_key):
        print(m["name"])
    user = client.exchange_auth_code(code)            # the code from the JS SDK
    me = client.get_user_info(user_access_token=user["access_token"])
"""
from __future__ import annotations

import json
import random
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterator, Mapping, Optional, Sequence, Tuple, cast

from ._meta import API_PREFIX, DEFAULT_BASE_URL, VERSION
from ._operations import Operations
from .errors import OpenApiError
from .types import Transport, UserAccessToken

RETRY_STATUSES = frozenset((500, 502, 503, 504))
IDEMPOTENT = frozenset(("GET", "PUT", "DELETE"))


def urllib_transport(
    method: str, url: str, headers: Mapping[str, str], body: Optional[bytes], timeout: float
) -> Tuple[int, Mapping[str, str], bytes]:
    """The default transport (the standard library's urllib)."""
    req = urllib.request.Request(url, data=body, method=method, headers=dict(headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status, dict(res.headers.items()), res.read()
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b""
        finally:
            e.close()
        return e.code, dict(e.headers.items()) if e.headers else {}, data
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            raise TimeoutError(str(e.reason)) from e
        raise OSError(str(e.reason)) from e
    except socket.timeout as e:
        raise TimeoutError(str(e)) from e


class _Cached:
    __slots__ = ("token", "expires_at")

    def __init__(self, token: str, expires_at: float) -> None:
        self.token = token
        self.expires_at = expires_at


class Client(Operations):
    """A client of the open API for one app.

    Args:
        app_id: the App ID from the developer console.
        app_secret: the App Secret (keep it on your server).
        base_url: the open API's address (default ``DEFAULT_BASE_URL``, from the release configuration).
            One address for every region: tokens carry their region and the gateway routes by it.
        max_retries: retries after a rate limit (429), a server error (5xx) or a network failure. Default 3.
        timeout: per request, in seconds. Default 30.
        transport: your own HTTP function (tests, proxies, ``requests``); see ``types.Transport``.
        refresh_before_seconds: renew a cached app or tenant token this many seconds before it expires.
        user_agent: appended to the ``User-Agent`` header.

    The client is thread-safe: one instance can serve every thread of your app.
    """

    #: Base of the retry backoff in seconds (tests make it small).
    retry_base_seconds: float = 0.5

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        *,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 30.0,
        transport: Optional[Transport] = None,
        refresh_before_seconds: float = 300,
        user_agent: Optional[str] = None,
    ) -> None:
        if not app_id or not app_secret:
            raise TypeError("app_id and app_secret are required")
        self.app_id = app_id
        self._app_secret = app_secret
        base = (base_url or DEFAULT_BASE_URL).rstrip("/")
        if base.endswith(API_PREFIX):
            base = base[: -len(API_PREFIX)]
        self.base_url = base
        self.max_retries = max_retries
        self.timeout = timeout
        self._transport: Transport = transport or urllib_transport
        self.refresh_before_seconds = refresh_before_seconds
        self.user_agent = f"ichinese-open-sdk-python/{VERSION}" + (f" {user_agent}" if user_agent else "")
        self._tokens: Dict[str, _Cached] = {}
        self._key_locks: Dict[str, threading.Lock] = {}
        self._lock = threading.Lock()

    # ── tokens ───────────────────────────────────────────────────────────────

    def app_access_token(self) -> str:
        """The app token (cached, renewed before it expires)."""

        def fetch() -> Tuple[str, float]:
            r = self._send("POST", "/auth/app_access_token", body=self._credentials())
            return r["app_access_token"], r["expires_in"]

        return self._cached("app", fetch)

    def tenant_access_token(self, tenant_key: str) -> str:
        """The tenant token of an institution that installed the app (cached per institution, renewed)."""

        def fetch() -> Tuple[str, float]:
            body = dict(self._credentials(), tenant_key=tenant_key)
            r = self._send("POST", "/auth/tenant_access_token", body=body)
            return r["tenant_access_token"], r["expires_in"]

        return self._cached(f"tenant:{tenant_key}", fetch)

    def exchange_auth_code(
        self, code: str, redirect_uri: Optional[str] = None, code_verifier: Optional[str] = None
    ) -> UserAccessToken:
        """The web login (免登): exchanges the code your page got from the JS SDK's ``requestAuthCode()``
        for a user token and the user's ``open_id``. A code from the plain-browser fallback (standard
        OIDC) also needs the ``redirect_uri`` and ``code_verifier`` the JS SDK returned with it.
        Exchange codes on your backend only: the App Secret never goes to the page. Not retried (a
        code works once)."""
        body: Dict[str, Any] = dict(self._credentials(), code=code)
        if redirect_uri:
            body["redirect_uri"] = redirect_uri
        if code_verifier:
            body["code_verifier"] = code_verifier
        return cast(UserAccessToken, self._send("POST", "/auth/exchange_auth_code", body=body, retry_post=False))

    def refresh_user_token(self, refresh_token: str) -> UserAccessToken:
        """A new pair for a refresh token (the old one stops working)."""
        body = dict(self._credentials(), refresh_token=refresh_token)
        return cast(UserAccessToken, self._send("POST", "/auth/refresh_user_token", body=body, retry_post=False))

    def revoke_token(self, token: str) -> None:
        """Revokes a user or refresh token (when the user signs out of your app)."""
        self._send("POST", "/auth/revoke", body=dict(self._credentials(), token=token))

    def clear_token_cache(self) -> None:
        """Forgets the cached app and tenant tokens (they are fetched again when next needed)."""
        with self._lock:
            self._tokens.clear()

    # ── calls ────────────────────────────────────────────────────────────────

    def request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        body: Any = None,
        *,
        token_types: Sequence[str] = ("app", "tenant", "user"),
        tenant_key: Optional[str] = None,
        user_access_token: Optional[str] = None,
        access_token: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Any open API call by method and path (``/tenant/members``), for what the generated methods do not cover."""
        return self._call(
            path, method.upper(), path, {}, query, body, tuple(token_types),
            tenant_key=tenant_key, user_access_token=user_access_token, access_token=access_token, headers=headers,
        )

    def _call(
        self,
        op_id: str,
        method: str,
        path: str,
        path_params: Dict[str, str],
        query: Optional[Dict[str, Any]],
        body: Any,
        token_types: Tuple[str, ...],
        **options: Any,
    ) -> Any:
        def fill(name: str) -> str:
            v = path_params.get(name)
            if v is None or v == "":
                raise TypeError(f"{op_id}: {name} is required")
            return urllib.parse.quote(str(v), safe="")

        resolved = path
        for name in path_params:
            resolved = resolved.replace("{" + name + "}", fill(name))
        if "{" in resolved:
            raise TypeError(f"{op_id}: missing path parameter in {path}")
        return self._send(method, resolved, query=query, body=body, auth=(op_id, token_types, options))

    def _iterate(
        self,
        op_id: str,
        method: str,
        path: str,
        path_params: Dict[str, str],
        query: Optional[Dict[str, Any]],
        token_types: Tuple[str, ...],
        **options: Any,
    ) -> Iterator[Dict[str, Any]]:
        q: Dict[str, Any] = dict(query or {})
        q.setdefault("page_size", 100)
        q.pop("page_token", None)
        page_token: Optional[str] = None
        while True:
            page_q = dict(q, page_token=page_token) if page_token else q
            page = self._call(op_id, method, path, path_params, page_q, None, token_types, **options) or {}
            for item in page.get("items") or []:
                yield item
            page_token = page.get("page_token") if page.get("has_more") else None
            if not page_token:
                return

    # ── internals ────────────────────────────────────────────────────────────

    def _credentials(self) -> Dict[str, str]:
        return {"app_id": self.app_id, "app_secret": self._app_secret}

    def _fresh(self, key: str) -> Optional[str]:
        hit = self._tokens.get(key)
        if hit and hit.expires_at - self.refresh_before_seconds > time.time():
            return hit.token
        return None

    def _cached(self, key: str, fetch: Any) -> str:
        with self._lock:
            token = self._fresh(key)
            if token:
                return token
            key_lock = self._key_locks.setdefault(key, threading.Lock())
        # One fetch per key at a time: the others wait for it and take its result.
        with key_lock:
            with self._lock:
                token = self._fresh(key)
            if token:
                return token
            token, expires_in = fetch()
            with self._lock:
                self._tokens[key] = _Cached(token, time.time() + float(expires_in))
            return token

    def _drop(self, key: str) -> None:
        with self._lock:
            self._tokens.pop(key, None)

    def _token_for(self, op_id: str, token_types: Tuple[str, ...], o: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        if o.get("access_token"):
            return o["access_token"], None
        if o.get("user_access_token"):
            return o["user_access_token"], None
        tenant_key = o.get("tenant_key")
        if tenant_key:
            return self.tenant_access_token(tenant_key), f"tenant:{tenant_key}"
        if "app" in token_types:
            return self.app_access_token(), "app"
        raise OpenApiError(
            0,
            "TOKEN_REQUIRED",
            f"{op_id} takes a {' or '.join(token_types)} token: pass tenant_key= or user_access_token=",
        )

    def _url(self, path: str, query: Optional[Dict[str, Any]]) -> str:
        pairs = []
        for k, v in (query or {}).items():
            if v is None or v == "":
                continue
            for x in v if isinstance(v, (list, tuple)) else [v]:
                pairs.append((k, "true" if x is True else "false" if x is False else str(x)))
        url = f"{self.base_url}{API_PREFIX}{path}"
        return f"{url}?{urllib.parse.urlencode(pairs)}" if pairs else url

    def _backoff(self, attempt: int) -> float:
        base = self.retry_base_seconds * (2**attempt)
        return min(30.0, base + random.random() * base * 0.25)

    def _send(
        self,
        method: str,
        path: str,
        *,
        query: Optional[Dict[str, Any]] = None,
        body: Any = None,
        auth: Optional[Tuple[str, Tuple[str, ...], Dict[str, Any]]] = None,
        retry_post: bool = True,
    ) -> Any:
        options = auth[2] if auth else {}
        refreshed = False
        attempt = 0
        url = self._url(path, query)
        data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        # Token requests are safe to repeat; exchanging a one-time code is not.
        idempotent = method in IDEMPOTENT or (method == "POST" and retry_post and auth is None)
        while True:
            headers: Dict[str, str] = {"Accept": "application/json", "User-Agent": self.user_agent}
            headers.update(options.get("headers") or {})
            cache_key: Optional[str] = None
            if auth:
                token, cache_key = self._token_for(auth[0], auth[1], options)
                headers["Authorization"] = f"Bearer {token}"
            if data is not None:
                headers["Content-Type"] = "application/json"
            can_retry = attempt < self.max_retries
            try:
                status, res_headers, raw = self._transport(method, url, headers, data, self.timeout)
            except (TimeoutError, socket.timeout, OSError) as e:
                if can_retry and idempotent:
                    time.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                timed_out = isinstance(e, (TimeoutError, socket.timeout))
                raise OpenApiError(0, "TIMEOUT" if timed_out else "NETWORK", f"{method} {path}: {e}") from e
            h = {k.lower(): v for k, v in res_headers.items()}
            if 200 <= status < 300:
                if status == 204 or not raw:
                    return None
                return json.loads(raw.decode("utf-8"))
            error = _to_error(status, h, raw)
            if status == 429 and can_retry and error.reason != "daily_quota_exceeded":
                # A daily quota does not come back within a retry.
                wait = error.retry_after
                if wait is None:
                    reset = _number(h.get("x-ratelimit-reset"))
                    wait = reset if reset is not None and reset > 0 else None
                time.sleep(wait if wait is not None else self._backoff(attempt))
                attempt += 1
                continue
            if status in RETRY_STATUSES and can_retry and idempotent:
                time.sleep(self._backoff(attempt))
                attempt += 1
                continue
            if status == 401 and cache_key and not refreshed and error.reason in ("token_expired", "invalid_token"):
                self._drop(cache_key)
                refreshed = True
                continue
            raise error


def _number(v: Optional[str]) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _to_error(status: int, headers: Dict[str, str], raw: bytes) -> OpenApiError:
    err: Dict[str, Any] = {}
    try:
        parsed = json.loads(raw.decode("utf-8")) if raw else {}
        if isinstance(parsed, dict) and isinstance(parsed.get("error"), dict):
            err = parsed["error"]
    except (ValueError, UnicodeDecodeError):
        err = {}
    return OpenApiError(
        status,
        err.get("code") or f"HTTP_{status}",
        err.get("message") or f"HTTP {status}",
        request_id=err.get("request_id") or headers.get("x-request-id"),
        details=err.get("details") or {},
        retry_after=_number(headers.get("retry-after")),
    )
