# callbacks/selection.py
from dash import Input, Output, State, Patch, ctx, no_update

from dash_app import app
from startup import CENSUS_YEARS
from app.aesthetics.config import (
    MAP_ZOOM_MIN, MAP_ZOOM_MAX, MAP_REF_HEIGHT, MAP_REF_ZOOM,
    MAP_METRICS, COLOR_PRIMARY, COLOR_TEXT_MID, FONT_SIZE_AXIS_TITLE,
)



app.clientside_callback(
    f"""
    function(n) {{
        const panel = document.querySelector('.map-panel');
        if (!panel) return window.dash_clientside.no_update;
        const h = panel.getBoundingClientRect().height;
        if (h < 10) return window.dash_clientside.no_update;
        const zoom = Math.min({MAP_ZOOM_MAX}, Math.max({MAP_ZOOM_MIN},
            {MAP_REF_ZOOM} + Math.log2(h / {MAP_REF_HEIGHT})));
        return zoom;
    }}
    """,
    Output("map-init-zoom", "data"),
    Input("zoom-init", "n_intervals"),
    prevent_initial_call=True,
)


app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        if (window.refitMap) window.refitMap();
        return window.dash_clientside.no_update;
    }
    """,
    Output("map-init-zoom", "data", allow_duplicate=True),
    Input("map-resize-btn", "n_clicks"),
    prevent_initial_call=True,
)


app.clientside_callback(
    """
    function(hoverData) {
        if (!hoverData?.points?.length) return window.dash_clientside.no_update;
        var raw = hoverData.points[0].bbox;
        if (!raw) return window.dash_clientside.no_update;
        var outer     = document.querySelector('.dashboard-outer');
        var chartEl   = document.querySelector('#map-graph');
        var z         = parseFloat(outer?.style?.zoom) || 1.0;
        var rect      = outer.getBoundingClientRect();
        var chartRect = chartEl.getBoundingClientRect();
        var c         = window.TOOLTIP_CONFIG.map;
        var out = {
            x0: (chartRect.left + raw.x0 - rect.left) / z + c.x,
            x1: (chartRect.left + raw.x1 - rect.left) / z + c.x,
            y0: (chartRect.top  + raw.y0 - rect.top)  / z - c.y,
            y1: (chartRect.top  + raw.y1 - rect.top)  / z - c.y,
        };
        window.__tooltipDebug = { chart: 'map', raw, z, rect, chartRect, out,
            mouse: {x: window.__lastMouseX, y: window.__lastMouseY} };
        return out;
    }
    """,
    Output("map-tooltip", "bbox"),
    Input("map-graph", "hoverData"),
)

app.clientside_callback(
    """
    function(hoverData) {
        if (!hoverData?.points?.length) return window.dash_clientside.no_update;
        var raw = hoverData.points[0].bbox;
        if (!raw) return window.dash_clientside.no_update;
        var outer     = document.querySelector('.dashboard-outer');
        var chartEl   = document.querySelector('#pyramid-chart');
        var z         = parseFloat(outer?.style?.zoom) || 1.0;
        var rect      = outer.getBoundingClientRect();
        var chartRect = chartEl.getBoundingClientRect();
        var c         = window.TOOLTIP_CONFIG.pyramid;
        var xOff      = (hoverData.points[0].x || 0) < 0 ? -c.x : c.x;
        var out = {
            x0: (chartRect.left + raw.x0 - rect.left) / z + xOff,
            x1: (chartRect.left + raw.x1 - rect.left) / z + xOff,
            y0: (chartRect.top  + raw.y0 - rect.top)  / z - c.y,
            y1: (chartRect.top  + raw.y1 - rect.top)  / z - c.y,
        };
        window.__tooltipDebug = { chart: 'pyramid', raw, z, rect, chartRect, out,
            mouse: {x: window.__lastMouseX, y: window.__lastMouseY} };
        return out;
    }
    """,
    Output("pyramid-tooltip", "bbox"),
    Input("pyramid-chart", "hoverData"),
)

app.clientside_callback(
    """
    function(hoverData) {
        if (!hoverData?.points?.length) return window.dash_clientside.no_update;
        var raw = hoverData.points[0].bbox;
        if (!raw) return window.dash_clientside.no_update;
        var outer     = document.querySelector('.dashboard-outer');
        var chartEl   = document.querySelector('#timeseries-chart');
        var z         = parseFloat(outer?.style?.zoom) || 1.0;
        var rect      = outer.getBoundingClientRect();
        var chartRect = chartEl.getBoundingClientRect();
        var c         = window.TOOLTIP_CONFIG.ts;
        var out = {
            x0: (chartRect.left + raw.x0 - rect.left) / z - c.x,
            x1: (chartRect.left + raw.x1 - rect.left) / z - c.x,
            y0: (chartRect.top  + raw.y0 - rect.top)  / z - c.y,
            y1: (chartRect.top  + raw.y1 - rect.top)  / z - c.y,
        };
        window.__tooltipDebug = { chart: 'ts', raw, z, rect, chartRect, out,
            mouse: {x: window.__lastMouseX, y: window.__lastMouseY} };
        return out;
    }
    """,
    Output("timeseries-tooltip", "bbox"),
    Input("timeseries-chart", "hoverData"),
)


@app.callback(
    Output("selected-prefecture", "data"),
    Output("map-graph", "clickData"),
    Input("map-graph", "clickData"),
    Input("reset-prefecture-btn", "n_clicks"),
    State("selected-prefecture", "data"),
    prevent_initial_call=True,
)
def update_selected_prefecture(click_data, reset_clicks, current_area):
    if ctx.triggered_id == "reset-prefecture-btn":
        return None, None
    if click_data is None:
        return no_update, None
    points = click_data.get("points", [])
    if not points or "location" not in points[0]:
        return None, None
    clicked_area = points[0]["location"]
    new_area = None if clicked_area == current_area else clicked_area
    return new_area, None

@app.callback(
    Output("reset-prefecture-btn", "style"),
    Input("selected-prefecture", "data"),
)
def toggle_reset_button(area_estat):
    return {"display": "block" if area_estat else "none"}


@app.callback(
    Output("year-slider", "value", allow_duplicate=True),
    Output("year-slider", "min"),
    Output("year-slider", "max"),
    Output("year-slider", "marks"),
    Input("metric-selector", "value"),
    State("year-slider", "value"),
    prevent_initial_call=True,
)
def snap_year_to_metric_coverage(metric, current_year):
    """
    On metric change: constrains the slider to the metric's valid census years.
    Updates min, max, and marks so the slider physically can't land outside
    coverage. Value snaps to nearest valid year if needed.
    """
    meta     = MAP_METRICS.get(metric, {})
    min_year = meta.get("min_year") or CENSUS_YEARS[0]
    max_year = meta.get("max_year") or CENSUS_YEARS[-1]

    valid_years = [yr for yr in CENSUS_YEARS if min_year <= yr <= max_year]

    if current_year < valid_years[0]:
        new_value = valid_years[0]
    elif current_year > valid_years[-1]:
        new_value = valid_years[-1]
    else:
        new_value = no_update

    new_marks = {
        yr: {
            "label": str(yr),
            "style": {
                "color":      COLOR_PRIMARY if yr == 1945 else COLOR_TEXT_MID,
                "fontSize":   f"{FONT_SIZE_AXIS_TITLE}px",
                "fontWeight": "bold" if yr == 1945 else "normal",
            },
        }
        for yr in valid_years
    }

    return new_value, valid_years[0], valid_years[-1], new_marks