# app/timeseries.py
from functools import lru_cache

import duckdb as ddb
import plotly.graph_objects as go

from app.config import (
    PANEL_BG, PANEL_BORDER, FONT_MAIN, FONT_MAIN_COLOR, FONT_COLOR_JPRED, FONT_COLOR_JPWHT,
    ACCENT_THRESHOLD,
    TIMESERIES_PREF_COLOR,
)

# Aging index crossed 100 between the 1995 and 2000 census years.
# We annotate at ~1997 — the midpoint, not a data point.
_CROSSOVER_YEAR = 1997


@lru_cache(maxsize=8)
def _get_aging_index_data(area_estat: str | None) -> tuple:
    """
    Returns (national_df, pref_df_or_None, pref_label_or_None).
    Cached on area_estat only — year is not a factor in the underlying data.
    """
    con = ddb.connect("data/japan_population.duckdb")

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

    con.close()
    return national_df, pref_df, pref_label


@lru_cache(maxsize=128)
def build_aging_index_fig(selected_year: int, area_estat: str | None = None) -> go.Figure:
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
        line=dict(color=FONT_MAIN_COLOR, width=2),
        hovertemplate="<b>%{x}</b><br>高齢化指数: <b>%{y:.1f}</b><extra>全国</extra>",
    ))

    # Regular census year dots (non-1945 only)
    traces.append(go.Scatter(
        x=df_non_1945["year"],
        y=df_non_1945["aging_index"],
        mode="markers",
        showlegend=False,
        marker=dict(color=FONT_MAIN_COLOR, size=5),
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
                size=11,
                color="#d0021b",
                line=dict(width=2.5, color="#d0021b"),
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
            line=dict(color=TIMESERIES_PREF_COLOR, width=1.5, dash="dot"),
            marker=dict(size=4, color=TIMESERIES_PREF_COLOR),
            hovertemplate=f"<b>%{{x}}</b><br>高齢化指数: <b>%{{y:.1f}}</b><extra>{pref_label}</extra>",
        ))

    fig = go.Figure(data=traces)

    # ── Reference line at aging index = 100 ───────────────────────────────────
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=ACCENT_THRESHOLD,
        line_width=1.2,
        opacity=0.55,
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
        line_color=FONT_MAIN_COLOR,
        line_width=1,
        line_dash="dot",
        opacity=0.35,
    )

    fig.update_layout(
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
        margin=dict(l=48, r=24, t=28, b=32),
        autosize=True,
        legend=dict(
            orientation="h",
            x=0.01, xanchor="left",
            y=0.99, yanchor="top",
            font=dict(color=FONT_MAIN_COLOR, size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            tickfont=dict(color=FONT_MAIN_COLOR, size=11),
            gridcolor="#1a2440",
            showline=False,
            dtick=10,
        ),
        yaxis=dict(
            title=dict(
                text="高齢化指数",
                font=dict(color=FONT_MAIN_COLOR, size=11),
            ),
            tickfont=dict(color=FONT_MAIN_COLOR, size=11),
            gridcolor="#1a2440",
            showline=False,
            zeroline=False,
        ),
    )

    return fig