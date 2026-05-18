# app/viz/timeseries.py
from functools import lru_cache
from math import floor

import plotly.graph_objects as go

from app.aesthetics.config import (
    FONT_SIZE_AXIS_TICK, FONT_SIZE_AXIS_TITLE, FONT_SIZE_CHART_TITLE,
    COLOR_PRIMARY, COLOR_WARNING, COLOR_TEXT_MID, COLOR_TEXT_HI, CHART_PLOT_COLOR, ACCENT_DANKAI_JR,
    PANEL_BORDER, ACCENT_THRESHOLD, TIMESERIES_PREF_COLOR,
    LINE_WIDTH_MAIN, LINE_WIDTH_PREF, LINE_WIDTH_1945,
    LINE_WIDTH_THRESHOLD, LINE_WIDTH_YEAR_MARKER,
    MARKER_SIZE_DOT, MARKER_SIZE_1945,
    OPACITY_THRESHOLD_LINE, OPACITY_YEAR_VLINE,
    YAXIS_TICK_STANDOFF,
    TIMESERIES_MARGIN_L, TIMESERIES_MARGIN_R, TIMESERIES_MARGIN_T, TIMESERIES_MARGIN_B,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
    TFR_REPLACEMENT_RATE, TFR_CUTOFF_YEAR,
    IPSS_HANDOFF_YEAR, PROJECTION_BAND_ALPHA,
)
from app.utils import hex_to_rgb
from app.data.db import get_con
from app.data import figure_cache



_CROSSOVER_YEAR = 1997

@lru_cache(maxsize=8)
def _get_pop_share_data(area_estat: str | None) -> tuple:
    """
    Returns (national_df, pref_df_or_None, pref_label_or_None).
    Columns: year, youth_share, working_share, old_share  (all as %).
    Cached on area_estat only — year doesn't affect the underlying series.
    """
    con = get_con()

    _SHARE_CTE = """
        WITH age_buckets AS (
            SELECT year,
                SUM(CASE WHEN age_start <= 10 AND age_end   <= 14 THEN population ELSE 0 END) AS pop_0_14,
                SUM(CASE WHEN age_start >= 15 AND age_end   <= 64 THEN population ELSE 0 END) AS pop_15_64,
                SUM(CASE WHEN age_start >= 65                     THEN population ELSE 0 END) AS pop_65_plus
            FROM v_census
            WHERE age_scheme = 'scheme_a'
              AND age_group  != 'Total'
              AND sex         = 'total'
              {where_extra}
            GROUP BY year
        )
        SELECT year,
            ROUND(pop_0_14    * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS youth_share,
            ROUND(pop_15_64   * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS working_share,
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS old_share,
            pop_0_14,
            pop_15_64,
            pop_65_plus
        FROM age_buckets
        ORDER BY year
    """

    national_df = con.execute(
        _SHARE_CTE.format(where_extra="AND area_level = 2")
    ).df()

    pref_df    = None
    pref_label = None

    if area_estat is not None:
        name_row = con.execute(
            "SELECT prefecture_name_ja, prefecture_name FROM d_prefectures WHERE area_estat = ?",
            [area_estat],
        ).fetchone()
        pref_label = f"{name_row[0]}  {name_row[1]}" if name_row else area_estat

        pref_df = con.execute(
            _SHARE_CTE.format(where_extra="AND area_estat = ?"),
            [area_estat],
        ).df()

    return national_df, pref_df, pref_label


