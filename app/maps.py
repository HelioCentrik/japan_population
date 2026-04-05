# app/maps.py
import json
import numpy as np
from functools import lru_cache

import geopandas as gpd
from app.db import get_con
from plotly import graph_objects as go

from app.config import (
    COLOR_TEXT_MID, MAP_GEO,
    MAP_TILE_STYLE,
    MAP_CENTER_LAT, MAP_CENTER_LON, MAP_DEFAULT_ZOOM, MAP_BORDER_WIDTH,
    MAP_HIGHLIGHT_LINE_COLOR, MAP_HIGHLIGHT_LINE_WIDTH, MAP_HIGHLIGHT_FILL,
    FONT_SIZE_COLORBAR, FONT_SIZE_COLORBAR_TICK,
    MAP_METRICS, MAP_METRIC_DEFAULT, OKINAWA_AREA_ESTAT,
    MAX_YEAR,
)
from app import figure_cache



_OKINAWA_GREY_YEARS = {1950, 1955}
_OKINAWA_GREY_FILL  = "rgba(140, 140, 140, 0.55)"
_OKINAWA_GREY_LINE  = "rgba(180, 180, 180, 0.7)"


@lru_cache(maxsize=1)
def _get_global_metric_bounds() -> dict:
    """
    Queries global min/max for each metric across all years and prefectures.
    Cached once — bounds are fixed for the lifetime of the process.
    Pins colorscale ranges so the map scale stays stable while scrubbing years.
    """
    con = get_con()  # shared in-memory singleton — do NOT close
    row = con.execute("""
        SELECT
            MIN(population),        MAX(population),
            MIN(aging_index),       MAX(aging_index),
            MIN(old_age_dep),       MAX(old_age_dep),
            MIN(working_age_share), MAX(working_age_share)
        FROM v_map_metrics
    """).fetchone()

    aging_mid     = 100.0
    aging_max_dev = max(abs(row[3] - aging_mid), abs(row[2] - aging_mid))

    return {
        "population":        (float(np.log1p(row[0])), float(np.log1p(row[1]))),
        "aging_index":       (aging_mid - aging_max_dev, aging_mid + aging_max_dev),
        "old_age_dep":       (float(row[4]), float(row[5])),
        "working_age_share": (float(row[6]), float(row[7])),
    }


