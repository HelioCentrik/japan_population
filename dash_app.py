# dash_app.py
import os

import dash
from flask import send_from_directory

from app.aesthetics.index_string import INDEX_STRING
from app.aesthetics.plotly_template import register_plotly_template

app = dash.Dash(__name__, title="少子高齢化 A Century of Japan's Population")
app.index_string = INDEX_STRING
register_plotly_template()
server = app.server

DOCS_DIR = os.path.join(os.path.dirname(__file__), 'docs')

@server.route('/docs/<path:filename>')
def serve_docs(filename):
    return send_from_directory(DOCS_DIR, filename)