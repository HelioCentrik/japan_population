# app/index_string.py
"""
Generates the Dash HTML shell, injecting all design-system tokens as CSS custom
properties in the <head>. This is the bridge between config.py (Python constants)
and style.css (CSS consumers via var(--name)).

Google Fonts [GF] are also loaded here. Only families actually referenced in the
configured FONT_STACK_* constants are included — avoid loading fonts not in use.
"""

from app.config import (
    # Backgrounds
    PAGE_BG, PANEL_BG, PANEL_BORDER,
    # Text scale
    COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_TEXT_HI, COLOR_TEXT_MID, COLOR_TEXT_LO, COLOR_TEXT_HINT,
    # UI accents
    COLOR_UI_HOVER, SLIDER_TRACK_COLOR, CHART_PLOT_COLOR, CHART_GRID_COLOR,
    # Shadows (pre-computed rgba strings)
    SHADOW_PANEL, SHADOW_MAP_INSET, SHADOW_BEZEL, SHADOW_DROP, SHADOW_FULL,
    # Font stacks
    FONT_STACK_SANS, FONT_STACK_SERIF, FONT_STACK_MONO,
    # Font sizes
    FONT_SIZE_AXIS_TICK, FONT_SIZE_AXIS_TITLE,
    FONT_SIZE_LEGEND, FONT_SIZE_CHART_TITLE,
    FONT_SIZE_COLORBAR, FONT_SIZE_COLORBAR_TICK,
    FONT_SIZE_KPI_LABEL, FONT_SIZE_KPI_VALUE, FONT_SIZE_KPI_SUB,
    FONT_SIZE_TITLE,
    # Borders
    PANEL_BORDER_RADIUS, PANEL_BORDER_THICKNESS,
    # Play button
    PLAY_BTN_SIZE, PLAY_BTN_FONT_SIZE,
    # Layout
    LAYOUT_GAP, LAYOUT_OUTER_PAD, LAYOUT_MIN_HEIGHT,
    CHARTS_ROW_FLEX, CHARTS_TS_FLEX,
    MAP_MIN_HEIGHT, MAP_FLEX, PYRAMID_FLEX,
    # Tooltip
    TOOLTIP_BG, TOOLTIP_BORDER, TOOLTIP_BORDER_SIZE,
    TOOLTIP_TEXT_HI, TOOLTIP_TEXT_MID,
    TOOLTIP_HINT, TOOLTIP_WARNING, TOOLTIP_DIVIDER,
)

INDEX_STRING = f'''<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}

        <!-- Google Fonts: JP-compatible families marked [GF] in fonts.py  -->
        <!-- Single combined request; display=swap prevents FOIT on load   -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@400;700&family=BIZ+UDGothic&family=JetBrains+Mono&family=Noto+Sans+Mono&display=swap" rel="stylesheet">

        {{%css%}}
        <style>
            :root {{

                /* Backgrounds */
                --page-bg          : {PAGE_BG};
                --panel-bg         : {PANEL_BG};
                --panel-border     : {PANEL_BORDER};

                /* Text scale */
                --color-primary    : {COLOR_PRIMARY};
                --color-secondary  : {COLOR_SECONDARY};
                --color-text-hi    : {COLOR_TEXT_HI};
                --color-text-mid   : {COLOR_TEXT_MID};
                --color-text-lo    : {COLOR_TEXT_LO};
                --color-text-hint  : {COLOR_TEXT_HINT};

                /* UI accents */
                --color-ui-hover   : {COLOR_UI_HOVER};
                --slider-track     : {SLIDER_TRACK_COLOR};
                --chart-plot-color : {CHART_PLOT_COLOR};
                --chart-grid       : {CHART_GRID_COLOR};

                /* Shadows (derived from PAGE_BG x SHADOW_DARKNESS in config.py) */
                --shadow-panel     : {SHADOW_PANEL};
                --shadow-map-inset : {SHADOW_MAP_INSET};
                --shadow-full      : {SHADOW_FULL};
                --shadow-bezel     : {SHADOW_BEZEL};
                --shadow-drop      : {SHADOW_DROP};

                /* Font stacks */
                --font-sans        : {FONT_STACK_SANS};
                --font-serif       : {FONT_STACK_SERIF};
                --font-mono        : {FONT_STACK_MONO};
                --font-main        : {COLOR_TEXT_MID};   /* legacy alias for --color-text-mid */

                /* Font sizes */
                --font-size-axis-tick     : {FONT_SIZE_AXIS_TICK}px;
                --font-size-axis-title    : {FONT_SIZE_AXIS_TITLE}px;
                --font-size-legend        : {FONT_SIZE_LEGEND}px;
                --font-size-chart-title   : {FONT_SIZE_CHART_TITLE}px;
                --font-size-colorbar      : {FONT_SIZE_COLORBAR}px;
                --font-size-colorbar-tick : {FONT_SIZE_COLORBAR_TICK}px;
                --font-size-kpi-label     : {FONT_SIZE_KPI_LABEL}px;
                --font-size-kpi-value     : {FONT_SIZE_KPI_VALUE}px;
                --font-size-kpi-sub       : {FONT_SIZE_KPI_SUB}px;
                --font-size-title         : {FONT_SIZE_TITLE}px;

                /* Borders */
                --border-radius            : {PANEL_BORDER_RADIUS};
                --panel-border-thickness   : {PANEL_BORDER_THICKNESS};

                /* Play button */
                --play-btn-size      : {PLAY_BTN_SIZE};
                --play-btn-font-size : {PLAY_BTN_FONT_SIZE};

                /* Layout */
                --layout-gap       : {LAYOUT_GAP};
                --outer-pad        : {LAYOUT_OUTER_PAD};
                --min-height       : {LAYOUT_MIN_HEIGHT};
                --charts-row-flex  : {CHARTS_ROW_FLEX};
                --charts-ts-flex   : {CHARTS_TS_FLEX};
                --map-min-height   : {MAP_MIN_HEIGHT};
                --map-flex         : {MAP_FLEX};
                --pyramid-flex     : {PYRAMID_FLEX};

                /* Tooltip */
                --tooltip-bg          : {TOOLTIP_BG};
                --tooltip-border      : {TOOLTIP_BORDER};
                --tooltip-border-size : {TOOLTIP_BORDER_SIZE};
                --tooltip-text-hi     : {TOOLTIP_TEXT_HI};
                --tooltip-text-mid    : {TOOLTIP_TEXT_MID};
                --tooltip-hint        : {TOOLTIP_HINT};
                --tooltip-warning     : {TOOLTIP_WARNING};
                --tooltip-divider     : {TOOLTIP_DIVIDER};
            }}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>'''