def build_ts_pop_share_fig(selected_year: int, area_estat: str | None = None) -> go.Figure:
    _key = figure_cache.make_key("pop_share", selected_year, area_estat)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    national_df, pref_df, pref_label = _get_pop_share_data(area_estat)

    df_non_1945 = national_df[national_df["year"] != 1945]
    df_1945     = national_df[national_df["year"] == 1945]

    # ── Shared customdata ─────────────────────────────────────────────────────
    # Shape: [year, youth_share, working_share, old_share,
    #         pref_youth, pref_working, pref_old, pref_label, flag]
    if pref_df is not None and not pref_df.empty:
        merged = national_df.merge(
            pref_df[["year", "youth_share", "working_share", "old_share",
                     "pop_0_14", "pop_15_64", "pop_65_plus"]].rename(columns={
                "youth_share":   "pref_youth",
                "working_share": "pref_working",
                "old_share":     "pref_old",
                "pop_0_14":      "pref_pop_0_14",
                "pop_15_64":     "pref_pop_15_64",
                "pop_65_plus":   "pref_pop_65_plus",
            }),
            on="year",
            how="left",
        )
    else:
        merged = national_df.copy()
        merged["pref_youth"]       = float("nan")
        merged["pref_working"]     = float("nan")
        merged["pref_old"]         = float("nan")
        merged["pref_pop_0_14"]    = float("nan")
        merged["pref_pop_15_64"]   = float("nan")
        merged["pref_pop_65_plus"] = float("nan")

    pl = pref_label or ""

    def _nan_to_none(v):
        return None if v != v else float(v)

    cd_by_year = {
        int(row.year): [
            int(row.year),
            float(row.youth_share),
            float(row.working_share),
            float(row.old_share),
            _nan_to_none(row.pref_youth),
            _nan_to_none(row.pref_working),
            _nan_to_none(row.pref_old),
            pl,
            "1945" if row.year == 1945 else "",
            # indices 9–11: national raw headcounts
            float(row.pop_0_14),
            float(row.pop_15_64),
            float(row.pop_65_plus),
            # indices 12–14: prefecture raw headcounts (None when no pref selected)
            _nan_to_none(row.pref_pop_0_14),
            _nan_to_none(row.pref_pop_15_64),
            _nan_to_none(row.pref_pop_65_plus),
        ]
        for row in merged.itertuples()
    }

    traces = []

    # ── National lines ────────────────────────────────────────────────────────
    # Fade when a prefecture is active so the dotted overlay is easy to read.
    nat_opacity = 0.25 if area_estat is not None else 1.0

    share_series = [
        ("youth_share",   "年少人口 0–14",  PYRAMID_FEMALE_COLOR),
        ("working_share", "生産年齢 15–64", COLOR_TEXT_HI),
        ("old_share",     "老年人口 65+",   PYRAMID_MALE_COLOR),
    ]

    for col, label, color in share_series:
        traces.append(go.Scatter(
            x=national_df["year"],
            y=national_df[col],
            mode="lines",
            name=label,
            line=dict(color=color, width=LINE_WIDTH_MAIN),
            opacity=nat_opacity,
            hoverinfo="none",
            customdata=[cd_by_year[yr] for yr in national_df["year"]],
        ))
        traces.append(go.Scatter(
            x=df_non_1945["year"],
            y=df_non_1945[col],
            mode="markers",
            showlegend=False,
            marker=dict(color=color, size=MARKER_SIZE_DOT),
            opacity=nat_opacity,
            hoverinfo="skip",
        ))

    # ── 1945 — one filled dot per series at its actual y-value ───────────────
    if not df_1945.empty:
        for col, _, _ in share_series:
            traces.append(go.Scatter(
                x=df_1945["year"],
                y=df_1945[col],
                mode="markers",
                showlegend=False,
                marker=dict(color=COLOR_PRIMARY, size=MARKER_SIZE_DOT + 2),
                opacity=nat_opacity,
                hoverinfo="none",
                customdata=[cd_by_year[1945]],
            ))

    # ── Prefecture overlay ────────────────────────────────────────────────────
    if pref_df is not None and not pref_df.empty:
        for col, color in [
            ("youth_share",   PYRAMID_FEMALE_COLOR),
            ("working_share", COLOR_TEXT_HI),
            ("old_share",     PYRAMID_MALE_COLOR),
        ]:
            traces.append(go.Scatter(
                x=pref_df["year"],
                y=pref_df[col],
                mode="lines+markers",
                showlegend=False,
                line=dict(color=color, width=LINE_WIDTH_PREF, dash="dot"),
                marker=dict(size=4, color=color),
                hoverinfo="none",
                customdata=[cd_by_year[yr] for yr in pref_df["year"]],
            ))

    # ── IPSS national projection bolt-on ──────────────────────────────────────
    proj    = _get_national_projection_data()
    med_p   = proj["medium"]
    hi_p    = proj["high"]
    lo_p    = proj["low"]

    # Medium dashed continuations of all three share lines
    for col, label, color in [
        ("youth_share",   "年少 Youth 推計",   PYRAMID_FEMALE_COLOR),
        ("working_share", "生産 Working 推計", COLOR_TEXT_HI),
        ("old_share",     "老年 Old 推計",     PYRAMID_MALE_COLOR),
    ]:
        traces.append(go.Scatter(
            x=med_p["year"], y=med_p[col],
            mode="lines",
            name=label,
            line=dict(color=color, width=LINE_WIDTH_MAIN, dash="dash"),
            showlegend=False,   # don't clutter legend — lines are visually continuous
            hoverinfo="none",
        ))

    # Old-share high/low band — the headline story
    for col, color in [
        ("youth_share",   PYRAMID_FEMALE_COLOR),
        ("working_share", COLOR_TEXT_HI),
        ("old_share",     PYRAMID_MALE_COLOR),
    ]:
        r, g, b = hex_to_rgb(color)
        band_color = f"rgba({r},{g},{b},{PROJECTION_BAND_ALPHA})"

        traces.append(go.Scatter(
            x=lo_p["year"], y=lo_p[col],
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
        ))
        traces.append(go.Scatter(
            x=hi_p["year"], y=hi_p[col],
            mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor=band_color,
            showlegend=False, hoverinfo="skip",
        ))

    fig = go.Figure(data=traces)

    # ── Working-age peak annotation ───────────────────────────────────────────
    # Derived from data — not hardcoded — the peak census year is empirical.
    peak_idx  = national_df["working_share"].idxmax()
    peak_year = int(national_df.loc[peak_idx, "year"])
    peak_val  = float(national_df.loc[peak_idx, "working_share"])

    fig.add_annotation(
        x=peak_year,
        y=peak_val,
        text=f"生産年齢人口 ピーク {peak_year}年  ↓",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_AXIS_TITLE),
        bgcolor="rgba(0,0,0,0)",
    )

    # ── Crossover annotation (old-age share exceeds youth share) ─────────────
    # Same demographic event as aging index > 100 — same interpolated crossover year.
    fig.add_annotation(
        x=_CROSSOVER_YEAR,
        y=1,
        yref="paper",
        text="老年 > 年少  ↑",
        showarrow=False,
        xanchor="left",
        yanchor="top",
        font=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_AXIS_TITLE),
        bgcolor="rgba(0,0,0,0)",
    )

    # ── Selected year indicator ───────────────────────────────────────────────
    fig.add_vline(
        x=selected_year,
        line_color=COLOR_TEXT_MID,
        line_width=LINE_WIDTH_YEAR_MARKER,
        line_dash="dot",
        opacity=OPACITY_YEAR_VLINE,
    )

    fig.update_layout(
        margin=dict(l=TIMESERIES_MARGIN_L, r=TIMESERIES_MARGIN_R, t=TIMESERIES_MARGIN_T, b=TIMESERIES_MARGIN_B),
        autosize=True,
        plot_bgcolor=CHART_PLOT_COLOR,
        legend=dict(
            orientation="h",
            x=0.195, xanchor="left",
            y=0.98, yanchor="top",
            font=dict(color=COLOR_TEXT_HI),
        ),
        xaxis=dict(
            showline=True,
            linecolor=PANEL_BORDER,
            linewidth=2,
            mirror=True,
            dtick=10,
            automargin=False,
        ),
        yaxis=dict(
            showline=True,
            linecolor=PANEL_BORDER,
            linewidth=0.8,
            mirror=True,
            title=dict(
                text="人口割合 / Share %",
                font=dict(color=COLOR_TEXT_HI, size=FONT_SIZE_AXIS_TITLE),
            ),
            zeroline=False,
            tickformat=".0f",
            ticksuffix="%",
            range=[0, 100],
            ticklabelstandoff=YAXIS_TICK_STANDOFF,
            automargin=False,
        ),
    )

    figure_cache.put(_key, fig)
    return fig