def build_japan_map_fig(
    year: int = MAX_YEAR,
    area_estat: str | None = None,
    metric: str = MAP_METRIC_DEFAULT,
) -> go.Figure:
    _key = figure_cache.make_key("map", year, metric, area_estat)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    prefectures = gpd.read_parquet("data/japan_prefectures_simplified.parquet").to_crs(epsg=4326)
    prefectures = prefectures.rename(columns={"prefecture_code": "area_estat"})

    con = get_con()
    df = con.execute(f"""
        SELECT
            area_estat,
            population, aging_index, old_age_dep, working_age_share,
            pop_delta, aging_index_delta, old_age_dep_delta, working_age_share_delta,
            prev_year, year_gap
        FROM v_map_metrics
        WHERE year = {year}
    """).df()

    prefectures = prefectures.merge(df, on="area_estat", how="left")
    meta = MAP_METRICS[metric]

    # ── Delta strings ─────────────────────────────────────────────────────────
    _delta_cols = {
        "population":        "pop_delta",
        "aging_index":       "aging_index_delta",
        "old_age_dep":       "old_age_dep_delta",
        "working_age_share": "working_age_share_delta",
    }

    def _fmt_delta(row, col):
        d = row[_delta_cols[col]]
        if d != d:  # NaN
            return "First census"
        sign = "▲" if d >= 0 else "▼"
        suffix = f"  since {int(row['prev_year'])} ({int(row['year_gap'])} yrs)"
        return f"{sign} {int(abs(d)):,}{suffix}" if col == "population" else f"{sign} {abs(d):.1f}{suffix}"

    prefectures["metric_value_str"] = prefectures[metric].apply(meta["fmt"])
    prefectures["metric_delta_str"] = prefectures.apply(lambda r: _fmt_delta(r, metric), axis=1)

    # ── Z column + colorscale bounds ──────────────────────────────────────────
    if metric == "population":
        prefectures["_z"] = np.log1p(prefectures["population"])
        colorbar_label    = "人口 (log)"
    else:
        prefectures["_z"] = prefectures[metric]
        colorbar_label    = meta["label"].split("  ")[0]   # JA half only

    # ── Z column + colorscale bounds ──────────────────────────────────────────
    if metric == "population":
        prefectures["_z"] = np.log1p(prefectures["population"])
        colorbar_label    = "人口 (log)"
    else:
        prefectures["_z"] = prefectures[metric]
        colorbar_label    = meta["label"].split("  ")[0]   # JA half only

    zmin, zmax = _get_global_metric_bounds()[metric]

    prefectures_js = json.loads(prefectures.to_json())

    # ── Base choropleth ───────────────────────────────────────────────────────
    base_trace = go.Choroplethmapbox(
        geojson=prefectures_js,
        locations=prefectures["area_estat"],
        z=prefectures["_z"],
        zmin=zmin, zmax=zmax,
        featureidkey="properties.area_estat",
        colorscale=meta["colorscale"],
        marker_line_width=MAP_BORDER_WIDTH,
        marker_line_color=MAP_GEO.get("line_color"),
        customdata=prefectures[[
            "prefecture_name_ja",   # [0]
            "prefecture_name",      # [1]
            "population",           # [2]
            "aging_index",          # [3]
            "metric_value_str",     # [4]  active metric, formatted
            "metric_delta_str",     # [5]  active metric delta
        ]].values,
        hovertemplate=(
            "<b style='font-size:16px'>%{customdata[0]}  "
            "<span style='font-size:18px'>%{customdata[1]}</span></b><br><br>"
            f"<b style='font-size:14px'>{meta['label']}</b><br>"
            "<b style='font-size:16px'>%{customdata[4]}</b><br>"
            "Change:  %{customdata[5]}<br>"
            "<span style='color:#445566'>──────────────────</span><br>"
            "Population:   <b>%{customdata[2]:,.0f}</b><br>"
            "Aging index:  <b>%{customdata[3]:.1f}</b><br>"
            "<span style='color:#667799;font-size:11px'>再選択でクリア / Reselect to clear</span><br>"
            "<extra></extra>"
        ),
        colorbar=dict(
            title=dict(
                text=colorbar_label,
                side="bottom",
                font=dict(size=FONT_SIZE_COLORBAR, color=COLOR_TEXT_MID),
            ),
            x=0.02, xanchor="left",
            thickness=16, len=0.6,
            tickfont=dict(size=FONT_SIZE_COLORBAR_TICK, color=COLOR_TEXT_MID),
        ),
    )

    traces = [base_trace]

    # ── Okinawa grey-out for 1950 & 1955 ─────────────────────────────────────
    # Figures rendered beneath the base — but the hovertemplate overrides the
    # base trace because this trace is layered on top.
    if year in _OKINAWA_GREY_YEARS:
        oki = prefectures[prefectures["area_estat"] == OKINAWA_AREA_ESTAT]
        if not oki.empty:
            traces.append(go.Choroplethmapbox(
                geojson=json.loads(oki.to_json()),
                locations=oki["area_estat"],
                z=[1],
                featureidkey="properties.area_estat",
                colorscale=[[0, _OKINAWA_GREY_FILL], [1, _OKINAWA_GREY_FILL]],
                showscale=False,
                marker_line_width=1.0,
                marker_line_color=_OKINAWA_GREY_LINE,
                hovertemplate=(
                    "<b>沖縄県  Okinawa</b><br><br>"
                    "<span style='color:#bbbbbb'>⚠ データ品質に注意</span><br>"
                    "米国統治期の集計方法の違いにより<br>"
                    "他年度と比較できません。<br>"
                    "<span style='font-size:11px;color:#999'>"
                    "Age band inflation under US administration.<br>"
                    "Not comparable to other census years.</span>"
                    "<extra></extra>"
                ),
            ))

    # ── Highlight selected prefecture ─────────────────────────────────────────
    if area_estat is not None:
        selected = prefectures[prefectures["area_estat"] == area_estat]
        if not selected.empty:
            traces.append(go.Choroplethmapbox(
                geojson=json.loads(selected.to_json()),
                locations=selected["area_estat"],
                z=[1],
                featureidkey="properties.area_estat",
                colorscale=[[0, MAP_HIGHLIGHT_FILL], [1, MAP_HIGHLIGHT_FILL]],
                showscale=False,
                marker_line_width=MAP_HIGHLIGHT_LINE_WIDTH,
                marker_line_color=MAP_HIGHLIGHT_LINE_COLOR,
                hovertemplate="<extra></extra>",
            ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        mapbox=dict(
            style=MAP_TILE_STYLE,
            center=dict(lat=MAP_CENTER_LAT, lon=MAP_CENTER_LON),
            zoom=MAP_DEFAULT_ZOOM,
        ),
        margin=dict(l=6, r=7, t=6, b=6),
        autosize=True,
    )

    figure_cache.put(_key, fig)
    return fig