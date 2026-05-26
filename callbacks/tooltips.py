# callbacks/tooltips.py
from dash import html, Input, Output, State, no_update

from dash_app import app
from app.aesthetics.config import (
    COLOR_PRIMARY, COLOR_WARNING, COLOR_TEXT_MID, COLOR_TEXT_HI,
    TOOLTIP_TEXT_MID, TOOLTIP_TEXT_HI,
    MAP_METRICS, MAP_TOOLTIP_OFFSET_X, MAP_TOOLTIP_OFFSET_Y, OKINAWA_AREA_ESTAT,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
    PYRAMID_TOOLTIP_OFFSET_X, PYRAMID_TOOLTIP_OFFSET_Y, PYRAMID_GRAPH_TOP_OFFSET,
    ACCENT_DANKAI, ACCENT_DANKAI_JR,
    TIMESERIES_PREF_COLOR, TS_TOOLTIP_OFFSET_X, TS_TOOLTIP_OFFSET_Y,
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

def _render_signed_metric(metric: str, value_str: str):
    """Signed metrics get a colored directional arrow; the value itself stays neutral."""
    if metric not in ("net_migration", "pop_delta") or value_str in ("—", ""):
        return value_str
    is_positive = value_str.startswith("+")
    arrow_color = ACCENT_DANKAI_JR if is_positive else COLOR_PRIMARY
    arrow       = "▲" if is_positive else "▼"
    plain       = value_str.lstrip("+-")
    return [
        html.Span(arrow, style={"color": arrow_color, "marginRight": "3px"}),
        html.Span(plain),
    ]

def _metric_value_style(metric: str, value_str: str) -> dict:
    """Conditional color for metrics where sign carries directional meaning."""
    if metric == "net_migration" and value_str not in ("—", ""):
        color = ACCENT_DANKAI_JR if value_str.startswith("+") else COLOR_PRIMARY
        return {"color": color}
    return {}


@app.callback(
    Output("map-tooltip", "show"),
    Output("map-tooltip", "children"),
    Input("map-graph", "hoverData"),
    State("metric-selector", "value"),
    prevent_initial_call=True,
)
def show_map_tooltip(hover_data, metric):
    if hover_data is None or not hover_data.get("points"):
        return False, no_update

    pt   = hover_data["points"][0]
    cd   = pt.get("customdata")

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
            return True, children
        return False, no_update

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
    if show_aging and aging_index is not None:
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
        html.Div(_render_signed_metric(metric, metric_str), className="tt-metric-value"),
        html.Div(_render_delta(delta_str), className="tt-delta"),
        html.Hr(className="tt-divider") if secondary else None,
        *secondary,
        html.Div("再選択でクリア  /  Reselect to clear", className="tt-hint"),
    ], className="tt-card", style={"--arrow-y-offset": f"{MAP_TOOLTIP_OFFSET_Y}px"})

    return True, children


@app.callback(
    Output("pyramid-tooltip", "show"),
    Output("pyramid-tooltip", "children"),
    Output("pyramid-tooltip", "direction"),
    Input("pyramid-chart", "hoverData"),
    prevent_initial_call=True,
)
def show_pyramid_tooltip(hover_data):
    if hover_data is None or not hover_data.get("points"):
        return False, no_update, no_update

    pt           = hover_data["points"][0]
    cd           = pt.get("customdata")
    curve_number = pt.get("curveNumber", 0)
    if cd is None:
        return False, no_update, no_update

    try:
        x_val     = pt.get("x", 0)
        direction = "left" if x_val < 0 else "right"
        arrow_cls = "tt-card arrow-right" if direction == "left" else "tt-card"
        x_offset  = PYRAMID_TOOLTIP_OFFSET_X if direction == "right" else -PYRAMID_TOOLTIP_OFFSET_X

        # ── Bar tooltip — curveNumber 0 (male) or 1 (female) ─────────────────
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

            return True, children, direction

        # ── Scatter cohort marker tooltips — curveNumber 2+ ──────────────────
        # customdata shape: [name_ja, birth_range, accent_hex, age_label]
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

        return True, children, direction

    except Exception as e:
        return False, no_update, no_update

@app.callback(
    Output("timeseries-tooltip", "show"),
    Output("timeseries-tooltip", "children"),
    Output("timeseries-tooltip", "direction"),
    Input("timeseries-chart", "hoverData"),
    State("ts-view-selector", "value"),
    prevent_initial_call=True,
)
def show_timeseries_tooltip(hover_data, ts_view):
    if hover_data is None or not hover_data.get("points"):
        return False, no_update, no_update

    pt = hover_data["points"][0]
    cd = pt.get("customdata")
    if cd is None:
        return False, no_update, no_update

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

    elif ts_view == "tfr":
        # customdata shape: [year, national_tfr, pref_tfr_or_None, pref_label]
        national_tfr = cd[1]
        pref_tfr     = cd[2]
        pref_lbl     = cd[3]

        def tfr_row(label, value_str, color):
            return html.Div([
                html.Div(className="pyramid-tt-cohort-strip",
                         style={"--cohort-color": color}),
                html.Div([
                    html.Span(f"{label}  ", className="tt-label"),
                    html.Span(value_str,    className="tt-value"),
                ]),
            ], className="pyramid-tt-cohort-row")

        pref_row = None
        if pref_tfr is not None:
            pref_row = tfr_row(pref_lbl, f"{pref_tfr:.2f}", TIMESERIES_PREF_COLOR)

        children = html.Div([
            html.Div(str(int(year)),           className="tt-title"),
            html.Div("合計特殊出生率 / TFR",   className="tt-metric-label"),
            html.Hr(className="tt-divider"),
            tfr_row("全国", f"{national_tfr:.2f}", COLOR_TEXT_MID),
            pref_row,
            html.Div("replacement: 2.10", className="tt-hint"),
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

    return True, children, "top"
