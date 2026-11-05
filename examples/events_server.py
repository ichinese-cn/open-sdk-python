"""Receives event pushes at your request address: verifies the signature on the raw body, decrypts when
an encrypt key is set (needs ``pip install "ichinese-open-sdk[crypto]"``), answers the address check,
and dedupes by event_id.

    SIGNING_SECRET=… [ENCRYPT_KEY=…] PORT=3001 python examples/events_server.py
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ichinese_open import OpenApiError, challenge_response, is_url_verification, parse_event

seen = set()  # use your own store (and expire old ids) in production


class EventsHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            push = parse_event(
                self.headers,  # case-insensitive lookup of X-Ich-Timestamp / X-Ich-Nonce / X-Ich-Signature
                raw,  # the raw bytes, not re-serialized JSON
                os.environ["SIGNING_SECRET"],
                encrypt_key=os.environ.get("ENCRYPT_KEY"),
            )
        except OpenApiError as e:
            self.send_response(401 if e.code == "INVALID_SIGNATURE" else 400)
            self.end_headers()
            return
        answer = json.dumps(challenge_response(push) if is_url_verification(push) else {}).encode()
        # Answer within 5 seconds; do the work afterwards.
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(answer)))
        self.end_headers()
        self.wfile.write(answer)
        if is_url_verification(push):
            return
        header = push["header"]
        if header["event_id"] in seen:  # a retry of one already handled
            return
        seen.add(header["event_id"])
        print(header["event_type"], header.get("tenant_key"), push["event"])


if __name__ == "__main__":
    ThreadingHTTPServer(("", int(os.environ.get("PORT", "3001"))), EventsHandler).serve_forever()
