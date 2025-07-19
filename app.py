# app/app.py
import streamlit as st
import pandas as pd
import geopandas as gpd

from app.config import PAGE_BG, PANEL_BG, PANEL_BORDER, PANEL_H


# Load prefectures
gdf = gpd.read_file("data/japan_prefectures.geojson")


# ---------- 1. Page config & dark theme ----------
st.set_page_config(
    page_title="Japanese Population",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with st.container():
    _, center, _ = st.columns([1, 6, 1])
    with center:
        pass
