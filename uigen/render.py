"""Rendering: tokens -> CSS custom properties and a self-contained demo page.

Output is pure HTML/CSS — no JS frameworks, no network fonts. The demo
page exercises every component class so a generated theme can be judged
at a glance.
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
  --shadow: %(shadow)s;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: var(--fs-m)/1.6 var(--font); }
a { color: var(--link); }
.wrap { max-width: 46rem; margin: 0 auto; padding: var(--sp-5) var(--sp-4); }
h1 { font-size: var(--fs-3xl); line-height: 1.15; margin: 0 0 var(--sp-2); }
h2 { font-size: var(--fs-xl); margin: var(--sp-5) 0 var(--sp-2); }
p.lead { font-size: var(--fs-l); color: var(--text-muted); margin: 0 0 var(--sp-4); }
.btn { display: inline-block; border: 1px solid transparent;
  border-radius: var(--radius); padding: var(--sp-2) var(--sp-4);
  font-size: var(--fs-m); cursor: pointer; text-decoration: none; }
.btn-primary { background: var(--primary); color: var(--on-primary); }
.btn-primary:hover { background: var(--primary-hover); color: var(--on-primary); }
.btn-secondary { background: transparent; color: var(--text);
  border-color: var(--border); }
.card { background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: var(--sp-4); box-shadow: var(--shadow);
  margin: var(--sp-3) 0; }
label { display: block; font-size: var(--fs-s); margin: var(--sp-3) 0 var(--sp-1);
  color: var(--text); }
input, select { width: 100%%; padding: var(--sp-2) var(--sp-3);
  border: 1px solid var(--border); border-radius: var(--radius);
  font-size: var(--fs-m); background: var(--surface); color: var(--text); }
input:focus, select:focus { outline: 2px solid var(--primary); outline-offset: 1px; }
table { border-collapse: collapse; width: 100%%; font-size: var(--fs-s); }
th, td { text-align: left; padding: var(--sp-2) var(--sp-3);
  border-bottom: 1px solid var(--border); }
th { color: var(--text-muted); font-weight: 600; }
.alert { border-left: 3px solid var(--primary); background: var(--surface);
  border-radius: var(--radius); padding: var(--sp-3) var(--sp-4);
  font-size: var(--fs-s); margin: var(--sp-3) 0; }
.badge { display: inline-block; font-size: var(--fs-xs); padding: 2px var(--sp-2);
  border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-muted); margin-right: var(--sp-1); }
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
    flat["shadow"] = tokens["shadow"]
    return CSS_TEMPLATE % flat


def build_page(tokens, title="uigen demo"):
    css = build_css(tokens)
    p = tokens["params"]
    meta = "hue=%d sat=%.2f harmony=%s ratio=%s density=%s radius=%d" % (
        p["hue"], p["saturation"], p["harmony"], p["ratio"], p["density"],
        p["radius"])
    contrast = tokens["contrast"]
    repairs = ("none — every pair passed as generated" if not tokens["repairs"]
               else ", ".join("%s %s→%s" % (r["role"], r["was"], r["now"])
                              for r in tokens["repairs"]))
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title><style>%s</style></head>
<body><div class="wrap">
<h1>Generated theme</h1>
<p class="lead">Every color below traces to the parameter set — deterministic,
and contrast-checked against WCAG.</p>
<span class="badge">%s</span><span class="badge">repairs: %s</span>
<div class="card">
  <h2>Components</h2>
  <p><a href="#">A link in the accent harmony color</a> — body text in the
  generated text role, muted text below.</p>
  <p style="color:var(--text-muted)">This sentence uses the muted text role.</p>
  <p><a class="btn btn-primary" href="#">Primary action</a>
  <a class="btn btn-secondary" href="#">Secondary</a></p>
</div>
<div class="card">
  <h2>A form</h2>
  <label for="n">Project name</label>
  <input id="n" placeholder="e.g. northwind">
  <label for="s">Density</label>
  <select id="s"><option>%s</option><option>other</option></select>
</div>
<div class="card">
  <h2>A table</h2>
  <table><tr><th>Token</th><th>Value</th><th>Contrast on bg</th></tr>
  <tr><td>text</td><td>%s</td><td>%s:1</td></tr>
  <tr><td>link</td><td>%s</td><td>%s:1</td></tr>
  <tr><td>primary</td><td>%s</td><td>on-primary %s:1</td></tr></table>
</div>
<div class="alert"><strong>Attention.</strong> Alerts use the primary role
as an edge accent and the surface role as their ground.</div>
<p class="meta">params: %s · text/bg %s:1 · generated by uigen</p>
</div></body></html>""" % (
        title, css, meta, repairs, p["density"],
        tokens["color"]["text"], contrast["text_on_bg"],
        tokens["color"]["link"], contrast["link_on_bg"],
        tokens["color"]["primary"], contrast["on_primary_on_primary"],
        meta, contrast["text_on_bg"])
