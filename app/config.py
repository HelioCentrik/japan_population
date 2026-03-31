# app/config.py
"""
Single source of truth for all dashboard constants.

Colors and shadows come from the active theme in app/themes.py.
Everything else (layout, fonts, sizes, structural map config, etc.) is defined here.

To swap themes: change ACTIVE_THEME_NAME in app/themes.py and restart the app.

Sections:
  1.  Private helpers     (hex parsing, rgba builder, HSL adjustment utility)
  2.  Layout
  3.  Colors              (unpacked from active theme — do not hardcode here)
  4.  Shadows             (derived from theme's shadow_color × shadow_darkness)
  5.  Fonts
  6.  Font sizes
  7.  Spacing & borders
  8.  Map configuration   (structural — center, zoom, widths are theme-independent)
  9.  Pyramid configuration
  10. Play button
  11. Playback
  12. Markers & lines
  13. THEME dict
  14. Legacy constants
"""

import colorsys

from app.fonts import _stack
from app.themes import ACTIVE_THEME as _t, ACTIVE_THEME_NAME


# ── 1. Private helpers ────────────────────────────────────────────────────────

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Parse a 6-digit hex color string into (r, g, b) ints."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgba(hex_color: str, alpha: float) -> str:
    """Return a CSS rgba() string from a hex color and alpha in [0, 1]."""
    r, g, b = _hex_to_rgb(hex_color)
    a = max(0.0, min(1.0, alpha))
    return f"rgba({r}, {g}, {b}, {a:.2f})"


def _hsl_adjust(hex_color: str, l_scale: float = 1.0, s_scale: float = 1.0) -> str:
    """
    Utility: derive a color from hex_color with lightness and saturation scaled.
    Useful for building subordinate or hover variants from a base color.
    Not used at module load time — theme text scales are defined explicitly in themes.py.
    """
    r, g, b = _hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    l_new = max(0.0, min(1.0, l * l_scale))
    s_new = max(0.0, min(1.0, s * s_scale))
    r2, g2, b2 = colorsys.hls_to_rgb(h, l_new, s_new)
    return f"#{round(r2 * 255):02x}{round(g2 * 255):02x}{round(b2 * 255):02x}"


# ── 2. Layout ─────────────────────────────────────────────────────────────────

LAYOUT_GAP          = "0.8rem"
LAYOUT_OUTER_PAD    = "1rem"
LAYOUT_MIN_HEIGHT   = "700px"

CHARTS_ANCHOR       = 10
CHARTS_ROW_FLEX     = 7
CHARTS_TS_FLEX      = CHARTS_ANCHOR - CHARTS_ROW_FLEX  # = 3

MAP_MIN_HEIGHT      = "320px"
MAP_FLEX            = 7
PYRAMID_FLEX        = 3


# ── 3. Colors ─────────────────────────────────────────────────────────────────
# All color constants are unpacked from the active theme.
# Do not hardcode hex values here — add them to themes.py instead.

# Surfaces
PAGE_BG         = _t["page_bg"]
PANEL_BG        = _t["panel_bg"]
PANEL_BORDER    = _t["panel_border"]

# Brand
COLOR_PRIMARY   = _t["primary"]
COLOR_SECONDARY = _t["secondary"]

# Text scale
COLOR_TEXT_HI   = _t["text_hi"]
COLOR_TEXT_MID  = _t["text_mid"]
COLOR_TEXT_LO   = _t["text_lo"]
COLOR_TEXT_HINT = _t["text_hint"]

# UI interaction
COLOR_UI_HOVER     = _t["ui_hover"]
SLIDER_TRACK_COLOR = _t["slider_track"]

# Chart
CHART_GRID_COLOR      = _t["chart_grid"]
ACCENT_THRESHOLD      = _t["accent_threshold"]
TIMESERIES_PREF_COLOR = _t["timeseries_pref"]

# Cohort annotations
ACCENT_DANKAI       = _t["accent_dankai"]
ACCENT_DANKAI_JR    = _t["accent_dankai_jr"]
ACCENT_WARTIME_GEN  = _t["accent_wartime_gen"]
ACCENT_SHOUSHIKA    = _t["accent_shoushika"]

WWII_SEX_RATIO_THRESHOLD = 90   # structural threshold — not a color

COHORT_COLORS = {
    "dankai":       ACCENT_DANKAI,
    "dankai_jr":    ACCENT_DANKAI_JR,
    "wwii_scar":    ACCENT_WARTIME_GEN,
    "shoushika":    ACCENT_SHOUSHIKA,
    "threshold":    ACCENT_THRESHOLD,
}

# Pyramid
PYRAMID_MALE_COLOR   = _t["pyramid_male"]
PYRAMID_FEMALE_COLOR = _t["pyramid_female"]

