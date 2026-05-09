# wsgi.py — Dash entrypoint
import sys
sys.path.insert(0, ".")
from pathlib import Path


import dash
from dash import Dash, html, dcc, Input, Output, State, ctx, no_update, Patch
import duckdb as ddb

from app.config import (PAGE_BG, PANEL_BG, PANEL_BORDER,
                        COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WARNING, COLOR_TEXT_MID, COLOR_TEXT_HI,
                        TOOLTIP_TEXT_MID, TOOLTIP_TEXT_HI,
                        HEADER_TITLE_JA, HEADER_TITLE_EN,
                        FONT_SIZE_AXIS_TITLE,
                        PLAY_INTERVAL_MS, LAYOUT_GAP,
                        MAP_METRICS, MAP_METRIC_DEFAULT, MAP_TOOLTIP_OFFSET_X, MAP_TOOLTIP_OFFSET_Y,
                        MAP_ZOOM_MIN, MAP_ZOOM_MAX, MAP_REF_HEIGHT, MAP_REF_ZOOM,
                        PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
                        PYRAMID_TOOLTIP_OFFSET_X, PYRAMID_TOOLTIP_OFFSET_Y, PYRAMID_GRAPH_TOP_OFFSET,
                        TIMESERIES_PREF_COLOR, TS_VIEWS, TS_VIEW_DEFAULT, TS_TOOLTIP_OFFSET_X, TS_TOOLTIP_OFFSET_Y,
                        ACCENT_DANKAI, ACCENT_DANKAI_JR,
                        MAX_YEAR, OKINAWA_AREA_ESTAT,
                        get_scaled_fonts, )
from app.index_string import INDEX_STRING
from app.kpi import build_kpi_data, render_kpi_cards
from app.maps import build_japan_map_fig
from app.pyramid import build_pyramid_fig, get_pyramid_axis_max
from app.timeseries import build_ts_population_fig, build_ts_aging_index_fig, build_ts_pop_share_fig
from app.plotly_template import register_plotly_template
from app import figure_cache



# ── App instance ──────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="少子高齢化 A Century of Japan's Population")
app.index_string = INDEX_STRING
register_plotly_template()
server = app.server  # expose for deployment (Gunicorn etc.)


# ── Census years for slider ───────────────────────────────────────────────────
con = ddb.connect("data/japan_population.duckdb")
years_df = con.execute(
    "SELECT DISTINCT year, era_name, era_year FROM d_years ORDER BY year"
).df()
PREFECTURE_LOOKUP = {
    row.area_estat: (row.prefecture_name_ja, row.prefecture_name)
    for row in con.execute(
        "SELECT area_estat, prefecture_name_ja, prefecture_name FROM d_prefectures WHERE level = 2"
    ).df().itertuples()
}
con.close()

CENSUS_YEARS = years_df["year"].tolist()
YEAR_LABELS = {
    int(row.year): f"{row.year} ({row.era_name}{row.era_year})"
    for row in years_df.itertuples()
}
YEAR_MIN = min(CENSUS_YEARS)
PLAYBACK_YEARS = [yr for yr in CENSUS_YEARS]


# ── Cache pre-warm ────────────────────────────────────────────────────────────
_prewarm_axis_max = get_pyramid_axis_max(None)

if figure_cache.is_valid():
    print("Loading figure cache from disk...")
    figure_cache.load_all()
    for _yr in CENSUS_YEARS:
        build_kpi_data(_yr)
    print(f"  Disk cache loaded — {len(CENSUS_YEARS)} years ready.")
else:
    print("Building figure cache...")
    figure_cache.clear()
    for _yr in CENSUS_YEARS:
        build_kpi_data(_yr)
        fig = build_japan_map_fig(year=_yr, metric=MAP_METRIC_DEFAULT)
        figure_cache.save(figure_cache.make_key("map", _yr, MAP_METRIC_DEFAULT), fig)
        fig = build_pyramid_fig(year=_yr, area_estat=None, axis_max=_prewarm_axis_max)
        figure_cache.save(figure_cache.make_key("pyramid", _yr, None, _prewarm_axis_max), fig)
        fig = build_ts_population_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("population", _yr, None), fig)
        fig = build_ts_aging_index_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("timeseries", _yr, None), fig)
        fig = build_ts_pop_share_fig(selected_year=_yr, area_estat=None)
        figure_cache.save(figure_cache.make_key("pop_share", _yr, None), fig)
    figure_cache.write_fingerprint()
    print(f"  Cache built and saved — {len(CENSUS_YEARS)} years × 3 builders.")


# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    className="dashboard-outer",
    style={
        "backgroundColor": PAGE_BG,
        "maxWidth": "clamp(800px,66.67vw, 1800px)",
        "margin": "0 auto",
        "overflow-y": "visible",
    },
    children=[
        dcc.Store(id="selected-prefecture", data=None),
        dcc.Store(id="resume-year", data=None),
        dcc.Store(id="map-init-zoom", data=None),
        dcc.Store(id="font-tier", data="lg"),
        # dcc.Interval(id="resize-poll", interval=200, n_intervals=0),
        dcc.Interval(
            id="zoom-init",
            interval=200,    # fires once 200ms after page load — enough for flex layout to settle
            max_intervals=1,
            n_intervals=0,
        ),

        dcc.Interval(
            id="play-interval",
            interval=PLAY_INTERVAL_MS,
            disabled=True,  # starts paused; callbacks toggle this
            n_intervals=0,
        ),


        # ── Header ────────────────────────
        html.Div(
            className="dashboard-header",
            children=[
                html.Div(
                    className="header-byline-group",
                    children=[
                        html.Div(
                            className="header-info-icon",
                            children=[
                                html.Span("i", className="header-info-i"),
                                html.Div(
                                    className="header-info-tooltip",
                                    children=[
                                        html.Div("Data Sources", className="header-info-title"),
                                        html.Div([html.Span("Census — ", className="header-info-label"),
                                                  "Statistics Bureau of Japan (e-Stat), 国勢調査 1920–2020"],
                                                 className="header-info-row"),
                                        html.Div([html.Span("Geometry — ", className="header-info-label"),
                                                  "Geospatial Information Authority of Japan (国土地理院) via dataofjapan/land"],
                                                 className="header-info-row"),
                                        html.Div([html.Span("Photo — ", className="header-info-label"),
                                                  "Bert Mosher / The American Photo Service, Remembering Okinawa"],
                                                 className="header-info-row"),
                                    ],
                                ),
                            ],
                        ),
                        html.A(
                            "deanallton.com",
                            href="https://deanallton.com",
                            target="_blank",
                            className="header-byline",
                        ),
                    ],
                ),
                html.Div(
                    className="header-text",
                    children=[
                        html.Div(HEADER_TITLE_JA, className="header-title-ja"),
                        html.Div(HEADER_TITLE_EN, className="header-title-en"),
                    ],
                ),
            ],
        ),

        # KPI Cards
        html.Div(
            id="kpi-row",
            children=render_kpi_cards(build_kpi_data(MAX_YEAR), YEAR_LABELS.get(MAX_YEAR, str(MAX_YEAR))),
        ),

        # Play Button + Year Slider
        html.Div(
            style={
                "display": "flex",
                "alignItems": "stretch",
                "gap": f"{LAYOUT_GAP}",
            },
            children=[

                # Play / Pause button
                html.Button(
                    "▶",
                    id="play-btn",
                    className="play-btn",
                ),

                # Slider panel
                html.Div(
                    className="playback-panel",
                    children=[
                        dcc.Slider(
                            id="year-slider",
                            min=min(CENSUS_YEARS),
                            max=max(CENSUS_YEARS),
                            step=None,
                            value=MAX_YEAR,
                            marks={
                                yr: {
                                    "label": str(yr),
                                    "style": {
                                        "color": COLOR_PRIMARY if yr == 1945 else COLOR_TEXT_MID,
                                        "fontSize": f"{FONT_SIZE_AXIS_TITLE}px",
                                        "fontWeight": "bold" if yr == 1945 else "normal",
                                    }
                                }
                                for yr in CENSUS_YEARS
                            },
                            tooltip=None,
                            included=False,
                        )
                    ]
                ),
            ]
        ),

        html.Div(
            className="charts-area",
            children=[

                # Map + Pyramid columns
                html.Div(
                    className="map-pyramid-row",
                    style={},
                    children=[
                        # Map container
                        html.Div(
                            className="map-panel",
                            children=[
                                html.Div(
                                    className="metric-selector-strip",
                                    children=[
                                        dcc.Dropdown(
                                            id="metric-selector",
                                            options=[
                                                {"label": meta["label"], "value": key}
                                                for key, meta in MAP_METRICS.items()
                                            ],
                                            value=MAP_METRIC_DEFAULT,
                                            clearable=False,
                                            searchable=False,
                                        ),
                                        html.Button(
                                            "✕ Clear",
                                            id="reset-prefecture-btn",
                                        ),
                                    ]
                                ),
                                html.Button(
                                    "⤢",
                                    id="map-resize-btn",
                                    className="map-resize-btn",
                                    title="Refit map",
                                    n_clicks=0,
                                ),
                                html.Div(
                                    className="map-inner",
                                    children=[
                                        dcc.Graph(
                                            id="map-graph",
                                            clear_on_unhover=True,
                                            figure=build_japan_map_fig(year=MAX_YEAR, metric=MAP_METRIC_DEFAULT),
                                            config={"displayModeBar": False, "responsive": False},
                                            style={"height": "100%"},
                                        ),
                                    ]
                                ),
                                dcc.Tooltip(
                                    id="map-tooltip",
                                    direction="right",
                                ),
                            ]
                        ),

                        # Population Pyramid
                        html.Div(
                            className="pyramid-panel",
                            children=[
                                html.Div(
                                    className="pyramid-legend",
                                    children=[
                                        html.Span("■", style={"color": PYRAMID_MALE_COLOR}),
                                        html.Span("男 Male", style={"marginRight": "10px"}),
                                        html.Span("■", style={"color": PYRAMID_FEMALE_COLOR}),
                                        html.Span("女 Female"),
                                    ]
                                ),
                                html.Div(
                                    className="pyramid-inner",
                                    children=[
                                        html.Div(
                                            className="pyramid-graph-container",
                                            children=[
                                                dcc.Graph(
                                                    id="pyramid-chart",
                                                    className="pyramid-graph",
                                                    clear_on_unhover=True,
                                                    figure=build_pyramid_fig(year=MAX_YEAR,
                                                                             area_estat=None,
                                                                             axis_max=_prewarm_axis_max),
                                                    config={"displayModeBar": False, "responsive": True},
                                                    style={"height": "100%"},
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                                dcc.Tooltip(
                                    id="pyramid-tooltip",
                                    direction="right",
                                ),
                            ]
                        ),
                    ]
                ),

                # Time Series
                html.Div(
                    className="timeseries-panel",
                    children=[
                        html.Div(
                            className="metric-selector-strip ts-selector-strip",
                            children=[
                                dcc.Dropdown(
                                    id="ts-view-selector",
                                    options=[{"label": v, "value": k} for k, v in TS_VIEWS.items()],
                                    value=TS_VIEW_DEFAULT,
                                    clearable=False,
                                    searchable=False,
                                ),
                            ],
                        ),
                        dcc.Graph(
                            id="timeseries-chart",
                            clear_on_unhover=True,
                            figure=build_ts_population_fig(selected_year=MAX_YEAR, area_estat=None),
                            config={"displayModeBar": False, "responsive": True},
                            style={"height": "100%"},
                        ),
                        dcc.Tooltip(
                            id="timeseries-tooltip",
                            direction="top",
                        ),
                    ]
                ),
            ]
        ),
    ]
)


# ── Callbacks ─────────────────────────────────────────────────────────────────
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


def _render_delta(delta_str: str):
    """Split a pre-formatted delta string into colored Dash spans.

    Handles three cases:
      - ""              → empty string (suppressed metric)
      - "First census"  → plain mid-tone string
      - "▲/▼ val  since YYYY (N yrs)" → arrow + value + suffix, each styled
    """
    if not delta_str:
        return ""
    if delta_str == "First census":
        return html.Span(delta_str, style={"color": TOOLTIP_TEXT_MID})

    arrow, rest     = delta_str.split(" ", 1)
    is_positive     = arrow == "▲"
    arrow_color     = ACCENT_DANKAI_JR if is_positive else COLOR_WARNING
    value, suffix   = rest.split("  since ", 1)

    return [
        html.Span(arrow,              style={"color": arrow_color}),
        html.Span(f" {value}",        style={"color": TOOLTIP_TEXT_HI}),
        html.Span(f"  since {suffix}", style={"color": TOOLTIP_TEXT_MID}),
    ]


@app.callback(
    Output("play-interval", "disabled"),
    Output("play-btn", "children"),
    Output("resume-year", "data"),
    Output("year-slider", "value", allow_duplicate=True),
    Input("play-btn", "n_clicks"),
    State("play-interval", "disabled"),
    State("year-slider", "value"),
    prevent_initial_call=True,
)
def toggle_playback(n_clicks, is_disabled, current_year):
    if is_disabled:
        # toggle_playback — starting from max year, jump to min
        if current_year == MAX_YEAR:
            return False, "⏸", MAX_YEAR, YEAR_MIN
        return False, "⏸", current_year, no_update  # normal: store current, don't move slider
    # Pausing — don't touch resume year or slider
    return True, "▶", no_update, no_update

@app.callback(
    Output("year-slider", "value"),
    Output("play-interval", "disabled", allow_duplicate=True),
    Output("play-btn", "children", allow_duplicate=True),
    Input("play-interval", "n_intervals"),
    State("year-slider", "value"),
    State("resume-year", "data"),
    prevent_initial_call=True,
)
def advance_year(n_intervals, current_year, resume_year):
    if current_year not in PLAYBACK_YEARS:
        next_year = next((yr for yr in PLAYBACK_YEARS if yr > current_year), None)
    else:
        idx = PLAYBACK_YEARS.index(current_year)
        next_year = PLAYBACK_YEARS[idx + 1] if idx + 1 < len(PLAYBACK_YEARS) else None

    if next_year is None:
        # advance_year — fallback if resume_year store is empty
        return resume_year if resume_year is not None else MAX_YEAR, True, "▶"

    return next_year, False, no_update

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

@app.callback(
    Output("map-tooltip", "show"),
    Output("map-tooltip", "bbox"),
    Output("map-tooltip", "children"),
    Input("map-graph", "hoverData"),
    State("metric-selector", "value"),
    prevent_initial_call=True,
)
def show_map_tooltip(hover_data, metric):
    if hover_data is None or not hover_data.get("points"):
        return False, no_update, no_update

    pt   = hover_data["points"][0]
    cd   = pt.get("customdata")
    raw  = pt.get("bbox", {})

    # Push tooltip away from cursor so the hovered feature can breathe
    bbox = {
        "x0": raw.get("x0", 0) + MAP_TOOLTIP_OFFSET_X,
        "x1": raw.get("x1", 0) + MAP_TOOLTIP_OFFSET_X,
        "y0": raw.get("y0", 0) - MAP_TOOLTIP_OFFSET_Y,
        "y1": raw.get("y1", 0) - MAP_TOOLTIP_OFFSET_Y,
    }

    # ── Okinawa warning card ──────────────────────────────────────────────────
    if cd is None:
        if pt.get("location") == OKINAWA_AREA_ESTAT:
            children = html.Div([
                html.Div("沖縄県  Okinawa", className="tt-title"),
                html.Div("⚠ データ品質に注意", className="tt-warning"),
                html.Div(
                    "米国統治期の集計方法の違いにより他年度と比較できません。",
                    className="tt-body",
                ),
                html.Div(
                    "Age band inflation under US administration — not comparable to other census years.",
                    className="tt-hint",
                ),
            ], className="tt-card", style={"--arrow-y-offset": f"{MAP_TOOLTIP_OFFSET_Y}px"})
            return True, bbox, children
        return False, no_update, no_update

    # ── Normal prefecture card ────────────────────────────────────────────────
    meta         = MAP_METRICS[metric]
    name_ja      = cd[0]
    name_en      = cd[1]
    population   = cd[2]
    aging_index  = cd[3]
    metric_str   = cd[4]
    delta_str    = cd[5]

    # Suppress redundant secondary rows when they'd duplicate the active metric
    show_pop    = metric != "population"
    show_aging  = metric != "aging_index"

    secondary = []
    if show_pop:
        secondary.append(
            html.Div([
                html.Span("人口  ", className="tt-label"),
                html.Span(f"{int(population):,}", className="tt-value"),
            ])
        )
    if show_aging:
        secondary.append(
            html.Div([
                html.Span("高齢化指数  ", className="tt-label"),
                html.Span(f"{aging_index:.1f}", className="tt-value"),
            ])
        )

    children = html.Div([
        html.Div([
            html.Span(name_ja, className="tt-name-ja"),
            html.Span(f"  {name_en}", className="tt-name-en"),
        ], className="tt-title"),
        html.Div(meta["label"], className="tt-metric-label"),
        html.Div(metric_str,    className="tt-metric-value"),
        html.Div(_render_delta(delta_str), className="tt-delta"),
        html.Hr(className="tt-divider") if secondary else None,
        *secondary,
        html.Div("再選択でクリア  /  Reselect to clear", className="tt-hint"),
    ], className="tt-card", style={"--arrow-y-offset": f"{MAP_TOOLTIP_OFFSET_Y}px"})

    return True, bbox, children

@app.callback(
    Output("pyramid-tooltip", "show"),
    Output("pyramid-tooltip", "bbox"),
    Output("pyramid-tooltip", "children"),
    Output("pyramid-tooltip", "direction"),
    Input("pyramid-chart", "hoverData"),
    prevent_initial_call=True,
)
def show_pyramid_tooltip(hover_data):
    if hover_data is None or not hover_data.get("points"):
        return False, no_update, no_update, no_update

    pt           = hover_data["points"][0]
    cd           = pt.get("customdata")
    curve_number = pt.get("curveNumber", 0)
    if cd is None:
        return False, no_update, no_update, no_update

    # Direction logic is the same for all trace types:
    # negative x (male side) → tooltip left, arrow points right
    # zero or positive x     → tooltip right, arrow points left
    x_val     = pt.get("x", 0)
    direction = "left" if x_val < 0 else "right"
    arrow_cls = "tt-card arrow-right" if direction == "left" else "tt-card"
    x_offset  = PYRAMID_TOOLTIP_OFFSET_X if direction == "right" else -PYRAMID_TOOLTIP_OFFSET_X

    raw  = pt.get("bbox", {})
    bbox = {
        "x0": raw.get("x0", 0) + x_offset,
        "x1": raw.get("x1", 0) + x_offset,
        "y0": raw.get("y0", 0) + PYRAMID_GRAPH_TOP_OFFSET - PYRAMID_TOOLTIP_OFFSET_Y,
        "y1": raw.get("y1", 0) + PYRAMID_GRAPH_TOP_OFFSET - PYRAMID_TOOLTIP_OFFSET_Y,
    }

    # ── Bar tooltip — curveNumber 0 (male) or 1 (female) ─────────────────────
    if curve_number in (0, 1):
        age_label  = cd[0]
        male_pop   = cd[1]
        female_pop = cd[2]
        cohort_key = cd[3] if len(cd) > 3 else ""

        cohort_strip = None
        if cohort_key:
            _COHORT_META = {
                "dankai":    ("団塊の世代", "1947–1949年生まれ", ACCENT_DANKAI),
                "dankai_jr": ("団塊ジュニア", "1971–1974年生まれ", ACCENT_DANKAI_JR),
            }
            cohort_name, birth_range, cohort_color = _COHORT_META[cohort_key]
            cohort_strip = html.Div([
                html.Hr(className="tt-divider"),
                html.Div([
                    html.Div(className="pyramid-tt-cohort-strip",
                             style={"--cohort-color": cohort_color}),
                    html.Div([
                        html.Span(cohort_name, className="tt-label",
                                  style={"color": cohort_color}),
                        html.Span(f"  {birth_range}", className="tt-hint"),
                    ]),
                ], className="pyramid-tt-cohort-row"),
            ])

        children = html.Div([
            html.Div(f"年齢: {age_label}", className="tt-title"),
            html.Div([
                html.Div(className="pyramid-tt-cohort-strip",
                         style={"--cohort-color": PYRAMID_MALE_COLOR}),
                html.Div([
                    html.Span("男 Male  ", className="tt-label"),
                    html.Span(f"{int(male_pop):,}", className="tt-value"),
                ]),
            ], className="pyramid-tt-cohort-row"),
            html.Div([
                html.Div(className="pyramid-tt-cohort-strip",
                         style={"--cohort-color": PYRAMID_FEMALE_COLOR}),
                html.Div([
                    html.Span("女 Female  ", className="tt-label"),
                    html.Span(f"{int(female_pop):,}", className="tt-value"),
                ]),
            ], className="pyramid-tt-cohort-row"),
            cohort_strip,
        ], className=arrow_cls, style={"--arrow-y-offset": f"{PYRAMID_TOOLTIP_OFFSET_Y}px"})

        return True, bbox, children, direction

    # ── Scatter cohort marker tooltips — curveNumber 2 (war_gen) or 3 (shoushika) ──
    # customdata shape (set in pyramid.py Step 1): [name_ja, birth_range, accent_hex, age_label]
    cohort_name  = cd[0]
    birth_range  = cd[1]
    cohort_color = cd[2]
    age_label    = cd[3]

    children = html.Div([
        html.Div([
            html.Div(className="pyramid-tt-cohort-strip",
                     style={"--cohort-color": cohort_color}),
            html.Div(cohort_name, className="tt-title",
                     style={"color": cohort_color}),
        ], className="pyramid-tt-cohort-row"),
        html.Div(birth_range, className="tt-hint"),
        html.Hr(className="tt-divider"),
        html.Div([
            html.Span("年齢  ", className="tt-label"),
            html.Span(age_label, className="tt-value"),
        ]),
    ], className=arrow_cls, style={"--arrow-y-offset": f"{PYRAMID_TOOLTIP_OFFSET_Y}px"})

    return True, bbox, children, direction

@app.callback(
    Output("timeseries-tooltip", "show"),
    Output("timeseries-tooltip", "bbox"),
    Output("timeseries-tooltip", "children"),
    Output("timeseries-tooltip", "direction"),
    Input("timeseries-chart", "hoverData"),
    State("ts-view-selector", "value"),
    prevent_initial_call=True,
)
def show_timeseries_tooltip(hover_data, ts_view):
    if hover_data is None or not hover_data.get("points"):
        return False, no_update, no_update, no_update

    pt = hover_data["points"][0]
    cd = pt.get("customdata")
    if cd is None:
        return False, no_update, no_update, no_update

    raw   = pt.get("bbox", {})
    bbox = {
        "x0": raw.get("x0", 0) - TS_TOOLTIP_OFFSET_X,
        "x1": raw.get("x1", 0) - TS_TOOLTIP_OFFSET_X,
        "y0": raw.get("y0", 0) - TS_TOOLTIP_OFFSET_Y,
        "y1": raw.get("y1", 0) - TS_TOOLTIP_OFFSET_Y,
    }

    year = cd[0]

    # population metric
    if ts_view == "population":
        total_M       = cd[1]
        male_M        = cd[2]
        female_M      = cd[3]
        series_prefix = cd[4]

        def pop_row(label, value_str, color):
            return html.Div([
                html.Div(className="pyramid-tt-cohort-strip",
                         style={"--cohort-color": color}),
                html.Div([
                    html.Span(f"{label}  ", className="tt-label"),
                    html.Span(value_str,    className="tt-value"),
                ]),
            ], className="pyramid-tt-cohort-row")

        provisional_banner = (
            html.Div("臨時国勢調査  /  Provisional Census", className="tt-provisional-banner")
            if year == 1945 else None
        )

        children = html.Div([
            provisional_banner,
            html.Hr(className="tt-divider") if provisional_banner else None,
            html.Div(str(int(year)), className="tt-title"),
            html.Div("人口 / Population", className="tt-metric-label"),
            html.Hr(className="tt-divider"),
            pop_row("総数", f"{total_M:.1f}M",  COLOR_TEXT_HI),
            pop_row("男",   f"{male_M:.1f}M",   PYRAMID_MALE_COLOR),
            pop_row("女",   f"{female_M:.1f}M", PYRAMID_FEMALE_COLOR),
            html.Div(series_prefix, className="tt-hint"),
        ], className="tt-card arrow-bottom", style={
            "--arrow-y-offset": f"{TS_TOOLTIP_OFFSET_Y}px",
            "--arrow-x-offset": f"{TS_TOOLTIP_OFFSET_X}px",
        })

    elif ts_view == "aging_index":
        national_ai = cd[1]
        pref_ai     = cd[2]
        pref_lbl    = cd[3]
        flag        = cd[4]

        def ai_row(label, value_str, color):
            return html.Div([
                html.Div(className="pyramid-tt-cohort-strip",
                         style={"--cohort-color": color}),
                html.Div([
                    html.Span(f"{label}  ", className="tt-label"),
                    html.Span(value_str,    className="tt-value"),
                ]),
            ], className="pyramid-tt-cohort-row")

        pref_row = None
        if pref_ai is not None:
            pref_row = ai_row(pref_lbl, f"{pref_ai:.1f}", TIMESERIES_PREF_COLOR)

        provisional_banner = (
            html.Div("臨時国勢調査  /  Provisional Census", className="tt-provisional-banner")
            if flag == "1945" else None
        )

        children = html.Div([
            provisional_banner,
            html.Hr(className="tt-divider") if provisional_banner else None,
            html.Div(str(int(year)),            className="tt-title"),
            html.Div("高齢化指数 / Aging Index", className="tt-metric-label"),
            html.Hr(className="tt-divider"),
            ai_row("全国", f"{national_ai:.1f}", COLOR_TEXT_MID),
            pref_row,
        ], className="tt-card arrow-bottom", style={
            "--arrow-y-offset": f"{TS_TOOLTIP_OFFSET_Y}px",
            "--arrow-x-offset": f"{TS_TOOLTIP_OFFSET_X}px",
        })

    else:  # pop_share
        # customdata shape:
        # [0]year  [1]youth_share  [2]working_share  [3]old_share
        # [4]pref_youth  [5]pref_working  [6]pref_old  [7]pref_label  [8]flag
        # [9]nat_pop_0_14  [10]nat_pop_15_64  [11]nat_pop_65_plus
        # [12]pref_pop_0_14  [13]pref_pop_15_64  [14]pref_pop_65_plus
        youth_share      = cd[1]
        working_share    = cd[2]
        old_share        = cd[3]
        pref_youth       = cd[4]
        pref_working     = cd[5]
        pref_old         = cd[6]
        pref_lbl         = cd[7]
        flag             = cd[8]
        nat_pop_0_14     = cd[9]
        nat_pop_15_64    = cd[10]
        nat_pop_65_plus  = cd[11]
        pref_pop_0_14    = cd[12]
        pref_pop_15_64   = cd[13]
        pref_pop_65_plus = cd[14]

        def _fmt_pop(n):
            """Format headcount to nearest sensible unit."""
            if n is None:
                return None
            if n >= 1_000_000:
                return f"{n / 1_000_000:.1f}M"
            return f"{round(n / 1_000):,}K"

        def share_row(label, share_val, pop_count, color):
            pop_str = _fmt_pop(pop_count)
            return html.Div([
                html.Div(className="pyramid-tt-cohort-strip",
                         style={"--cohort-color": color}),
                html.Div([
                    html.Span(f"{label}  ", className="tt-label"),
                    html.Span(f"{share_val:.1f}%", className="tt-value"),
                    html.Span(f"  {pop_str}", className="tt-hint") if pop_str else None,
                ]),
            ], className="pyramid-tt-cohort-row")

        def dep_ratio_row(old, working):
            """Old-age dependency ratio: 老年従属比 = pop_65+ / pop_15-64 × 100."""
            if old is None or not working:
                return None
            ratio = old / working * 100
            return html.Div([
                html.Span("老年従属比  ", className="tt-label"),
                html.Span(f"{ratio:.1f}%", className="tt-value"),
            ], style={"paddingLeft": "12px", "marginTop": "2px", "opacity": "0.85"})

        provisional_banner = (
            html.Div("臨時国勢調査  /  Provisional Census", className="tt-provisional-banner")
            if flag == "1945" else None
        )

        pref_rows = None
        if pref_youth is not None:
            pref_rows = html.Div([
                html.Hr(className="tt-divider"),
                html.Div(pref_lbl, className="tt-hint"),
                share_row("年少 0–14",  pref_youth,   pref_pop_0_14,    PYRAMID_FEMALE_COLOR),
                share_row("生産 15–64", pref_working, pref_pop_15_64,   COLOR_TEXT_HI),
                share_row("老年 65+",   pref_old,     pref_pop_65_plus, PYRAMID_MALE_COLOR),
                dep_ratio_row(pref_old, pref_working),
            ])

        children = html.Div([
            provisional_banner,
            html.Hr(className="tt-divider") if provisional_banner else None,
            html.Div(str(int(year)),               className="tt-title"),
            html.Div("人口割合 / Population Share", className="tt-metric-label"),
            html.Hr(className="tt-divider"),
            share_row("年少 0–14",  youth_share,   nat_pop_0_14,    PYRAMID_FEMALE_COLOR),
            share_row("生産 15–64", working_share, nat_pop_15_64,   COLOR_TEXT_HI),
            share_row("老年 65+",   old_share,     nat_pop_65_plus, PYRAMID_MALE_COLOR),
            dep_ratio_row(old_share, working_share),
            pref_rows,
        ], className="tt-card arrow-bottom", style={
            "--arrow-y-offset": f"{TS_TOOLTIP_OFFSET_Y}px",
            "--arrow-x-offset": f"{TS_TOOLTIP_OFFSET_X}px",
        })

    return True, bbox, children, "top"

@app.callback(
    Output("map-graph", "figure"),
    Output("pyramid-chart", "figure"),
    Output("kpi-row", "children"),
    Output("timeseries-chart", "figure"),
    Input("year-slider", "value"),
    Input("selected-prefecture", "data"),
    Input("metric-selector", "value"),
    Input("ts-view-selector", "value"),
    prevent_initial_call=True,
)
def update_charts(year, area_estat, metric, ts_view):
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
        # Patch only the highlight trace (data[2]) — viewport is untouched.
        patched = Patch()
        patched["data"][2]["locations"] = [area_estat] if area_estat else []
        patched["data"][2]["z"] = [1] if area_estat else []
        map_fig = patched
    else:
        # Year or metric changed — update data traces only, never layout.
        # Leaving layout.mapbox.zoom out of the payload means Plotly keeps
        # whatever zoom is currently set (initial-load Patch or ResizeObserver).
        fig = build_japan_map_fig(year=y, metric=metric)
        fd  = fig.to_dict()
        patched = Patch()
        # Base choropleth (data[0])
        patched["data"][0]["z"]          = fd["data"][0]["z"]
        patched["data"][0]["customdata"] = fd["data"][0]["customdata"]
        patched["data"][0]["colorscale"] = fd["data"][0]["colorscale"]
        patched["data"][0]["zmin"]       = fd["data"][0]["zmin"]
        patched["data"][0]["zmax"]       = fd["data"][0]["zmax"]
        patched["data"][0]["colorbar"]   = fd["data"][0]["colorbar"]
        # Okinawa overlay (data[1]) — active for 1950/1955, empty otherwise
        patched["data"][1]["locations"]  = fd["data"][1]["locations"]
        patched["data"][1]["z"]          = fd["data"][1]["z"]
        map_fig = patched

    if ts_view == "population":
        ts_fig = build_ts_population_fig(selected_year=y, area_estat=area_estat)
    elif ts_view == "aging_index":
        ts_fig = build_ts_aging_index_fig(selected_year=y, area_estat=area_estat)
    else:
        ts_fig = build_ts_pop_share_fig(selected_year=y, area_estat=area_estat)

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


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, dev_tools_ui=False)