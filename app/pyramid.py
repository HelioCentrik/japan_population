# app/pyramid.py
import math
from functools import lru_cache

import plotly.graph_objects as go

from app.config import (
    PANEL_BORDER,
    COLOR_TEXT_MID,
    ACCENT_DANKAI, ACCENT_DANKAI_JR, ACCENT_SHOUSHIKA, ACCENT_WARTIME_GEN,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
    PYRAMID_BARGAP, PYRAMID_MAX_BANDS, COHORT_OUTLINE_WIDTH,
    PYRAMID_MARGIN_T, PYRAMID_MARGIN_B, PYRAMID_MARGIN_L, PYRAMID_MARGIN_R,
    FONT_SIZE_AXIS_TITLE, FONT_SIZE_CHART_TITLE,
    MARKER_SIZE_DIAMOND, MARKER_SIZE_LEGEND_SQ,
)
from app.db import get_con



@lru_cache(maxsize=8)
def get_pyramid_axis_max(area_estat: str | None) -> int:
    """
    Pre-query the maximum single-sex band population across ALL years for this
    selection. Cached per area_estat so the axis stays stable while scrubbing years.
    """
    con = get_con()
    if area_estat is not None:
        result = con.execute("""
            SELECT MAX(population) AS max_pop
            FROM v_census
            WHERE age_scheme  = 'scheme_a'
              AND age_group   != 'Total'
              AND sex         != 'total'
              AND area_estat   = ?
        """, [area_estat]).fetchone()
    else:
        result = con.execute("""
            SELECT MAX(band_pop) AS max_pop
            FROM (
                SELECT year, age_start, sex, SUM(population) AS band_pop
                FROM v_census
                WHERE age_scheme  = 'scheme_a'
                  AND age_group   != 'Total'
                  AND sex         != 'total'
                  AND area_level   = 2
                GROUP BY year, age_start, sex
            )
        """).fetchone()
    return int(result[0]) if result and result[0] else 5_000_000


def _nice_axis(max_val: int) -> tuple[float, float]:
    """
    Returns (dtick, half_range). half_range is always a clean dtick multiple
    with one full tick of headroom above max_val — prevents Plotly from snapping
    the range down and clipping bars.
    """
    if max_val <= 0:
        return 1_000_000, 4_000_000

    raw_step   = max_val / 3
    magnitude  = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude

    if normalized < 1.5:
        snapped = 1
    elif normalized < 3.5:
        snapped = 2
    else:
        snapped = 5

    dtick      = snapped * magnitude
    n_ticks    = math.ceil(max_val / dtick)
    half_range = dtick * (n_ticks + 0.25)
    return dtick, half_range


# ── Cohort birth year ranges ──────────────────────────────────────────────────
_COHORTS = {
    "dankai":    (1947, 1949, ACCENT_DANKAI),
    "dankai_jr": (1971, 1974, ACCENT_DANKAI_JR),
}
# Canonical scheme_a labels in display order — y-axis pinned to this so
# early years with fewer bands (80+ terminal instead of 85+) don't collapse the axis
# _SCHEME_A_LABELS = [
#     "0–4", "5–9", "10–14", "15–19", "20–24", "25–29",
#     "30–34", "35–39", "40–44", "45–49", "50–54", "55–59",
#     "60–64", "65–69", "70–74", "75–79", "80+"
# ]


def _shorten_label(label: str) -> str:
    """'0–4 years old' → '0–4',  '85 years and older' → '85+' """
    return (label
            .replace(" years and older", "+")
            .replace(" years old", ""))


