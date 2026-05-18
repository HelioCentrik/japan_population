# app/viz/maps.py
import json
import numpy as np
from functools import lru_cache

import geopandas as gpd
from app.data.db import get_con
from plotly import graph_objects as go

from app.utils import ceil_half_magnitude
from app.aesthetics.config import (
    COLOR_TEXT_HI, COLOR_TEXT_MID, MAP_GEO,
    MAP_MARGINS, MAP_TILE_STYLE,
    MAP_CENTER_LAT, MAP_CENTER_LON, MAP_DEFAULT_ZOOM, MAP_BORDER_WIDTH,
    MAP_HIGHLIGHT_LINE_COLOR, MAP_HIGHLIGHT_LINE_WIDTH, MAP_HIGHLIGHT_FILL,
    FONT_SIZE_COLORBAR, FONT_SIZE_COLORBAR_TICK,
    MAP_METRICS, MAP_METRIC_DEFAULT, OKINAWA_AREA_ESTAT,
    MAX_YEAR, POP_DELTA_SIGMA, NET_MIGRATION_SIGMA, MAP_NO_DATA_COLOR,
)
from app.data import figure_cache



_OKINAWA_GREY_YEARS = {1950, 1955}
_OKINAWA_GREY_FILL  = "rgba(140, 140, 140, 0.55)"
_OKINAWA_GREY_LINE  = "rgba(180, 180, 180, 0.7)"


@lru_cache(maxsize=1)
def _get_global_metric_bounds() -> dict:
    """
    Queries global min/max for each map metric across all years and prefectures.
    Cached once — bounds are fixed for the lifetime of the process.
    Pins colorscale ranges so the map scale stays stable while scrubbing years.

    pop_delta and net_migration use sigma-clipping to prevent outliers from
    compressing the diverging scale. tfr uses raw min/max — values are
    naturally bounded (~0.8–3.0) and well-behaved across the full dataset.
    """
    con = get_con()

    row = con.execute("""
        SELECT
            MIN(population), MAX(population),
            MIN(pop_delta),  MAX(pop_delta),
            MIN(tfr),        MAX(tfr)
        FROM v_map_metrics
    """).fetchone()

    delta_row = con.execute("""
        SELECT AVG(pop_delta), STDDEV(pop_delta)
        FROM v_map_metrics
        WHERE pop_delta IS NOT NULL
    """).fetchone()

    mig_row = con.execute("""
        SELECT AVG(net_migration), STDDEV(net_migration)
        FROM v_map_metrics
        WHERE net_migration IS NOT NULL
    """).fetchone()

    # pop_delta — symmetric diverging bounds via sigma-clip
    delta_mean, delta_sigma = delta_row
    delta_bound = delta_sigma * POP_DELTA_SIGMA
    delta_dev   = ceil_half_magnitude(
        max(abs(delta_mean - delta_bound), abs(delta_mean + delta_bound))
    )

    # net_migration — same approach, own sigma constant
    mig_mean, mig_sigma = mig_row
    mig_bound = mig_sigma * NET_MIGRATION_SIGMA
    mig_dev   = ceil_half_magnitude(
        max(abs(mig_mean - mig_bound), abs(mig_mean + mig_bound))
    )

    return {
        "population":    (float(np.log1p(row[0])), float(np.log1p(row[1]))),
        "pop_delta":     (-delta_dev, delta_dev),
        "tfr":           (float(row[4]), float(row[5])),
        "net_migration": (-mig_dev, mig_dev),
    }


def build_japan_map_fig(year: int, metric: str = MAP_METRIC_DEFAULT) -> go.Figure:
    _key = figure_cache.make_key("map", year, metric)
    if (fig := figure_cache.get(_key)) is not None:
        return fig

    prefectures = gpd.read_parquet("data/japan_prefectures_simplified.parquet").to_crs(epsg=4326)
    prefectures = prefectures.rename(columns={"prefecture_code": "area_estat"})
    prefectures = prefectures.drop(columns=["prefecture_name"])

    con = get_con()
    df = con.execute(f"""
        SELECT
            area_estat,
            prefecture_name,
            population,
            aging_index,
            pop_delta,
            prev_year, year_gap,
            tfr,
            net_migration
        FROM v_map_metrics
        WHERE year = {year}
    """).df()

    prefectures = prefectures.merge(df, on="area_estat", how="left")
    meta = MAP_METRICS[metric]

    # ── Delta strings ─────────────────────────────────────────────────────────
    _delta_cols = {
        "population":    "pop_delta",
        "pop_delta":     None,
        "tfr":           None,
        "net_migration": None,
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


    # ── Null-coverage check ───────────────────────────────────────────────────
    # Primary guard is the year-snap callback in callbacks/selection.py.
    # This fallback renders a grey map with a notice rather than crashing or
    # showing an empty choropleth if the snap somehow doesn't fire.
    all_null = prefectures[metric].isna().all()
    colorscale_override = None

    # ── Z column + colorscale bounds ──────────────────────────────────────────
    if all_null:
        prefectures["_z"] = 0.0
        zmin, zmax         = 0.0, 1.0
        colorscale_override = [[0, MAP_NO_DATA_COLOR], [1, MAP_NO_DATA_COLOR]]
        colorbar_label      = meta["label"].split("  ")[0]
    elif metric == "population":
        prefectures["_z"] = np.log1p(prefectures["population"])
        colorbar_label    = "人口 (log)"
        zmin, zmax        = _get_global_metric_bounds()["population"]
    elif metric in ("pop_delta", "net_migration"):
        zmin, zmax        = _get_global_metric_bounds()[metric]
        prefectures["_z"] = prefectures[metric].clip(lower=zmin, upper=zmax)
        colorbar_label    = meta["label"].split("  ")[0]
    else:
        # tfr — raw bounds, no clipping needed
        prefectures["_z"] = prefectures[metric]
        zmin, zmax        = _get_global_metric_bounds()[metric]
        colorbar_label    = meta["label"].split("  ")[0]


    colorbar_extra = {}
    if metric in ("pop_delta", "net_migration"):
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
    base_trace = go.Choroplethmap(
        geojson=prefectures_js,
        locations=prefectures["area_estat"],
        z=prefectures["_z"],
        zmin=zmin, zmax=zmax,
        featureidkey="properties.area_estat",
        colorscale=colorscale_override or meta["colorscale"],
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
                font=dict(size=FONT_SIZE_COLORBAR, color=COLOR_TEXT_HI),
            ),
            x=0.02, xanchor="left",
            thickness=16, len=0.6,
            tickfont=dict(size=FONT_SIZE_COLORBAR_TICK, color=COLOR_TEXT_HI),
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

    traces.append(go.Choroplethmap(
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
    traces.append(go.Choroplethmap(
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
        uirevision="map-view",
        map=dict(
            style=MAP_TILE_STYLE,
            center=dict(lat=MAP_CENTER_LAT, lon=MAP_CENTER_LON),
        ),
        margin=dict(l=MAP_MARGINS, r=MAP_MARGINS, t=MAP_MARGINS, b=MAP_MARGINS),
        autosize=True,
    )

    if all_null:
        fig.add_annotation(
            text="この年はデータなし  /  No data for this year",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(color=COLOR_TEXT_MID, size=14),
            bgcolor="rgba(0,0,0,0)",
        )

    figure_cache.put(_key, fig)
    return fig
