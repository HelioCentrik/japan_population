# app/index_string.py
from app.config import PAGE_BG, PANEL_BG, PANEL_BORDER, FONT_MAIN_COLOR

INDEX_STRING = f'''<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            :root {{
                --page-bg: {PAGE_BG};
                --panel-bg: {PANEL_BG};
                --panel-border: {PANEL_BORDER};
                --font-main: {FONT_MAIN_COLOR};
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