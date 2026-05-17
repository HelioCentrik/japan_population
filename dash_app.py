# dash_app.py
import dash
from app.aesthetics.index_string import INDEX_STRING
from app.aesthetics.plotly_template import register_plotly_template

app = dash.Dash(__name__, title="少子高齢化 A Century of Japan's Population")
app.index_string = INDEX_STRING
register_plotly_template()
server = app.server
