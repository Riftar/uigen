"""Loopback server tests: playground, APIs, param validation."""
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uigen import server as srv  # noqa: E402


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), srv.Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def get(self, path):
        url = "http://127.0.0.1:%d%s" % (self.port, path)
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return r.status, r.read(), r.headers.get("Content-Type")
        except urllib.error.HTTPError as e:
            body = e.read()
            e.close()
            return e.code, body, e.headers.get("Content-Type")

    def test_playground_served(self):
        status, body, ctype = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn(b"playground", body)

    def test_tokens_api(self):
        status, body, ctype = self.get("/api/tokens?hue=130&ratio=1.618")
        self.assertEqual(status, 200)
        self.assertIn("application/json", ctype)
        t = json.loads(body)
        self.assertEqual(t["params"]["hue"], 130)
        self.assertGreaterEqual(t["contrast"]["text_on_bg"], 4.5)

    def test_css_api(self):
        status, body, ctype = self.get("/api/tokens.css?hue=10")
        self.assertEqual(status, 200)
        self.assertIn("text/css", ctype)
        self.assertIn(b"--primary:", body)

    def test_page_api(self):
        status, body, ctype = self.get("/api/page?hue=260&harmony=triadic")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertTrue(body.startswith(b"<!doctype html>"))

    def test_style_and_sections_params(self):
        status, body, _ = self.get(
            "/api/page?style=harmony&sections=header,pricing,footer")
        self.assertEqual(status, 200)
        self.assertIn(b'class="tier"', body)
        self.assertIn(b"radius: 20px", body)
        status, _, _ = self.get("/api/page?sections=warpdrive")
        self.assertEqual(status, 400)
        status, _, _ = self.get("/api/page?style=brutalist")
        self.assertEqual(status, 400)

    def test_static_www_served(self):
        status, body, ctype = self.get("/builder.html")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn(b"uigen builder", body)

    def test_no_subpath_static(self):
        status, _, _ = self.get("/www/../uigen/server.py")
        self.assertIn(status, (400, 404))

    def test_builder_api(self):
        status, body, ctype = self.get(
            "/api/builder?preset=grid&columns=3&items=6&seed=7")
        self.assertEqual(status, 200)
        doc = json.loads(body)
        self.assertEqual(len(doc["nodes"]), 6)
        status, _, _ = self.get("/api/builder?items=99")
        self.assertEqual(status, 400)

    def test_bad_params_400(self):
        for bad in ("?hue=999", "?ratio=2.0", "?vibes=loud", "?harmony=nope"):
            status, _, _ = self.get("/api/tokens" + bad)
            self.assertEqual(status, 400, bad)

    def test_404(self):
        status, _, _ = self.get("/nope")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
