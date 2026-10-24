"""The token engine: parameters in, a complete design-token system out.

Deterministic: same params, same tokens, byte-identical. The engine
either guarantees WCAG contrast for every role pair it emits or raises
— it never ships an inaccessible combination silently. When a
harmony-derived color fails its contrast pair, it is repaired by
fixed-step lightening/darkening and the repair is recorded in
tokens["repairs"].

Parameters (all optional, defaults in DEFAULTS):
  hue          0..360         base hue for the brand color
  saturation   0..1           brand saturation
  harmony      complementary | analogous | triadic
  ratio        1.2 | 1.25 | 1.333 | 1.5 | 1.618   type scale ratio
  density      compact | normal | comfortable      spacing unit
  radius       0..24          corner radius in px
"""
from . import color as C
from . import sections as sections_mod

DEFAULTS = {
    "hue": 222,
    "saturation": 0.62,
    "harmony": "complementary",
    "ratio": 1.25,
    "density": "normal",
    "radius": 8,
    "style": "neutral",       # neutral | material | harmony
    "sections": "header,hero,features,footer",
}

# Style presets shape the token MATH (parameter bundles), never copied
# code from the systems that inspired them: neutral = shadcn-like
# bordered minimalism; material = elevation and tonal color; harmony =
# soft, round, comfortable.
STYLES = {
    "neutral": {
        "radius": 8, "density": "normal", "saturation": 0.38,
        "border_strength": 0.30,
        "elev_1": "0 1px 2px rgba(0,0,0,.05)",
        "elev_2": "0 2px 6px rgba(0,0,0,.08)",
    },
    "material": {
        "radius": 12, "density": "normal", "saturation": 0.62,
        "border_strength": 0.18,
        "elev_1": "0 1px 3px rgba(0,0,0,.12), 0 1px 2px rgba(0,0,0,.10)",
        "elev_2": "0 3px 8px rgba(0,0,0,.14), 0 1px 3px rgba(0,0,0,.10)",
    },
    "harmony": {
        "radius": 20, "density": "comfortable", "saturation": 0.48,
        "border_strength": 0.22,
        "elev_1": "0 2px 10px rgba(0,0,0,.06)",
        "elev_2": "0 6px 18px rgba(0,0,0,.09)",
    },
}

RATIOS = (1.2, 1.25, 1.333, 1.5, 1.618)
DENSITIES = {"compact": 3, "normal": 4, "comfortable": 6}
HARMONIES = ("complementary", "analogous", "triadic")

# role pair -> (foreground role, background role, minimum contrast)
CONTRAST_RULES = (
    ("text", "bg", 4.5),
    ("text_muted", "bg", 4.5),
    ("link", "bg", 4.5),
    ("on_primary", "primary", 4.5),
    ("text", "surface", 4.5),
    ("border", "bg", 3.0),
    ("on_primary", "primary_hover", 4.5),
)


def parse_params(query):
    """Coerce query-string-ish dict -> validated params. Raises ValueError."""
    p = dict(DEFAULTS)
    explicit = set()
    for key, raw in query.items():
        if key not in DEFAULTS:
            raise ValueError("unknown parameter %r" % key)
        explicit.add(key)
        if key in ("hue", "radius"):
            p[key] = int(raw)
        elif key == "saturation":
            p[key] = float(raw)
        else:
            p[key] = str(raw).lower()
    # Style preset fills only what the caller did not set explicitly.
    preset = STYLES.get(p["style"])
    if preset is None:
        raise ValueError("style must be one of %s" % (tuple(STYLES),))
    for key in ("radius", "density", "saturation"):
        if key not in explicit:
            p[key] = preset[key]
    p["sections"] = ",".join(sections_mod.normalize_sections(p["sections"]))
    if not 0 <= p["hue"] < 360:
        raise ValueError("hue must be in [0,360)")
    if not 0.0 <= p["saturation"] <= 1.0:
        raise ValueError("saturation must be in [0,1]")
    if p["harmony"] not in HARMONIES:
        raise ValueError("harmony must be one of %s" % (HARMONIES,))
    if p["ratio"] not in RATIOS:
        p["ratio"] = float(p["ratio"])
        if p["ratio"] not in RATIOS:
            raise ValueError("ratio must be one of %s" % (RATIOS,))
    if p["density"] not in DENSITIES:
        raise ValueError("density must be one of %s" % (tuple(DENSITIES),))
    if not 0 <= p["radius"] <= 24:
        raise ValueError("radius must be in [0,24]")
    return p


def _harmony_hue(hue, harmony):
    if harmony == "complementary":
        return (hue + 180) % 360
    if harmony == "analogous":
        return (hue + 30) % 360
    return (hue + 120) % 360  # triadic


def _repair(role, fg, bg, minimum):
    """Push fg lighter/darker in fixed steps until contrast passes."""
    for step in range(1, 41):
        candidate = C.darken(fg, step * 0.04)
        if C.contrast(candidate, bg) >= minimum:
            return candidate, "darkened"
        candidate = C.lighten(fg, step * 0.04)
        if C.contrast(candidate, bg) >= minimum:
            return candidate, "lightened"
    raise ValueError(
        "role %r: no repair within 40 steps (fg=%s bg=%s)" %
        (role, C.css_hex(fg), C.css_hex(bg)))


