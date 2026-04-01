# app/app.py
import streamlit as st

from app.config import PANEL_BG, PANEL_H
from backup.ui_styles_streamlit_backup import inject_dashboard_style
from app.maps import build_japan_map_fig


# ---------- 1. Page config & dark theme ----------
st.set_page_config(
    page_title="Japanese Population Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_dashboard_style()

st.markdown("<h2 style='text-align:center; color:#aad;'>Japanese Population</h2>", unsafe_allow_html=True)
st.write("")

with st.container():
    _, center, _ = st.columns([1, 6, 1])
    with center:
        japan_map = build_japan_map_fig(year=2015)
        japan_map.update_layout(height=PANEL_H, paper_bgcolor=PANEL_BG)
        st.plotly_chart(
            japan_map,
            use_container_width=True,
            config=dict(displayModeBar=False)
        )