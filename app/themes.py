# app/themes.py
"""
Theme definitions for the Japan Population Dashboard.

Each theme is built by a function that defines three internal color buckets,
then resolves them into the flat token dict that config.py expects.

  N — Neutral scale: 9–10 steps, low=light, high=dark.
      Covers all surfaces, borders, and text. One step per semantic token.
  A — Accent palette: named keys for brand and annotation colors.
  D — Data palette: named keys for chart data encoding.

Non-color values (map config, colorscales, shadow floats) are passthroughs.
_neutral, _accent, _data expose raw buckets for introspection / template builder.

To swap themes: change ACTIVE_THEME_NAME below and restart.
"""


def _build_dark_theme() -> dict:
    # ── Neutral scale: navy, 100=near-white → 900=near-black ──────────
    N = {
        100: "#e0e8ff",  # → text_hi
        200: "#aaaadd",  # → text_mid
        300: "#5959a5",  # → text_lo
        400: "#45456b",  # → text_hint
        500: "#243558",  # → ui_hover
        600: "#1a2a44",  # → slider_track
        700: "#1a2440",  # → chart_grid
        800: "#334477",  # → panel_border
        850: "#06091a",  # → panel_bg
        900: "#091023",  # → page_bg
    }

    # ── Accent palette ─────────────────────────────────────────────────
    A = {
        "primary": "#bc002d",  # Japan red
        "white":   "#ffffff",
        "teal":    "#50e3c2",  # threshold reference line
        "amber":   "#f5a623",  # 団塊の世代
        "lime":    "#7ed321",  # 団塊ジュニア
        "sky":     "#9ee0ff",  # 少子化世代
    }

    # ── Data palette ───────────────────────────────────────────────────
    D = {
        "male":   "#4a90d9",
        "female": "#e07b8a",
        "pref":   "#ffffff",  # timeseries prefecture overlay
    }

    return {
        # Surfaces
        "page_bg":      N[900],
        "panel_bg":     N[850],
        "panel_border": N[800],
        # Brand
        "primary":   A["primary"],
        "secondary": A["white"],
        # Text scale
        "text_hi":   N[100],
        "text_mid":  N[200],
        "text_lo":   N[300],
        "text_hint": N[400],
        # UI interaction
        "ui_hover":     N[500],
        "slider_track": N[600],
        # Chart
        "chart_grid":       N[700],
        "accent_threshold": A["teal"],
        "timeseries_pref":  D["pref"],
        # Cohort annotations
        "accent_dankai":      A["amber"],
        "accent_dankai_jr":   A["lime"],
        "accent_wartime_gen": A["primary"],
        "accent_shoushika":   A["sky"],
        # Population pyramid
        "pyramid_male":   D["male"],
        "pyramid_female": D["female"],
        # Map (passthroughs)
        "map_geo": {
            "bg_color":   N[900],
            "land_color": "#1c1f30",  # no neutral-scale equivalent
            "line_color": "#6089A0",  # map-specific mid blue-grey
        },
        "map_highlight_line_color": A["white"],
        "map_highlight_fill":       "rgba(255, 255, 255, 0.08)",
        "map_colorscale": "plasma_r",
        "map_tile_style": "carto-darkmatter",
        # Shadows
        "shadow_color":    N[900],
        "shadow_darkness": 0.40,
        # Raw scales for introspection
        "_neutral": N,
        "_accent":  A,
        "_data":    D,
    }


def _build_light_theme() -> dict:
    # ── Neutral scale: warm paper, 100=near-white → 900=near-black ────
    N = {
        100: "#f5f0e8",  # → page_bg
        150: "#ede2d0",  # → panel_bg
        200: "#ece4d8",  # → ui_hover
        250: "#dfcdb7",  # → chart_grid
        300: "#d4c4aa",  # → slider_track
        350: "#c8b99a",  # → panel_border
        500: "#b0a090",  # → text_hint
        600: "#8a7a6a",  # → text_lo
        700: "#4a3f30",  # → text_mid
        900: "#1a1209",  # → text_hi
    }

    # ── Accent palette ─────────────────────────────────────────────────
    A = {
        "primary": "#bc002d",  # Japan red
        "ink":     "#2d1f0e",  # sumi dark brown
        "forest":  "#2d6a4f",  # threshold reference line (legible on light)
        "amber":   "#e69225",  # 団塊の世代 (darkened for light bg)
        "lime":    "#6bbb26",  # 団塊ジュニア
        "sky":     "#9ee0ff",  # 少子化世代
    }

    # ── Data palette ───────────────────────────────────────────────────
    D = {
        "male":   "#2d6a9f",
        "female": "#c0445a",
        "pref":   "#2d4a7a",  # indigo timeseries overlay
    }

    return {
        # Surfaces
        "page_bg":      N[100],
        "panel_bg":     N[150],
        "panel_border": N[350],
        # Brand
        "primary":   A["primary"],
        "secondary": A["ink"],
        # Text scale
        "text_hi":   N[900],
        "text_mid":  N[700],
        "text_lo":   N[600],
        "text_hint": N[500],
        # UI interaction
        "ui_hover":     N[200],
        "slider_track": N[300],
        # Chart
        "chart_grid":       N[250],
        "accent_threshold": A["forest"],
        "timeseries_pref":  D["pref"],
        # Cohort annotations
        "accent_dankai":      A["amber"],
        "accent_dankai_jr":   A["lime"],
        "accent_wartime_gen": A["primary"],
        "accent_shoushika":   A["sky"],
        # Population pyramid
        "pyramid_male":   D["male"],
        "pyramid_female": D["female"],
        # Map (passthroughs)
        "map_geo": {
            "bg_color":   N[100],
            "land_color": "#e0d5c0",
            "line_color": N[600],
        },
        "map_highlight_line_color": N[900],
        "map_highlight_fill":       "rgba(26, 18, 9, 0.08)",
        "map_colorscale": "YlOrRd",
        "map_tile_style": "carto-positron",
        # Shadows
        "shadow_color":    A["ink"],
        "shadow_darkness": 0.12,
        # Raw scales for introspection
        "_neutral": N,
        "_accent":  A,
        "_data":    D,
    }


# ── Registry + active selection ───────────────────────────────────────────────

THEMES = {
    "dark":  _build_dark_theme(),
    "light": _build_light_theme(),
}

# ↓ Change this line to swap themes. Restart the app after changing.
ACTIVE_THEME_NAME = "dark"

ACTIVE_THEME = THEMES[ACTIVE_THEME_NAME]