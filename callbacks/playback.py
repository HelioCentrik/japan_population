# callbacks/playback.py
from dash import Input, Output, State, no_update

from dash_app import app
from startup import PLAYBACK_YEARS, YEAR_MIN
from app.aesthetics.config import MAX_YEAR


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
