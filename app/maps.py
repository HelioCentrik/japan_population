# app/maps.py ────────────────────────────────────────────────────────────────────
import json
import numpy as np
from functools import lru_cache

import geopandas as gpd
import duckdb as ddb
from plotly import graph_objects as go

from app.config import (
    PANEL_BG, FONT_MAIN, MAP_GEO,
    MAP_HIGHLIGHT_LINE_COLOR, MAP_HIGHLIGHT_LINE_WIDTH, MAP_HIGHLIGHT_FILL,
)


@lru_cache(maxsize=64)
def build_japan_map_fig(year: int = 2015, area_estat: str | None = None) -> go.Figure:
    prefectures = gpd.read_parquet("data/japan_prefectures_simplified.parquet").to_crs(epsg=4326)

    if "prefecture_code" not in prefectures.columns:
        prefectures["prefecture_code"] = prefectures["id"].apply(lambda x: str(x * 1000).zfill(5))

    con = ddb.connect("data/japan_population.duckdb")
    df = con.execute(f"""
        SELECT
            area_estat,
            population,
            aging_index,
            pop_delta,
            aging_index_delta,
            prev_year,
            year_gap
        FROM v_map_metrics
        WHERE year = {year}
    """).df()
    con.close()

    prefectures = prefectures.rename(columns={"prefecture_code": "area_estat"})
    prefectures = prefectures.merge(df, on="area_estat", how="left")

    def fmt_pop_delta(row):
        if row["pop_delta"] is None or row["pop_delta"] != row["pop_delta"]:
            return "First census"
        sign = "▲" if row["pop_delta"] >= 0 else "▼"
        return f"{sign} {abs(int(row['pop_delta'])):,}  since {int(row['prev_year'])} ({int(row['year_gap'])} yrs)"

    def fmt_aging_delta(row):
        if row["aging_index_delta"] is None or row["aging_index_delta"] != row["aging_index_delta"]:
            return "First census"
        sign = "▲" if row["aging_index_delta"] >= 0 else "▼"
        return f"{sign} {abs(row['aging_index_delta']):.1f}  since {int(row['prev_year'])} ({int(row['year_gap'])} yrs)"

    prefectures["pop_delta_str"]         = prefectures.apply(fmt_pop_delta, axis=1)
    prefectures["aging_index_delta_str"] = prefectures.apply(fmt_aging_delta, axis=1)
    prefectures["log_population"]        = np.log1p(prefectures["population"])

    prefectures_js = json.loads(prefectures.to_json())

    # ── Base choropleth trace ─────────────────────────────────────────────────
    base_trace = go.Choroplethmapbox(
        geojson=prefectures_js,
        locations=prefectures["area_estat"],
        z=prefectures["log_population"],
        featureidkey="properties.area_estat",
        colorscale="plasma_r",
        marker_line_width=0.8,
        marker_line_color=MAP_GEO.get("line_color"),
        customdata=prefectures[[
            "prefecture_name_ja",        # customdata[0]
            "prefecture_name",           # customdata[1]
            "population",                # customdata[2]
            "aging_index",               # customdata[3]
            "pop_delta_str",             # customdata[4]
            "aging_index_delta_str"      # customdata[5]
        ]].values,
        hovertemplate=(
            "<b style='font-size:16px'>%{customdata[0]}  <span style='font-size:18px'>%{customdata[1]}</span></b><br>"
            "<br>"
            "Population:    <b>%{customdata[2]:,.0f}</b><br>"
            "Aging index:   <b>%{customdata[3]:.1f}</b><br>"
            "Pop change:    %{customdata[4]}<br>"
            "Aging change:  %{customdata[5]}<br>"
            "<span style='color:#445566'>──────────────────</span><br>"
            "<span style='color:#667799;font-size:11px'>再選択でクリア / Reselect to clear</span><br>"
            "<extra></extra>"
        ),
        colorbar=dict(
            title=dict(
                text="logₑ(Pop + 1)",
                side="right",
                font=dict(size=12, color=FONT_MAIN)
            ),
            x=0.02,
            xanchor="left",
            thickness=16,
            len=0.8,
            tickfont=dict(size=14, color=FONT_MAIN),
        )
    )

    traces = [base_trace]

    # ── Highlight trace — only when a prefecture is selected ─────────────────
    # A second Choroplethmapbox layered on top of the base. marker_line applies
    # uniformly across all features in a trace, so we can't style one feature
    # in the base trace — a separate single-feature trace is the only clean option.
    if area_estat is not None:
        selected = prefectures[prefectures["area_estat"] == area_estat]
        if not selected.empty:
            selected_js = json.loads(selected.to_json())
            highlight_trace = go.Choroplethmapbox(
                geojson=selected_js,
                locations=selected["area_estat"],
                z=[1],                          # dummy z — colorscale is a flat color
                featureidkey="properties.area_estat",
                colorscale=[[0, MAP_HIGHLIGHT_FILL], [1, MAP_HIGHLIGHT_FILL]],
                showscale=False,
                marker_line_width=MAP_HIGHLIGHT_LINE_WIDTH,
                marker_line_color=MAP_HIGHLIGHT_LINE_COLOR,
                hoverinfo="skip",               # base trace handles hover
            )
            traces.append(highlight_trace)

    fig = go.Figure(data=traces)

    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=35.5, lon=135.5),
            zoom=3.9,
        ),
        margin=dict(l=6, r=7, t=6, b=6),
        autosize=True,
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
    )

    return fig