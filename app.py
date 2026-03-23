# app.py — Dash entrypoint
import dash
from dash import html, dcc, Input, Output
import duckdb as ddb

from app.config import PAGE_BG, PANEL_BG, PANEL_BORDER, PANEL_H
from app.maps import build_japan_map_fig



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
        "maxWidth": "1600px",
        "margin": "0 auto",
    },
    children=[
        # Header
        html.H2(
            "Japanese Population 日本の人口統計",
            style={"textAlign": "center", "color": "#aad", "marginBottom": "1.5rem"}
        ),

        # Year Slider
        html.Div(
            style={"padding": "0 2rem 1.5rem 2rem"},
            children=[
                html.Div(
                    id="era-label",
                    style={
                        "textAlign": "center",
                        "color": "#aad",
                        "fontSize": "13px",
                        "marginBottom": "0.5rem",
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
                                "color": "#d0021b" if yr == 1945 else "#aad",
                                "fontSize": "11px",
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
                        "flex": "3",
                        "height": "68vh",
                        "borderRadius": "8px",
                        "border": "1px solid #1a2440",
                        "boxShadow": (
                            "inset 0 3px 14px rgba(0,0,0,0.65), "
                            "inset 0 1px 4px rgba(0,0,0,0.4)"
                        ),
                        "overflow": "hidden",
                        "backgroundColor": "#06091a",
                    },
                    children=[
                        dcc.Graph(
                            id="choropleth-map",
                            figure=build_japan_map_fig(year=2000),
                            config={"displayModeBar": False, "responsive": True},
                            style={"height": "100%"},
                        ),
                    ]
                ),

                # Pyramid placeholder — Phase 2
                html.Div(
                    style={
                        "flex": "1",
                        "border": f"1px solid {PANEL_BORDER}",
                        "borderRadius": "6px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "color": "#445",
                        "fontSize": "14px",
                        "height": "68vh",
                    },
                    children="Population pyramid — Phase 2"
                ),

            ]
        ),
    ]
)


# ── Callbacks ─────────────────────────────────────────────────────────────────
@app.callback(
    Output("choropleth-map", "figure"),
    Output("era-label", "children"),
    Input("year-slider", "value")
)
def update_map(year):
    label = YEAR_LABELS.get(int(year), str(year))
    return build_japan_map_fig(year=int(year)), label


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)