_POPULATION_DIVISOR = 1_000_000  # display in millions; y-axis label says 百万人

@lru_cache(maxsize=8)
def _get_population_data(area_estat: str | None) -> tuple:
    """
    Returns (national_df, pref_df_or_None, pref_label_or_None).

    national_df / pref_df columns: year, total, male, female — population in raw headcount.
    Divide by _POPULATION_DIVISOR in the figure builder for axis display.
    Cached on area_estat only — the full time series is fetched once per selection.
    """
    con = get_con()

    national_df = con.execute("""
        SELECT year, sex, SUM(population) AS population
        FROM v_census
        WHERE age_group  = 'Total'
          AND sex        IN ('total', 'male', 'female')
          AND area_level  = 2
        GROUP BY year, sex
        ORDER BY year, sex
    """).df()

    national_df = (
        national_df
        .pivot(index="year", columns="sex", values="population")
        .reset_index()
    )
    national_df.columns.name = None  # drop the 'sex' axis label left by pivot

    pref_df    = None
    pref_label = None

    if area_estat is not None:
        name_row = con.execute(
            "SELECT prefecture_name_ja, prefecture_name FROM d_prefectures WHERE area_estat = ?",
            [area_estat],
        ).fetchone()
        pref_label = f"{name_row[0]}  {name_row[1]}" if name_row else area_estat

        pref_df = con.execute("""
            SELECT year, sex, SUM(population) AS population
            FROM v_census
            WHERE age_group  = 'Total'
              AND sex        IN ('total', 'male', 'female')
              AND area_estat  = ?
            GROUP BY year, sex
            ORDER BY year, sex
        """, [area_estat]).df()

        pref_df = (
            pref_df
            .pivot(index="year", columns="sex", values="population")
            .reset_index()
        )
        pref_df.columns.name = None

    return national_df, pref_df, pref_label


