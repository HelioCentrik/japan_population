# app.py — Dash entrypoint
import dash
from dash import html, dcc
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
    style={"backgroundColor": PAGE_BG, "minHeight": "100vh", "padding": "1.5rem"},
    children=[

        # Header
        html.H2(
            "Japanese Population 日本の人口統計",
            style={"textAlign": "center", "color": "#aad", "marginBottom": "1rem"}
        ),

        # Map (placeholder for pyramid col later)
        html.Div(
            style={"display": "flex", "gap": "1rem"},
            children=[
                dcc.Graph(
                    id="choropleth-map",
                    figure=build_japan_map_fig(year=2015),
                    config={"displayModeBar": False},
                    style={"flex": "3"}
                ),
            ]
        ),

    ]
)

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)