import socket
import tempfile
import threading
import unittest
import uuid

from ichinese_open import VERSION, Client, OpenApiError
from tests.mock_server import MockServer, Recorded

P = "/open-apis/v1"


def token_routes(srv: MockServer, expires_in: int = 7200) -> None:
    n = {"app": 0, "tenant": 0}

    def app(r: Recorded):
        n["app"] += 1
        return 200, {}, {"app_access_token": f"a-{n['app']}", "expires_in": expires_in}

    def tenant(r: Recorded):
        n["tenant"] += 1
        return 200, {}, {
            "tenant_access_token": f"t-{n['tenant']}",
            "expires_in": expires_in,
            "tenant_key": r.body["tenant_key"],
            "scopes": [],
        }

    srv.routes[("POST", P + "/auth/app_access_token")] = app
    srv.routes[("POST", P + "/auth/tenant_access_token")] = tenant


class ClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.srv = MockServer().__enter__()
        token_routes(self.srv)

    def tearDown(self) -> None:
        self.srv.__exit__(None, None, None)

    def client(self, **kw) -> Client:
        c = Client("cn.cli_x", "secret", base_url=self.srv.base + "/open-apis/v1/", **kw)
        c.retry_base_seconds = 0.001
        return c

    def test_base_url_and_headers(self):
        self.srv.routes[("GET", P + "/tenant")] = lambda r: (200, {}, {"tenant_key": "cn.k"})
        c = self.client()
        self.assertEqual(c.base_url, self.srv.base)
        self.assertEqual(c.get_tenant(tenant_key="cn.k"), {"tenant_key": "cn.k"})
        r = self.srv.of(P + "/tenant")[0]
        self.assertEqual(r.headers["authorization"], "Bearer t-1")
        self.assertEqual(r.headers["user-agent"], f"ichinese-open-sdk-python/{VERSION}")
        self.assertEqual(r.headers["accept"], "application/json")
        tok = self.srv.of(P + "/auth/tenant_access_token")[0]
        self.assertEqual(tok.body, {"app_id": "cn.cli_x", "app_secret": "secret", "tenant_key": "cn.k"})
        self.assertEqual(tok.headers["content-type"], "application/json")

    def test_tenant_token_is_fetched_once_and_cached(self):
        self.srv.routes[("GET", P + "/tenant")] = lambda r: (200, {}, {"ok": True})
        c = self.client()
        c.get_tenant(tenant_key="cn.k")
        c.get_tenant(tenant_key="cn.k")
        threads = [threading.Thread(target=lambda: c.get_tenant(tenant_key="cn.k2")) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        keys = [r.body["tenant_key"] for r in self.srv.of(P + "/auth/tenant_access_token")]
        self.assertEqual(sorted(keys), ["cn.k", "cn.k2"])
        self.assertEqual(self.srv.count(P + "/tenant"), 10)

    def test_token_renewed_before_expiry(self):
        self.srv.routes[("POST", P + "/auth/app_access_token")] = lambda r: (
            200, {}, {"app_access_token": "a", "expires_in": 200})
        c = self.client()  # refresh_before_seconds=300 > 200: never considered fresh
        c.app_access_token()
        c.app_access_token()
        self.assertEqual(self.srv.count(P + "/auth/app_access_token"), 2)

    def test_401_token_expired_refetches_and_retries_once(self):
        def tenant(r: Recorded):
            if r.headers["authorization"] == "Bearer t-1":
                return 401, {}, {"error": {"code": "UNAUTHENTICATED", "message": "expired", "details": {"reason": "token_expired"}}}
            return 200, {}, {"ok": r.headers["authorization"]}

        self.srv.routes[("GET", P + "/tenant")] = tenant
        c = self.client()
        self.assertEqual(c.get_tenant(tenant_key="cn.k"), {"ok": "Bearer t-2"})
        self.assertEqual(self.srv.count(P + "/auth/tenant_access_token"), 2)

    def test_401_with_own_token_is_not_retried(self):
        self.srv.routes[("GET", P + "/user/info")] = lambda r: (
            401, {}, {"error": {"code": "UNAUTHENTICATED", "message": "x", "details": {"reason": "token_expired"}}})
        with self.assertRaises(OpenApiError) as ctx:
            self.client().get_user_info(user_access_token="u")
        self.assertEqual(ctx.exception.reason, "token_expired")
        self.assertEqual(self.srv.count(P + "/user/info"), 1)

    def test_429_waits_for_retry_after(self):
        calls = {"n": 0}

        def members(r: Recorded):
            calls["n"] += 1
            if calls["n"] == 1:
                return 429, {"Retry-After": "0"}, {"error": {"code": "RATE_LIMITED", "message": "slow", "details": {"reason": "rate_limited"}}}
            return 200, {}, {"items": [], "has_more": False}

        self.srv.routes[("GET", P + "/tenant/members")] = members
        self.client().list_tenant_members(tenant_key="cn.k")
        self.assertEqual(calls["n"], 2)

    def test_429_daily_quota_is_not_retried(self):
        self.srv.routes[("GET", P + "/tenant/members")] = lambda r: (
            429, {"Retry-After": "0"}, {"error": {"code": "RATE_LIMITED", "message": "q", "details": {"reason": "daily_quota_exceeded"}}})
        with self.assertRaises(OpenApiError) as ctx:
            self.client().list_tenant_members(tenant_key="cn.k")
        self.assertEqual(ctx.exception.status, 429)
        self.assertEqual(ctx.exception.retry_after, 0)
        self.assertEqual(self.srv.count(P + "/tenant/members"), 1)

    def test_get_5xx_is_retried(self):
        calls = {"n": 0}

        def tenant(r: Recorded):
            calls["n"] += 1
            return (503, {}, None) if calls["n"] < 3 else (200, {}, {"ok": True})

        self.srv.routes[("GET", P + "/tenant")] = tenant
        self.assertEqual(self.client().get_tenant(tenant_key="cn.k"), {"ok": True})
        self.assertEqual(calls["n"], 3)

    def test_get_5xx_gives_up_after_max_retries(self):
        self.srv.routes[("GET", P + "/tenant")] = lambda r: (500, {}, None)
        with self.assertRaises(OpenApiError) as ctx:
            self.client(max_retries=2).get_tenant(tenant_key="cn.k")
        self.assertEqual((ctx.exception.status, ctx.exception.code), (500, "HTTP_500"))
        self.assertEqual(self.srv.count(P + "/tenant"), 3)

    def test_post_5xx_is_not_retried(self):
        self.srv.routes[("POST", P + "/tenant/invitations")] = lambda r: (503, {}, None)
        with self.assertRaises(OpenApiError) as ctx:
            self.client().invite_tenant_member({"email": "a@b.c"}, tenant_key="cn.k")
        self.assertEqual(ctx.exception.status, 503)
        self.assertEqual(self.srv.count(P + "/tenant/invitations"), 1)
        self.assertEqual(self.srv.of(P + "/tenant/invitations")[0].body, {"email": "a@b.c"})

    def test_exchange_auth_code_is_not_retried(self):
        self.srv.routes[("POST", P + "/auth/exchange_auth_code")] = lambda r: (503, {}, None)
        with self.assertRaises(OpenApiError):
            self.client().exchange_auth_code("c1", redirect_uri="https://x/cb", code_verifier="v")
        reqs = self.srv.of(P + "/auth/exchange_auth_code")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].body, {"app_id": "cn.cli_x", "app_secret": "secret", "code": "c1",
                                        "redirect_uri": "https://x/cb", "code_verifier": "v"})
        self.assertNotIn("authorization", reqs[0].headers)

    def test_token_post_5xx_is_retried(self):
        calls = {"n": 0}

        def app(r: Recorded):
            calls["n"] += 1
            return (502, {}, None) if calls["n"] == 1 else (200, {}, {"app_access_token": "a", "expires_in": 7200})

        self.srv.routes[("POST", P + "/auth/app_access_token")] = app
        self.assertEqual(self.client().app_access_token(), "a")
        self.assertEqual(calls["n"], 2)

    def test_paging_iterates_every_page(self):
        pages = {None: (["m1", "m2"], "p2"), "p2": (["m3"], "p3"), "p3": (["m4"], None)}

        def members(r: Recorded):
            token = r.query.get("page_token", [None])[0]
            items, nxt = pages[token]
            return 200, {}, {"items": [{"open_id": i} for i in items], "has_more": nxt is not None, "page_token": nxt}

        self.srv.routes[("GET", P + "/tenant/members")] = members
        got = [m["open_id"] for m in self.client().iter_list_tenant_members({"department": "x"}, tenant_key="cn.k")]
        self.assertEqual(got, ["m1", "m2", "m3", "m4"])
        reqs = self.srv.of(P + "/tenant/members")
        self.assertEqual(len(reqs), 3)
        self.assertEqual(reqs[0].query, {"page_size": ["100"], "department": ["x"]})
        self.assertEqual(reqs[2].query["page_token"], ["p3"])

    def test_path_params_are_encoded(self):
        self.srv.routes[("DELETE", P + "/classes/c%2F1/members/ou_1")] = lambda r: (204, {}, None)
        self.assertIsNone(self.client().remove_class_member("c/1", "ou_1", tenant_key="cn.k"))
        self.assertEqual(self.srv.count(P + "/classes/c%2F1/members/ou_1", "DELETE"), 1)
        with self.assertRaises(TypeError):
            self.client().get_class("", tenant_key="cn.k")

    def test_error_parsing(self):
        self.srv.routes[("GET", P + "/user/info")] = lambda r: (403, {"X-Request-Id": "hdr"}, {"error": {
            "code": "FORBIDDEN", "message": "denied", "request_id": "req_123",
            "details": {"reason": "scope_denied", "scope": "profile", "never_ask": True}}})
        with self.assertRaises(OpenApiError) as ctx:
            self.client().get_user_info(user_access_token="u")
        e = ctx.exception
        self.assertEqual((e.status, e.code, e.message, e.request_id), (403, "FORBIDDEN", "denied", "req_123"))
        self.assertEqual(e.reason, "scope_denied")
        self.assertTrue(e.is_scope_error)
        self.assertEqual(e.scope, "profile")
        self.assertTrue(e.never_ask)

    def test_error_without_json(self):
        self.srv.routes[("GET", P + "/user/info")] = lambda r: (404, {"X-Request-Id": "rid"}, b"nope")
        with self.assertRaises(OpenApiError) as ctx:
            self.client().get_user_info(user_access_token="u")
        self.assertEqual((ctx.exception.code, ctx.exception.request_id), ("HTTP_404", "rid"))
        self.assertFalse(ctx.exception.is_scope_error)

    def test_token_required(self):
        with self.assertRaises(OpenApiError) as ctx:
            self.client().get_tenant()
        self.assertEqual((ctx.exception.status, ctx.exception.code), (0, "TOKEN_REQUIRED"))
        self.assertEqual(len(self.srv.requests), 0)

    def test_access_token_wins(self):
        self.srv.routes[("GET", P + "/tenant")] = lambda r: (200, {}, {"auth": r.headers["authorization"]})
        c = self.client()
        self.assertEqual(c.get_tenant(access_token="raw", tenant_key="cn.k"), {"auth": "Bearer raw"})
        self.assertEqual(c.get_tenant(user_access_token="usr", tenant_key="cn.k"), {"auth": "Bearer usr"})
        self.assertEqual(self.srv.count(P + "/auth/tenant_access_token"), 0)

    def test_request_uses_app_token_by_default(self):
        self.srv.routes[("GET", P + "/custom")] = lambda r: (200, {}, {"auth": r.headers["authorization"], "q": r.query})
        r = self.client().request("GET", "/custom", {"a": [1, 2], "b": True, "c": None})
        self.assertEqual(r, {"auth": "Bearer a-1", "q": {"a": ["1", "2"], "b": ["true"]}})