def build_ts_population_fig(selected_year: int, area_estat: str | None = None) -> go.Figure:
    _key = figure_cache.make_key("population", selected_year, area_estat)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    national_df, pref_df, pref_label = _get_population_data(area_estat)

    M = _POPULATION_DIVISOR

    # ── Shared customdata — all traces carry full year snapshot ───────────────
    # Shape per point: [year, total_M, male_M, female_M, series_prefix]
    df_source     = national_df if area_estat is None else pref_df
    series_prefix = "全国" if area_estat is None else pref_label

    cd_rows = [
        [int(row.year), row.total / M, row.male / M, row.female / M, series_prefix]
        for row in df_source.itertuples()
    ]
    cd_by_year = {int(row[0]): row for row in cd_rows}

    traces = []

    # ── National lines ────────────────────────────────────────────────────────
    if area_estat is None:
        national_series = [
            ("total",  "全国 Total",  COLOR_TEXT_HI,       LINE_WIDTH_MAIN),
            ("male",   "全国 Male",   PYRAMID_MALE_COLOR,   LINE_WIDTH_MAIN),
            ("female", "全国 Female", PYRAMID_FEMALE_COLOR, LINE_WIDTH_MAIN),
        ]

        df_non_1945 = national_df[national_df["year"] != 1945]
        df_1945     = national_df[national_df["year"] == 1945]

        for col, label, color, width in national_series:
            # Line — connects all years including 1945
            traces.append(go.Scatter(
                x=national_df["year"],
                y=national_df[col] / M,
                mode="lines",
                name=label,
                line=dict(color=color, width=width),
                hoverinfo="none",
                customdata=[cd_by_year[yr] for yr in national_df["year"]],
            ))
            # Regular census year dots (non-1945)
            traces.append(go.Scatter(
                x=df_non_1945["year"],
                y=df_non_1945[col] / M,
                mode="markers",
                showlegend=False,
                marker=dict(color=color, size=MARKER_SIZE_DOT),
                hoverinfo="skip",
            ))
            # 1945 — filled COLOR_PRIMARY dot at this series' y-value
            if not df_1945.empty:
                traces.append(go.Scatter(
                    x=df_1945["year"],
                    y=df_1945[col] / M,
                    mode="markers",
                    showlegend=False,
                    marker=dict(color=COLOR_PRIMARY, size=MARKER_SIZE_DOT + 2),
                    hoverinfo="none",
                    customdata=[cd_by_year[1945]],
                ))

    # ── Prefecture overlays ───────────────────────────────────────────────────
    if pref_df is not None and not pref_df.empty:
        pref_series = [
            ("total",  f"{pref_label} Total",  COLOR_TEXT_HI),
            ("male",   f"{pref_label} Male",   PYRAMID_MALE_COLOR),
            ("female", f"{pref_label} Female", PYRAMID_FEMALE_COLOR),
        ]

        for col, label, color in pref_series:
            traces.append(go.Scatter(
                x=pref_df["year"],
                y=pref_df[col] / M,
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=LINE_WIDTH_PREF, dash="dot"),
                marker=dict(color=color, size=4),
                hoverinfo="none",
                customdata=[cd_by_year[yr] for yr in pref_df["year"]],
            ))

    # ── IPSS national projection bolt-on (total line only — no M/F split) ─────
    proj = _get_national_projection_data()
    med  = proj["medium"]
    hi   = proj["high"]
    lo   = proj["low"]

    r, g, b = hex_to_rgb(COLOR_TEXT_HI)
    band_color = f"rgba({r},{g},{b},{PROJECTION_BAND_ALPHA})"

    # Low bound — invisible line, anchors the fill
    traces.append(go.Scatter(
        x=lo["year"], y=lo["total_population"] / M,
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    ))
    # High bound — fills down to low
    traces.append(go.Scatter(
        x=hi["year"], y=hi["total_population"] / M,
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor=band_color,
        showlegend=False,
        hoverinfo="skip",
    ))
    # Medium — dashed continuation of total line
    traces.append(go.Scatter(
        x=med["year"], y=med["total_population"] / M,
        mode="lines",
        name="IPSS 中位推計 Medium",
        line=dict(color=COLOR_TEXT_HI, width=LINE_WIDTH_MAIN, dash="dash"),
        showlegend=True,
        hoverinfo="none",
    ))

    # ── Prefecture projection overlay ─────────────────────────────────────────
    if area_estat is not None:
        pref_proj = _get_ipss_prefecture_data(area_estat)
        if not pref_proj.empty:
            traces.append(go.Scatter(
                x=pref_proj["year"], y=pref_proj["total"] / M,
                mode="lines",
                name=f"{pref_label} 推計",
                line=dict(color=ACCENT_DANKAI_JR, width=LINE_WIDTH_PREF, dash="dash"),
                showlegend=True,
                hoverinfo="none",
            ))

    fig = go.Figure(data=traces)

    # ── Selected year indicator ───────────────────────────────────────────────
    fig.add_vline(
        x=selected_year,
        line_color=COLOR_TEXT_MID,
        line_width=LINE_WIDTH_YEAR_MARKER,
        line_dash="dot",
        opacity=OPACITY_YEAR_VLINE,
    )

    all_totals = list(national_df["total"] / M) + list(proj["medium"]["total_population"] / M)
    all_mins = list(national_df["male"] / M) + list(national_df["female"] / M)
    y_min = floor(min(all_mins) * 10) / 10 / 1.4
    y_max = round(max(all_totals) * 1.2, 1)

    fig.update_layout(
        margin=dict(l=TIMESERIES_MARGIN_L, r=TIMESERIES_MARGIN_R, t=TIMESERIES_MARGIN_T, b=TIMESERIES_MARGIN_B),
        autosize=True,
        plot_bgcolor=CHART_PLOT_COLOR,
        legend=dict(
            orientation="h",
            x=0.195, xanchor="left",
            y=0.98, yanchor="top",
            font=dict(color=COLOR_TEXT_HI),
        ),
        xaxis=dict(
            showline=True,
            linecolor=PANEL_BORDER,
            linewidth=2,
            mirror=True,
            dtick=10,
            automargin=False,
        ),
        yaxis=dict(
            showline=True,
            linecolor=PANEL_BORDER,
            linewidth=0.8,
            mirror=True,
            title=dict(
                text="百万人 / Millions",
                font=dict(color=COLOR_TEXT_HI, size=FONT_SIZE_AXIS_TITLE),
            ),
            range=[y_min, y_max],
            zeroline=False,
            ticklabelstandoff=YAXIS_TICK_STANDOFF,
            automargin=False,
        ),
    )

    figure_cache.put(_key, fig)
    return fig


