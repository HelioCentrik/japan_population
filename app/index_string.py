# app/index_string.py
from app.config import (
    PAGE_BG, PANEL_BG, PANEL_BORDER, FONT_MAIN_COLOR,
    LAYOUT_GAP, LAYOUT_OUTER_PAD, LAYOUT_MIN_HEIGHT,
    CHARTS_ROW_FLEX, CHARTS_TS_FLEX,
    MAP_MIN_HEIGHT, MAP_FLEX, PYRAMID_FLEX,
)

INDEX_STRING = f'''<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            :root {{
                --page-bg       : {PAGE_BG};
                --panel-bg      : {PANEL_BG};
                --panel-border  : {PANEL_BORDER};
                --font-main     : {FONT_MAIN_COLOR};
                --layout-gap    : {LAYOUT_GAP};
                --outer-pad     : {LAYOUT_OUTER_PAD};
                --min-height    : {LAYOUT_MIN_HEIGHT};
                --charts-row-flex: {CHARTS_ROW_FLEX};
                --charts-ts-flex : {CHARTS_TS_FLEX};
                --map-min-height: {MAP_MIN_HEIGHT};
                --map-flex      : {MAP_FLEX};
                --pyramid-flex  : {PYRAMID_FLEX};
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