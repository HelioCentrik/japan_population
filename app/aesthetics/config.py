# app/aesthetics/config.py
"""
Single source of truth for all dashboard constants.

Colors and shadows come from the active theme in app/aesthetics/themes.py.
Everything else (layout, fonts, sizes, structural map config, etc.) is defined here.

To swap themes: change ACTIVE_THEME_NAME in app/aesthetics/themes.py and restart the app.

Sections:
  Layout
  Colors              (unpacked from active theme — do not hardcode here)
  Shadows             (derived from theme's shadow_color × shadow_darkness)
  Fonts
  Font sizes
  Spacing & borders
  Headers
  Map configuration   (structural — center, zoom, widths are theme-independent)
  Pyramid configuration
  Play button
  Playback
  Markers & lines
  THEME dict
  Legacy constants
  AI / Gemini
"""

from app.utils import hex_to_rgb as _hex_to_rgb, rgba as _rgba, hsl_adjust as _hsl_adjust, _get_max_year
from app.aesthetics.fonts import _stack
from app.aesthetics.themes import ACTIVE_THEME as _t, ACTIVE_THEME_NAME




# ── Layout ─────────────────────────────────────────────────────────────────

SIDE_PANEL_WIDTH      = "400px"
SIDE_PANEL_TRANSITION = "0.3s ease"

LAYOUT_GAP        = "clamp(0.3rem, 0.35vw, 0.5rem)"
LAYOUT_OUTER_PAD  = "clamp(0.35rem, 0.6vw, 0.75rem)"
LAYOUT_MIN_HEIGHT = "700px"

CHARTS_ANCHOR     = 10
CHARTS_ROW_FLEX   = 7
CHARTS_TS_FLEX    = CHARTS_ANCHOR - CHARTS_ROW_FLEX  # = 3

MAP_MIN_HEIGHT    = "48px"
MAP_FLEX          = 7
PYRAMID_FLEX      = 3


# ── Colors ─────────────────────────────────────────────────────────────────
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
COLOR_SLIDER_TRACK = _t["slider_track"]
COLOR_WARNING      = _t["warning"]

# Chart
CHART_GRID_COLOR      = _t["chart_grid"]
CHART_PLOT_COLOR      = _t["chart_plot_color"]
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

# Tooltip
TOOLTIP_BG          = _t["tooltip_bg"]
TOOLTIP_BORDER      = _t["tooltip_border"]
TOOLTIP_BORDER_SIZE = _t["tooltip_border_size"]
TOOLTIP_TEXT_HI     = _t["tooltip_text_hi"]
TOOLTIP_TEXT_MID    = _t["tooltip_text_mid"]
TOOLTIP_HINT        = _t["tooltip_hint"]
TOOLTIP_DIVIDER     = _t["tooltip_divider"]


# ── Shadows ────────────────────────────────────────────────────────────────
# Derived from the theme's shadow_color and shadow_darkness knob.
# Using an explicit shadow_color (rather than PAGE_BG) lets light themes
# use dark shadows without coupling shadow depth to background hue.

SHADOW_DARKNESS  = _t["shadow_darkness"]
_SHADOW_COLOR    = _t["shadow_color"]
SHADOW_PANEL     = _rgba(_SHADOW_COLOR, SHADOW_DARKNESS)
SHADOW_MAP_INSET = _rgba(_SHADOW_COLOR, min(1.0, SHADOW_DARKNESS * 1.6))

# Panel drop shadow & bezel knobs — tweak these to adjust the 3-D feel.
PANEL_SHADOW_Y    = 3     # px — drop shadow Y offset (bottom)
PANEL_SHADOW_X    = 2     # px — drop shadow X offset (right)
PANEL_SHADOW_BLUR = 8     # px — drop shadow blur radius
PANEL_BEZEL_SIZE  = 1.5   # px — inset highlight/shadow thickness
BEZEL_BLUR        = 3     # px — bezel edge softness (0 = hard, keep low)
BEZEL_HI_ALPHA    = _t["bezel_hi_alpha"]
BEZEL_LO_ALPHA    = _t["bezel_lo_alpha"]
BEZEL_HI_COLOR    = _t.get("bezel_hi_color", "#ffffff")
BEZEL_LO_COLOR    = _t.get("bezel_lo_color", "#000000")

