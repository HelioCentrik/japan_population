# app.py — Dash entrypoint
import dash
from dash import html, dcc, Input, Output, State, no_update, ctx
import duckdb as ddb

from app.config import PAGE_BG, PANEL_BG, PANEL_BORDER, FONT_MAIN, PANEL_H
from app.maps import build_japan_map_fig
from app.pyramid import build_pyramid_fig



# ── App instance ──────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="Japanese Population Dashboard")
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
        "padding": "1.5rem",
        "maxWidth": "1400px",
        "margin": "0 auto",
    },
    children=[
        dcc.Store(id="selected-prefecture", data=None),

        # Header
        html.H2(
            "Japanese Population 日本の人口統計",
            style={"textAlign": "center", "fontSize": "32px", "color": FONT_MAIN, "marginBottom": "3.5rem"}
        ),

        # Year Slider
        html.Div(
            style={"padding": "0 2rem 1.5rem 2rem"},
            children=[
                html.Div(
                    id="era-label",
                    style={
                        "textAlign": "center",
                        "color": FONT_MAIN,
                        "fontSize": "22px",
                        "marginBottom": "2.5rem",
                        "letterSpacing": "0.05em",
                    }
                ),
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
                                "color": "#d0021b" if yr == 1945 else FONT_MAIN,
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
            style={"display": "flex", "gap": "1rem"},
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
                                "color": FONT_MAIN,
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
        "color": FONT_MAIN,
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
    Input("year-slider", "value"),
    Input("selected-prefecture", "data"),
)
def update_charts(year, area_estat):
    y = int(year)
    label = YEAR_LABELS.get(y, str(y))
    return build_japan_map_fig(year=y, area_estat=area_estat), build_pyramid_fig(year=y, area_estat=area_estat), label


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)