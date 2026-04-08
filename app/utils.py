# app/utils.py
"""
Pure utility functions — stdlib only, no app imports.

Reusable primitives for color manipulation, chart axis math, number rounding,
label normalization, and demographic band arithmetic.

Rules for this file:
  - No imports from anywhere in app/
  - No third-party imports (no numpy, plotly, pandas, etc.)
  - Every function must be independently testable with no setup
  - Safe to lift into any project as-is

Sections:
    1. Color      — hex parsing, CSS rgba/hsl builders
    2. Chart math — axis tick/range helpers, colorscale bound rounding
    3. String     — label normalization
    4. Demography — 5-year age band arithmetic
"""

import colorsys
import math


# ── 1. Color ──────────────────────────────────────────────────────────────────

TRANSPARENT = "rgba(0,0,0,0)"


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Parse a 6-digit hex color string into (r, g, b) ints.

    >>> hex_to_rgb("#bc002d")
    (188, 0, 45)
    >>> hex_to_rgb("142148")   # leading # is optional
    (20, 33, 72)
    """
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgba(hex_color: str, alpha: float) -> str:
    """Return a CSS rgba() string from a hex color and alpha in [0, 1].

    Alpha is clamped — values outside [0, 1] are silently corrected.

    >>> rgba("#bc002d", 0.5)
    'rgba(188, 0, 45, 0.50)'
    """
    r, g, b = hex_to_rgb(hex_color)
    a = max(0.0, min(1.0, alpha))
    return f"rgba({r}, {g}, {b}, {a:.2f})"


def hsl_adjust(hex_color: str, h_scale: float = 1.0, l_scale: float = 1.0, s_scale: float = 1.0) -> str:
    """Derive a hex color from hex_color with lightness and saturation scaled.

    Useful for building hover variants or subordinate tones from a base color
    without hardcoding a second hex value.

    l_scale > 1 → lighter, l_scale < 1 → darker.
    s_scale > 1 → more saturated, s_scale < 1 → more muted.
    Both values are clamped to [0, 1] after scaling.

    >>> hsl_adjust("#bc002d", l_scale=1.4)   # lighter red
    '#f20039'
    """
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    h_new = max(0.0, min(1.0, h * h_scale))
    l_new = max(0.0, min(1.0, l * l_scale))
    s_new = max(0.0, min(1.0, s * s_scale))
    r2, g2, b2 = colorsys.hls_to_rgb(h_new, l_new, s_new)
    return f"#{round(r2 * 255):02x}{round(g2 * 255):02x}{round(b2 * 255):02x}"


# ── 2. Chart math ─────────────────────────────────────────────────────────────

def nice_axis(max_val: int) -> tuple[float, float]:
    """Compute a clean (dtick, half_range) pair for a symmetric Plotly axis.

    half_range is always a clean dtick multiple with one full tick of headroom
    above max_val — prevents Plotly from snapping the range down and clipping bars.

    Returns a safe fallback for non-positive inputs.

    >>> nice_axis(4_800_000)
    (2000000, 5500000.0)
    """
    if max_val <= 0:
        return 1_000_000, 4_000_000

    raw_step   = max_val / 3
    magnitude  = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude

    if normalized < 1.5:
        snapped = 1
    elif normalized < 3.5:
        snapped = 2
    else:
        snapped = 5

    dtick      = snapped * magnitude
    n_ticks    = math.ceil(max_val / dtick)
    half_range = dtick * (n_ticks + 0.25)
    return dtick, half_range


def ceil_half_magnitude(val: float) -> float:
    """Round val up to the nearest 0.5 × 10^n.

    Used to pin colorscale bounds to clean display values.

    >>> ceil_half_magnitude(598_317)
    600000.0
    >>> ceil_half_magnitude(1_200_000)
    1500000.0
    """
    mag  = 10 ** math.floor(math.log10(abs(val)))
    step = mag * 0.5
    return math.ceil(val / step) * step


# ── 3. String ─────────────────────────────────────────────────────────────────

def shorten_age_label(label: str) -> str:
    """Strip verbose age suffixes used in Japanese census band labels.

    "0–4 years old"        → "0–4"
    "85 years and older"   → "85+"

    >>> shorten_age_label("0–4 years old")
    '0–4'
    >>> shorten_age_label("85 years and older")
    '85+'
    """
    return (label
            .replace(" years and older", "+")
            .replace(" years old", ""))


# ── 4. Demography ─────────────────────────────────────────────────────────────

def cohort_band(year: int, birth_start: int, birth_end: int) -> int | None:
    """Return the age_start of the scheme_a band containing the cohort in year.

    The cohort occupies ages (year - birth_end) to (year - birth_start).
    Snaps to the 5-year band floor of the older end (year - birth_end).
    Returns None if the cohort falls entirely outside the 0–85 range.

    >>> cohort_band(2015, 1947, 1949)   # dankai in 2015 → age 66–68 → band 65
    65
    >>> cohort_band(1920, 1947, 1949)   # not born yet
    None
    """
    age_low  = year - birth_end
    age_high = year - birth_start
    if age_high < 0 or age_low > 85:
        return None
    band_start = (max(age_low, 0) // 5) * 5
    return band_start


def cohort_band_range(year: int, birth_start: int, birth_end: int) -> list[int]:
    """Return all scheme_a band starts overlapping the cohort in year.

    A cohort born across multiple years can span two 5-year bands. This returns
    every band whose age range [b, b+4] overlaps the cohort's age range in year.

    >>> cohort_band_range(2015, 1947, 1949)   # dankai spans one band at 65
    [65]
    >>> cohort_band_range(2015, 1971, 1974)   # dankai jr spans 40 and 44
    [40, 44]
    """
    age_low  = max(year - birth_end, 0)
    age_high = min(year - birth_start, 85)
    if age_high < 0 or age_low > 85:
        return []
    return [b for b in range(0, 86, 5) if b <= age_high and b + 4 >= age_low]