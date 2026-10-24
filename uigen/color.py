"""Color math: HSL/RGB conversion and WCAG contrast. Pure functions.

Contrast per the WCAG 2.x relative-luminance formula. These functions
are the trust boundary of the whole engine: the accessibility gate is
only as honest as this math.
"""


def hsl_to_rgb(h, s, l):
    """h in [0,360), s and l in [0,1] -> (r, g, b) each in [0,255]."""
    h = h % 360.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = l - c / 2
    if h < 60:
        rgb = (c, x, 0)
    elif h < 120:
        rgb = (x, c, 0)
    elif h < 180:
        rgb = (0, c, x)
    elif h < 240:
        rgb = (0, x, c)
    elif h < 300:
        rgb = (x, 0, c)
    else:
        rgb = (c, 0, x)
    return tuple(round((v + m) * 255) for v in rgb)


def _srgb_channel(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (_srgb_channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(rgb_a, rgb_b):
    la, lb = luminance(rgb_a), luminance(rgb_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def css_hex(rgb):
    return "#%02x%02x%02x" % rgb


def darken(rgb, step):
    return tuple(max(0, round(c * (1 - step))) for c in rgb)


def lighten(rgb, step):
    return tuple(min(255, round(c + (255 - c) * step)) for c in rgb)