# Derived — do not edit these; change the knobs above.
_BEZEL_HI = _rgba(BEZEL_HI_COLOR, BEZEL_HI_ALPHA)
_BEZEL_LO = _rgba(BEZEL_LO_COLOR, BEZEL_LO_ALPHA)

SHADOW_DROP = (
    f"{PANEL_SHADOW_X}px {PANEL_SHADOW_Y}px "
    f"{PANEL_SHADOW_BLUR}px {_rgba(_SHADOW_COLOR, SHADOW_DARKNESS)}"
)
SHADOW_BEZEL = (
    f"inset 0 {PANEL_BEZEL_SIZE}px {BEZEL_BLUR}px {_BEZEL_HI}, "
    f"inset {PANEL_BEZEL_SIZE}px 0 {BEZEL_BLUR}px {_BEZEL_HI}, "
    f"inset 0 -{PANEL_BEZEL_SIZE}px {BEZEL_BLUR}px {_BEZEL_LO}, "
    f"inset -{PANEL_BEZEL_SIZE}px 0 {BEZEL_BLUR}px {_BEZEL_LO}"
)
SHADOW_FULL = f"{SHADOW_DROP}, {SHADOW_BEZEL}"


# ── Fonts ──────────────────────────────────────────────────────────────────
# Font names match the catalogue in app/aesthetics/fonts.py.
# [GF] families must be linked in app/aesthetics/index_string.py to load on client.

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


# ── Font sizes ─────────────────────────────────────────────────────────────

FONT_SIZE_AXIS_TICK     = 12.5
FONT_SIZE_AXIS_TITLE    = 12.5
FONT_SIZE_LEGEND        = 13
FONT_SIZE_CHART_TITLE   = 13
FONT_SIZE_COLORBAR      = 12
FONT_SIZE_COLORBAR_TICK = 14
FONT_SIZE_KPI_LABEL     = 12
FONT_SIZE_KPI_VALUE     = 22
FONT_SIZE_KPI_SUB       = 12
FONT_SIZE_TITLE         = 32
FONT_SIZE_AI_PANEL      = 15

# ── Font tier scaling ─────────────────────────────────────────────────────
# Breakpoints mirror the @media thresholds in style.css exactly.
# Scale is a plain multiplier applied to base font sizes above.
# Floors prevent any value from dropping below 8px.

FONT_TIER_BREAKPOINTS = {"lg": 1100, "sm": 768}  # px — upper edge of each tier
FONT_SCALE            = {"lg": 1.0, "md": 0.9, "sm": 0.8}


def get_scaled_fonts(tier: str) -> dict:
    s = FONT_SCALE[tier]
    return {
        "axis_tick":     max(8, round(FONT_SIZE_AXIS_TICK     * s)),
        "axis_title":    max(8, round(FONT_SIZE_AXIS_TITLE    * s)),
        "legend":        max(8, round(FONT_SIZE_LEGEND        * s)),
        "chart_title":   max(8, round(FONT_SIZE_CHART_TITLE   * s)),
        "colorbar":      max(8, round(FONT_SIZE_COLORBAR      * s)),
        "colorbar_tick": max(8, round(FONT_SIZE_COLORBAR_TICK * s)),
    }


# ── Spacing & borders ──────────────────────────────────────────────────────

PANEL_BORDER_RADIUS    = "3px"
PANEL_BORDER_THICKNESS = "0px"
YAXIS_TICK_STANDOFF    = 0


# ── Header ────────────────────────────────────────────────────────────────
# Photo strip header — all creator-controlled knobs in one place.
# HEADER_IMAGE: filename only; file must live in assets/.
# HEADER_BG_POS: CSS background-position — adjust to reframe the photo crop.
# HEADER_TEXT_SHADOW: hard drop + soft glow for legibility over the photo.

MAX_YEAR: int = _get_max_year()