def _cohort_band(year: int, birth_start: int, birth_end: int) -> int | None:
    """
    Return the age_start of the scheme_a band containing the cohort in `year`.
    The cohort is at ages (year - birth_end) to (year - birth_start).
    We snap to the 5-year band floor of the older end (year - birth_end).
    Returns None if the cohort would be outside the 0–85 range.
    """
    age_low  = year - birth_end
    age_high = year - birth_start
    if age_high < 0 or age_low > 85:
        return None
    band_start = (max(age_low, 0) // 5) * 5
    return band_start

def _cohort_band_range(year: int, birth_start: int, birth_end: int) -> list[int]:
    """Return all scheme_a band starts containing any birth year in [birth_start, birth_end]."""
    age_low  = max(year - birth_end, 0)
    age_high = min(year - birth_start, 85)
    if age_high < 0 or age_low > 85:
        return []
    return [b for b in range(0, 86, 5) if b <= age_high and b + 4 >= age_low]


@lru_cache(maxsize=64)
def build_pyramid_fig(year: int, area_estat: str | None = None, axis_max: int = 5_000_000) -> go.Figure:
    con = get_con()

    if area_estat is not None:
        df = con.execute("""
            SELECT age_group, age_start, sex, SUM(population) AS population
            FROM v_census
            WHERE year       = ?
              AND age_scheme  = 'scheme_a'
              AND age_group  != 'Total'
              AND sex        != 'total'
              AND area_estat  = ?
            GROUP BY age_group, age_start, sex
            ORDER BY age_start
        """, [year, area_estat]).df()
    else:
        df = con.execute("""
            SELECT age_group, age_start, sex, SUM(population) AS population
            FROM v_census
            WHERE year      = ?
              AND age_scheme = 'scheme_a'
              AND age_group != 'Total'
              AND sex       != 'total'
              AND area_level = 2
            GROUP BY age_group, age_start, sex
            ORDER BY age_start
        """, [year]).df()

    if area_estat is not None:
        name_row = con.execute(
            "SELECT prefecture_name_ja, prefecture_name FROM d_prefectures WHERE area_estat = ?",
            [area_estat]
        ).fetchone()
        pref_label = f"<b>{name_row[0]}<br>{name_row[1]}</b>" if name_row else area_estat
    else:
        pref_label = "<b>全国<br>National</b>"

    male_df   = df[df["sex"] == "male"  ].sort_values("age_start")
    female_df = df[df["sex"] == "female"].sort_values("age_start")

    age_labels = [_shorten_label(l) for l in male_df["age_group"].tolist()]
    age_starts = male_df["age_start"].tolist()

    # fig_height = len(age_labels) * PYRAMID_BAND_HEIGHT + PYRAMID_MARGIN_T + PYRAMID_MARGIN_B

    # ── Cohort colour mapping ─────────────────────────────────────────────────
    cohort_bands = {}
    if area_estat is None:
        for name, (b_start, b_end, color) in _COHORTS.items():
            band = _cohort_band(year, b_start, b_end)
            if band is not None:
                cohort_bands[band] = color

    male_colors   = [cohort_bands.get(a, PYRAMID_MALE_COLOR)   for a in age_starts]
    female_colors = [cohort_bands.get(a, PYRAMID_FEMALE_COLOR) for a in age_starts]

    # ── Traces ────────────────────────────────────────────────────────────────
    male_trace = go.Bar(
        name="男 Male",
        y=age_labels,
        x=[-v for v in male_df["population"]],
        orientation="h",
        showlegend=False,
        marker=dict(color=PYRAMID_MALE_COLOR, line=dict(width=0)),
        hovertemplate="<b>Age (Years): %{y}</b><br>Male: %{customdata:,.0f}<extra></extra>",
        customdata=male_df["population"],
    )

    female_trace = go.Bar(
        name="女 Female",
        y=age_labels,
        x=female_df["population"],
        orientation="h",
        showlegend=False,
        marker=dict(color=PYRAMID_FEMALE_COLOR, line=dict(width=0)),
        hovertemplate="<b>Age (Years): %{y}</b><br>Female: %{customdata:,.0f}<extra></extra>",
        customdata=female_df["population"],
    )

    # Invisible traces purely for legend — fixes color mirroring the first bar's cohort color
    legend_male = go.Scatter(
        x=[None], y=[None],
        mode="markers",
        name="男 Male",
        marker=dict(symbol="square", size=MARKER_SIZE_LEGEND_SQ, color=PYRAMID_MALE_COLOR),
        showlegend=True,
    )
    legend_female = go.Scatter(
        x=[None], y=[None],
        mode="markers",
        name="女 Female",
        marker=dict(symbol="square", size=MARKER_SIZE_LEGEND_SQ, color=PYRAMID_FEMALE_COLOR),
        showlegend=True,
    )

    # ── 戦中世代 — Wartime cohort marker ──────────────────────────────────────
    # Men born 1910–1925 were prime conscription age during the war.
    valid_bands  = set(male_df["age_start"].tolist())
    wartime_bands = [b for b in _cohort_band_range(year, 1910, 1925) if b in valid_bands] if (
                area_estat is None and 1950 <= year <= 2015) else []
    war_gen_rows = male_df[male_df["age_start"].isin(wartime_bands)]

    war_gen_trace = go.Scatter(
        x=[-v for v in war_gen_rows["population"]] if not war_gen_rows.empty else [None],
        y=[_shorten_label(l) for l in war_gen_rows["age_group"]] if not war_gen_rows.empty else [None],
        mode="markers",
        name="戦中世代",
        showlegend=False,
        marker=dict(
            symbol="diamond",
            size=MARKER_SIZE_DIAMOND,
            color=ACCENT_WARTIME_GEN,
            line=dict(width=1, color=ACCENT_WARTIME_GEN),
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "戦中世代 (1910–1925年生まれ)<br>"
            "<extra></extra>"
        ),
    )

    # ── 少子化 — Shoushika cohort marker ─────────────────────────────────────
    shoushika_bands = [b for b in _cohort_band_range(year, 1986, 1990) if b in valid_bands] if (
                area_estat is None and year >= 1990) else []
    shoushika_rows = male_df[male_df["age_start"].isin(shoushika_bands)]

    shoushika_trace = go.Scatter(
        x=[0] * len(shoushika_rows) if not shoushika_rows.empty else [None],
        y=[_shorten_label(l) for l in shoushika_rows["age_group"]] if not shoushika_rows.empty else [None],
        mode="markers",
        name="少子化世代",
        showlegend=False,
        marker=dict(
            symbol="diamond",
            size=MARKER_SIZE_DIAMOND,
            color=ACCENT_SHOUSHIKA,
            line=dict(width=1, color=ACCENT_SHOUSHIKA),
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "少子化世代 (1986–1990年生まれ)<br>"
            "<extra></extra>"
        ),
    )

    # ── Layout ────────────────────────────────────────────────────────────────
    fig = go.Figure(data=[
        male_trace,
        female_trace,
        war_gen_trace,
        shoushika_trace,
    ])

    # ── Cohort outline shapes ──────────────────────────────────────────────────
    # 4 lines per band: top, bottom, outer left (male), outer right (female).
    # No center line — deliberately omitted to avoid the bisect artifact.
    bar_half = (1 - PYRAMID_BARGAP) / 2
    for band_start, color in cohort_bands.items():
        if band_start not in age_starts:
            continue
        idx   = age_starts.index(band_start)
        m_pop = male_df[male_df["age_start"] == band_start]["population"].values[0]
        f_pop = female_df[female_df["age_start"] == band_start]["population"].values[0]
        y0, y1 = idx - bar_half, idx + bar_half
        for shape in [
            dict(x0=-m_pop, x1=f_pop,  y0=y1,  y1=y1),   # top
            dict(x0=-m_pop, x1=f_pop,  y0=y0,  y1=y0),   # bottom
            dict(x0=-m_pop, x1=-m_pop, y0=y0,  y1=y1),   # left (male outer)
            dict(x0=f_pop,  x1=f_pop,  y0=y0,  y1=y1),   # right (female outer)
        ]:
            fig.add_shape(type="line", xref="x", yref="y",
                          line=dict(color=color, width=COHORT_OUTLINE_WIDTH), **shape)

    dtick, half_range = _nice_axis(axis_max)

    fig.update_layout(
        barmode="overlay",
        bargap=PYRAMID_BARGAP,
        autosize=True,
        # height=fig_height,
        margin=dict(l=PYRAMID_MARGIN_L, r=PYRAMID_MARGIN_R, t=PYRAMID_MARGIN_T, b=PYRAMID_MARGIN_B),
        legend=dict(
            orientation="h",
            x=0.5, xanchor="center",
            y=1.02, yanchor="bottom",
        ),
        xaxis=dict(
            tickformat="~s",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor=PANEL_BORDER,
            range=[-half_range, half_range],
            dtick=dtick,
        ),
        yaxis=dict(
            title=dict(
                text="Age (Years)",
                font=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_AXIS_TITLE),
            ),
            showgrid=False,
            categoryorder="array",
            categoryarray=age_labels,
            range=[-0.5, PYRAMID_MAX_BANDS - 0.5],  # always 18 slots — 1920's 80+ terminal leaves top empty
        ),
    )

    # fig.update_layout(
    #     title=dict(
    #         text=pref_label,
    #         x=0.12,
    #         y=0.95,
    #         xanchor="center",
    #         font=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_CHART_TITLE),
    #     )
    # )

    return fig