# Map colors
MAP_GEO                  = _t["map_geo"]
MAP_HIGHLIGHT_LINE_COLOR = _t["map_highlight_line_color"]
MAP_HIGHLIGHT_FILL       = _t["map_highlight_fill"]
MAP_COLORSCALE           = _t["map_colorscale"]
MAP_TILE_STYLE           = _t["map_tile_style"]


# ── 4. Shadows ────────────────────────────────────────────────────────────────
# Derived from the theme's shadow_color and shadow_darkness knob.
# Using an explicit shadow_color (rather than PAGE_BG) lets light themes
# use dark shadows without coupling shadow depth to background hue.

SHADOW_DARKNESS  = _t["shadow_darkness"]
_SHADOW_COLOR    = _t["shadow_color"]
SHADOW_PANEL     = _rgba(_SHADOW_COLOR, SHADOW_DARKNESS)
SHADOW_MAP_INSET = _rgba(_SHADOW_COLOR, min(1.0, SHADOW_DARKNESS * 1.6))


# ── 5. Fonts ──────────────────────────────────────────────────────────────────
# Font names match the catalogue in app/fonts.py.
# [GF] families must be linked in app/index_string.py to load on client.

FONT_STACK_SANS = _stack(
    "Noto Sans JP",   # [GF]
    "M PLUS 1p",      # [GF]
    "BIZ UDGothic",   # [GF]
    "Hiragino Sans",  # macOS system
    "Yu Gothic UI",   # Windows 10+ system
    "Meiryo",         # Windows legacy
    "system-ui",
    "sans-serif",
)

FONT_STACK_SERIF = _stack(
    "Noto Serif JP",       # [GF]
    "Hiragino Mincho Pro", # macOS system
    "Yu Mincho",           # Windows system
    "serif",
)

FONT_STACK_MONO = _stack(
    "JetBrains Mono",  # [GF]
    "Source Code Pro", # [GF]
    "Noto Sans Mono",  # [GF]
    "monospace",
)


# ── 6. Font sizes ─────────────────────────────────────────────────────────────

FONT_SIZE_AXIS_TICK     = 11
FONT_SIZE_AXIS_TITLE    = 11
FONT_SIZE_LEGEND        = 14
FONT_SIZE_CHART_TITLE   = 13
FONT_SIZE_COLORBAR      = 12
FONT_SIZE_COLORBAR_TICK = 14
FONT_SIZE_KPI_LABEL     = 11
FONT_SIZE_KPI_VALUE     = 22
FONT_SIZE_KPI_SUB       = 12
FONT_SIZE_TITLE         = 32


# ── 7. Spacing & borders ──────────────────────────────────────────────────────

PANEL_BORDER_RADIUS = "6px"


# ── 8. Map configuration ──────────────────────────────────────────────────────
# Structural values — these don't vary by theme.

MAP_CENTER_LAT           = 35.5
MAP_CENTER_LON           = 135.5
MAP_DEFAULT_ZOOM         = 3.65
MAP_BORDER_WIDTH         = 0.8
MAP_HIGHLIGHT_LINE_WIDTH = 2.5


# ── 9. Pyramid configuration ─────────────────────────────────────────────────

PYRAMID_BARGAP       = 0.15
COHORT_OUTLINE_WIDTH = 3.5


# ── 10. Play button ───────────────────────────────────────────────────────────

PLAY_BTN_SIZE_PX   = 52
PLAY_BTN_SIZE      = f"{PLAY_BTN_SIZE_PX}px"
PLAY_BTN_FONT_SIZE = f"{round(PLAY_BTN_SIZE_PX * 0.538)}px"


# ── 11. Playback ──────────────────────────────────────────────────────────────

PLAY_INTERVAL_MS = 1000


# ── 12. Markers & lines ───────────────────────────────────────────────────────

MARKER_SIZE_DOT         = 5
MARKER_SIZE_1945        = 11
MARKER_SIZE_DIAMOND     = 8
MARKER_SIZE_LEGEND_SQ   = 10

LINE_WIDTH_MAIN         = 2.0
LINE_WIDTH_PREF         = 1.5
LINE_WIDTH_1945         = 2.5
LINE_WIDTH_THRESHOLD    = 1.2
LINE_WIDTH_YEAR_MARKER  = 1.0

OPACITY_THRESHOLD_LINE  = 0.55
OPACITY_YEAR_VLINE      = 0.35


# ── 13. THEME dict ────────────────────────────────────────────────────────────

