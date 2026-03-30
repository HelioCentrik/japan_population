# app/config.py
import colorsys

from app.fonts import _stack


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers — run once at import time, not called at runtime
# ─────────────────────────────────────────────────────────────────────────────

def _expand_hex(h: str) -> str:
    """Normalize 3- or 6-digit hex (with or without #) to 6 lowercase digits."""
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return h.lower()


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex color + alpha to a CSS rgba() string."""
    h = _expand_hex(hex_color)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def _derive_tone(hex_mid: str, target_lightness: float) -> str:
    """
    Derive a hex color from hex_mid by pinning its HSL lightness to target_lightness.
    Hue and saturation are preserved — the result is a darker/lighter tint of the
    same hue family, suitable for building a text hierarchy below COLOR_TEXT_MID.

    Note: colorsys.rgb_to_hls returns (H, L, S) order — not (H, S, L).
    """
    h = _expand_hex(hex_mid)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, _, sat = colorsys.rgb_to_hls(r, g, b)
    nr, ng, nb = colorsys.hls_to_rgb(hue, max(0.0, min(1.0, target_lightness)), sat)
    return "#{:02x}{:02x}{:02x}".format(round(nr * 255), round(ng * 255), round(nb * 255))


# ─────────────────────────────────────────────────────────────────────────────
# Layout
# ─────────────────────────────────────────────────────────────────────────────
LAYOUT_GAP        = "0.5rem"   # uniform gap between all dashboard rows / panels
LAYOUT_OUTER_PAD  = "1rem"     # left/right padding on .dashboard-outer
LAYOUT_MIN_HEIGHT = "700px"    # below this viewport height the page scrolls

# Flex ratios — charts-area row vs timeseries
CHARTS_ANCHOR   = 10
CHARTS_ROW_FLEX = 7
CHARTS_TS_FLEX  = CHARTS_ANCHOR - CHARTS_ROW_FLEX   # = 3

# Flex ratios — map vs pyramid within the row
MAP_MIN_HEIGHT = "320px"
MAP_FLEX       = 7
PYRAMID_FLEX   = 3


# ─────────────────────────────────────────────────────────────────────────────
# Color Palette
# ─────────────────────────────────────────────────────────────────────────────

# ── Surface colors ────────────────────────────────────────────────────────────
PAGE_BG      = "#091023"   # outermost background — dark navy
PANEL_BG     = "#06091a"   # chart / card interiors — near-black
PANEL_BORDER = "#334477"   # border stroke + slider track background

# ── Panel geometry ────────────────────────────────────────────────────────────
PANEL_BORDER_RADIUS = "6px"

# ── Brand / primary ───────────────────────────────────────────────────────────
COLOR_PRIMARY   = "#bc002d"   # Japan flag red — title, 1945 marker, wartime accent
COLOR_SECONDARY = "#ffffff"   # pure white — secondary emphasis

# ── Text hierarchy (light-on-dark) ────────────────────────────────────────────
COLOR_TEXT_HI   = "#e0e8ff"   # highest contrast — KPI values, selected labels
COLOR_TEXT_MID  = "#aad"      # mid-tone — axis labels, legends, body  (= #aaaadd)

# LO and HINT are derived from COLOR_TEXT_MID by reducing HSL lightness.
# They preserve the hue/saturation of COLOR_TEXT_MID (#aad, H=240°, S≈43%).
# Computed values: LO ≈ #4646af (L=0.48), HINT ≈ #2c2c6d (L=0.30).
# These will diverge from the current hardcoded #667799 / #445566 in maps.py
# hovertemplate — reconcile during the maps.py update step.
COLOR_TEXT_LO   = _derive_tone(COLOR_TEXT_MID, 0.48)   # dim labels, secondary annotations
COLOR_TEXT_HINT = _derive_tone(COLOR_TEXT_MID, 0.30)   # hairline separators, placeholder text

# ── UI interaction ─────────────────────────────────────────────────────────────
COLOR_UI_HOVER     = "#243558"   # button / element hover fill
SLIDER_TRACK_COLOR = "#1a2a44"   # slider rail
CHART_GRID_COLOR   = "#1a2440"   # chart gridlines (Plotly gridcolor)

# ── Cohort & annotation accents ───────────────────────────────────────────────
ACCENT_DANKAI      = "#f5a623"        # 団塊の世代 — primary baby boom cohort
ACCENT_DANKAI_JR   = "#7ed321"        # 団塊ジュニア — secondary cohort
ACCENT_WARTIME_GEN = COLOR_PRIMARY    # 戦中世代 — matches Japan red
ACCENT_SHOUSHIKA   = "#9ee0ff"        # 少子化世代 — first gen born into sustained decline
ACCENT_THRESHOLD   = "#50e3c2"        # aging index = 100 reference line

WWII_SEX_RATIO_THRESHOLD = 90         # sex ratio below this → flag as WWII scar

COHORT_COLORS = {
    "dankai":     ACCENT_DANKAI,
    "dankai_jr":  ACCENT_DANKAI_JR,
    "wwii_scar":  ACCENT_WARTIME_GEN,
    "shoushika":  ACCENT_SHOUSHIKA,
    "threshold":  ACCENT_THRESHOLD,
}

# ── Map colors ────────────────────────────────────────────────────────────────
MAP_GEO = {
    "bg_color":   PANEL_BG,      # ocean / base layer — matches panel background
    "land_color": "#1c1f30",     # surrounding land (Korea, Russia) — mid-tier
    "line_color": "#6089A0",     # prefecture border stroke — creates lift
}

MAP_COLORSCALE           = "plasma_r"
MAP_TILE_STYLE           = "carto-darkmatter"
MAP_CENTER_LAT           = 35.5
MAP_CENTER_LON           = 135.5
MAP_DEFAULT_ZOOM         = 3.75   # reference zoom (see also map_resize.js REF_ZOOM)
MAP_BORDER_WIDTH         = 0.8    # default prefecture marker_line_width
MAP_HIGHLIGHT_LINE_COLOR = "#ffffff"
MAP_HIGHLIGHT_LINE_WIDTH = 2.5
MAP_HIGHLIGHT_FILL       = "rgba(255,255,255,0.08)"   # barely-there selected-prefecture fill

# ── Population pyramid colors ─────────────────────────────────────────────────
PYRAMID_MALE_COLOR   = "#4a90d9"
PYRAMID_FEMALE_COLOR = "#e07b8a"

# ── Time series colors ─────────────────────────────────────────────────────────
TIMESERIES_PREF_COLOR = COLOR_SECONDARY   # prefecture overlay line


# ─────────────────────────────────────────────────────────────────────────────
# Typography
# ─────────────────────────────────────────────────────────────────────────────

# ── Font stacks ───────────────────────────────────────────────────────────────
# [GF] families require a <link> or @import in index_string.py to load.
# System fonts and CSS generics resolve without loading.
FONT_STACK_SANS = _stack(
    "Noto Sans JP",     # [GF] — primary, best JP coverage
    "M PLUS 1p",        # [GF] — fallback sans
    "Hiragino Sans",    # macOS
    "Yu Gothic UI",     # Windows
    "Meiryo",           # Windows legacy
    "system-ui",
    "sans-serif",
)

FONT_STACK_SERIF = _stack(
    "Noto Serif JP",        # [GF] — primary
    "Hiragino Mincho Pro",  # macOS
    "Yu Mincho",            # Windows
    "serif",
)

FONT_STACK_MONO = _stack(
    "JetBrains Mono",   # [GF] — primary
    "Source Code Pro",  # [GF] — fallback
    "Noto Sans Mono",   # [GF] — Noto-consistent
    "monospace",
)

# ── Font sizes ─────────────────────────────────────────────────────────────────
# Integers = pixel values for Plotly font dicts (dict(size=N)).
# CSS injections (index_string.py, style.css) append "px" as needed.
FONT_SIZE_AXIS_TICK    = 11   # axis tick labels on all charts
FONT_SIZE_AXIS_TITLE   = 11   # axis title text
FONT_SIZE_LEGEND       = 14   # chart legend entries (pyramid)
FONT_SIZE_CHART_TITLE  = 13   # per-chart title (e.g., pyramid prefecture label)
FONT_SIZE_COLORBAR     = 12   # colorbar title
FONT_SIZE_COLORBAR_TICK = 14  # colorbar tick labels
FONT_SIZE_KPI_LABEL    = 11   # KPI card label line
FONT_SIZE_KPI_VALUE    = 22   # KPI card primary value
FONT_SIZE_KPI_SUB      = 12   # KPI card sub-label

# Dashboard title uses a CSS clamp — not a single px value.
# Injected as --font-size-title in index_string.py; consumed by .dashboard-title.
FONT_SIZE_TITLE = "clamp(24px, 3vw, 40px)"


# ─────────────────────────────────────────────────────────────────────────────
# Panel & Shadow System
# ─────────────────────────────────────────────────────────────────────────────
# Adjust SHADOW_DARKNESS (0.0–1.0) to globally scale all shadow depth.
# The two rgba strings become CSS variables injected via index_string.py.
#   --shadow-panel-color  →  standard box-shadow color
#   --shadow-map-color    →  deeper inset shadow on the map panel (1.6× darker)

SHADOW_DARKNESS    = 0.4
SHADOW_PANEL = _rgba(PAGE_BG, SHADOW_DARKNESS)                      # rgba(9, 16, 35, 0.40)
SHADOW_MAP_INSET   = _rgba(PAGE_BG, min(1.0, SHADOW_DARKNESS * 1.6))      # rgba(9, 16, 35, 0.64)


# ─────────────────────────────────────────────────────────────────────────────
# Chart Constants
# ─────────────────────────────────────────────────────────────────────────────
CHART_ZEROLINE_COLOR = PANEL_BORDER   # x=0 zeroline on pyramid


# ─────────────────────────────────────────────────────────────────────────────
# Pyramid Constants
# ─────────────────────────────────────────────────────────────────────────────
PYRAMID_BARGAP       = 0.15   # gap between age-band bars (Plotly barmode layout bargap)
COHORT_OUTLINE_WIDTH = 3.5    # line width for dankai / dankai_jr outline shapes


# ─────────────────────────────────────────────────────────────────────────────
# Marker & Line Constants
# ─────────────────────────────────────────────────────────────────────────────

# Marker sizes (Plotly marker.size — diameter in px)
MARKER_SIZE_DOT       = 5    # regular census year dot on time series
MARKER_SIZE_1945      = 11   # open-circle for the 1945 provisional census
MARKER_SIZE_DIAMOND   = 8    # cohort annotation diamonds (戦中世代, 少子化世代)
MARKER_SIZE_LEGEND_SQ = 10   # invisible legend-only square markers on pyramid

# Line widths (Plotly line.width)
LINE_WIDTH_MAIN        = 2    # national aging-index primary line
LINE_WIDTH_PREF        = 1.5  # prefecture overlay on time series
LINE_WIDTH_1945        = 2.5  # open-circle stroke for the 1945 marker
LINE_WIDTH_THRESHOLD   = 1.2  # aging-index = 100 horizontal reference line
LINE_WIDTH_YEAR_MARKER = 1    # vertical selected-year cursor line

# Opacities
OPACITY_THRESHOLD_LINE = 0.55   # aging-index = 100 dashed reference line
OPACITY_YEAR_VLINE     = 0.35   # selected-year cursor vline


# ─────────────────────────────────────────────────────────────────────────────
# Playback
# ─────────────────────────────────────────────────────────────────────────────
PLAY_INTERVAL_MS   = 800                                      # ms per year step
PLAY_BTN_SIZE_PX   = 52                                       # button square size in px
PLAY_BTN_SIZE      = f"{PLAY_BTN_SIZE_PX}px"                  # CSS string → "52px"
PLAY_BTN_FONT_SIZE = f"{round(PLAY_BTN_SIZE_PX * 0.538)}px"  # ≈ 28px — icon scales with button


# ─────────────────────────────────────────────────────────────────────────────
# THEME — consolidated reference dict
# ─────────────────────────────────────────────────────────────────────────────
# For external portability and introspection. Python modules import constants
# directly — this dict is not used at runtime within the app itself.

THEME = {
    "colors": {
        "page_bg":            PAGE_BG,
        "panel_bg":           PANEL_BG,
        "border":             PANEL_BORDER,
        "primary":            COLOR_PRIMARY,
        "secondary":          COLOR_SECONDARY,
        "text_hi":            COLOR_TEXT_HI,
        "text_mid":           COLOR_TEXT_MID,
        "text_lo":            COLOR_TEXT_LO,
        "text_hint":          COLOR_TEXT_HINT,
        "ui_hover":           COLOR_UI_HOVER,
        "grid":               CHART_GRID_COLOR,
        "slider_track":       SLIDER_TRACK_COLOR,
        "shadow_panel":       SHADOW_PANEL,
        "shadow_map":         SHADOW_MAP_INSET,
        "accent_dankai":      ACCENT_DANKAI,
        "accent_dankai_jr":   ACCENT_DANKAI_JR,
        "accent_wartime":     ACCENT_WARTIME_GEN,
        "accent_shoushika":   ACCENT_SHOUSHIKA,
        "accent_threshold":   ACCENT_THRESHOLD,
        "map_highlight_line": MAP_HIGHLIGHT_LINE_COLOR,
        "map_highlight_fill": MAP_HIGHLIGHT_FILL,
        "pyramid_male":       PYRAMID_MALE_COLOR,
        "pyramid_female":     PYRAMID_FEMALE_COLOR,
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
        "gap":           LAYOUT_GAP,
        "outer_pad":     LAYOUT_OUTER_PAD,
        "min_height":    LAYOUT_MIN_HEIGHT,
        "border_radius": PANEL_BORDER_RADIUS,
    },
    "map": {
        "colorscale": MAP_COLORSCALE,
        "tile_style": MAP_TILE_STYLE,
        "center_lat": MAP_CENTER_LAT,
        "center_lon": MAP_CENTER_LON,
        "zoom":       MAP_DEFAULT_ZOOM,
    },
    "playback": {
        "interval_ms": PLAY_INTERVAL_MS,
        "btn_size":    PLAY_BTN_SIZE,
        "btn_font":    PLAY_BTN_FONT_SIZE,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Deprecated aliases — zero-breakage bridge while downstream modules update
# Remove once maps.py, pyramid.py, timeseries.py, kpi.py, index_string.py,
# app.py, and style.css have been updated to use the new names.
# ─────────────────────────────────────────────────────────────────────────────
FONT_MAIN        = FONT_STACK_SANS     # → FONT_STACK_SANS
FONT_HEADER      = FONT_STACK_SERIF    # → FONT_STACK_SERIF
FONT_MAIN_COLOR  = COLOR_TEXT_MID      # → COLOR_TEXT_MID
FONT_COLOR_JPRED = COLOR_PRIMARY       # → COLOR_PRIMARY
FONT_COLOR_JPWHT = COLOR_SECONDARY     # → COLOR_SECONDARY