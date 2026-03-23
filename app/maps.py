# app/maps.py ────────────────────────────────────────────────────────────────────
import json
import numpy as np
from functools import lru_cache

import geopandas as gpd
import duckdb as ddb
from plotly import graph_objects as go

from app.config import PANEL_BG, PAGE_BG, MAP_GEO


# @lru_cache(maxsize=32)
def build_japan_map_fig(year=2015):
    prefectures = gpd.read_parquet("data/japan_prefectures_simplified.parquet").to_crs(epsg=4326)

    if "prefecture_code" not in prefectures.columns:
        prefectures["prefecture_code"] = prefectures["id"].apply(lambda x: str(x * 1000).zfill(5))

    con = ddb.connect("data/japan_population.duckdb")
    df = con.execute(f"""
        SELECT area_estat, population
        FROM v_census
        WHERE year = {year} AND sex = 'total' AND age_group = 'Total' AND area_level = 2
    """).df()
    con.close()

    prefectures = prefectures.rename(columns={"prefecture_code": "area_estat"})
    prefectures = prefectures.merge(df, on="area_estat", how="left")

    prefectures_js = json.loads(prefectures.to_json())
    prefectures["log_population"] = np.log1p(prefectures["population"])

    fig = go.Figure(go.Choropleth(
        geojson=prefectures_js,
        locations=prefectures["area_estat"],
        z=prefectures["log_population"],
        featureidkey="properties.area_estat",
        colorscale="YlGnBu",
        marker_line_width=0.5,
        marker_line_color="black",
        colorbar=dict(
            title=dict(
                text="logₑ(Pop + 1)",
                side="right",
                font=dict(size=10, color="#aad")
            ),
            x=0.01,
            xanchor="left",
            thickness=12,
            len=0.65,
            tickfont=dict(size=10, color="#aad"),
        )
    ))

    fig.update_geos(
        fitbounds="locations",
        visible=True,
        # showcountries=False,
        showcoastlines=False,
        # showland=False,
        landcolor=MAP_GEO.get("land_color"),
        # showocean=True,
        # oceancolor=PAGE_BG,
        # showlakes=False,
        # showrivers=False,
        showframe=False,
        bgcolor=MAP_GEO.get("bg_color"),
    )
    fig.update_layout(
        margin=dict(l=80, r=0, t=0, b=0),
        autosize=True,
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG,
    )


    return fig