THEME = {
    "active_theme": ACTIVE_THEME_NAME,
    "colors": {
        "page_bg":              PAGE_BG,
        "panel_bg":             PANEL_BG,
        "panel_border":         PANEL_BORDER,
        "primary":              COLOR_PRIMARY,
        "secondary":            COLOR_SECONDARY,
        "text_hi":              COLOR_TEXT_HI,
        "text_mid":             COLOR_TEXT_MID,
        "text_lo":              COLOR_TEXT_LO,
        "text_hint":            COLOR_TEXT_HINT,
        "ui_hover":             COLOR_UI_HOVER,
        "slider_track":         SLIDER_TRACK_COLOR,
        "chart_grid":           CHART_GRID_COLOR,
        "threshold":            ACCENT_THRESHOLD,
        "dankai":               ACCENT_DANKAI,
        "dankai_jr":            ACCENT_DANKAI_JR,
        "wartime_gen":          ACCENT_WARTIME_GEN,
        "shoushika":            ACCENT_SHOUSHIKA,
        "pyramid_male":         PYRAMID_MALE_COLOR,
        "pyramid_female":       PYRAMID_FEMALE_COLOR,
        "timeseries_pref":      TIMESERIES_PREF_COLOR,
        "map_highlight_line":   MAP_HIGHLIGHT_LINE_COLOR,
        "map_highlight_fill":   MAP_HIGHLIGHT_FILL,
    },
    "shadows": {
        "darkness":  SHADOW_DARKNESS,
        "panel":     SHADOW_PANEL,
        "map_inset": SHADOW_MAP_INSET,
    },
    "fonts": {
        "sans":  FONT_STACK_SANS,
        "serif": FONT_STACK_SERIF,
        "mono":  FONT_STACK_MONO,
        "sizes": {
            "axis_tick":     FONT_SIZE_AXIS_TICK,
            "axis_title":    FONT_SIZE_AXIS_TITLE,
            "legend":        FONT_SIZE_LEGEND,
            "chart_title":   FONT_SIZE_CHART_TITLE,
            "colorbar":      FONT_SIZE_COLORBAR,
            "colorbar_tick": FONT_SIZE_COLORBAR_TICK,
            "kpi_label":     FONT_SIZE_KPI_LABEL,
            "kpi_value":     FONT_SIZE_KPI_VALUE,
            "kpi_sub":       FONT_SIZE_KPI_SUB,
            "title":         FONT_SIZE_TITLE,
        },
    },
    "layout": {
        "gap":             LAYOUT_GAP,
        "outer_pad":       LAYOUT_OUTER_PAD,
        "min_height":      LAYOUT_MIN_HEIGHT,
        "border_radius":   PANEL_BORDER_RADIUS,
        "charts_row_flex": CHARTS_ROW_FLEX,
        "charts_ts_flex":  CHARTS_TS_FLEX,
        "map_flex":        MAP_FLEX,
        "pyramid_flex":    PYRAMID_FLEX,
    },
    "map": {
        "colorscale":           MAP_COLORSCALE,
        "tile_style":           MAP_TILE_STYLE,
        "center_lat":           MAP_CENTER_LAT,
        "center_lon":           MAP_CENTER_LON,
        "default_zoom":         MAP_DEFAULT_ZOOM,
        "border_width":         MAP_BORDER_WIDTH,
        "highlight_line_color": MAP_HIGHLIGHT_LINE_COLOR,
        "highlight_line_width": MAP_HIGHLIGHT_LINE_WIDTH,
        "highlight_fill":       MAP_HIGHLIGHT_FILL,
        "geo":                  MAP_GEO,
    },
    "pyramid": {
        "bargap":               PYRAMID_BARGAP,
        "cohort_outline_width": COHORT_OUTLINE_WIDTH,
        "male_color":           PYRAMID_MALE_COLOR,
        "female_color":         PYRAMID_FEMALE_COLOR,
    },
    "playback": {
        "interval_ms": PLAY_INTERVAL_MS,
        "btn_size":    PLAY_BTN_SIZE,
        "btn_font":    PLAY_BTN_FONT_SIZE,
    },
    "markers": {
        "dot":         MARKER_SIZE_DOT,
        "marker_1945": MARKER_SIZE_1945,
        "diamond":     MARKER_SIZE_DIAMOND,
        "legend_sq":   MARKER_SIZE_LEGEND_SQ,
    },
    "lines": {
        "main":               LINE_WIDTH_MAIN,
        "pref":               LINE_WIDTH_PREF,
        "marker_1945":        LINE_WIDTH_1945,
        "threshold":          LINE_WIDTH_THRESHOLD,
        "year_marker":        LINE_WIDTH_YEAR_MARKER,
        "opacity_threshold":  OPACITY_THRESHOLD_LINE,
        "opacity_year_vline": OPACITY_YEAR_VLINE,
    },
}


# ── 14. Legacy constants ──────────────────────────────────────────────────────
# Aliases for renamed constants — kept for backward compat with older imports.
# Remove once all consumers have been updated.

FONT_COLOR_JPRED   = COLOR_PRIMARY
FONT_COLOR_JPWHT   = COLOR_SECONDARY
FONT_MAIN_COLOR    = COLOR_TEXT_MID
FONT_MAIN          = FONT_STACK_SANS
FONT_HEADER        = FONT_STACK_SERIF

PANEL_H            = 720
LEGEND_H           = int(PANEL_H * 1.03)
TIME_H             = 180