def build_tokens(params):
    """Params -> token dict (JSON-safe, deterministic)."""
    p = parse_params(params)
    hue, sat = p["hue"], p["saturation"]
    hue2 = _harmony_hue(hue, p["harmony"])

    bg = C.hsl_to_rgb(hue, min(sat, 0.12), 0.975)          # near-white tint
    surface = C.hsl_to_rgb(hue, min(sat, 0.16), 0.99)       # cards sit above bg
    text = C.hsl_to_rgb(hue, min(sat, 0.45), 0.13)
    text_muted = C.hsl_to_rgb(hue, min(sat, 0.30), 0.34)
    preset = STYLES[p["style"]]
    border_l = 0.88 - preset["border_strength"] * 0.45
    border = C.hsl_to_rgb(hue, min(sat, 0.25), border_l)
    primary = C.hsl_to_rgb(hue, sat, 0.40)
    primary_hover = C.darken(primary, 0.12)
    accent = C.hsl_to_rgb(hue2, sat, 0.42)
    # text-on-brand: pure black or white, whichever keeps >= contrast
    # against BOTH primary and its (darker) hover state
    b, w = (0, 0, 0), (255, 255, 255)
    worst = lambda c: min(C.contrast(c, primary), C.contrast(c, primary_hover))
    on_primary = b if worst(b) >= worst(w) else w

    roles = {
        "bg": bg, "surface": surface, "text": text, "text_muted": text_muted,
        "border": border, "primary": primary, "primary_hover": primary_hover,
        "accent": accent, "link": accent, "on_primary": on_primary,
    }

    # Contrast gate: repair deterministic, record every intervention.
    repairs = []
    for role, bg_role, minimum in CONTRAST_RULES:
        fg, bgc = roles[role], roles[bg_role]
        if C.contrast(fg, bgc) >= minimum:
            continue
        if role == "on_primary":
            # Dead-zone brand color: neither black nor white text passes,
            # so repairing the TEXT is impossible. Darken the brand until
            # one of them does; hover stays 12% darker than the brand.
            for step in range(1, 41):
                cand = C.darken(roles["primary"], step * 0.04)
                cand_hover = C.darken(cand, 0.12)
                wb = min(C.contrast(b, cand), C.contrast(b, cand_hover))
                ww = min(C.contrast(w, cand), C.contrast(w, cand_hover))
                pick, best = (b, wb) if wb >= ww else (w, ww)
                if best >= minimum:
                    repairs.append({
                        "role": "primary", "against": "on_primary",
                        "was": C.css_hex(roles["primary"]),
                        "now": C.css_hex(cand), "how": "darkened",
                        "ratio_before": round(C.contrast(fg, bgc), 2)})
                    roles["primary"] = cand
                    roles["primary_hover"] = cand_hover
                    roles["on_primary"] = pick
                    break
            else:
                raise ValueError(
                    "brand hue %.0f at saturation %.2f is too mid-tone: "
                    "no on-brand text color reaches %.1f:1" %
                    (hue, sat, minimum))
            continue
        fixed, how = _repair(role, fg, bgc, minimum)
        roles[role] = fixed
        repairs.append({"role": role, "against": bg_role,
                        "was": C.css_hex(fg), "now": C.css_hex(fixed),
                        "how": how, "ratio_before":
                        round(C.contrast(fg, bgc), 2)})
    for role, bg_role, minimum in CONTRAST_RULES:  # final assert, no repair
        got = C.contrast(roles[role], roles[bg_role])
        if got < minimum:
            raise AssertionError("gate bug: %s on %s = %.2f" %
                                 (role, bg_role, got))

    # Type scale: base 16px at the middle step (m), two steps down to xs.
    names = ("xs", "s", "m", "l", "xl", "2xl", "3xl")
    sizes = {}
    for i, name in enumerate(names):
        sizes["font_%s" % name] = round(16.0 * p["ratio"] ** (i - 2), 2)

    unit = DENSITIES[p["density"]]
    spacing = {"sp_%d" % i: unit * m for i, m in enumerate((1, 2, 3, 4, 6, 8), 1)}

    tokens = {
        "params": p,
        "color": {role: C.css_hex(rgb) for role, rgb in roles.items()},
        "contrast": {"%s_on_%s" % (role, bg_role):
                     round(C.contrast(roles[role], roles[bg_role]), 2)
                     for role, bg_role, _min in CONTRAST_RULES},
        "font": {"family": "system-ui, sans-serif", **sizes},
        "spacing": spacing,
        "radius": {"radius": p["radius"],
                   "radius_lg": min(24, p["radius"] * 2)},
        "elevation": {"elev_1": preset["elev_1"],
                      "elev_2": preset["elev_2"]},
        "shadow": preset["elev_1"],
        "repairs": repairs,
    }
    return tokens
