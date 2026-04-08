# app/themes.py
"""
Theme definitions for the Japan Population Dashboard.

Each theme is built by a function that defines three internal color buckets,
then resolves them into the flat token dict that config.py expects.

  surface — Named neutrals: surfaces, borders, UI states, and text scale.
            Keys are descriptive — what the color does, not an abstract index.
  accent  — Brand and annotation colors: named by intent.
  data    — Chart data-encoding colors: named by the series they represent.

Non-color values (map config, colorscales, shadow floats) are passthroughs.
All three buckets are internal scaffolding — only semantic tokens leave the
builder via the return dict. Nothing outside themes.py reads the raw buckets.

To swap themes: change ACTIVE_THEME_NAME below and restart.
"""
from app.utils import hsl_adjust



def _build_dark_theme() -> dict:
    # ── Surfaces, borders, UI states, text scale ───────────────────────
    surface = {
        "page":      "#06091a",  # → page_bg
        "panel":     "#142148",  # → panel_bg
        "border":    "#324a8f",  # → panel_border
        "hover":     "#162a64",  # → ui_hover
        "grid":      "#272f53",  # → chart_grid
        "plot":      "#0f142e",  # → chart_plot_color
        "track":     "#1a2a44",  # → slider_track
        "text_hint": "#6a6a9e",  # → text_hint  (de-emphasised, still legible)
        "text_lo":   "#8c8cca",  # → text_lo    (subordinate text)
        "text_mid":  "#b6b6f6",  # → text_mid   (body / axis text)
        "text_hi":   "#cfdbff",  # → text_hi    (headings / primary values)
    }

    # ── Brand and annotation colors ────────────────────────────────────
    accent = {
        "primary": "#bc002d",  # Japan red
        "white":   "#ffffff",
        "warning": "#f0a830",  # warning red
        "teal":    "#00ccaa",  # threshold reference line
        "amber":   "#f08d0b",  # 団塊の世代
        "lime":    "#64b909",  # 団塊ジュニア
        "sky":     "#9ee0ff",  # 少子化世代
        "ink":     "#2d1f0e",  # sumi dark brown
    }

    # ── Data encoding colors ───────────────────────────────────────────
    data = {
        "male":   "#3f67d5",
        "female": "#ce3b51",
        "pref":   "#ffffff",  # timeseries prefecture overlay
    }

    return {
        # Surfaces
        "page_bg":      surface["page"],
        "panel_bg":     surface["panel"],
        "panel_border": surface["border"],
        # Brand
        "primary":   accent["primary"],
        "secondary": accent["white"],
        # Text scale
        "text_hi":   surface["text_hi"],
        "text_mid":  surface["text_mid"],
        "text_lo":   surface["text_lo"],
        "text_hint": surface["text_hint"],
        # UI interaction
        "ui_hover":     surface["hover"],
        "slider_track": surface["track"],
        # Chart
        "chart_grid":       surface["grid"],
        "chart_plot_color": surface["plot"],
        "accent_threshold": accent["teal"],
        "timeseries_pref":  data["pref"],
        # Cohort annotations
        "accent_dankai":      accent["amber"],
        "accent_dankai_jr":   accent["lime"],
        "accent_wartime_gen": accent["primary"],
        "accent_shoushika":   accent["sky"],
        # Population pyramid
        "pyramid_male":   data["male"],
        "pyramid_female": data["female"],
        # Tooltip
        "tooltip_bg": hsl_adjust(surface["panel"], h_scale=1.035, s_scale=0.7, l_scale=1.15),
        "tooltip_border": surface["border"],
        "tooltip_border_size": "1px",
        "tooltip_text_hi": surface["text_hi"],
        "tooltip_text_mid": surface["text_mid"],
        "tooltip_hint": surface["text_hint"],
        "tooltip_divider": "rgba(255, 255, 255, 0.20)",
        # Map (passthroughs)
        "map_geo": {
            "bg_color":   surface["page"],
            "land_color": "#1c1f30",
            "line_color": "#6089A0",
        },
        "map_highlight_line_color": accent["white"],
        "map_highlight_fill":       "rgba(255, 255, 255, 0.08)",
        "map_colorscale": "plasma_r",
        "map_tile_style": "carto-darkmatter",
        # Shadows
        "bezel_hi_alpha":  0.25,
        "bezel_lo_alpha":  0.85,
        "shadow_color":    accent["white"],
        "shadow_darkness": 0.2,
        # Miscellaneous
        "warning": accent["warning"],
    }


