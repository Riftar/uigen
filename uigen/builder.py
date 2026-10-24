"""The builder engine: layout rules in, a deterministic component tree out.

Same contract as the rest of uigen: pure function, strict validation,
seeded determinism (same rules + seed = byte-identical project). Nodes
are JSON-safe data describing an ALLOWLISTED set of component kinds —
never markup, never executable code. A renderer maps kinds to known
components; anything unknown is rejected at the boundary.
"""
import json

PRESETS = ("grid", "stack", "feature")
KINDS = ("metric", "bar-chart", "activity-list", "table", "callout", "heading")

DEFAULT_RULES = {
    "preset": "grid",
    "columns": 3,
    "gap": 16,
    "items": 6,
    "seed": 7,
}

_METRIC_TITLES = ("Active users", "Monthly revenue", "P95 latency",
                  "Error rate", "Signups this week", "Storage used",
                  "API calls", "Churn rate")
_METRIC_VALUES = ("12,480", "$48,210", "184 ms", "0.42%", "1,207",
                  "6.8 TB", "2.1 M", "2.9%")
_ACTIVITY = (
    ("Deploy finished", "production, build 4211"),
    ("New comment", "Ana on 'Roadmap draft'"),
    ("Alert cleared", "cpu back under 70%"),
    ("Member joined", "dev-team workspace"),
    ("Report ready", "weekly summary generated"),
    ("Backup done", "nightly snapshot ok"),
    ("Ticket opened", "checkout page slow"),
    ("Invite sent", "3 collaborators"),
)
_TABLES = (
    ("Region", ("APAC 31%", "EMEA 27%", "AMER 42%")),
    ("Plan", ("Starter 61%", "Team 29%", "Studio 10%")),
    ("Channel", ("Organic 44%", "Ads 38%", "Referral 18%")),
)
_CALLOUTS = (
    ("Heads up", "Traffic spike expected during the launch window."),
    ("Tip", "Pin this dashboard to the team home for faster standups."),
    ("Note", "Data refreshes every 15 minutes."),
    ("Warning", "Two checks failed on the staging deployment."),
)
_HEADINGS = ("Overview", "Team activity", "Growth", "Operations",
             "Reliability", "Accounts")


def _lcg(seed):
    """Deterministic PRNG (same sequence the client textures use)."""
    state = seed & 0xFFFFFFFF

    def rnd():
        nonlocal state
        state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
        return state / 4294967296

    return rnd


def parse_rules(query):
    """Coerce/validate rule params. Unknown or out-of-range -> ValueError."""
    p = dict(DEFAULT_RULES)
    for key, raw in query.items():
        if key not in DEFAULT_RULES:
            raise ValueError("unknown rule %r" % key)
        if key == "preset":
            p[key] = str(raw).lower()
        else:
            try:
                p[key] = int(raw)
            except (TypeError, ValueError):
                raise ValueError("rule %r must be an integer" % key)
    if p["preset"] not in PRESETS:
        raise ValueError("preset must be one of %s" % (PRESETS,))
    if not 1 <= p["columns"] <= 4:
        raise ValueError("columns must be in [1,4]")
    if not 8 <= p["gap"] <= 40:
        raise ValueError("gap must be in [8,40]")
    if not 3 <= p["items"] <= 12:
        raise ValueError("items must be in [3,12]")
    if not 0 <= p["seed"] < 2 ** 31:
        raise ValueError("seed must be in [0, 2^31)")
    return p


def _node(kind, i, rnd):
    node = {"id": "n%d" % (i + 1), "kind": kind}
    if kind == "heading":
        node["title"] = _HEADINGS[int(rnd() * len(_HEADINGS))]
    elif kind == "metric":
        node["title"] = _METRIC_TITLES[int(rnd() * len(_METRIC_TITLES))]
        node["value"] = _METRIC_VALUES[int(rnd() * len(_METRIC_VALUES))]
        node["description"] = ("+12.4% vs last month" if rnd() < 0.5
                               else "-3.1% vs last month")
    elif kind == "bar-chart":
        node["title"] = _HEADINGS[int(rnd() * len(_HEADINGS))]
        node["data"] = [round(20 + rnd() * 80, 1) for _ in range(8)]
    elif kind == "activity-list":
        node["title"] = "Activity"
        node["items"] = ["%s — %s" % _ACTIVITY[int(rnd() * len(_ACTIVITY))]
                         for _ in range(4)]
    elif kind == "table":
        head, rows = _TABLES[int(rnd() * len(_TABLES))]
        node["title"] = head
        node["items"] = list(rows)
    elif kind == "callout":
        node["title"], node["description"] = \
            _CALLOUTS[int(rnd() * len(_CALLOUTS))]
    return node


def generate(rules):
    """Rules -> UIProject dict (JSON-safe, deterministic)."""
    p = parse_rules(rules)
    rnd = _lcg(p["seed"])
    pool = [k for k in KINDS if k != "heading"]
    nodes = []
    # feature preset: first node is always a heading banner
    if p["preset"] == "feature":
        nodes.append(_node("heading", 0, rnd))
    while len(nodes) < p["items"]:
        i = len(nodes)
        kind = pool[int(rnd() * len(pool))]
        nodes.append(_node(kind, i, rnd))
    return {
        "version": 1,
        "name": "uigen project",
        "rules": p,
        "nodes": nodes[:p["items"]],
    }


def project_json(rules):
    return json.dumps(generate(rules), sort_keys=True,
                      separators=(",", ":"))
