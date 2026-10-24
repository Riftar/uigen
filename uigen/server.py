"""Loopback dev server: playground + token/page APIs.

python3 -m uigen.server [port] — binds 127.0.0.1.

Routes:
  /                     interactive playground (www/index.html)
  /api/tokens?...       token system as JSON
  /api/tokens.css?...   CSS custom properties as a stylesheet
  /api/page?...         full self-contained demo page
Query params are validated by uigen.tokens.parse_params; unknown or
out-of-range values are a 400, not a guess.
"""
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from . import tokens as tokens_mod
from . import render as render_mod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW = os.path.join(ROOT, "www")


def _params_from(query):
    qs = parse_qs(query)
    flat = {k: v[0] for k, v in qs.items() if k != "title"}
    return flat, (qs.get("title", ["uigen demo"])[0])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        try:
            if url.path == "/":
                with open(os.path.join(WWW, "index.html"), "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            if url.path in ("/api/tokens", "/api/tokens.css", "/api/page"):
                flat, title = _params_from(url.query)
                try:
                    t = tokens_mod.build_tokens(flat)
                except ValueError as e:
                    return self._send(400, ("bad params: %s\n" % e).encode())
                if url.path == "/api/tokens":
                    import json
                    body = json.dumps(t, sort_keys=True,
                                      separators=(",", ":")).encode()
                    return self._send(200, body, "application/json")
                if url.path == "/api/tokens.css":
                    return self._send(200, render_mod.build_css(t).encode(),
                                      "text/css; charset=utf-8")
                return self._send(200, render_mod.build_page(t, title).encode(),
                                  "text/html; charset=utf-8")
            return self._send(404, b"not found")
        except BrokenPipeError:
            pass


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("uigen on http://127.0.0.1:%d/" % port)
    srv.serve_forever()


if __name__ == "__main__":
    main()
