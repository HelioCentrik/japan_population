# layout.py
from pathlib import Path

from dash import html, dcc

from dash_app import app
from startup import CENSUS_YEARS, YEAR_LABELS
from app.aesthetics.config import (
    PAGE_BG, PANEL_BG, COLOR_PRIMARY, COLOR_TEXT_MID,
    PLAY_INTERVAL_MS,
    MAP_METRICS, MAP_METRIC_DEFAULT,
    MAP_REF_ZOOM, MAP_CENTER_LAT, MAP_CENTER_LON,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
    TS_VIEWS, TS_VIEW_DEFAULT,
    FONT_SIZE_AXIS_TITLE,
    HEADER_TITLE_JA, HEADER_TITLE_EN,
    MAX_YEAR,
)
from app.data import figure_cache



_PROJECT_MD = Path("PROJECT.md").read_text(encoding="utf-8")

_DARK_PLACEHOLDER = {
    "layout": {
        "paper_bgcolor": PANEL_BG,
        "plot_bgcolor":  PANEL_BG,
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
    }
}

# Initializes the MapLibre GL context during newPlot so Plotly.react
# (called 150ms later with the real choropleth) is a data update on an
# already-running GL instance — not a from-scratch GL init. Prevents the
# "can't read layers" crash that happens when react tries to create GL async
# and plotly_afterplot fires before it finishes.
_DARK_MAP_PLACEHOLDER = {
    "data": [],
    "layout": {
        "paper_bgcolor": PANEL_BG,
        "plot_bgcolor":  PANEL_BG,
        "map": {
            "style":  "carto-darkmatter",
            "zoom":   MAP_REF_ZOOM,
            "center": {"lat": MAP_CENTER_LAT, "lon": MAP_CENTER_LON},
        },
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
    },
}

def serve_layout():
    _cache_valid = figure_cache.is_valid()
    return html.Div(
        className="page-root",
        children=[
            dcc.Store(id="panel-mode", data="project"),
            dcc.Store(id="last-panel-mode", data="project"),
            html.Div(
                style={
                    "flex": "1",
                    "minWidth": "0",
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                },
                children=[
                    html.Div(
                        className="dashboard-outer",
                        style={
                            "minWidth": "0",
                        },
                        children=[
                            dcc.Store(id="charts-ready-trigger", data=None),
                            dcc.Store(id="map-init-zoom", data=None),
                            dcc.Store(id="selected-prefecture", data=None),
                            dcc.Store(id="resume-year", data=None),
                            dcc.Store(id="font-tier", data="lg"),
                            dcc.Store(id="show-projections", data=True),
                            dcc.Store(id="ai-chat-history", data=[], storage_type="local"),
                            dcc.Store(id="ai-pending-question", data=None),
                            dcc.Interval(
                                id="zoom-init",
                                interval=200,    # fires once 200ms after page load — enough for flex layout to settle
                                max_intervals=1,
                                n_intervals=0,
                            ),
                            dcc.Interval(
                                id="ready-poll",
                                interval=150,         # fast enough to feel instant after Plotly init
                                max_intervals=800,    # 150ms × 800 = 120s cold-cache coverage
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

                            # KPI Cards — skeleton shells reserve row height before update_charts fires
                            html.Div(
                                id="kpi-row",
                                className="kpi-row",
                                children=[
                                    html.Div([
                                        html.Div(className="kpi-label"),
                                        html.Div(className="kpi-value"),
                                        html.Div(className="kpi-sub"),
                                    ], className="card kpi-skeleton")
                                    for _ in range(6)
                                ],
                            ),

                            # Play Button + Year Slider
                            html.Div(
                                className="playback-row",
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
                                                                figure=_DARK_MAP_PLACEHOLDER,
                                                                config={"displayModeBar": False, "responsive": False},
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
                                                                        # className="pyramid-graph",
                                                                        clear_on_unhover=True,
                                                                        figure=_DARK_PLACEHOLDER,
                                                                        config={"displayModeBar": False, "responsive": True},
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
                                            html.Button(
                                                children=[
                                                    html.Span("推計", className="proj-toggle-label"),
                                                    html.Div(
                                                        html.Div(className="proj-toggle-thumb"),
                                                        className="proj-toggle-track",
                                                    ),
                                                ],
                                                id="proj-toggle-btn",
                                                className="proj-toggle-btn active",
                                                n_clicks=0,
                                                title="Toggle IPSS projections",
                                            ),
                                            dcc.Graph(
                                                id="timeseries-chart",
                                                clear_on_unhover=True,
                                                figure=_DARK_PLACEHOLDER,
                                                config={"displayModeBar": False, "responsive": True},
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
                    ),  # end dashboard-outer
                ],
            ),

            # ── Side panel controls ──────────────────────────────────────
            html.Div(
                className="side-panel-controls",
                children=[
                    html.Button("›", id="side-panel-toggle-btn", className="side-panel-btn active",
                                n_clicks=0, title="Project info"),
                    html.Button(
                        html.Img(src="/assets/gemini-color.png", style={"width": "28px", "height": "28px"}),
                        id="side-panel-ai-btn", className="side-panel-btn",
                        n_clicks=0, title="Ask Gemini",
                    ),
                ]
            ),

            # ── Side panel ──────────────────────────────────────────
            html.Div(
                id="side-panel",
                className="side-panel open",
                children=[
                    html.Div(
                        id="side-panel-inner",
                        className="side-panel-inner",
                        children=[
                            html.Div(
                                id="side-panel-content",
                                children=dcc.Markdown(_PROJECT_MD, link_target="_blank"),
                            ),
                            html.Div(
                                id="ai-panel",
                                className="ai-panel",
                                style={"display": "none"},
                                children=[
                                    html.Div(
                                        className="ai-chat-wrapper",
                                        children=[
                                            html.Div(id="ai-chat-output", className="ai-chat-output"),
                                            html.Div(
                                                html.Div(id="ai-thinking-indicator"),
                                                className="ai-thinking-wrapper",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        className="ai-input-row",
                                        children=[
                                            html.Div(
                                                className="ai-input-wrapper",
                                                children=[
                                                    html.Img(
                                                        src="/assets/gemini-color.png",
                                                        id="ai-input-icon",
                                                        className="ai-input-icon",
                                                    ),
                                                    dcc.Textarea(
                                                        id="ai-input",
                                                        placeholder="日本の人口について質問してください…",
                                                        className="ai-input",
                                                        rows=1,
                                                    ),
                                                ]
                                            ),
                                            html.Button(
                                                "送信",
                                                id="ai-submit-btn",
                                                className="ai-submit-btn",
                                                n_clicks=0,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ]
                    ),
                ]
            ),
            html.Div(
                id="loading-overlay",
                className="loading-overlay hidden" if _cache_valid else "loading-overlay",
                children=[
                    html.Div(
                        className="loading-overlay-content",
                        children=[
                            html.Div("日本の人口ダッシュボード", className="loading-overlay-title"),
                            html.Div(
                                className="loading-overlay-message",
                                children=[
                                    html.Span("データと図を読み込んでいます"),
                                    html.Span("Loading data and figures…", className="loading-overlay-en"),
                                ],
                            ),
                            html.Div(className="loading-dots", children=[
                                html.Span(), html.Span(), html.Span(),
                            ]),
                        ],
                    ),
                ],
            ),
        ]
    )

app.layout = serve_layout
