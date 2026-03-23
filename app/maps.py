# app/maps.py ────────────────────────────────────────────────────────────────────
import json
import numpy as np
from functools import lru_cache

import geopandas as gpd
import duckdb as ddb
from plotly import graph_objects as go

from app.config import PANEL_BG


@lru_cache(maxsize=32)
def build_japan_map_fig(year=2015):
    # Load simplified prefectures
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
        colorbar_title="logₑ(Population + 1)"
    ))

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=800,
        paper_bgcolor=PANEL_BG,
        plot_bgcolor=PANEL_BG
    )

    return fig