ASSET = "8a1f2c3d-4e5f-4a6b-9c7d-0e1f2a3b4c5d"


class CommunityTest(unittest.TestCase):
    """Posting in a person's name (D105)."""

    def setUp(self) -> None:
        self.srv = MockServer().__enter__()

    def tearDown(self) -> None:
        self.srv.__exit__(None, None, None)

    def client(self) -> Client:
        c = Client("cn.cli_x", "secret", base_url=self.srv.base)
        c.retry_base_seconds = 0.001
        return c

    def test_upload_image_puts_to_the_slot_and_returns_the_key(self):
        self.srv.routes[("POST", P + "/community/images")] = lambda r: (201, {}, {
            "key": "img/k1", "upload_url": self.srv.base + "/upload/img-1?sig=x", "method": "PUT",
            "headers": {"Content-Type": "image/png", "X-Amz-Meta-A": "1"}, "expires_at": "2026-11-06T10:00:00Z"})
        self.srv.routes[("PUT", "/upload/img-1")] = lambda r: (200, {}, None)
        self.assertEqual(self.client().upload_image("cn.u-1", b"\x89PNG", "image/png"), "img/k1")
        slot = self.srv.of(P + "/community/images")[0]
        self.assertEqual(slot.body, {"content_type": "image/png", "size_bytes": 4})
        self.assertEqual(slot.headers["authorization"], "Bearer cn.u-1")
        put = self.srv.of("/upload/img-1")[0]
        self.assertEqual((put.method, put.raw, put.query), ("PUT", b"\x89PNG", {"sig": ["x"]}))
        self.assertEqual((put.headers["content-type"], put.headers["x-amz-meta-a"]), ("image/png", "1"))
        self.assertNotIn("authorization", put.headers)

    def test_refused_put_is_an_error(self):
        self.srv.routes[("POST", P + "/community/images")] = lambda r: (201, {}, {
            "key": "k", "upload_url": self.srv.base + "/upload/x", "method": "PUT", "headers": {}, "expires_at": ""})
        self.srv.routes[("PUT", "/upload/x")] = lambda r: (403, {}, b"denied")
        with self.assertRaises(OpenApiError) as ctx:
            self.client().upload_image("u", b"x", "image/jpeg")
        self.assertEqual((ctx.exception.status, ctx.exception.code), (403, "UPLOAD_FAILED"))

    def test_upload_video_creates_puts_and_completes(self):
        self.srv.routes[("POST", P + "/community/videos")] = lambda r: (201, {}, {
            "asset_id": ASSET, "status": "uploading",
            "upload": {"url": self.srv.base + "/upload/v-1", "method": "PUT", "headers": {"X-H": "v"}, "expires_at": ""}})
        self.srv.routes[("PUT", "/upload/v-1")] = lambda r: (200, {}, None)
        self.srv.routes[("POST", P + f"/community/videos/{ASSET}/complete")] = lambda r: (
            200, {}, {"asset_id": ASSET, "status": "queued"})
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            f.write(b"\x00\x01\x02\x03\x04")
            f.flush()
            v = self.client().upload_video("u", f.name, "a.mp4", "video/mp4")
        self.assertEqual(v, {"asset_id": ASSET, "status": "queued"})
        self.assertEqual([(r.method, r.path) for r in self.srv.requests], [
            ("POST", P + "/community/videos"), ("PUT", "/upload/v-1"), ("POST", P + f"/community/videos/{ASSET}/complete")])
        self.assertEqual(self.srv.requests[0].body, {"filename": "a.mp4", "content_type": "video/mp4", "size_bytes": 5})
        self.assertEqual((self.srv.requests[1].raw, self.srv.requests[1].headers["x-h"]), (b"\x00\x01\x02\x03\x04", "v"))
        self.assertEqual(self.srv.requests[2].headers["authorization"], "Bearer u")

    def test_wait_video_ready(self):
        states = ["queued", "processing", "ready"]
        self.srv.routes[("GET", P + f"/community/videos/{ASSET}")] = lambda r: (
            200, {}, {"asset_id": ASSET, "status": states.pop(0), "duration_s": 12})
        v = self.client().wait_video_ready("u", ASSET, interval=0.001)
        self.assertEqual((v["status"], v["duration_s"]), ("ready", 12))
        self.assertEqual(self.srv.count(P + f"/community/videos/{ASSET}"), 3)

    def test_wait_video_failed_and_timeout(self):
        self.srv.routes[("GET", P + f"/community/videos/{ASSET}")] = lambda r: (
            200, {}, {"asset_id": ASSET, "status": "failed", "error": "unsupported_codec"})
        with self.assertRaises(OpenApiError) as ctx:
            self.client().wait_video_ready("u", ASSET, interval=0.001)
        self.assertEqual((ctx.exception.reason, ctx.exception.details["error"]), ("video_failed", "unsupported_codec"))
        self.srv.routes[("GET", P + f"/community/videos/{ASSET}")] = lambda r: (
            200, {}, {"asset_id": ASSET, "status": "processing"})
        with self.assertRaises(OpenApiError) as ctx:
            self.client().wait_video_ready("u", ASSET, timeout=0.03, interval=0.005)
        self.assertEqual((ctx.exception.code, ctx.exception.reason), ("TIMEOUT", "video_not_ready"))

    def test_create_post_adds_a_uuid_and_reuses_it_on_retries(self):
        calls = {"n": 0}

        def posts(r: Recorded):
            calls["n"] += 1
            return (503, {}, None) if calls["n"] == 1 else (201, {}, {"post_id": "cn:post:1"})

        self.srv.routes[("POST", P + "/community/posts")] = posts
        self.assertEqual(self.client().create_post("u", {"body": "你好 #学中文"}), {"post_id": "cn:post:1"})
        sent = [r.body for r in self.srv.of(P + "/community/posts")]
        self.assertEqual(len(sent), 2)
        self.assertEqual(str(uuid.UUID(sent[0]["uuid"], version=4)), sent[0]["uuid"])
        self.assertEqual(sent[1]["uuid"], sent[0]["uuid"])
        self.assertEqual(sent[0]["body"], "你好 #学中文")

        self.srv.requests.clear()
        post = {"uuid": "mine-1", "title": "T"}
        self.client().create_post("u", post)
        self.assertEqual(self.srv.of(P + "/community/posts")[0].body, {"uuid": "mine-1", "title": "T"})
        self.assertEqual(post, {"uuid": "mine-1", "title": "T"})

    def test_posting_as_the_institution_uses_its_tenant_token(self):
        token_routes(self.srv)
        self.srv.routes[("POST", P + "/community/images")] = lambda r: (201, {}, {
            "key": "img/org", "upload_url": self.srv.base + "/upload/org-1", "method": "PUT", "headers": {},
            "expires_at": ""})
        self.srv.routes[("PUT", "/upload/org-1")] = lambda r: (200, {}, None)
        self.srv.routes[("POST", P + "/community/posts")] = lambda r: (201, {}, {"post_id": "cn:post:2"})
        c = self.client()
        self.assertEqual(c.upload_image_as_org("cn.org-1", b"\x09", "image/png"), "img/org")
        c.create_post_as_org("cn.org-1", {"body": "招生啦"})
        self.assertEqual(self.srv.of("/upload/org-1")[0].method, "PUT")
        self.assertEqual(self.srv.of(P + "/community/images")[0].headers["authorization"], "Bearer t-1")
        sent = self.srv.of(P + "/community/posts")[0]
        self.assertEqual(sent.headers["authorization"], "Bearer t-1")
        self.assertEqual(str(uuid.UUID(sent.body["uuid"], version=4)), sent.body["uuid"])
        self.assertEqual(sent.body["body"], "招生啦")
        self.assertEqual(self.srv.of(P + "/auth/tenant_access_token")[0].body["tenant_key"], "cn.org-1")

    def test_get_all_insights_reads_every_tab_with_the_same_query(self):
        token_routes(self.srv)

        def page(r):
            tab = (r.query.get("tab") or ["enrollment"])[0]
            return (200, {}, {"tab": tab, "tabs": ["enrollment", "teaching", "income"], "range": r.query["range"][0]})

        self.srv.routes[("GET", P + "/insights")] = page
        pages = self.client().get_all_insights("cn.org-1", {"range": "7d", "tab": "ignored"})
        self.assertEqual(list(pages), ["enrollment", "teaching", "income"])
        self.assertEqual(pages["income"]["range"], "7d")
        seen = self.srv.of(P + "/insights")
        self.assertEqual([r.query.get("tab") for r in seen], [None, ["teaching"], ["income"]])
        self.assertEqual(seen[0].headers["authorization"], "Bearer t-1")

    def test_consent_required(self):
        self.srv.routes[("POST", P + "/community/posts")] = lambda r: (409, {}, {"error": {
            "code": "CONFLICT", "message": "consent",
            "details": {"reason": "consent_required", "consent_url": "https://www.ichinese.cn/consent/x"}}})
        with self.assertRaises(OpenApiError) as ctx:
            self.client().create_post("u", {"body": "x"})
        e = ctx.exception
        self.assertEqual((e.status, e.reason, e.consent_url), (409, "consent_required", "https://www.ichinese.cn/consent/x"))
        self.assertEqual(self.srv.count(P + "/community/posts"), 1)


