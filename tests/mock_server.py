"""A tiny scripted HTTP server for the unit tests (standard library only)."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

Reply = Tuple[int, Dict[str, str], Any]


class Recorded:
    def __init__(self, method: str, path: str, query: Dict[str, List[str]], headers: Dict[str, str], body: Any,
                 raw: bytes = b""):
        self.raw = raw
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body


class MockServer:
    """Routes ``(METHOD, path)`` to a handler ``(Recorded) -> (status, headers, json body or None)``."""

    def __init__(self) -> None:
        self.routes: Dict[Tuple[str, str], Callable[[Recorded], Reply]] = {}
        self.requests: List[Recorded] = []
        self.lock = threading.Lock()
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: Any) -> None:
                pass

            def handle_any(self) -> None:
                u = urlsplit(self.path)
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b""
                try:
                    body = json.loads(raw) if raw else None
                except ValueError:  # an upload's bytes
                    body = None
                rec = Recorded(self.command, u.path, parse_qs(u.query), {k.lower(): v for k, v in self.headers.items()}, body, raw)
                with outer.lock:
                    outer.requests.append(rec)
                route = outer.routes.get((self.command, u.path))
                status, headers, payload = route(rec) if route else (404, {}, {"error": {"code": "NOT_FOUND", "message": "no route"}})
                data = b"" if payload is None else (payload if isinstance(payload, bytes) else json.dumps(payload).encode())
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                if payload is not None and not isinstance(payload, bytes):
                    self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = handle_any

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.httpd.daemon_threads = True
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)

    def __enter__(self) -> "MockServer":
        self.thread.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()

    def count(self, path: str, method: Optional[str] = None) -> int:
        with self.lock:
            return sum(1 for r in self.requests if r.path == path and (method is None or r.method == method))

    def of(self, path: str) -> List[Recorded]:
        with self.lock:
            return [r for r in self.requests if r.path == path]
