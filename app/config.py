# app/config.py ────────────────────────────────────────────────────────────────────

PAGE_BG = str("#091023")
PANEL_BG = str("rgba(0, 0, 0, 0)")
PANEL_BORDER = str("#334466")
FONT_MAIN = str("#aad")

PANEL_H = 720
LEGEND_H = PANEL_H * 1.03
TIME_H = 180

MAP_GEO = {
    "bg_color":   "#06091a",   # near-black ocean — the "floor"
    "land_color": "#1c1f30",   # surrounding land (Korea/Russia) — mid-tier
    "line_color": "#6089A0",   # prefecture borders — edge highlight, creates lift
}

# Cohort & annotation accent colors
ACCENT_DANKAI        = str("#f5a623")   # Dankai generation highlight (primary)
ACCENT_DANKAI_JR     = str("#7ed321")   # Dankai Junior highlight (secondary)
ACCENT_WARTIME_GEN     = str("#d0021b")   # Sex ratio flag (WWII male deficit)
ACCENT_HINOEUMA      = str("#9b9b9b")   # Hinoeuma notch (subtle)
ACCENT_THRESHOLD     = str("#50e3c2")   # Aging index = 100 reference line
WWII_SEX_RATIO_THRESHOLD = 90

COHORT_COLORS = {
    "dankai":       ACCENT_DANKAI,
    "dankai_jr":    ACCENT_DANKAI_JR,
    "wwii_scar":    ACCENT_WARTIME_GEN,
    "hinoeuma":     ACCENT_HINOEUMA,
    "threshold":    ACCENT_THRESHOLD,
}
# Population pyramid sex colors
PYRAMID_MALE_COLOR   = str("#4a90d9")
PYRAMID_FEMALE_COLOR = str("#e07b8a")