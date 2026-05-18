# callbacks/playback.py
from dash import Input, Output, State, no_update

from dash_app import app
from startup import PLAYBACK_YEARS, CENSUS_YEARS
from app.aesthetics.config import MAX_YEAR, MAP_METRICS


def _valid_playback_years(metric: str) -> list[int]:
    """Filter PLAYBACK_YEARS to the metric's coverage window."""
    meta     = MAP_METRICS.get(metric, {})
    min_year = meta.get("min_year") or CENSUS_YEARS[0]
    max_year = meta.get("max_year") or CENSUS_YEARS[-1]
    return [yr for yr in PLAYBACK_YEARS if min_year <= yr <= max_year]


@app.callback(
    Output("play-interval", "disabled"),
    Output("play-btn", "children"),
    Output("resume-year", "data"),
    Output("year-slider", "value", allow_duplicate=True),
    Input("play-btn", "n_clicks"),
    State("play-interval", "disabled"),
    State("year-slider", "value"),
    State("metric-selector", "value"),
    prevent_initial_call=True,
)
def toggle_playback(n_clicks, is_disabled, current_year, metric):
    valid_years = _valid_playback_years(metric)
    year_min    = valid_years[0]  if valid_years else CENSUS_YEARS[0]
    year_max    = valid_years[-1] if valid_years else MAX_YEAR

    if is_disabled:
        # Starting — rewind to metric's first valid year if already at the end
        if current_year == year_max:
            return False, "⏸", year_max, year_min
        return False, "⏸", current_year, no_update
    # Pausing — leave slider and resume year alone
    return True, "▶", no_update, no_update


@app.callback(
    Output("year-slider", "value"),
    Output("play-interval", "disabled", allow_duplicate=True),
    Output("play-btn", "children", allow_duplicate=True),
    Input("play-interval", "n_intervals"),
    State("year-slider", "value"),
    State("resume-year", "data"),
    State("metric-selector", "value"),
    prevent_initial_call=True,
)
def advance_year(n_intervals, current_year, resume_year, metric):
    valid_years = _valid_playback_years(metric)
    year_max    = valid_years[-1] if valid_years else MAX_YEAR

    if current_year not in valid_years:
        # Current year outside coverage — jump to next valid year
        next_year = next((yr for yr in valid_years if yr > current_year), None)
    else:
        idx       = valid_years.index(current_year)
        next_year = valid_years[idx + 1] if idx + 1 < len(valid_years) else None

    if next_year is None:
        # Reached the end — stop and restore resume position
        return resume_year if resume_year is not None else year_max, True, "▶"

    return next_year, False, no_update