class NetworkTest(unittest.TestCase):
    def test_network_error(self):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        c = Client("a", "b", base_url=f"http://127.0.0.1:{port}", max_retries=1)
        c.retry_base_seconds = 0.001
        with self.assertRaises(OpenApiError) as ctx:
            c.get_user_info(user_access_token="u")
        self.assertEqual((ctx.exception.status, ctx.exception.code), (0, "NETWORK"))

    def test_timeout_and_custom_transport(self):
        calls = []

        def transport(method, url, headers, body, timeout):
            calls.append((method, url, timeout))
            raise TimeoutError("slow")

        c = Client("a", "b", base_url="https://example.invalid", transport=transport, timeout=2, max_retries=2)
        c.retry_base_seconds = 0.001
        with self.assertRaises(OpenApiError) as ctx:
            c.get_user_info(user_access_token="u")
        self.assertEqual(ctx.exception.code, "TIMEOUT")
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0], ("GET", "https://example.invalid/open-apis/v1/user/info", 2))

    def test_default_base_url(self):
        from ichinese_open import DEFAULT_BASE_URL

        self.assertEqual(Client("a", "b").base_url, DEFAULT_BASE_URL.rstrip("/"))
        with self.assertRaises(TypeError):
            Client("", "b")


if __name__ == "__main__":
    unittest.main()
