# app/timeseries.py
from functools import lru_cache

import plotly.graph_objects as go

from app.config import (
    FONT_SIZE_AXIS_TICK, FONT_SIZE_AXIS_TITLE, FONT_SIZE_CHART_TITLE,
    COLOR_PRIMARY, COLOR_TEXT_MID, COLOR_TEXT_HI, CHART_PLOT_COLOR,
    PANEL_BORDER, ACCENT_THRESHOLD, TIMESERIES_PREF_COLOR,
    LINE_WIDTH_MAIN, LINE_WIDTH_PREF, LINE_WIDTH_1945,
    LINE_WIDTH_THRESHOLD, LINE_WIDTH_YEAR_MARKER,
    MARKER_SIZE_DOT, MARKER_SIZE_1945,
    OPACITY_THRESHOLD_LINE, OPACITY_YEAR_VLINE,
    YAXIS_TICK_STANDOFF,
    TIMESERIES_MARGIN_L, TIMESERIES_MARGIN_R, TIMESERIES_MARGIN_T, TIMESERIES_MARGIN_B,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
)
from app.db import get_con
from app import figure_cache



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

        for col, label, color, width in national_series:
            traces.append(go.Scatter(
                x=national_df["year"],
                y=national_df[col] / M,
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=width),
                marker=dict(color=color, size=MARKER_SIZE_DOT),
                hoverinfo="none",
                customdata=[cd_by_year[yr] for yr in national_df["year"]],
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

    fig = go.Figure(data=traces)

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
                text="百万人 / Millions",
                font=dict(color=COLOR_TEXT_HI, size=FONT_SIZE_AXIS_TITLE),
            ),
            zeroline=False,
            ticklabelstandoff=YAXIS_TICK_STANDOFF,
            automargin=False,
        ),
    )

    figure_cache.put(_key, fig)
    return fig


# Aging index crossed 100 between the 1995 and 2000 census years.
# Annotated at ~1997 — the midpoint, not a data point.
_CROSSOVER_YEAR = 1997

@lru_cache(maxsize=8)
def _get_aging_index_data(area_estat: str | None) -> tuple:
    """
    Returns (national_df, pref_df_or_None, pref_label_or_None).
    Cached on area_estat only — year is not a factor in the underlying data.
    """
    con = get_con()

    national_df = con.execute("""
        WITH age_buckets AS (
            SELECT year,
                SUM(CASE WHEN age_start >= 65 THEN population ELSE 0 END)                   AS pop_65_plus,
                SUM(CASE WHEN age_start <= 10 AND age_end <= 14 THEN population ELSE 0 END)  AS pop_0_14
            FROM v_census
            WHERE age_scheme = 'scheme_a'
              AND age_group  != 'Total'
              AND sex         = 'total'
              AND area_level  = 2
            GROUP BY year
        )
        SELECT year,
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14, 0), 1) AS aging_index
        FROM age_buckets
        ORDER BY year
    """).df()

    pref_df    = None
    pref_label = None

    if area_estat is not None:
        name_row = con.execute(
            "SELECT prefecture_name_ja, prefecture_name FROM d_prefectures WHERE area_estat = ?",
            [area_estat]
        ).fetchone()
        pref_label = f"{name_row[0]}  {name_row[1]}" if name_row else area_estat

        pref_df = con.execute("""
            WITH age_buckets AS (
                SELECT year,
                    SUM(CASE WHEN age_start >= 65 THEN population ELSE 0 END)                   AS pop_65_plus,
                    SUM(CASE WHEN age_start <= 10 AND age_end <= 14 THEN population ELSE 0 END)  AS pop_0_14
                FROM v_census
                WHERE age_scheme = 'scheme_a'
                  AND age_group  != 'Total'
                  AND sex         = 'total'
                  AND area_estat  = ?
                GROUP BY year
            )
            SELECT year,
                ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14, 0), 1) AS aging_index
            FROM age_buckets
            ORDER BY year
        """, [area_estat]).df()

    return national_df, pref_df, pref_label


