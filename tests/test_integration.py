"""Integration test against a running ``DEV_SLOT=n pnpm dev:regions``: ``ICH_OPEN_IT`` holds the fixture
(sdks/tools/src/it-fixture.ts) as JSON, or the path of a file holding it; without it the test is skipped::

    {"base", "app_id", "app_secret", "tenant_key", "code_url"}   # GET code_url -> {"code": "<one-time code>"}
"""
import json
import os
import re
import unittest
import urllib.request

from ichinese_open import Client, OpenApiError


def _fixture():
    raw = (os.environ.get("ICH_OPEN_IT") or "").strip()
    if not raw:
        return None
    if raw.startswith("{"):
        return json.loads(raw)
    with open(raw, encoding="utf-8") as f:
        return json.load(f)


FX = _fixture()
OPEN_ID = re.compile(r"^ou_")


@unittest.skipIf(FX is None, "ICH_OPEN_IT not set")
class OpenApiIntegrationTest(unittest.TestCase):
    def client(self) -> Client:
        return Client(FX["app_id"], FX["app_secret"], base_url=FX["base"])

    def fresh_code(self) -> str:
        with urllib.request.urlopen(FX["code_url"], timeout=30) as r:
            return json.loads(r.read())["code"]

    def test_tenant_token_lists_members_page_by_page(self):
        c = self.client()
        tenant = c.get_tenant(tenant_key=FX["tenant_key"])
        self.assertEqual(tenant["tenant_key"], FX["tenant_key"])
        members = list(c.iter_list_tenant_members({"page_size": 1}, tenant_key=FX["tenant_key"]))
        self.assertGreater(len(members), 0)
        self.assertRegex(members[0]["open_id"], OPEN_ID)

    def test_exchange_auth_code_gives_user_token_once(self):
        c = self.client()
        code = self.fresh_code()
        user = c.exchange_auth_code(code)
        self.assertRegex(user["open_id"], OPEN_ID)
        me = c.get_user_info(user_access_token=user["access_token"])
        self.assertEqual(me["open_id"], user["open_id"])
        with self.assertRaises(OpenApiError) as ctx:
            c.exchange_auth_code(code)
        self.assertEqual((ctx.exception.status, ctx.exception.reason), (400, "code_used"))
        refreshed = c.refresh_user_token(user["refresh_token"])
        self.assertEqual(refreshed["open_id"], user["open_id"])

    def test_tenant_endpoint_refuses_user_token(self):
        c = self.client()
        user = c.exchange_auth_code(self.fresh_code())
        with self.assertRaises(OpenApiError) as ctx:
            c.get_tenant(user_access_token=user["access_token"])
        self.assertEqual(ctx.exception.status, 403)
        self.assertTrue(ctx.exception.request_id)


if __name__ == "__main__":
    unittest.main()
