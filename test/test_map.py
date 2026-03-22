# test_map.py ─ simplified and fixed for Japan
import geopandas as gpd
import json
import streamlit as st
from plotly import graph_objects as go
import duckdb as ddb

# Load simplified prefectures
prefectures = gpd.read_parquet("data/japan_prefectures_simplified.parquet").to_crs(epsg=4326)

# Add 5-digit code if not already there
if "prefecture_code" not in prefectures.columns:
    prefectures["prefecture_code"] = prefectures["id"].apply(lambda x: str(x * 1000).zfill(5))

# Load census data
con = ddb.connect("data/japan_population.duckdb")
df = con.execute("""
    SELECT area_estat, population
    FROM v_census
    WHERE year = 2015 AND sex = 'total'
""").df()
con.close()

# Merge by code
prefectures = prefectures.rename(columns={"prefecture_code": "area_estat"})
prefectures = prefectures.merge(df, on="area_estat", how="left")

# Convert to GeoJSON
prefectures_js = json.loads(prefectures.to_json())

# Build map
fig = go.Figure(go.Choropleth(
    geojson=prefectures_js,
    locations=prefectures["area_estat"],
    z=prefectures["population"],
    featureidkey="properties.area_estat",
    colorscale="YlGnBu",
    marker_line_width=0.5,
    marker_line_color="black",
    colorbar_title="Population"
))

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=800)

# Display in Streamlit
st.title("Japanese Prefectural Population")
st.plotly_chart(fig, use_container_width=True)
