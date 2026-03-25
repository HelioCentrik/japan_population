# app/maps.py ────────────────────────────────────────────────────────────────────
import json
import numpy as np
from functools import lru_cache

import geopandas as gpd
import duckdb as ddb
from plotly import graph_objects as go

from app.config import PANEL_BG, PAGE_BG, FONT_MAIN, MAP_GEO


# @lru_cache(maxsize=32)
def build_japan_map_fig(year=2015):
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

    # Pre-format delta strings so NULLs render cleanly in the hovertemplate
    def fmt_pop_delta(row):
        if row["pop_delta"] is None or row["pop_delta"] != row["pop_delta"]:  # NaN check
            return "First census"
        sign = "▲" if row["pop_delta"] >= 0 else "▼"
        return f"{sign} {abs(int(row['pop_delta'])):,}  since {int(row['prev_year'])} ({int(row['year_gap'])} yrs)"

    def fmt_aging_delta(row):
        if row["aging_index_delta"] is None or row["aging_index_delta"] != row["aging_index_delta"]:
            return "First census"
        sign = "▲" if row["aging_index_delta"] >= 0 else "▼"
        return f"{sign} {abs(row['aging_index_delta']):.1f}  since {int(row['prev_year'])} ({int(row['year_gap'])} yrs)"

    prefectures["pop_delta_str"] = prefectures.apply(fmt_pop_delta, axis=1)
    prefectures["aging_index_delta_str"] = prefectures.apply(fmt_aging_delta, axis=1)

    prefectures_js = json.loads(prefectures.to_json())
    prefectures["log_population"] = np.log1p(prefectures["population"])

    fig = go.Figure(go.Choroplethmapbox(
        geojson=prefectures_js,
        locations=prefectures["area_estat"],
        z=prefectures["log_population"],
        featureidkey="properties.area_estat",
        colorscale="YlGnBu",
        marker_line_width=0.8,
        marker_line_color=MAP_GEO.get("line_color"),
        customdata=prefectures[[
            "prefecture_name_ja",  # customdata[0]
            "prefecture_name",  # customdata[1]
            "population",  # customdata[2]
            "aging_index",  # customdata[3]
            "pop_delta_str",  # customdata[4]
            "aging_index_delta_str"  # customdata[5]
        ]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b>  %{customdata[1]}<br>"
            "Population:    <b>%{customdata[2]:,.0f}</b><br>"
            "Aging index:   <b>%{customdata[3]:.1f}</b><br>"
            "<br>"
            "Pop change:    %{customdata[4]}<br>"
            "Aging change:  %{customdata[5]}<br>"
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
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",   # no token needed, dark ocean built in
            center=dict(lat=35.5, lon=135.5),
            zoom=4.2,                   # tune this — 4–5 is the right range for Japan
        ),
        margin=dict(l=4, r=5, t=4, b=4),
        autosize=True,
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
    )

    # fig.update_geos(
    #     visible=True,
    #     # fitbounds="locations",
    #     # lataxis_range=[24, 46],         # Okinawa → Hokkaido
    #     # lonaxis_range=[122, 148],       # west Kyushu → east Hokkaido
    #     projection_type="equirectangular",
    #     center=dict(lat=35, lon=136),   # center of Japan mainland — tune lat to shift N/S, lon for E/W
    #     projection_scale=7.5,           # tune this: higher = more zoomed in, lower = more zoomed out
    #     bgcolor=MAP_GEO.get("bg_color"),
    #     # showcountries=False,
    #     showcoastlines=False,
    #     # showland=False,
    #     landcolor=MAP_GEO.get("land_color"),
    #     # showocean=True,
    #     # oceancolor=PAGE_BG,
    #     showlakes=True,
    #     lakecolor=MAP_GEO.get("bg_color"),
    #     # showrivers=False,
    #     showframe=False,
    # )
    # fig.update_layout(
    #     margin=dict(l=6, r=7, t=6, b=6),
    #     autosize=True,
    #     paper_bgcolor=PANEL_BG,
    #     plot_bgcolor=PANEL_BG,
    #     geo=dict(
    #         domain=dict(x=[0, 1], y=[0, 1])  # geo subplot fills the entire figure area
    #     ),
    # )


    return fig