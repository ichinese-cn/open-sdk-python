"""The backend half of the web login (免登): the page calls the JS SDK's ``requestAuthCode()`` and posts
what it got here; we exchange the code for a user token (the App Secret stays on the server), read who
it is and start the app's own session.

    APP_ID=… APP_SECRET=… PORT=3000 python examples/web_login_backend.py
    POST /login  {"code": "…", "state": "…", "redirect_uri"?: "…", "code_verifier"?: "…"}
"""
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ichinese_open import Client, OpenApiError

client = Client(os.environ["APP_ID"], os.environ["APP_SECRET"], base_url=os.environ.get("OPEN_API_BASE"))
sessions = {}  # sid -> {"open_id", "token", "refresh"}; use your own session store


class LoginHandler(BaseHTTPRequestHandler):
    def reply(self, status, payload, extra_headers=None):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/login":
            return self.reply(404, {"error": "not_found"})
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            body = json.loads(raw or b"{}")
            # Check `state` against what your page stored before asking (the JS SDK does this for the fallback).
            user = client.exchange_auth_code(
                body["code"], redirect_uri=body.get("redirect_uri"), code_verifier=body.get("code_verifier")
            )
            me = client.get_user_info(user_access_token=user["access_token"])
            sid = secrets.token_urlsafe(16)
            sessions[sid] = {"open_id": user["open_id"], "token": user["access_token"], "refresh": user["refresh_token"]}
            self.reply(
                200,
                {"open_id": me["open_id"], "name": me.get("name"), "denied": user["denied_scopes"]},
                {"Set-Cookie": f"sid={sid}; HttpOnly; SameSite=Lax; Path=/"},
            )
        except OpenApiError as e:
            # code_expired / code_used / code_invalid: ask the page to call requestAuthCode() again.
            self.reply(e.status or 502, {"error": e.reason or e.code})
        except (KeyError, ValueError):
            self.reply(400, {"error": "bad_request"})


if __name__ == "__main__":
    ThreadingHTTPServer(("", int(os.environ.get("PORT", "3000"))), LoginHandler).serve_forever()
