"""Rendering: tokens -> CSS custom properties and a composed page.

Output is pure HTML/CSS — no JS frameworks, no network fonts. Pages are
composed from the section model (uigen.sections), so parameters control
both the skin (tokens) and the structure (which sections exist).
"""

CSS_TEMPLATE = """:root {
  --bg: %(bg)s;
  --surface: %(surface)s;
  --text: %(text)s;
  --text-muted: %(text_muted)s;
  --border: %(border)s;
  --primary: %(primary)s;
  --primary-hover: %(primary_hover)s;
  --accent: %(accent)s;
  --link: %(link)s;
  --on-primary: %(on_primary)s;
  --font: %(font_family)s;
  --fs-xs: %(font_xs)spx; --fs-s: %(font_s)spx; --fs-m: %(font_m)spx;
  --fs-l: %(font_l)spx; --fs-xl: %(font_xl)spx; --fs-2xl: %(font_2xl)spx;
  --fs-3xl: %(font_3xl)spx;
  --sp-1: %(sp_1)dpx; --sp-2: %(sp_2)dpx; --sp-3: %(sp_3)dpx;
  --sp-4: %(sp_4)dpx; --sp-5: %(sp_5)dpx; --sp-6: %(sp_6)dpx;
  --radius: %(radius)dpx; --radius-lg: %(radius_lg)dpx;
  --elev-1: %(elev_1)s; --elev-2: %(elev_2)s;
  --elev-3: %(elev_3)s; --elev-4: %(elev_4)s;
  --shadow-primary: %(shadow_primary)s;
  --gradient-primary: %(gradient_primary)s;
  --gradient-surface: %(gradient_surface)s;
  --ease-out: %(ease_out)s; --ease-spring: %(ease_spring)s;
  --shadow: %(elev_1)s;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--gradient-surface); color: var(--text);
  font: var(--fs-m)/1.6 var(--font);
  -webkit-font-smoothing: antialiased; }
a { color: var(--link); text-decoration-thickness: 1px;
  text-underline-offset: 2px;
  transition: color .18s var(--ease-out); }
a:hover { color: var(--primary); }
.wrap { max-width: 46rem; margin: 0 auto; padding: var(--sp-4) var(--sp-4); }
h1 { font-size: var(--fs-3xl); line-height: 1.12; margin: 0 0 var(--sp-2);
  letter-spacing: -0.02em; font-weight: 800; }
h2 { font-size: var(--fs-xl); letter-spacing: -0.015em; }
p.lead { font-size: var(--fs-l); color: var(--text-muted); }
.btn { display: inline-block; border: 1px solid transparent;
  border-radius: var(--radius); padding: var(--sp-2) var(--sp-4);
  font-size: var(--fs-m); font-weight: 600; cursor: pointer;
  text-decoration: none;
  transition: transform .18s var(--ease-out), box-shadow .18s var(--ease-out),
    background .18s var(--ease-out), filter .18s var(--ease-out); }
.btn:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }
.btn-primary { background: var(--gradient-primary); color: var(--on-primary);
  box-shadow: var(--shadow-primary); }
.btn-primary:hover { transform: translateY(-1px); filter: brightness(1.06);
  color: var(--on-primary); }
.btn-primary:active { transform: translateY(0); filter: brightness(.97); }
.btn-secondary { background: transparent; color: var(--text);
  border-color: var(--border); }
.btn-secondary:hover { border-color: var(--primary); color: var(--primary);
  transform: translateY(-1px); }
.btn-sm { padding: var(--sp-1) var(--sp-3); font-size: var(--fs-s); }
.btn-invert { background: var(--on-primary); color: var(--primary); }
.btn-invert:hover { transform: translateY(-1px); filter: brightness(1.08);
  color: var(--primary); }
.nav { display: flex; justify-content: space-between; align-items: center;
  padding: var(--sp-3) 0; border-bottom: 1px solid var(--border); }
.nav .brand { font-size: var(--fs-l); font-weight: 800; letter-spacing: -.01em;
  background: var(--gradient-primary);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.nav ul { display: flex; gap: var(--sp-4); list-style: none; margin: 0;
  padding: 0; align-items: center; font-size: var(--fs-s); }
.hero { padding: var(--sp-6) 0 var(--sp-4); }
.actions { display: flex; gap: var(--sp-2); flex-wrap: wrap; }
.sect { margin: var(--sp-5) 0; }
.sect h2 { margin: 0 0 var(--sp-3); }
.grid { display: grid; grid-template-columns: repeat(auto-fit,
  minmax(200px, 1fr)); gap: var(--sp-3); }
.feature, .tier { background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: var(--sp-4); box-shadow: var(--elev-1);
  transition: transform .18s var(--ease-out), box-shadow .18s var(--ease-out); }
.feature:hover, .tier:hover { transform: translateY(-2px);
  box-shadow: var(--elev-3); }
.feature h3, .tier h3 { font-size: var(--fs-l); margin: 0 0 var(--sp-1); }
.feature p, .tier p { font-size: var(--fs-s); color: var(--text-muted);
  margin: var(--sp-1) 0; }
.tier .price { font-size: var(--fs-2xl); color: var(--text); font-weight: 700; }
.tier .per { font-size: var(--fs-xs); color: var(--text-muted); }
.tier.featured { border-color: var(--primary);
  box-shadow: var(--shadow-primary); }
.cta-band { background: var(--gradient-primary); color: var(--on-primary);
  box-shadow: var(--elev-2);
  border-radius: var(--radius-lg); padding: var(--sp-5) var(--sp-4);
  text-align: center; margin: var(--sp-5) 0; }
.cta-band h2 { margin: 0 0 var(--sp-2); color: var(--on-primary); }
.cta-band .actions { justify-content: center; }
.hero .btn-primary { padding: var(--sp-2) var(--sp-5); }
.footer { display: flex; justify-content: space-between; gap: var(--sp-3);
  flex-wrap: wrap; border-top: 1px solid var(--border);
  margin-top: var(--sp-6); padding: var(--sp-4) 0; }
.meta { font-size: var(--fs-xs); color: var(--text-muted);
  border-top: 1px solid var(--border); padding-top: var(--sp-3);
  margin-top: var(--sp-5); }
"""


def build_css(tokens):
    flat = {}
    flat.update(tokens["color"])
    flat["font_family"] = tokens["font"]["family"]
    flat.update(tokens["font"])
    flat.update(tokens["spacing"])
    flat.update(tokens["radius"])
    flat.update(tokens["elevation"])
    flat.update(tokens["gradient"])
    flat.update(tokens["easing"])
    return CSS_TEMPLATE % flat


def build_page(tokens, title="uigen demo"):
    from . import sections as S
    css = build_css(tokens)
    p = tokens["params"]
    meta = "hue=%d sat=%.2f style=%s harmony=%s ratio=%s density=%s radius=%d" % (
        p["hue"], p["saturation"], p["style"], p["harmony"], p["ratio"],
        p["density"], p["radius"])
    contrast = tokens["contrast"]
    body = S.render_sections(S.normalize_sections(p["sections"]))
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title><style>%s</style></head>
<body><div class="wrap">
%s
<p class="meta">params: %s · sections: %s · text/bg %s:1 · link/bg %s:1 ·
on-primary/primary %s:1 · repairs: %d · generated by uigen</p>
</div></body></html>""" % (
        title, css, body, meta, p["sections"],
        contrast["text_on_bg"], contrast["link_on_bg"],
        contrast["on_primary_on_primary"], len(tokens["repairs"]))
