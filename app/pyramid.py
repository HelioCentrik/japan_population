# app/pyramid.py
from functools import lru_cache

import duckdb as ddb
import plotly.graph_objects as go

# Replace the existing config import
from app.config import (
    PANEL_BG, PANEL_BORDER,
    FONT_MAIN,
    ACCENT_DANKAI, ACCENT_DANKAI_JR, ACCENT_SHOUSHIKA, ACCENT_WARTIME_GEN,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
)



# ── Cohort birth year ranges ──────────────────────────────────────────────────
_COHORTS = {
    "dankai":    (1947, 1949, ACCENT_DANKAI),      # 団塊の世代
    "dankai_jr": (1971, 1974, ACCENT_DANKAI_JR),   # 団塊ジュニア
    # "hinoeuma": (1966, 1966, ACCENT_HINOEUMA),
}


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
    # Snap to scheme_a band floor (multiples of 5, starting at 0)
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
def build_pyramid_fig(year: int, area_estat: str | None = None) -> go.Figure:
    con = ddb.connect("data/japan_population.duckdb")

    if area_estat is not None:
        df = con.execute("""
            SELECT age_group, age_start, sex, population
            FROM v_census
            WHERE year       = ?
              AND age_scheme  = 'scheme_a'
              AND age_group  != 'Total'
              AND sex        != 'total'
              AND area_estat  = ?
            ORDER BY age_start
        """, [year, area_estat]).df()
    else:
        df = con.execute(f"""
            SELECT age_group, age_start, sex, SUM(population) AS population
            FROM v_census
            WHERE year      = {year}
              AND age_scheme = 'scheme_a'
              AND age_group != 'Total'
              AND sex       != 'total'
              AND area_level = 2
            GROUP BY age_group, age_start, sex
            ORDER BY age_start
        """).df()

    con.close()

    male_df   = df[df["sex"] == "male"  ].sort_values("age_start")
    female_df = df[df["sex"] == "female"].sort_values("age_start")

    age_labels = [_shorten_label(l) for l in male_df["age_group"].tolist()]
    age_starts = male_df["age_start"].tolist()

    # ── Cohort colour mapping ─────────────────────────────────────────────────
    # Build a per-band colour list for male and female traces.
    # Default colours apply; cohort bands get their accent colour.
    cohort_bands = {}
    for name, (b_start, b_end, color) in _COHORTS.items():
        band = _cohort_band(year, b_start, b_end)
        if band is not None:
            cohort_bands[band] = color

    male_colors = [cohort_bands.get(a, PYRAMID_MALE_COLOR) for a in age_starts]
    female_colors = [cohort_bands.get(a, PYRAMID_FEMALE_COLOR) for a in age_starts]
    # cohort_line_colors = [cohort_bands.get(a, "rgba(0,0,0,0)") for a in age_starts]
    # cohort_line_widths = [4 if a in cohort_bands else 0 for a in age_starts]

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
        marker=dict(symbol="square", size=10, color=PYRAMID_MALE_COLOR),
        showlegend=True,
    )
    legend_female = go.Scatter(
        x=[None], y=[None],
        mode="markers",
        name="女 Female",
        marker=dict(symbol="square", size=10, color=PYRAMID_FEMALE_COLOR),
        showlegend=True,
    )

    # ── 戦中世代 — Wartime cohort marker ──────────────────────────────────────
    # Men born 1910–1925 were prime conscription age during the war.
    # Track by birth year, not sex ratio math — same logic as dankai cohorts.
    wartime_bands = _cohort_band_range(year, 1910, 1925) if 1950 <= year <= 2015 else []
    war_gen_rows = male_df[male_df["age_start"].isin(wartime_bands)]

    war_gen_trace = go.Scatter(
        x=[-v for v in war_gen_rows["population"]],
        y=[_shorten_label(l) for l in war_gen_rows["age_group"]],
        mode="markers",
        name="戦中世代",
        showlegend=len(war_gen_rows) > 0,
        marker=dict(
            symbol="diamond",
            size=8,
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
    # Birth years 1986–1990: first cohort born into sustained population decline.
    # Diamond at x=0 (center) — symmetric and neutral, distinct from 戦中世代
    # which sits on the male side.
    shoushika_bands = _cohort_band_range(year, 1986, 1990) if year >= 1990 else []
    shoushika_rows = male_df[male_df["age_start"].isin(shoushika_bands)]

    shoushika_trace = go.Scatter(
        x=[0] * len(shoushika_rows),
        y=[_shorten_label(l) for l in shoushika_rows["age_group"]],
        mode="markers",
        name="少子化世代",
        showlegend=len(shoushika_rows) > 0,
        marker=dict(
            symbol="diamond",
            size=8,
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
        legend_male,
        legend_female,
        war_gen_trace,
        shoushika_trace
    ])

    # ── Cohort outline shapes ──────────────────────────────────────────────────
    # 3 lines per band: top, bottom, outer left (male), outer right (female).
    # Deliberately no center line.
    bar_half = (1 - 0.15) / 2
    for band_start, color in cohort_bands.items():
        if band_start not in age_starts:
            continue
        idx = age_starts.index(band_start)
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
                          line=dict(color=color, width=3.5), **shape)

    fig.update_layout(
        barmode="overlay",          # bars share the same y-position, not stacked
        bargap=0.15,
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        margin=dict(l=16, r=16, t=28, b=20),
        legend=dict(
            orientation="h",
            x=0.5, xanchor="center",
            y=1.02, yanchor="bottom",
            font=dict(color=FONT_MAIN, size=14),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            tickformat="~s",  # 5000000 → "5M", -5000000 → "-5M"
            tickfont=dict(color=FONT_MAIN, size=12),
            gridcolor="#1a2440",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor=PANEL_BORDER,
            showline=False,
            range=[-7000000, 7000000],
            # autorange=True,
            dtick=3_000_000,
        ),
        yaxis=dict(
            title=dict(
                text="Age (Years)",
                font=dict(color=FONT_MAIN, size=12),
            ),
            tickfont=dict(color=FONT_MAIN, size=12),
            showgrid=False,
            autorange=True,
        ),
    )

    return fig