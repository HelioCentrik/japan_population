# app/timeseries.py
from functools import lru_cache

import plotly.graph_objects as go

from app.config import (
    COLOR_TEXT_MID, COLOR_PRIMARY, CHART_PLOT_COLOR,
    PANEL_BORDER, ACCENT_THRESHOLD, TIMESERIES_PREF_COLOR,
    LINE_WIDTH_MAIN, LINE_WIDTH_PREF, LINE_WIDTH_1945,
    LINE_WIDTH_THRESHOLD, LINE_WIDTH_YEAR_MARKER,
    MARKER_SIZE_DOT, MARKER_SIZE_1945,
    OPACITY_THRESHOLD_LINE, OPACITY_YEAR_VLINE,
    YAXIS_TICK_STANDOFF,
    TIMESERIES_MARGIN_L, TIMESERIES_MARGIN_R, TIMESERIES_MARGIN_T, TIMESERIES_MARGIN_B,
    FONT_SIZE_AXIS_TITLE,
)
from app.db import get_con
from app import figure_cache


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


def build_aging_index_fig(selected_year: int, area_estat: str | None = None) -> go.Figure:
    _key = figure_cache.make_key("timeseries", selected_year, area_estat)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    national_df, pref_df, pref_label = _get_aging_index_data(area_estat)

    df_non_1945 = national_df[national_df["year"] != 1945]
    df_1945     = national_df[national_df["year"] == 1945]

    traces = []

    # ── National line (connects all years including 1945) ─────────────────────
    traces.append(go.Scatter(
        x=national_df["year"],
        y=national_df["aging_index"],
        mode="lines",
        name="全国 National",
        line=dict(color=COLOR_TEXT_MID, width=LINE_WIDTH_MAIN),
        hovertemplate="<b>%{x}</b><br>高齢化指数: <b>%{y:.1f}</b><extra>全国</extra>",
    ))

    # Regular census year dots (non-1945 only)
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
            hovertemplate=(
                "<b>1945</b><br>"
                "高齢化指数: <b>%{y:.1f}</b><br>"
                "臨時国勢調査<br>"
                "<span style='font-size:11px;color:#aaa'>Provisional Wartime Census</span>"
                "<extra></extra>"
            ),
        ))

    # ── Prefecture overlay ────────────────────────────────────────────────────
    if pref_df is not None and not pref_df.empty:
        traces.append(go.Scatter(
            x=pref_df["year"],
            y=pref_df["aging_index"],
            mode="lines+markers",
            name=pref_label,
            line=dict(color=TIMESERIES_PREF_COLOR, width=LINE_WIDTH_PREF, dash="dot"),
            marker=dict(size=4, color=TIMESERIES_PREF_COLOR),  # 4px — intentionally smaller than national dots
            hovertemplate=f"<b>%{{x}}</b><br>高齢化指数: <b>%{{y:.1f}}</b><extra>{pref_label}</extra>",
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
        font=dict(size=11, color=ACCENT_THRESHOLD),
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
        # paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CHART_PLOT_COLOR,
        legend=dict(
            orientation="h",
            x=0.01, xanchor="left",
            y=0.99, yanchor="top",
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
                font=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_AXIS_TITLE),
            ),
            zeroline=False,
            ticklabelstandoff=YAXIS_TICK_STANDOFF,
            automargin=False
        ),
    )

    figure_cache.put(_key, fig)
    return fig