HEADER_IMAGE       = "OkinawaWomanBaby_hdr_dk.png"
HEADER_HEIGHT      = "132px"
HEADER_BG_SIZE     = "100% auto"
HEADER_BG_POS      = "center 22.5%"
HEADER_TEXT_SHADOW = "2px 2px 0 rgba(0,0,0,1.0), 0 0 10px rgba(0,0,0,0.85)"
HEADER_FONT_JA     = 52    # px — 少子高齢化 title
HEADER_FONT_EN     = 14    # px — English subtitle
HEADER_TITLE_JA    = "少子高齢化"
HEADER_TITLE_EN    = f"A Century of Japan's Population · 1920-{MAX_YEAR}"


# ── KPI card grid row heights ─────────────────────────────────────────────────

KPI_MARGIN  = 8
KPI_LABEL_H = 30   # px — label row (accommodates 2-line wrap)
KPI_VALUE_H = 30   # px — value row (anchor)
KPI_SUB_H   = 14   # px — sub row


# ── Map configuration ──────────────────────────────────────────────────────
# Structural values — these don't vary by theme.

POP_DELTA_SIGMA     = 2.0
NET_MIGRATION_SIGMA = 2.0   # sigma multiplier for net_migration diverging bounds

MAP_MARGINS              = 4
MAP_BORDER_WIDTH         = 0.8

MAP_CENTER_LAT           = 35.5
MAP_CENTER_LON           = 135.5

MAP_DEFAULT_ZOOM         = 2.5
MAP_ZOOM_MIN             = 1.0    # minimum zoom clamp (matches default baked into figures)
MAP_ZOOM_MAX             = 5.5    # maximum zoom clamp
MAP_REF_HEIGHT           = 582    # panel height (px) at which MAP_REF_ZOOM was calibrated
MAP_REF_ZOOM             = 3.75   # zoom that fits Japan at MAP_REF_HEIGHT

MAP_HIGHLIGHT_LINE_WIDTH = 2.5
MAP_TOOLTIP_OFFSET_X     = 28   # px rightward from hovered point
MAP_TOOLTIP_OFFSET_Y     = 40   # px upward from hovered point

MAP_NO_DATA_COLOR   = "rgba(100, 100, 100, 0.45)"   # grey fill when metric has no data for year

MAP_TFR_COLORSCALE = [
    [0.00, "#d73027"],   # red   — very low fertility
    [0.50, "#fee08b"],   # amber — replacement-level zone
    [1.00, "#1a9641"],   # green — high fertility
]

MAP_NET_MIGRATION_COLORSCALE = [
    [0.00, "#c0392b"],   # red        — heavy outflow
    [0.50, "#f5f5f5"],   # near-white — net zero
    [1.00, "#2166ac"],   # blue       — heavy inflow
]

# ── Metric selector ───────────────────────────────────────────────────────

OKINAWA_AREA_ESTAT = "47000"

MAP_METRICS = {
    "population": {
        "label":      "人口  Population",
        "colorscale": MAP_COLORSCALE,
        "diverging":  False,
        "midpoint":   None,
        "fmt":        lambda v: f"{int(v):,}"  if v == v else "—",
        "delta_fmt":  lambda v: f"{int(v):+,}" if v == v else "—",
        "min_year":   1920,
        "max_year":   None,
    },
    "pop_delta": {
        "label":      "人口増減  Population Change",
        "colorscale": [
            [0.00, "#c0392b"],
            [0.25, "#f5c518"],
            [0.50, "#f7f7f7"],
            [0.75, "#4575b4"],
            [1.00, "#5b2c8a"],
        ],
        "diverging":  True,
        "midpoint":   0.0,
        "fmt":        lambda v: f"{int(v):+,}" if v == v else "—",
        "delta_fmt":  lambda v: f"{int(v):+,}" if v == v else "—",
        "min_year":   1925,   # 1920 has no prev year → no delta
        "max_year":   None,
    },
    "tfr": {
        "label":      "合計特殊出生率  TFR",
        "colorscale": MAP_TFR_COLORSCALE,
        "diverging":  False,
        "midpoint":   None,
        "fmt":        lambda v: f"{v:.2f}" if v == v else "—",
        "delta_fmt":  lambda v: "",   # no delta column — suppressed in tooltip
        "min_year":   1960,
        "max_year":   None,
    },
    "net_migration": {
        "label":      "純移動数  Net Migration",
        "colorscale": MAP_NET_MIGRATION_COLORSCALE,
        "diverging":  True,
        "midpoint":   0.0,
        "fmt":        lambda v: f"{int(v):+,}" if v == v else "—",
        "delta_fmt":  lambda v: "",   # no delta column — suppressed in tooltip
        "min_year":   1985,
        "max_year":   2020,
    },
}

