# app/aesthetics/plotly_template.py
"""
Builds and registers a Plotly layout template from the active theme.
Call register_plotly_template() once at app startup, before any figure
builders run. All figures then inherit these defaults automatically.

Template scope: backgrounds, font color/family, axis styling, legend defaults.
Per-chart concerns (margins, axis ranges, dtick, zeroline, colorbar) stay
explicit in each figure builder.
"""

import plotly.graph_objects as go
import plotly.io as pio

from app.aesthetics.config import (
    PANEL_BG,
    COLOR_TEXT_MID,
    CHART_GRID_COLOR,
    FONT_STACK_SANS,
    FONT_SIZE_AXIS_TICK,
    FONT_SIZE_LEGEND,
)

_TEMPLATE_NAME = "jp_pop"


def register_plotly_template() -> None:
    template = go.layout.Template()

    template.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color=COLOR_TEXT_MID,
            family=FONT_STACK_SANS,
        ),
        xaxis=dict(
            tickfont=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_AXIS_TICK),
            gridcolor=CHART_GRID_COLOR,
            showline=False,
        ),
        yaxis=dict(
            tickfont=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_AXIS_TICK),
            gridcolor=CHART_GRID_COLOR,
            showline=False,
        ),
        legend=dict(
            font=dict(color=COLOR_TEXT_MID, size=FONT_SIZE_LEGEND),
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    pio.templates[_TEMPLATE_NAME] = template
    pio.templates.default = f"plotly+{_TEMPLATE_NAME}"
