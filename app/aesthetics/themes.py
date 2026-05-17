# app/aesthetics/themes.py
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
        "page":      "#0c0e21",  # darkest wave — near-black indigo
        "panel":     "#1b2750",  # deep wave body
        "border":    "#345a93",  # mid-wave blue border
        "hover":     "#183662",  # hover — just above panel
        "grid":      "#1b2843",  # chart grid
        "plot":      "#0e1a30",  # plot area — below panel
        "track":     "#1b2e4b",  # slider track
        "text_hint": "#6d5d46",  # dark sepia — barely legible
        "text_lo":   "#907b56",  # faded parchment — subordinate
        "text_mid":  "#e7cea6",  # parchment mid — body / axis text
        "text_hi":   "#f2e9d9",  # bright parchment sky — headings / values
    }

    # ── Brand and annotation colors ────────────────────────────────────
    accent = {
        "primary":  "#d4443a",  # boat-timber ochre — primary CTA / accent
        "kincha":   "#B08A40",  # muted gold — year label / secondary UI
        "warning":  "#d4443a",  # amber warning
        "blue":     "#3868B8",  # Great Wave mid-blue — threshold reference line
        "ink":      "#04080F",  # near-black — shadow_color
    }

    # ── Data encoding colors ───────────────────────────────────────────
    data = {
        "male":   "#477EEB",  # keep — discrimination matters
        "female": "#E4536B",  # keep — discrimination matters
        "pref":   "#C4A87A",  # parchment — timeseries pref overlay
    }

    return {
        # Surfaces
        "page_bg":      surface["page"],
        "panel_bg":     surface["panel"],
        "panel_border": surface["border"],
        # Brand
        "primary":   accent["primary"],
        "secondary": accent["kincha"],
        # Text scale — warm parchment, not blue
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
        "accent_threshold": accent["blue"],
        "timeseries_pref":  data["pref"],
        # Cohort annotations — hardcoded; must not drift with accent renames
        "accent_dankai":      "#D4873A",  # 団塊の世代
        "accent_dankai_jr":   "#7AB830",  # 団塊ジュニア
        "accent_wartime_gen": accent["warning"],  # 戦中世代
        "accent_shoushika":   "#9ECFDE",  # 少子化世代
        # Population pyramid
        "pyramid_male":   data["male"],
        "pyramid_female": data["female"],
        # Tooltip
        "tooltip_bg":          "#0D1428",
        "tooltip_border":      "#1A2840",
        "tooltip_border_size": "1.5px",
        "tooltip_text_hi":     surface["text_hi"],
        "tooltip_text_mid":    surface["text_mid"],
        "tooltip_hint":        surface["text_hint"],
        "tooltip_divider":     "rgba(200, 168, 122, 0.15)",
        # Map (passthroughs)
        "map_geo": {
            "bg_color":   surface["page"],
            "land_color": "#1A2840",
            "line_color": surface["text_lo"],
        },
        "map_highlight_line_color": surface["text_hi"],
        "map_highlight_fill":       "rgba(20, 60, 160, 0.15)",
        "map_colorscale": "plasma_r",
        "map_tile_style": "carto-darkmatter-nolabels",
        # Shadows — vestigial but still wired in config.py; do not remove keys
        "bezel_hi_alpha":  0.10,
        "bezel_lo_alpha":  0.50,
        "shadow_color":    accent["ink"],
        "shadow_darkness": 0.65,
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
        "tooltip_border_size": "2.5px",
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