MAP_METRIC_DEFAULT = "population"


# ── Pyramid configuration ─────────────────────────────────────────────────

PYRAMID_BARGAP       = 0.15
COHORT_OUTLINE_WIDTH = 3
PYRAMID_MAX_BANDS    = 18
PYRAMID_MARGIN_L     = 72
PYRAMID_MARGIN_R     = 12
PYRAMID_MARGIN_T     = 6
PYRAMID_MARGIN_B     = 28
PYRAMID_GRAPH_TOP_OFFSET    = 28
PYRAMID_TOOLTIP_OFFSET_X    = 12
PYRAMID_TOOLTIP_OFFSET_Y    = 20


# ── Timeseries configuration ──────────────────────────────────────────────
TIMESERIES_MARGIN_L  = 52
TIMESERIES_MARGIN_R  = 12
TIMESERIES_MARGIN_T  = 12
TIMESERIES_MARGIN_B  = 28

TS_SELECTOR_OFFSET_L = TIMESERIES_MARGIN_L + 8
TS_TOOLTIP_OFFSET_X  = 32
TS_TOOLTIP_OFFSET_Y  = 20

TS_VIEWS = {
    "pop_share":  "人口割合 Population Share",
    "population": "人口 Population",
    "tfr":        "合計特殊出生率 TFR",
}
TS_VIEW_DEFAULT = "pop_share"
TS_VIEW_TFR = "tfr"

TFR_REPLACEMENT_RATE  = 2.1
TFR_CUTOFF_YEAR       = 1960   # f_tfr coverage begins
MIGRATION_CUTOFF_YEAR = 1985   # f_migration coverage begins
IPSS_HANDOFF_YEAR     = 2020   # projection bolt-on starts here


# ── Play button ──────────────────────────────────────────────────────────

PLAY_BTN_SIZE_PX   = 52
PLAY_BTN_SIZE      = f"{PLAY_BTN_SIZE_PX}px"
PLAY_BTN_FONT_SIZE = f"{round(PLAY_BTN_SIZE_PX * 0.538)}px"


# ── Playback ─────────────────────────────────────────────────────────────

PLAY_INTERVAL_MS = 800


# ── Markers & lines ───────────────────────────────────────────────────────

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


# ── THEME dict ────────────────────────────────────────────────────────────

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
        "slider_track":         COLOR_SLIDER_TRACK,
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
        "tooltip_bg":           TOOLTIP_BG,
        "tooltip_border":       TOOLTIP_BORDER,
        "tooltip_text_hi":      TOOLTIP_TEXT_HI,
        "tooltip_text_mid":     TOOLTIP_TEXT_MID,
        "tooltip_hint":         TOOLTIP_HINT,
        "tooltip_divider":      TOOLTIP_DIVIDER,
    },

    "shadows": {
        "darkness":  SHADOW_DARKNESS,
        "panel":     SHADOW_PANEL,
        "map_inset": SHADOW_MAP_INSET,
        "full":      SHADOW_FULL,
        "bezel":     SHADOW_BEZEL,    # ← add
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


# ── AI / Gemini ─────────────────────────────────────────────────────────────
# API key sourced from environment variable GEMINI_API_KEY — never hardcoded.

AI_MODEL_NAME    = "gemini-3.1-flash-lite"
AI_MAX_TOKENS    = 384
AI_HISTORY_LIMIT = 6
