# callbacks/ui.py
from pathlib import Path

from dash import html, dcc, Input, Output, State, Patch, ctx, no_update

from dash_app import app
from app.aesthetics.config import TS_VIEW_TFR
from app.state import is_ready



_GEMINI_ICON = html.Img(
    src="/assets/gemini-color.png",
    style={"width": "28px", "height": "28px"},
)
_INFO_ICON = html.Img(
    src=(
        "data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E"
        "%3Ccircle cx='12' cy='12' r='11' stroke='white' stroke-width='2' fill='none'/%3E"
        "%3Ctext x='12' y='17' text-anchor='middle' font-family='Georgia%2C serif' "
        "font-style='italic' font-size='16' fill='white'%3Ei%3C/text%3E"
        "%3C/svg%3E"
    ),
    className="ai-btn-info-icon",
)

PROJECT_MD = Path("PROJECT.md").read_text(encoding="utf-8")


@app.callback(
    Output("loading-overlay", "className"),
    Output("ready-poll", "disabled"),
    Output("charts-ready-trigger", "data"),   # ← new
    Input("ready-poll", "n_intervals"),
)
def dismiss_loading_overlay(n):
    if is_ready():
        return "loading-overlay hidden", True, True
    return "loading-overlay", False, no_update


@app.callback(
    Output("panel-mode", "data"),
    Output("last-panel-mode", "data"),
    Input("side-panel-toggle-btn", "n_clicks"),
    Input("side-panel-ai-btn", "n_clicks"),
    State("panel-mode", "data"),
    State("last-panel-mode", "data"),
    prevent_initial_call=True,
)
def update_panel_mode(toggle_clicks, ai_clicks, current_mode, last_mode):
    trigger = ctx.triggered_id
    if trigger == "side-panel-toggle-btn":
        if current_mode is not None:
            return None, no_update          # collapse — remember last mode
        return last_mode, no_update         # reopen to last mode
    if trigger == "side-panel-ai-btn":
        new_mode = "project" if current_mode == "ai" else "ai"
        return new_mode, new_mode           # swap content + update last
    return no_update, no_update


@app.callback(
    Output("side-panel", "className"),
    Output("side-panel-toggle-btn", "children"),
    Output("side-panel-toggle-btn", "className"),
    Output("side-panel-ai-btn", "children"),
    Output("ai-panel", "style"),
    Output("side-panel-inner", "className"),
    Input("panel-mode", "data"),
)
def update_panel_state(mode):
    panel_cls  = "side-panel open" if mode is not None else "side-panel"
    chevron    = "›" if mode is not None else "‹"
    toggle_cls = "side-panel-btn active" if mode == "project" else "side-panel-btn"
    ai_icon    = _INFO_ICON if mode == "ai" else _GEMINI_ICON
    ai_style   = {"display": "flex"} if mode == "ai" else {"display": "none"}
    inner_cls  = "side-panel-inner ai-mode" if mode == "ai" else "side-panel-inner"
    return panel_cls, chevron, toggle_cls, ai_icon, ai_style, inner_cls


@app.callback(
    Output("side-panel-content", "children"),
    Input("panel-mode", "data"),
)
def render_panel_content(mode):
    if mode == "project":
        return dcc.Markdown(PROJECT_MD, link_target="_blank")
    return None


@app.callback(
    Output("show-projections", "data"),
    Output("proj-toggle-btn", "className"),
    Input("proj-toggle-btn", "n_clicks"),
    State("show-projections", "data"),
    prevent_initial_call=True,
)
def toggle_projections_store(n_clicks, currently_showing):
    new_val = not currently_showing
    cls     = "proj-toggle-btn active" if new_val else "proj-toggle-btn"
    return new_val, cls


@app.callback(
    Output("timeseries-chart", "figure", allow_duplicate=True),
    Input("show-projections", "data"),
    State("timeseries-chart", "figure"),
    State("ts-view-selector", "value"),
    prevent_initial_call=True,
)
def toggle_projection_traces(show, figure, ts_view):
    if ts_view == TS_VIEW_TFR:
        return no_update

    p = Patch()
    for i, trace in enumerate(figure["data"]):
        if trace.get("uid", "").startswith("proj_"):
            p["data"][i]["visible"] = show

    return p
