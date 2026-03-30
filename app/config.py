# app/config.py ────────────────────────────────────────────────────────────────────

# ── Layout ────────────────────────────────────────────────────────────────────
LAYOUT_GAP          = "0.5rem"   # uniform gap between all dashboard rows/panels
LAYOUT_OUTER_PAD    = "1rem"     # left/right padding on dashboard-outer
LAYOUT_MIN_HEIGHT   = "700px"    # below this viewport height, page scrolls

# Flex ratios — charts-area children (map+pyramid row vs timeseries)
CHARTS_ANCHOR       = 10
CHARTS_ROW_FLEX     = 7
CHARTS_TS_FLEX      = CHARTS_ANCHOR - CHARTS_ROW_FLEX

# Flex ratios — map+pyramid row children
MAP_MIN_HEIGHT      = "320px"
MAP_FLEX            = 7
PYRAMID_FLEX        = 3


# ── Colors ─────────────────────────────────────────────────────────────────────
PAGE_BG             = "#091023"
PANEL_BG            = "#06091a"
PANEL_BORDER        = "#334477"
FONT_HEADER         = "serif"
FONT_COLOR_JPRED    = "#bc002d"
FONT_COLOR_JPWHT    = "#ffffff"
FONT_MAIN           = "sans-serif"
FONT_MAIN_COLOR     = "#aad"

CHART_GRID_COLOR    = "#1a2440"   # gridlines in pyramid and timeseries


# ── Panel chrome ───────────────────────────────────────────────────────────────
PANEL_BORDER_RADIUS = "6px"       # injected as --border-radius CSS variable


# ── Playback ──────────────────────────────────────────────────────────────────
PLAY_INTERVAL_MS    = 800


# ── Map ───────────────────────────────────────────────────────────────────────
MAP_COLORSCALE      = "plasma_r"
MAP_TILE_STYLE      = "carto-darkmatter"
MAP_CENTER_LAT      = 35.5
MAP_CENTER_LON      = 135.5
MAP_DEFAULT_ZOOM    = 3.75
MAP_BORDER_WIDTH    = 0.8        # choropleth prefecture border line width

MAP_GEO = {
    "bg_color":   "#06091a",
    "land_color": "#1c1f30",
    "line_color": "#6089A0",
}

MAP_HIGHLIGHT_LINE_COLOR = "#ffffff"
MAP_HIGHLIGHT_LINE_WIDTH = 2.5
MAP_HIGHLIGHT_FILL       = "rgba(255,255,255,0.08)"


# ── Cohort & annotation accents ───────────────────────────────────────────────
ACCENT_DANKAI       = "#f5a623"
ACCENT_DANKAI_JR    = "#7ed321"
ACCENT_WARTIME_GEN  = FONT_COLOR_JPRED
ACCENT_SHOUSHIKA    = "#9ee0ff"
ACCENT_THRESHOLD    = "#50e3c2"

WWII_SEX_RATIO_THRESHOLD = 90

COHORT_COLORS = {
    "dankai":    ACCENT_DANKAI,
    "dankai_jr": ACCENT_DANKAI_JR,
    "wwii_scar": ACCENT_WARTIME_GEN,
    "shoushika": ACCENT_SHOUSHIKA,
    "threshold": ACCENT_THRESHOLD,
}


# ── Pyramid ───────────────────────────────────────────────────────────────────
PYRAMID_MALE_COLOR    = "#4a90d9"
PYRAMID_FEMALE_COLOR  = "#e07b8a"
PYRAMID_BARGAP        = 0.15
COHORT_OUTLINE_WIDTH  = 3.5


# ── Time series ───────────────────────────────────────────────────────────────
TIMESERIES_PREF_COLOR = FONT_COLOR_JPWHT


# ── Legacy (Streamlit ui_styles.py — not used by Dash app) ───────────────────
PANEL_H  = 720
LEGEND_H = int(PANEL_H * 1.03)
TIME_H   = 180


# ── Theme bundle ──────────────────────────────────────────────────────────────
# All visual properties in one exportable dict.
# Other projects: `from app.config import THEME`
# Future theme swap: replace this dict with an import from a theme module.
THEME = {
    # Backgrounds
    "page_bg":               PAGE_BG,
    "panel_bg":              PANEL_BG,
    "panel_border":          PANEL_BORDER,
    "border_radius":         PANEL_BORDER_RADIUS,
    "grid_color":            CHART_GRID_COLOR,
    # Typography
    "font_main":             FONT_MAIN,
    "font_header":           FONT_HEADER,
    "font_color":            FONT_MAIN_COLOR,
    "font_color_red":        FONT_COLOR_JPRED,
    "font_color_wht":        FONT_COLOR_JPWHT,
    # Map
    "map_colorscale":        MAP_COLORSCALE,
    "map_tile_style":        MAP_TILE_STYLE,
    "map_center_lat":        MAP_CENTER_LAT,
    "map_center_lon":        MAP_CENTER_LON,
    "map_default_zoom":      MAP_DEFAULT_ZOOM,
    "map_border_width":      MAP_BORDER_WIDTH,
    "map_geo":               MAP_GEO,
    "map_highlight_line_color": MAP_HIGHLIGHT_LINE_COLOR,
    "map_highlight_line_width": MAP_HIGHLIGHT_LINE_WIDTH,
    "map_highlight_fill":    MAP_HIGHLIGHT_FILL,
    # Pyramid
    "pyramid_male":          PYRAMID_MALE_COLOR,
    "pyramid_female":        PYRAMID_FEMALE_COLOR,
    "pyramid_bargap":        PYRAMID_BARGAP,
    "cohort_outline_width":  COHORT_OUTLINE_WIDTH,
    # Cohort accents
    "accent_dankai":         ACCENT_DANKAI,
    "accent_dankai_jr":      ACCENT_DANKAI_JR,
    "accent_wartime":        ACCENT_WARTIME_GEN,
    "accent_shoushika":      ACCENT_SHOUSHIKA,
    "accent_threshold":      ACCENT_THRESHOLD,
    # Time series
    "timeseries_pref_color": TIMESERIES_PREF_COLOR,
}