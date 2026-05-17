# main.py
import startup        # computes CENSUS_YEARS, YEAR_LABELS etc. — side effect
import layout         # sets app.layout — side effect
import callbacks      # registers all @app.callback decorators — side effect
import prewarm        # warms figure cache — side effect
from dash_app import server  # noqa: F401 — exposed for Gunicorn
if __name__ == "__main__":
    from dash_app import app
    app.run(debug=False)
