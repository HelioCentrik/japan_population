# app/aesthetics/fonts.py
"""
Japanese-compatible web font catalogue and CSS font-stack builder.
Font *sizes* are defined in app/aesthetics/config.py — not here.

[GF] = available on Google Fonts.
Google Fonts families must be loaded in index_string.py via <link> or @import
for the custom names to resolve. System fonts and generic keywords work without loading.
"""

# ── Catalogues ─────────────────────────────────────────────────────────────────
# Format: (family_name, notes)

FONTS_SANS: list[tuple[str, str]] = [
    ("Noto Sans JP",    "[GF] — broad JP glyph coverage, clean at all weights"),
    ("M PLUS 1p",       "[GF] — modern JP sans, strong legibility at small sizes"),
    ("BIZ UDGothic",    "[GF] — universal design, high legibility standard"),
    ("Source Han Sans", "Adobe — full JP/CN/KR coverage; not on GF"),
    ("Hiragino Sans",   "macOS / iOS system font — no-op on other platforms"),
    ("Yu Gothic UI",    "Windows 10+ system — UI variant preferred over plain 'Yu Gothic'"),
    ("Meiryo",          "Windows legacy — last-resort system fallback"),
    ("system-ui",       "OS default sans — final pre-generic fallback"),
    ("sans-serif",      "CSS generic"),
]

FONTS_SERIF: list[tuple[str, str]] = [
    ("Noto Serif JP",       "[GF] — elegant JP serif, designed to pair with Noto Sans JP"),
    ("Source Han Serif",    "Adobe — premium JP serif; not on GF"),
    ("Hiragino Mincho Pro", "macOS system serif"),
    ("Yu Mincho",           "Windows system serif"),
    ("serif",               "CSS generic"),
]

FONTS_MONO: list[tuple[str, str]] = [
    ("JetBrains Mono",  "[GF] — clean mono, reasonable JP symbol coverage"),
    ("Source Code Pro", "[GF] — reliable with decent JP fallback"),
    ("Noto Sans Mono",  "[GF] — consistent with Noto family"),
    ("monospace",       "CSS generic"),
]

# ── Stack builder ──────────────────────────────────────────────────────────────
_CSS_GENERICS = frozenset({
    "sans-serif", "serif", "monospace", "cursive", "fantasy", "system-ui"
})


def _stack(*names: str) -> str:
    """
    Build a CSS-ready font-family string from an ordered sequence of font names.
    Multi-word names are double-quoted. Single-word names and CSS generic keywords
    (sans-serif, serif, monospace, system-ui, etc.) are left unquoted.

    Example:
        _stack("Noto Sans JP", "Hiragino Sans", "system-ui", "sans-serif")
        → '"Noto Sans JP", "Hiragino Sans", system-ui, sans-serif'
    """
    parts = []
    for name in names:
        if name in _CSS_GENERICS or " " not in name:
            parts.append(name)
        else:
            parts.append(f'"{name}"')
    return ", ".join(parts)
