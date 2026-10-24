"""Offline unittest suite for uigen. Loopback-only; run from repo root:
    python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uigen import color as C  # noqa: E402
from uigen import tokens as T  # noqa: E402
from uigen import render as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXDIR = os.path.join(ROOT, "fixtures", "params")


def load_fixture(name):
    with open(os.path.join(FIXDIR, name)) as f:
        return json.load(f)


def hex_to_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


class TestColorMath(unittest.TestCase):
    def test_hsl_red(self):
        self.assertEqual(C.hsl_to_rgb(0, 1, 0.5), (255, 0, 0))
        self.assertEqual(C.hsl_to_rgb(120, 1, 0.5), (0, 255, 0))
        self.assertEqual(C.hsl_to_rgb(360 + 0, 1, 0.5), (255, 0, 0))  # wrap

    def test_contrast_extremes(self):
        self.assertAlmostEqual(C.contrast((0, 0, 0), (255, 255, 255)), 21.0,
                               places=1)
        self.assertEqual(C.contrast((0, 0, 0), (0, 0, 0)), 1.0)

    def test_contrast_known_pair(self):
        # WCAG's own worked example: #767676 on #ffffff is ~4.54:1
        self.assertGreater(C.contrast((0x76, 0x76, 0x76), (255, 255, 255)),
                           4.5)
        self.assertLess(C.contrast((0x76, 0x76, 0x76), (255, 255, 255)), 4.6)


class TestParams(unittest.TestCase):
    def test_defaults_when_empty(self):
        p = T.parse_params({})
        self.assertEqual(p, T.DEFAULTS)

    def test_unknown_key_rejected(self):
        with self.assertRaises(ValueError):
            T.parse_params({"vibes": "high"})

    def test_ranges_enforced(self):
        for bad in ({"hue": 400}, {"hue": -1}, {"saturation": "1.5"},
                    {"radius": 99}, {"harmony": "chaotic"},
                    {"density": "spacious"}, {"ratio": "2.0"}):
            with self.assertRaises(ValueError, msg=repr(bad)):
                T.parse_params(bad)

    def test_ratio_string_coerced(self):
        self.assertEqual(T.parse_params({"ratio": "1.618"})["ratio"], 1.618)


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.fixtures = [load_fixture(n) for n in
                         ("default.json", "lush.json", "harsh.json")]

    def test_every_fixture_passes_the_gate(self):
        for fx in self.fixtures:
            t = T.build_tokens(fx)
            for pair, ratio in t["contrast"].items():
                # border is a UI edge, not text: its minimum is 3.0
                minimum = 3.0 if pair == "border_on_bg" else 4.5
                self.assertGreaterEqual(ratio, minimum - 0.01,
                                        "%s: %s" % (fx["harmony"], pair))

    def test_deterministic_bytes(self):
        for fx in self.fixtures:
            a = json.dumps(T.build_tokens(fx), sort_keys=True)
            b = json.dumps(T.build_tokens(fx), sort_keys=True)
            self.assertEqual(a, b)

    def test_repairs_recorded_when_needed(self):
        # harsh fixture: orange brand + saturated accents force at least
        # one repair somewhere across the sweep below
        any_repairs = False
        for hue in range(0, 360, 15):
            fx = dict(load_fixture("harsh.json"), hue=hue)
            t = T.build_tokens(fx)
            if t["repairs"]:
                any_repairs = True
                for r in t["repairs"]:
                    self.assertIn(r["how"], ("darkened", "lightened"))
                    self.assertNotEqual(r["was"], r["now"])
        self.assertTrue(any_repairs, "expected at least one repair in the sweep")

    def test_repair_actually_fixes_contrast(self):
        fx = dict(load_fixture("harsh.json"), hue=55, saturation=1.0)
        t = T.build_tokens(fx)
        minimums = {"%s_on_%s" % (role, bg): minimum
                    for role, bg, minimum in T.CONTRAST_RULES}
        for r in t["repairs"]:
            fg = hex_to_rgb(r["now"])
            bg = hex_to_rgb(t["color"][r["against"]])
            minimum = minimums["%s_on_%s" % (r["role"], r["against"])]
            if r["role"] == "primary":  # repaired bg, not fg
                fg, bg = hex_to_rgb(t["color"]["on_primary"]), hex_to_rgb(r["now"])
                minimum = minimums["on_primary_on_primary"]
            self.assertGreaterEqual(C.contrast(fg, bg), minimum - 0.01)

    def test_type_scale_monotonic(self):
        t = T.build_tokens(load_fixture("lush.json"))  # ratio 1.618
        keys = ["font_xs", "font_s", "font_m", "font_l",
                "font_xl", "font_2xl", "font_3xl"]
        sizes = [t["font"][k] for k in keys]
        self.assertEqual(sizes, sorted(sizes))
        self.assertAlmostEqual(sizes[2], 16.0)  # font_m is the base

    def test_spacing_matches_density(self):
        t = T.build_tokens({"density": "compact"})
        self.assertEqual(t["spacing"]["sp_1"], 3)
        t = T.build_tokens({"density": "comfortable"})
        self.assertEqual(t["spacing"]["sp_1"], 6)


class TestRender(unittest.TestCase):
    def setUp(self):
        self.tokens = T.build_tokens(load_fixture("default.json"))

    def test_css_contains_all_token_vars(self):
        css = R.build_css(self.tokens)
        for var in ("--bg", "--primary", "--on-primary", "--fs-3xl",
                    "--sp-6", "--radius-lg", "--shadow", "--accent"):
            self.assertIn(var + ":", css)
        self.assertIn(self.tokens["color"]["primary"], css)

    def test_page_is_self_contained(self):
        page = R.build_page(self.tokens)
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn("<style>", page)
        self.assertNotIn("http://", page)  # no external resources
        self.assertNotIn("src=", page)

    def test_page_shows_params_and_contrast(self):
        page = R.build_page(self.tokens)
        self.assertIn("hue=222", page)
        self.assertIn(":1", page)


if __name__ == "__main__":
    unittest.main()