# TFR crossed 2.1 replacement rate between 1973 and 1974 census-adjacent years.
_TFR_CROSSOVER_YEAR = 1974

@lru_cache(maxsize=8)
def _get_tfr_data(area_estat: str | None) -> tuple:
    """
    Returns (national_df, pref_df_or_None, pref_label_or_None).
    national_df columns: year, tfr  (national average across all prefectures)
    pref_df columns:     year, tfr  (single prefecture)
    Cached on area_estat — year doesn't affect underlying series.
    """
    con = get_con()

    national_df = con.execute("""
        SELECT year, ROUND(AVG(tfr), 2) AS tfr
        FROM f_tfr
        GROUP BY year
        ORDER BY year
    """).df()

    pref_df    = None
    pref_label = None

    if area_estat is not None:
        name_row = con.execute(
            "SELECT prefecture_name_ja, prefecture_name FROM d_prefectures WHERE area_estat = ?",
            [area_estat],
        ).fetchone()
        pref_label = f"{name_row[0]}  {name_row[1]}" if name_row else area_estat

        pref_df = con.execute("""
            SELECT year, tfr
            FROM f_tfr
            WHERE area_estat = ?
            ORDER BY year
        """, [area_estat]).df()

    return national_df, pref_df, pref_label


def build_ts_tfr_fig(selected_year: int, area_estat: str | None = None) -> go.Figure:
    _key = figure_cache.make_key("tfr", selected_year, area_estat)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    national_df, pref_df, pref_label = _get_tfr_data(area_estat)

    # ── Customdata: [year, national_tfr, pref_tfr_or_None, pref_label] ───────
    if pref_df is not None and not pref_df.empty:
        merged = national_df.merge(
            pref_df[["year", "tfr"]].rename(columns={"tfr": "pref_tfr"}),
            on="year", how="left",
        )
    else:
        merged = national_df.copy()
        merged["pref_tfr"] = float("nan")

    pl = pref_label or ""
    cd_by_year = {
        int(row.year): [
            int(row.year),
            float(row.tfr),
            None if row.pref_tfr != row.pref_tfr else float(row.pref_tfr),
            pl,
        ]
        for row in merged.itertuples()
    }

    traces = []

    # ── National TFR line ─────────────────────────────────────────────────────
    traces.append(go.Scatter(
        x=national_df["year"],
        y=national_df["tfr"],
        mode="lines+markers",
        name="全国 National",
        line=dict(color=COLOR_TEXT_HI, width=LINE_WIDTH_MAIN),
        marker=dict(color=COLOR_TEXT_HI, size=MARKER_SIZE_DOT),
        hoverinfo="none",
        customdata=[cd_by_year[yr] for yr in national_df["year"]],
    ))

    # ── Prefecture overlay ────────────────────────────────────────────────────
    if pref_df is not None and not pref_df.empty:
        traces.append(go.Scatter(
            x=pref_df["year"],
            y=pref_df["tfr"],
            mode="lines+markers",
            name=pref_label,
            line=dict(color=ACCENT_DANKAI_JR, width=LINE_WIDTH_PREF, dash="dot"),
            marker=dict(color=ACCENT_DANKAI_JR, size=MARKER_SIZE_DOT),
            hoverinfo="none",
            customdata=[cd_by_year.get(yr, [yr, None, None, pl]) for yr in pref_df["year"]],
        ))

    # ── 2.1 replacement rate reference line ───────────────────────────────────
    traces.append(go.Scatter(
        x=[national_df["year"].min(), national_df["year"].max()],
        y=[TFR_REPLACEMENT_RATE, TFR_REPLACEMENT_RATE],
        mode="lines",
        name="replacement rate 2.10",
        line=dict(color=COLOR_WARNING, width=LINE_WIDTH_THRESHOLD, dash="dash"),
        hoverinfo="none",
        showlegend=True,
    ))

    fig = go.Figure(data=traces)

    # ── Crossover annotation (~1974) ──────────────────────────────────────────
    fig.add_annotation(
        x=_TFR_CROSSOVER_YEAR,
        y=TFR_REPLACEMENT_RATE,
        text="出生率 < 2.10  ↓",
        showarrow=False,
        xanchor="left",
        yanchor="top",
        font=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_AXIS_TITLE),
        bgcolor="rgba(0,0,0,0)",
    )

    # ── Selected year indicator ───────────────────────────────────────────────
    tfr_min_year = int(national_df["year"].min())
    clamped_year = max(selected_year, tfr_min_year)
    fig.add_vline(
        x=clamped_year,
        line_color=COLOR_TEXT_MID,
        line_width=LINE_WIDTH_YEAR_MARKER,
        line_dash="dot",
        opacity=OPACITY_YEAR_VLINE,
    )

    fig.update_layout(
        margin=dict(l=TIMESERIES_MARGIN_L, r=TIMESERIES_MARGIN_R, t=TIMESERIES_MARGIN_T, b=TIMESERIES_MARGIN_B),
        autosize=True,
        plot_bgcolor=CHART_PLOT_COLOR,
        legend=dict(
            orientation="h",
            x=0.195, xanchor="left",
            y=0.98, yanchor="top",
            font=dict(color=COLOR_TEXT_HI),
        ),
        xaxis=dict(
            showline=True,
            linecolor=PANEL_BORDER,
            linewidth=2,
            mirror=True,
            dtick=10,
            automargin=False,
        ),
        yaxis=dict(
            showline=True,
            linecolor=PANEL_BORDER,
            linewidth=0.8,
            mirror=True,
            title=dict(
                text="合計特殊出生率 TFR",
                font=dict(color=COLOR_TEXT_HI, size=FONT_SIZE_AXIS_TITLE),
            ),
            range=[floor(national_df["tfr"].min() * 10) / 10 / 1.25, round(national_df["tfr"].max() * 1.25, 1)],
            zeroline=False,
            ticklabelstandoff=YAXIS_TICK_STANDOFF,
            automargin=False,
        ),
    )

    figure_cache.put(_key, fig)
    return fig


