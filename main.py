# main.py
import threading

import startup    # computes CENSUS_YEARS, YEAR_LABELS etc. — side effect
import layout     # sets app.layout — side effect
import callbacks  # registers all @app.callback decorators — side effect
import prewarm    # _prewarm_axis_max computed at import; run() deferred to thread

from dash_app import server  # noqa: F401 — exposed for Gunicorn

# Launch prewarm in the background so the server starts immediately.
# db.py is already loaded (callbacks import triggered it), so the thread
# can safely call figure builders without waiting on the DB singleton.
threading.Thread(target=prewarm.run, daemon=True, name="prewarm").start()

if __name__ == "__main__":
    from dash_app import app
    app.run(debug=False)