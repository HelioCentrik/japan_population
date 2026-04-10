# app/maps.py
import json
import numpy as np
from functools import lru_cache

import geopandas as gpd
from app.db import get_con
from plotly import graph_objects as go

from app.utils import ceil_half_magnitude
from app.config import (
    COLOR_TEXT_MID, MAP_GEO,
    MAP_TILE_STYLE,
    MAP_CENTER_LAT, MAP_CENTER_LON, MAP_DEFAULT_ZOOM, MAP_BORDER_WIDTH,
    MAP_HIGHLIGHT_LINE_COLOR, MAP_HIGHLIGHT_LINE_WIDTH, MAP_HIGHLIGHT_FILL,
    FONT_SIZE_COLORBAR, FONT_SIZE_COLORBAR_TICK,
    MAP_METRICS, MAP_METRIC_DEFAULT, OKINAWA_AREA_ESTAT,
    MAX_YEAR, POP_DELTA_SIGMA,
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
            MIN(pop_delta),         MAX(pop_delta),
            MIN(working_age_share), MAX(working_age_share)
        FROM v_map_metrics
    """).fetchone()
    delta_row = con.execute("""
        SELECT
            AVG(pop_delta),
            STDDEV(pop_delta)
        FROM v_map_metrics
        WHERE pop_delta IS NOT NULL
    """).fetchone()

    aging_mid     = 100.0
    aging_max_dev = max(abs(row[3] - aging_mid), abs(row[2] - aging_mid))
    delta_mean  = delta_row[0]
    delta_sigma = delta_row[1]
    delta_bound = delta_sigma * POP_DELTA_SIGMA
    delta_lo    = delta_mean - delta_bound
    delta_hi    = delta_mean + delta_bound
    delta_dev = ceil_half_magnitude(max(abs(delta_lo), abs(delta_hi)))

    return {
        "population":        (float(np.log1p(row[0])), float(np.log1p(row[1]))),
        "aging_index":       (max(0.0, aging_mid - aging_max_dev), aging_mid + aging_max_dev),
        "pop_delta":         (-delta_dev, delta_dev),
        "working_age_share": (float(row[6]), float(row[7])),
    }


def build_japan_map_fig(year: int, metric: str = MAP_METRIC_DEFAULT) -> go.Figure:
    _key = figure_cache.make_key("map", year, metric)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    prefectures = gpd.read_parquet("data/japan_prefectures_simplified.parquet").to_crs(epsg=4326)
    prefectures = prefectures.rename(columns={"prefecture_code": "area_estat"})

    con = get_con()
    df = con.execute(f"""
        SELECT
            area_estat,
            population, aging_index, working_age_share,
            pop_delta, aging_index_delta, working_age_share_delta,
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
        "pop_delta":         None,
        "working_age_share": "working_age_share_delta",
    }

    def _fmt_delta(row, col):
        if _delta_cols[col] is None:
            return ""   # suppressed in tooltip for delta metrics
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
    elif metric == "pop_delta":
        zmin, zmax = _get_global_metric_bounds()["pop_delta"]
        prefectures["_z"] = prefectures["pop_delta"].clip(lower=zmin, upper=zmax)
        colorbar_label = "人口増減"
    else:
        prefectures["_z"] = prefectures[metric]
        colorbar_label    = meta["label"].split("  ")[0]

    zmin, zmax = _get_global_metric_bounds()[metric]

    colorbar_extra = {}
    if metric == "pop_delta":
        half = int(zmax / 2)
        colorbar_extra = dict(
            tickvals=[zmin, -half, 0, half, zmax],
            ticktext=[
                f"{abs(int(zmin)):,}▼",
                f"{half:,}",
                "0",
                f"{half:,}",
                f"{abs(int(zmax)):,}▲",
            ],
        )

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
            "metric_value_str",     # [4]
            "metric_delta_str",     # [5]
        ]].values,
        hoverinfo="none",           # dcc.Tooltip handles display; hoverData still fires
        colorbar=dict(
            title=dict(
                text=colorbar_label,
                side="bottom",
                font=dict(size=FONT_SIZE_COLORBAR, color=COLOR_TEXT_MID),
            ),
            x=0.02, xanchor="left",
            thickness=16, len=0.6,
            tickfont=dict(size=FONT_SIZE_COLORBAR_TICK, color=COLOR_TEXT_MID),
            **colorbar_extra,
        ),
    )

    traces = [base_trace]

    # ── Okinawa grey-out overlay — always at data[1], empty when inactive ────
    # Fixed index required: year/metric Patch updates data[1] by position.
    # Using the full prefectures_js geojson keeps the geojson stable so Patch
    # only needs to swap locations/z — never the geojson itself.
    oki_locs: list = []
    oki_z:    list = []
    if year in _OKINAWA_GREY_YEARS:
        oki = prefectures[prefectures["area_estat"] == OKINAWA_AREA_ESTAT]
        if not oki.empty:
            oki_locs = list(oki["area_estat"])
            oki_z    = [1.0]

    traces.append(go.Choroplethmapbox(
        geojson=prefectures_js,
        locations=oki_locs,
        z=oki_z,
        featureidkey="properties.area_estat",
        colorscale=[[0, _OKINAWA_GREY_FILL], [1, _OKINAWA_GREY_FILL]],
        showscale=False,
        marker_line_width=1.0,
        marker_line_color=_OKINAWA_GREY_LINE,
        hoverinfo="none",
    ))

    # ── Highlight trace — always at data[2], empty until prefecture selected ──
    traces.append(go.Choroplethmapbox(
        geojson=prefectures_js,
        locations=[],
        z=[],
        featureidkey="properties.area_estat",
        colorscale=[[0, MAP_HIGHLIGHT_FILL], [1, MAP_HIGHLIGHT_FILL]],
        showscale=False,
        marker_line_width=MAP_HIGHLIGHT_LINE_WIDTH,
        marker_line_color=MAP_HIGHLIGHT_LINE_COLOR,
        hoverinfo="skip",
    ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        uirevision="map-view",  # constant — Plotly never resets viewport on data updates
        mapbox=dict(
            style=MAP_TILE_STYLE,
            center=dict(lat=MAP_CENTER_LAT, lon=MAP_CENTER_LON),
            zoom=MAP_DEFAULT_ZOOM,
        ),
        margin=dict(l=8, r=8, t=8, b=8),
        autosize=True,
    )

    figure_cache.put(_key, fig)
    return fig