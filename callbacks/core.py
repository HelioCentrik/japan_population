# callbacks/core.py
from dash import Input, Output, Patch, State, ctx, no_update
import plotly.graph_objects as go

from dash_app import app
from startup import CENSUS_YEARS, YEAR_LABELS, PREFECTURE_LOOKUP
from app.aesthetics.config import (
    MAP_METRIC_DEFAULT, get_scaled_fonts, TS_VIEW_TFR,
)
from app.viz.maps import build_japan_map_fig
from app.viz.pyramid import build_pyramid_fig, get_pyramid_axis_max
from app.viz.timeseries import build_ts_pop_share_fig, build_ts_population_fig, build_ts_tfr_fig
from app.viz.kpi import build_kpi_data, render_kpi_cards



@app.callback(
    Output("map-graph", "figure"),
    Output("pyramid-chart", "figure"),
    Output("kpi-row", "children"),
    Output("timeseries-chart", "figure"),
    Input("year-slider", "value"),
    Input("selected-prefecture", "data"),
    Input("metric-selector", "value"),
    Input("ts-view-selector", "value"),
    Input("charts-ready-trigger", "data"),
    State("show-projections", "data"),
    prevent_initial_call=True,
)
def update_charts(year, area_estat, metric, ts_view, charts_ready, show_projections):
    if not charts_ready:
        return no_update, no_update, no_update, no_update
    y = int(year)
    year_part = YEAR_LABELS.get(y, str(y))
    if area_estat and area_estat in PREFECTURE_LOOKUP:
        name_ja, name_en = PREFECTURE_LOOKUP[area_estat]
        label = f"{year_part}  ｜  {name_ja}  {name_en}"
    else:
        label = year_part
    axis_max = get_pyramid_axis_max(area_estat)
    kpi_data = build_kpi_data(y)

    trigger = ctx.triggered_id

    if trigger == "selected-prefecture":
        patched = Patch()
        patched["data"][2]["locations"] = [area_estat] if area_estat else []
        patched["data"][2]["z"] = [1] if area_estat else []
        map_fig = patched
    elif trigger is None or trigger == "charts-ready-trigger":
        # Initial render (warm cache trigger=None) or post-prewarm (cold cache).
        # Base figure is {} — can't patch, must return full figure.
        map_fig = build_japan_map_fig(year=y, metric=metric)
    else:
        fig = build_japan_map_fig(year=y, metric=metric)
        fd = fig.to_dict()
        patched = Patch()
        patched["data"][0]["z"] = fd["data"][0]["z"]
        patched["data"][0]["customdata"] = fd["data"][0]["customdata"]
        patched["data"][0]["colorscale"] = fd["data"][0]["colorscale"]
        patched["data"][0]["zmin"] = fd["data"][0]["zmin"]
        patched["data"][0]["zmax"] = fd["data"][0]["zmax"]
        patched["data"][0]["colorbar"] = fd["data"][0]["colorbar"]
        patched["data"][1]["locations"] = fd["data"][1]["locations"]
        patched["data"][1]["z"] = fd["data"][1]["z"]
        map_fig = patched

    if ts_view == "pop_share":
        ts_fig = build_ts_pop_share_fig(selected_year=y, area_estat=area_estat)
    elif ts_view == "population":
        ts_fig = build_ts_population_fig(selected_year=y, area_estat=area_estat)
    else:
        ts_fig = build_ts_tfr_fig(selected_year=y, area_estat=area_estat)

    if not show_projections and ts_view != TS_VIEW_TFR:
        fig_dict = ts_fig.to_dict()
        for i, trace_dict in enumerate(fig_dict["data"]):
            if trace_dict.get("uid", "").startswith("proj_"):
                fig_dict["data"][i]["visible"] = False
        ts_fig = go.Figure(fig_dict)

    return (
        map_fig,
        build_pyramid_fig(year=y, area_estat=area_estat, axis_max=axis_max),
        render_kpi_cards(kpi_data, year_part),
        ts_fig,
    )


@app.callback(
    Output("map-graph", "figure", allow_duplicate=True),
    Input("font-tier", "data"),
    prevent_initial_call=True,
)
def patch_map_fonts(tier):
    fonts = get_scaled_fonts(tier)
    p = Patch()
    p["data"][0]["colorbar"]["tickfont"]["size"]    = fonts["colorbar_tick"]
    p["data"][0]["colorbar"]["title"]["font"]["size"] = fonts["colorbar"]
    return p


@app.callback(
    Output("pyramid-chart", "figure", allow_duplicate=True),
    Input("font-tier", "data"),
    prevent_initial_call=True,
)
def patch_pyramid_fonts(tier):
    fonts = get_scaled_fonts(tier)
    p = Patch()
    p["layout"]["xaxis"]["tickfont"]["size"]        = fonts["axis_tick"]
    p["layout"]["yaxis"]["tickfont"]["size"]        = fonts["axis_tick"]
    p["layout"]["yaxis"]["title"]["font"]["size"]   = fonts["axis_title"]
    return p


@app.callback(
    Output("timeseries-chart", "figure", allow_duplicate=True),
    Input("font-tier", "data"),
    prevent_initial_call=True,
)
def patch_timeseries_fonts(tier):
    fonts = get_scaled_fonts(tier)
    p = Patch()
    p["layout"]["xaxis"]["tickfont"]["size"]        = fonts["axis_tick"]
    p["layout"]["yaxis"]["tickfont"]["size"]        = fonts["axis_tick"]
    p["layout"]["yaxis"]["title"]["font"]["size"]   = fonts["axis_title"]
    p["layout"]["legend"]["font"]["size"]           = fonts["legend"]
    return p
