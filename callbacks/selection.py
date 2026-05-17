# callbacks/selection.py
from dash import Input, Output, State, Patch, ctx, no_update

from dash_app import app
from app.aesthetics.config import MAP_ZOOM_MIN, MAP_ZOOM_MAX, MAP_REF_HEIGHT, MAP_REF_ZOOM


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


@app.callback(
    Output("map-graph", "figure", allow_duplicate=True),
    Input("map-init-zoom", "data"),
    prevent_initial_call=True,
)
def apply_initial_map_zoom(zoom):
    if zoom is None:
        return no_update
    patched = Patch()
    patched["layout"]["map"]["zoom"] = zoom
    return patched

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
