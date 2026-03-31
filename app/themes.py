# app/themes.py
"""
Theme definitions for the Japan Population Dashboard.

Each theme is a flat-ish dict of color and shadow values. Non-color constants
(layout, font sizes, map center/zoom, line widths, etc.) live in config.py and
are theme-independent.

To swap themes: change ACTIVE_THEME_NAME below and restart the app.
"""


# ── Dark theme (default) ──────────────────────────────────────────────────────
# Deep navy — current production theme.

THEME_DARK = {

    # Surfaces
    "page_bg":      "#091023",   # outermost background — deep navy
    "panel_bg":     "#06091a",   # chart/card interiors — near-black
    "panel_border": "#334477",   # border stroke + slider track

    # Brand
    "primary":   "#bc002d",   # Japan red
    "secondary": "#ffffff",   # white

    # Text scale — light-on-dark
    # LO and HINT derived from MID via HSL lightness reduction:
    #   _hsl_adjust("#aaaadd", l_scale=0.65, s_scale=0.70) → #5959a5
    #   _hsl_adjust("#aaaadd", l_scale=0.45, s_scale=0.50) → #45456b
    "text_hi":   "#e0e8ff",   # highest contrast — KPI values
    "text_mid":  "#aaaadd",   # default — axis labels, legends, body
    "text_lo":   "#5959a5",   # subordinate labels, secondary annotations
    "text_hint": "#45456b",   # hint text, hairline separators

    # UI interaction
    "ui_hover":    "#243558",   # button/element hover fill
    "slider_track": "#1a2a44",  # slider rail

    # Chart
    "chart_grid":       "#1a2440",   # axis gridlines
    "accent_threshold": "#50e3c2",   # aging-index = 100 reference line
    "timeseries_pref":  "#ffffff",   # prefecture overlay line

    # Cohort annotations
    "accent_dankai":      "#f5a623",   # 団塊の世代
    "accent_dankai_jr":   "#7ed321",   # 団塊ジュニア
    "accent_wartime_gen": "#bc002d",   # 戦中世代 — matches Japan red
    "accent_shoushika":   "#9ee0ff",   # 少子化世代

    # Population pyramid
    "pyramid_male":   "#4a90d9",
    "pyramid_female": "#e07b8a",

    # Map
    "map_geo": {
        "bg_color":   "#091023",   # ocean / canvas — matches page bg
        "land_color": "#1c1f30",   # surrounding land — mid-tier depth
        "line_color": "#6089A0",   # prefecture border stroke
    },
    "map_highlight_line_color": "#ffffff",
    "map_highlight_fill":       "rgba(255, 255, 255, 0.08)",
    "map_colorscale": "plasma_r",
    "map_tile_style": "carto-darkmatter",

    # Shadows — derived from shadow_color × shadow_darkness in config.py
    "shadow_color":    "#091023",   # dark base = deep pool of page color
    "shadow_darkness": 0.40,
}


# ── Light theme — 和 (Wa) ─────────────────────────────────────────────────────
# Japanese traditional aesthetic: washi paper, sumi ink, indigo accents.
# Inspired by ukiyo-e palette — warm creams, deep earth tones, restrained color.

THEME_LIGHT = {

    # Surfaces
    "page_bg":      "#f5f0e8",   # washi paper cream
    "panel_bg":     "#ede2d0",   # slightly whiter panel interior
    "panel_border": "#c8b99a",   # warm tan border

    # Brand
    "primary":   "#bc002d",   # Japan red — consistent across themes
    "secondary": "#2d1f0e",   # sumi ink dark brown for secondary emphasis

    # Text scale — dark-on-light (hierarchy is inverted vs dark theme:
    # hi = darkest/most contrast, hint = lightest/least contrast)
    "text_hi":   "#1a1209",   # sumi ink near-black — highest contrast
    "text_mid":  "#4a3f30",   # warm dark brown — default body/labels
    "text_lo":   "#8a7a6a",   # medium warm grey-brown — secondary labels
    "text_hint": "#b0a090",   # light warm grey — hint, disabled, hairlines

    # UI interaction
    "ui_hover":    "#ece4d8",   # soft warm hover
    "slider_track": "#d4c4aa",  # warm tan track

    # Chart
    "chart_grid":       "#dfcdb7",   # subtle warm gridlines
    "accent_threshold": "#2d6a4f",   # forest green — legible on light bg
    "timeseries_pref":  "#2d4a7a",   # indigo blue

    # Cohort annotations — darkened for legibility on light background
    "accent_dankai":      "#e69225",   # amber
    "accent_dankai_jr":   "#6bbb26",   # emerald green
    "accent_wartime_gen": "#bc002d",   # Japan red
    "accent_shoushika":   "#9ee0ff",   # crystal

    # Population pyramid
    "pyramid_male":   "#2d6a9f",   # deep blue
    "pyramid_female": "#c0445a",   # deep rose

    # Map
    "map_geo": {
        "bg_color":   "#f5f0e8",   # ocean — matches page bg
        "land_color": "#e0d5c0",   # surrounding land — warm off-white
        "line_color": "#8a7a6a",   # prefecture border — warm brown
    },
    "map_highlight_line_color": "#1a1209",
    "map_highlight_fill":       "rgba(26, 18, 9, 0.08)",
    "map_colorscale": "YlOrRd",         # warm sequential — readable on light map
    "map_tile_style": "carto-positron",  # light Mapbox tile

    # Shadows — dark base against light panels
    "shadow_color":    "#3a2a1a",   # dark warm brown gives visible depth
    "shadow_darkness": 0.12,        # subtle — light themes need lighter shadows
}


# ── Registry + active selection ───────────────────────────────────────────────

THEMES = {
    "dark":  THEME_DARK,
    "light": THEME_LIGHT,
}

# ↓ Change this line to swap themes. Restart the app after changing.
ACTIVE_THEME_NAME = "light"

ACTIVE_THEME = THEMES[ACTIVE_THEME_NAME]