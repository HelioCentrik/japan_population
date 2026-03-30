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


# ── Display ────────────────────────────────────────────────────────────────────
PAGE_BG = str("#091023")
PANEL_BG = str("#06091a")
PANEL_BORDER = str("#334477")
FONT_HEADER = str("serif")
FONT_COLOR_JPRED = str("#bc002d")
FONT_COLOR_JPWHT = str("#ffffff")
FONT_MAIN = str("sans-serif")
FONT_MAIN_COLOR = str("#aad")

PANEL_H = 720
LEGEND_H = PANEL_H * 1.03
TIME_H = 180

PLAY_INTERVAL_MS = 800

MAP_GEO = {
    "bg_color":   "#06091a",   # near-black ocean — the "floor"
    "land_color": "#1c1f30",   # surrounding land (Korea/Russia) — mid-tier
    "line_color": "#6089A0",   # prefecture borders — edge highlight, creates lift
}

MAP_HIGHLIGHT_LINE_COLOR = str("#ffffff")               # selected prefecture border
MAP_HIGHLIGHT_LINE_WIDTH = 2.5                          # thick enough to read, not cartoonish
MAP_HIGHLIGHT_FILL       = str("rgba(255,255,255,0.08)") # barely-there overlay, keeps metric color visible

# Cohort & annotation accent colors
ACCENT_DANKAI       = str("#f5a623")   # Dankai generation highlight (primary)
ACCENT_DANKAI_JR    = str("#7ed321")   # Dankai Junior highlight (secondary)
ACCENT_WARTIME_GEN  = FONT_COLOR_JPRED   # Sex ratio flag (WWII male deficit)
ACCENT_SHOUSHIKA    = str("#9ee0ff")   # 少子化 cohort — first generation born into sustained decline
ACCENT_THRESHOLD    = str("#50e3c2")   # Aging index = 100 reference line
WWII_SEX_RATIO_THRESHOLD = 90

COHORT_COLORS = {
    "dankai":       ACCENT_DANKAI,
    "dankai_jr":    ACCENT_DANKAI_JR,
    "wwii_scar":    ACCENT_WARTIME_GEN,
    "shoushika":    ACCENT_SHOUSHIKA,
    "threshold":    ACCENT_THRESHOLD,
}
# Population pyramid sex colors
PYRAMID_MALE_COLOR   = str("#4a90d9")
PYRAMID_FEMALE_COLOR = str("#e07b8a")

TIMESERIES_PREF_COLOR = FONT_COLOR_JPWHT   # Prefecture overlay line on time series