@lru_cache(maxsize=1)
def _get_national_projection_data() -> dict:
    """
    Returns {"medium": df, "high": df, "low": df}.
    Each df has columns: year, total_population, pop_0_14, pop_15_64, pop_65_plus,
    plus computed shares: youth_share, working_share, old_share.
    Covers projection_year >= IPSS_HANDOFF_YEAR.
    lru_cache(maxsize=1) — no args, result never changes.
    """
    con = get_con()
    result = {}
    for variant in ("medium", "high", "low"):
        df = con.execute(f"""
            SELECT
                projection_year AS year,
                total_population,
                pop_0_14,
                pop_15_64,
                pop_65_plus,
                ROUND(pop_0_14    * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS youth_share,
                ROUND(pop_15_64   * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS working_share,
                ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS old_share
            FROM f_national_projections
            WHERE variant = '{variant}'
              AND projection_year >= {IPSS_HANDOFF_YEAR}
            ORDER BY projection_year
        """).df()
        result[variant] = df
    return result


@lru_cache(maxsize=8)
def _get_ipss_prefecture_data(area_estat: str) -> "pd.DataFrame":
    """
    Sums f_projections across all age groups and sexes for a single prefecture.
    Returns df with columns: year, total.
    Covers projection_year >= IPSS_HANDOFF_YEAR.
    """
    con = get_con()
    return con.execute(f"""
        SELECT projection_year AS year, SUM(population) AS total
        FROM f_projections
        WHERE area_estat = '{area_estat}'
          AND projection_year >= {IPSS_HANDOFF_YEAR}
        GROUP BY projection_year
        ORDER BY projection_year
    """).df()