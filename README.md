# uigen

A design system from six numbers. Zero dependencies: the engine is
Python stdlib, the playground is one vanilla HTML file. Same
parameters, same theme, forever — and every text/background pair it
emits is checked against WCAG contrast before you ever see it.

Parameters in (hue, saturation, harmony, type ratio, density, radius,
style preset, page sections) → a complete system out: color roles
derived by HSL harmony, a modular type scale, a spacing scale, radii,
elevation — rendered as CSS custom properties, a JSON token file, and a
composed page (header, hero, features, pricing, CTA, footer — you pick
which). Style presets (neutral / material / harmony) shape the token
math itself: bordered minimalism, elevation-forward, or soft-and-round.

The differentiator is the gate, not the palette: when a
harmony-derived pair fails WCAG, the engine repairs it in fixed
deterministic steps and *records the repair* — it never ships an
inaccessible combination silently, and it never invents anything a
parameter did not ask for.

## Play

```sh
python3 -m uigen.server 8000
# open http://127.0.0.1:8000/ and drag the sliders
# open http://127.0.0.1:8000/builder.html for the procedural builder
```

The **builder** (`www/builder.html`) is a rules-driven UI editor: pick a
layout preset, columns, gap, item count and seed; the engine generates
a deterministic component tree (metric, bar-chart, activity-list,
table, callout, heading) rendered live. Click any component to edit it
in the inspector, add or remove components, switch light/dark, save to
localStorage, export the project as JSON — the same blueprint as an
npm-starter version, with zero dependencies: the engine is Python
stdlib, the renderer is an allowlisted vanilla-DOM map, theming reuses
the WCAG-gated token engine, and validation is strict on both sides.

Or without a browser:

```sh
curl "http://127.0.0.1:8000/api/tokens.css?hue=160&ratio=1.333"   # stylesheet
curl "http://127.0.0.1:8000/api/tokens?hue=160"                    # JSON
curl "http://127.0.0.1:8000/api/page?hue=160"                      # demo page
```

## How it works

- `uigen/color.py` — HSL/RGB conversion and the WCAG relative
  luminance / contrast formulas. Pure functions; this math is the
  trust boundary of the accessibility gate.
- `uigen/sections.py` — the section model: which sections a page has
  (canonical order, unknown names rejected), each rendered with
  token-driven classes only.
- `uigen/tokens.py` — the engine. Validates parameters strictly
  (unknown keys and out-of-range values are errors, not guesses),
  derives color roles from hue + harmony (complementary / analogous /
  triadic), picks text-on-brand as pure black/white by whichever
  survives both primary and hover, builds the type scale
  (`base * ratio^k`) and the density-driven spacing scale, then runs
  the contrast gate with deterministic repair.
- `uigen/render.py` — tokens → CSS custom properties and a
  self-contained demo page (buttons, card, form, table, alert; no
  external resources at all).
- `uigen/server.py` — stdlib `http.server`, loopback by default:
  `/api/tokens`, `/api/tokens.css`, `/api/page`.
- `www/index.html` — the playground: sliders, live iframe preview,
  copy-CSS button.
- `fixtures/params/` — sample parameter sets (including a deliberately
  harsh one that exercises the repair path).
- `tests/` — offline `unittest` suite; loopback-only. Asserts the WCAG
  formulas against known values, that every fixture passes the gate,
  byte-identical determinism, that repairs actually fix the failing
  pair, scale monotonicity, and server param validation.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

## Status

Checkpoint 1 (MVP) plus sections and style presets: parameters →
tokens → CSS + composed page + playground, with the WCAG gate. Pages
now vary in structure (which sections) and character (which preset);
true structural layout generation (constraint solving) is deliberately
not here yet.

MIT license.