def _build_light_theme() -> dict:
    # ── Surfaces, borders, UI states, text scale ───────────────────────
    surface = {
        "page":      "#f5f0e8",  # → page_bg
        "panel":     "#ede2d0",  # → panel_bg
        "border":    "#d0c19f",  # → panel_border
        "hover":     "#e7d9c6",  # → ui_hover
        "grid":      "#dfcdb7",  # → chart_grid
        "plot":      "#f1ece4",  # → chart_plot_color
        "track":     "#e7dbc6",  # → slider_track
        "text_hint": "#b0a090",  # → text_hint
        "text_lo":   "#8a7a6a",  # → text_lo
        "text_mid":  "#4a3f30",  # → text_mid
        "text_hi":   "#1a1209",  # → text_hi
    }

    # ── Brand and annotation colors ────────────────────────────────────
    accent = {
        "primary": "#bc002d",  # Japan red
        "ink":     "#2d1f0e",  # sumi dark brown
        "warning": "#c47a00",  # warning red
        "forest":  "#2d6a4f",  # threshold reference line (legible on light)
        "amber":   "#faa434",  # 団塊の世代
        "lime":    "#6bd211",  # 団塊ジュニア
        "sky":     "#9ee0ff",  # 少子化世代
    }

    # ── Data encoding colors ───────────────────────────────────────────
    data = {
        "male":   "#2d6a9f",
        "female": "#c0445a",
        "pref":   "#2d4a7a",  # indigo timeseries overlay
    }

    return {
        # Surfaces
        "page_bg":      surface["page"],
        "panel_bg":     surface["panel"],
        "panel_border": surface["border"],
        # Brand
        "primary":   accent["primary"],
        "secondary": accent["ink"],
        # Text scale
        "text_hi":   surface["text_hi"],
        "text_mid":  surface["text_mid"],
        "text_lo":   surface["text_lo"],
        "text_hint": surface["text_hint"],
        # UI interaction
        "ui_hover":     surface["hover"],
        "slider_track": surface["track"],
        # Chart
        "chart_grid":       surface["grid"],
        "chart_plot_color": surface["plot"],
        "accent_threshold": accent["forest"],
        "timeseries_pref":  data["pref"],
        # Cohort annotations
        "accent_dankai":      accent["amber"],
        "accent_dankai_jr":   accent["lime"],
        "accent_wartime_gen": accent["primary"],
        "accent_shoushika":   accent["sky"],
        # Population pyramid
        "pyramid_male":   data["male"],
        "pyramid_female": data["female"],
        # Tooltip
        "tooltip_bg": "#f9f5ee",
        "tooltip_border": surface["border"],
        "tooltip_border_size": "1px",
        "tooltip_text_hi": surface["text_hi"],
        "tooltip_text_mid": surface["text_mid"],
        "tooltip_hint": surface["text_hint"],
        "tooltip_divider": "rgba(0, 0, 0, 0.10)",
        # Map (passthroughs)
        "map_geo": {
            "bg_color":   surface["page"],
            "land_color": "#e0d5c0",
            "line_color": surface["text_lo"],
        },
        "map_highlight_line_color": surface["text_hi"],
        "map_highlight_fill":       "rgba(26, 18, 9, 0.08)",
        "map_colorscale": "YlOrRd",
        "map_tile_style": "carto-positron",
        # Shadows
        "bezel_hi_alpha":  0.9,
        "bezel_lo_alpha":  0.4,
        "shadow_color":    accent["ink"],
        "shadow_darkness": 0.32,
        # Miscellaneous
        "warning": accent["warning"],
    }


# ── Registry + active selection ───────────────────────────────────────────────

THEMES = {
    "dark":  _build_dark_theme(),
    "light": _build_light_theme(),
}

# ↓ Change this line to swap themes. Restart the app after changing.
ACTIVE_THEME_NAME = "dark"

ACTIVE_THEME = THEMES[ACTIVE_THEME_NAME]