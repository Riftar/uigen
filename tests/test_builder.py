"""Builder engine tests: determinism, validation, allowlist."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uigen import builder as B  # noqa: E402
from uigen import tokens as T  # noqa: E402


class TestBuilder(unittest.TestCase):
    def test_deterministic(self):
        a = B.project_json({"seed": 42, "items": 8})
        b = B.project_json({"seed": 42, "items": 8})
        self.assertEqual(a, b)

    def test_seed_changes_output(self):
        a = B.generate({"seed": 1})
        b = B.generate({"seed": 2})
        self.assertNotEqual(a["nodes"], b["nodes"])

    def test_item_count_respected(self):
        for n in (3, 7, 12):
            p = B.generate({"items": n})
            self.assertEqual(len(p["nodes"]), n)

    def test_all_kinds_allowlisted(self):
        for seed in range(20):
            for node in B.generate({"seed": seed})["nodes"]:
                self.assertIn(node["kind"], B.KINDS)

    def test_feature_preset_leads_with_heading(self):
        p = B.generate({"preset": "feature", "items": 6, "seed": 5})
        self.assertEqual(p["nodes"][0]["kind"], "heading")

    def test_stack_grid_columns(self):
        p = B.generate({"preset": "stack"})
        self.assertEqual(p["rules"]["columns"], B.DEFAULT_RULES["columns"])

    def test_json_safe(self):
        json.loads(B.project_json({}))  # no exceptions

    def test_validation(self):
        for bad in ({"preset": "spiral"}, {"columns": 9}, {"columns": 0},
                    {"gap": 4}, {"gap": 99}, {"items": 2}, {"items": 13},
                    {"seed": -1}, {"seed": "x"}, {"mood": "playful"}):
            with self.assertRaises(ValueError, msg=repr(bad)):
                B.parse_rules(bad)

    def test_unknown_kind_never_generated(self):
        p = B.generate({"seed": 99})
        self.assertTrue(all(n["kind"] in B.KINDS for n in p["nodes"]))


class TestDarkModeGate(unittest.TestCase):
    def test_dark_tokens_pass_gate(self):
        for hue in (0, 60, 120, 240, 300):
            for style in ("neutral", "material", "harmony"):
                t = T.build_tokens({"hue": hue, "style": style, "mode": "dark"})
                self.assertGreaterEqual(t["contrast"]["text_on_bg"], 4.5)
                self.assertGreaterEqual(t["contrast"]["link_on_bg"], 4.5)
                self.assertGreaterEqual(
                    t["contrast"]["on_primary_on_primary"], 4.5)


if __name__ == "__main__":
    unittest.main()