def build_ts_aging_index_fig(selected_year: int, area_estat: str | None = None) -> go.Figure:
    _key = figure_cache.make_key("timeseries", selected_year, area_estat)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    national_df, pref_df, pref_label = _get_aging_index_data(area_estat)

    df_non_1945 = national_df[national_df["year"] != 1945]
    df_1945     = national_df[national_df["year"] == 1945]

    # ── Shared customdata — all traces carry full year snapshot ───────────────
    # Shape per point: [year, national_ai, pref_ai_or_None, pref_label, flag]
    if pref_df is not None and not pref_df.empty:
        merged = national_df.merge(
            pref_df[["year", "aging_index"]].rename(columns={"aging_index": "pref_ai"}),
            on="year",
            how="left",
        )
    else:
        merged = national_df.copy()
        merged["pref_ai"] = float("nan")

    pl = pref_label or ""

    cd_by_year = {
        int(row.year): [
            int(row.year),
            float(row.aging_index),
            None if row.pref_ai != row.pref_ai else float(row.pref_ai),  # NaN → None
            pl,
            "1945" if row.year == 1945 else "",
        ]
        for row in merged.itertuples()
    }

    traces = []

    # ── National line (connects all years including 1945) ─────────────────────
    traces.append(go.Scatter(
        x=national_df["year"],
        y=national_df["aging_index"],
        mode="lines",
        name="全国 National",
        line=dict(color=COLOR_TEXT_HI, width=LINE_WIDTH_MAIN),
        hoverinfo="none",
        customdata=[cd_by_year[yr] for yr in national_df["year"]],
    ))

    # Regular census year dots (non-1945 only) — visual overlay, no hover
    traces.append(go.Scatter(
        x=df_non_1945["year"],
        y=df_non_1945["aging_index"],
        mode="markers",
        showlegend=False,
        marker=dict(color=COLOR_TEXT_MID, size=MARKER_SIZE_DOT),
        hoverinfo="skip",
    ))

    # 1945 — open circle, red to match the slider mark styling
    if not df_1945.empty:
        traces.append(go.Scatter(
            x=df_1945["year"],
            y=df_1945["aging_index"],
            mode="markers",
            name="1945 臨時国勢調査",
            marker=dict(
                symbol="circle-open",
                size=MARKER_SIZE_1945,
                color=COLOR_PRIMARY,
                line=dict(width=LINE_WIDTH_1945, color=COLOR_PRIMARY),
            ),
            hoverinfo="none",
            customdata=[cd_by_year[1945]],
        ))

    # ── Prefecture overlay ────────────────────────────────────────────────────
    if pref_df is not None and not pref_df.empty:
        traces.append(go.Scatter(
            x=pref_df["year"],
            y=pref_df["aging_index"],
            mode="lines+markers",
            name=pref_label,
            line=dict(color=TIMESERIES_PREF_COLOR, width=LINE_WIDTH_PREF, dash="dot"),
            marker=dict(size=4, color=TIMESERIES_PREF_COLOR),
            hoverinfo="none",
            customdata=[cd_by_year[yr] for yr in pref_df["year"]],
        ))

    fig = go.Figure(data=traces)

    # ── Reference line at aging index = 100 ───────────────────────────────────
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=ACCENT_THRESHOLD,
        line_width=LINE_WIDTH_THRESHOLD,
        opacity=OPACITY_THRESHOLD_LINE,
    )

    # ── Crossover annotation ──────────────────────────────────────────────────
    fig.add_annotation(
        x=_CROSSOVER_YEAR,
        y=100,
        text="高齢化指数 > 100  ↑",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
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
            linewidth=1,
            mirror=True,
            title=dict(
                text="高齢化指数",
                font=dict(color=COLOR_TEXT_HI, size=FONT_SIZE_AXIS_TITLE),
            ),
            zeroline=False,
            ticklabelstandoff=YAXIS_TICK_STANDOFF,
            automargin=False
        ),
    )

    figure_cache.put(_key, fig)
    return fig


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
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS old_share
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
            pref_df[["year", "youth_share", "working_share", "old_share"]].rename(columns={
                "youth_share":   "pref_youth",
                "working_share": "pref_working",
                "old_share":     "pref_old",
            }),
            on="year",
            how="left",
        )
    else:
        merged = national_df.copy()
        merged["pref_youth"]   = float("nan")
        merged["pref_working"] = float("nan")
        merged["pref_old"]     = float("nan")

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
        ]
        for row in merged.itertuples()
    }

    traces = []

    # ── National lines ────────────────────────────────────────────────────────
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
            hoverinfo="none",
            customdata=[cd_by_year[yr] for yr in national_df["year"]],
        ))
        traces.append(go.Scatter(
            x=df_non_1945["year"],
            y=df_non_1945[col],
            mode="markers",
            showlegend=False,
            marker=dict(color=color, size=MARKER_SIZE_DOT),
            hoverinfo="skip",
        ))

    # ── 1945 — single trace, three open circles ───────────────────────────────
    # Batched into one trace to avoid three legend entries.
    if not df_1945.empty:
        traces.append(go.Scatter(
            x=[1945, 1945, 1945],
            y=[
                float(df_1945["youth_share"].iloc[0]),
                float(df_1945["working_share"].iloc[0]),
                float(df_1945["old_share"].iloc[0]),
            ],
            mode="markers",
            name="1945 臨時国勢調査",
            marker=dict(
                symbol="circle-open",
                size=MARKER_SIZE_1945,
                color=COLOR_PRIMARY,
                line=dict(width=LINE_WIDTH_1945, color=COLOR_PRIMARY),
            ),
            hoverinfo="none",
            customdata=[cd_by_year[1945]] * 3,
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
