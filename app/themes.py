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
        100: "#06091a",  # → page_bg
        150: "#142148",  # → panel_bg
        160: "#324a8f",  # → panel_border
        200: "#27418e",  # → ui_hover
        250: "#455892",  # → chart_grid
        260: "#7684b2",  # → chart_plot
        300: "#1a2a44",  # → slider_track
        500: "#45456b",  # → text_hint
        550: "#2f2f62",  # → text_dark
        600: "#5959a5",  # → text_lo
        700: "#b6b6f6",  # → text_mid
        900: "#cfdbff",  # → text_hi
    }

    # ── Accent palette ─────────────────────────────────────────────────
    A = {
        "primary": "#bc002d",  # Japan red
        "white":   "#ffffff",
        "teal":    "#00ccaa",  # threshold reference line
        "amber":   "#f08d0b",  # 団塊の世代
        "lime":    "#64b909",  # 団塊ジュニア
        "sky":     "#9ee0ff",  # 少子化世代
        "ink":     "#2d1f0e",  # sumi dark brown
    }

    # ── Data palette ───────────────────────────────────────────────────
    D = {
        "male":   "#183a95",
        "female": "#97172a",
        "pref":   "#ffffff",  # timeseries prefecture overlay
    }

    return {
        # Surfaces
        "page_bg":      N[100],
        "panel_bg":     N[150],
        "panel_border": N[160],
        # Brand
        "primary":   A["primary"],
        "secondary": A["white"],
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
        "chart_plot_color": N[260],
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
            "bg_color":   N[100],
            "land_color": "#1c1f30",  # no neutral-scale equivalent
            "line_color": "#6089A0",  # map-specific mid blue-grey
        },
        "map_highlight_line_color": A["white"],
        "map_highlight_fill":       "rgba(255, 255, 255, 0.08)",
        "map_colorscale": "plasma_r",
        "map_tile_style": "carto-darkmatter",
        # Shadows
        "bezel_hi_alpha": 0.25,
        "bezel_lo_alpha": 1,
        "shadow_color":   A["white"],
        "shadow_darkness": 0.2,
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
        160: "#d0c19f",  # → panel_border
        200: "#e7d9c6",  # → ui_hover
        250: "#dfcdb7",  # → chart_grid
        260: "#f1ece4",  # → chart_plot_color
        300: "#e7dbc6",  # → slider_track
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
        "amber":   "#faa434",  # 団塊の世代 (darkened for light bg)
        "lime":    "#6bd211",  # 団塊ジュニア
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
        "panel_border": N[160],
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
        "chart_plot_color": N[260],
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
        "shadow_darkness": 0.32,
        "bezel_hi_alpha": 0.9,
        "bezel_lo_alpha": 0.4,
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