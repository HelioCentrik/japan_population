# app.py — Dash entrypoint
import dash
from dash import html, dcc, Input, Output, State, no_update, ctx
import duckdb as ddb

from app.config import (PAGE_BG, PANEL_BG, PANEL_BORDER,
                        FONT_MAIN, FONT_MAIN_COLOR, FONT_HEADER, FONT_HEADER_JPRED, FONT_HEADER_JPWHT,
                        PANEL_H)
from app.index_string import INDEX_STRING
from app.maps import build_japan_map_fig
from app.pyramid import build_pyramid_fig, get_pyramid_axis_max
from app.kpi import build_kpi_data, render_kpi_cards
from app.timeseries import build_aging_index_fig



# ── App instance ──────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="Japanese Population Dashboard")
app.index_string = INDEX_STRING
server = app.server  # expose for deployment (Gunicorn etc.)

# ── Census years for slider ───────────────────────────────────────────────────
con = ddb.connect("data/japan_population.duckdb")
years_df = con.execute(
    "SELECT DISTINCT year, era_name, era_year FROM d_years ORDER BY year"
).df()
con.close()

CENSUS_YEARS = years_df["year"].tolist()
YEAR_LABELS = {
    int(row.year): f"{row.year} ({row.era_name}{row.era_year})"
    for row in years_df.itertuples()
}


# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    style={
        "backgroundColor": PAGE_BG,
        "minHeight": "100vh",
        "padding": "0rem",
        "maxWidth": "1400px",
        "margin": "0 auto",
    },
    children=[
        dcc.Store(id="selected-prefecture", data=None),

        # Header
        html.H2(
            "日本の人口統計 Japanese Population",
            style={
                "textAlign": "center",
                "fontSize": "40px",
                "color": FONT_HEADER_JPRED,
                "marginBottom": "3rem",
            }
        ),

        html.Div(
            id="era-label",
            style={
                "textAlign": "center",
                "color": FONT_HEADER_JPWHT,
                "fontSize": "28px",
                "marginBottom": "1.25rem",
                "letterSpacing": "0.05em",
            }
        ),

        # KPI Cards
        html.Div(
            id="kpi-row",
            style={
                "display": "flex",
                "gap": "0.75rem",
                "marginBottom": "1rem",
            },
            children=render_kpi_cards(build_kpi_data(2000)),
        ),

        # Year Slider
        html.Div(
            style={
                "marginBottom": "1rem",
                "padding": "0.75rem 1rem 0.5rem 1rem",
                "backgroundColor": PANEL_BORDER,
                "borderRadius": "6px",
            },
            children=[
                dcc.Slider(
                    id="year-slider",
                    min=min(CENSUS_YEARS),
                    max=max(CENSUS_YEARS),
                    step=None,
                    value=2000,
                    marks={
                        yr: {
                            "label": str(yr),
                            "style": {
                                "color": FONT_HEADER_JPRED if yr == 1945 else FONT_MAIN_COLOR,
                                "fontSize": "13px",
                                "fontWeight": "bold" if yr == 1945 else "normal",
                            }
                        }
                        for yr in CENSUS_YEARS
                    },
                    tooltip={
                        "placement": "top",
                        "always_visible": False,
                        # "template": {str(yr): label for yr, label in YEAR_LABELS.items()},
                    },
                    included=False,
                )
            ]
        ),

        # Map + Pyramid columns
        html.Div(
            style={"marginBottom": "1rem", "display": "flex", "gap": "1rem"},
            children=[

                # Map container — the styled bezel
                html.Div(
                    style={
                        "flex": "7",
                        "height": "56vh",
                        "borderRadius": "8px",
                        "border": f"1px solid {PANEL_BORDER}",
                        "boxShadow": (
                            "inset 0 3px 14px rgba(0,0,0,0.65), "
                            "inset 0 1px 4px rgba(0,0,0,0.4)"
                        ),
                        "overflow": "hidden",
                        "backgroundColor": "#06091a",
                        "position": "relative",  # ← enables absolute child positioning
                    },
                    children=[
                        dcc.Graph(
                            id="choropleth-map",
                            figure=build_japan_map_fig(year=2000),
                            config={"displayModeBar": False, "responsive": True},
                            style={"height": "100%"},
                        ),
                        html.Button(
                            "✕ Clear",
                            id="reset-prefecture-btn",
                            style={
                                "display": "none",  # shown/hidden via callback
                                "position": "absolute",
                                "bottom": "12px",
                                "right": "12px",
                                "backgroundColor": "rgba(0,0,0,0.55)",
                                "color": FONT_MAIN_COLOR,
                                "border": f"1px solid {PANEL_BORDER}",
                                "borderRadius": "4px",
                                "padding": "4px 10px",
                                "fontSize": "12px",
                                "cursor": "pointer",
                                "zIndex": "1000",
                            }
                        ),
                    ]
                ),

                # Population Pyramid
                html.Div(
                    style={
                        "flex": "3",
                        "height": "56vh",
                        "borderRadius": "6px",
                        "border": f"1px solid {PANEL_BORDER}",
                        "boxShadow": "0 0 8px #00112266",
                        "overflow": "hidden",
                        "backgroundColor": "#06091a",
                    },
                    children=[
                        dcc.Graph(
                            id="pyramid-chart",
                            figure=build_pyramid_fig(year=2000),
                            config={"displayModeBar": False, "responsive": True},
                            style={"height": "100%"},
                        ),
                    ]
                ),
            ]
        ),

        # Time Series
        html.Div(
            style={
                "marginTop": "0rem",
                "marginBottom": "1rem",
                "height": "260px",
                "borderRadius": "6px",
                "border": f"1px solid {PANEL_BORDER}",
                "boxShadow": "0 0 8px #00112266",
                "overflow": "hidden",
                "backgroundColor": "#06091a",
            },
            children=[
                dcc.Graph(
                    id="timeseries-chart",
                    figure=build_aging_index_fig(selected_year=2000),
                    config={"displayModeBar": False, "responsive": True},
                    style={"height": "100%"},
                ),
            ]
        ),
    ]
)


# ── Callbacks ─────────────────────────────────────────────────────────────────
@app.callback(
    Output("selected-prefecture", "data"),
    Output("choropleth-map", "clickData"),
    Input("choropleth-map", "clickData"),
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
    base = {
        "position": "absolute",
        "bottom": "12px",
        "right": "12px",
        "backgroundColor": "rgba(0,0,0,0.55)",
        "color": FONT_MAIN_COLOR,
        "border": f"1px solid {PANEL_BORDER}",
        "borderRadius": "4px",
        "padding": "4px 10px",
        "fontSize": "12px",
        "cursor": "pointer",
        "zIndex": "1000",
        "display": "block" if area_estat else "none",
    }
    return base

@app.callback(
    Output("choropleth-map", "figure"),
    Output("pyramid-chart", "figure"),
    Output("era-label", "children"),
    Output("kpi-row", "children"),
    Output("timeseries-chart", "figure"),
    Input("year-slider", "value"),
    Input("selected-prefecture", "data"),
)
def update_charts(year, area_estat):
    y = int(year)
    label = YEAR_LABELS.get(y, str(y))
    axis_max = get_pyramid_axis_max(area_estat)
    kpi_data = build_kpi_data(y)
    return (
        build_japan_map_fig(year=y, area_estat=area_estat),
        build_pyramid_fig(year=y, area_estat=area_estat, axis_max=axis_max),
        label,
        render_kpi_cards(kpi_data),
        build_aging_index_fig(selected_year=y, area_estat=area_estat),
    )


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)