# app/db.py
"""
In-memory DuckDB singleton.

Loads all tables from the file DB into an in-memory DuckDB instance at import
time, then creates v_census and v_map_metrics on top. All figure builders query
the in-memory connection via get_con() — no file I/O on any subsequent call.

Startup cost: ~1-2s on first import. All queries after that run against RAM.
"""

import duckdb as ddb
from app.utils import DB_PATH
from app.sql import V_CENSUS, V_MAP_METRICS



_DB_FILE = DB_PATH

_TABLES = [
    "d_prefectures",
    "d_age_groups",
    "d_sex",
    "d_years",
    "f_census",
]


def _init_memory_db() -> ddb.DuckDBPyConnection:
    if not _DB_FILE.exists():
        raise FileNotFoundError(
            f"Database not found at {_DB_FILE}. "
            "Run scripts/build_db.py to generate it."
        )

    print(f"Loading {_DB_FILE.name} into memory ...")
    file_con = ddb.connect(str(_DB_FILE), read_only=True)
    mem_con  = ddb.connect(":memory:")

    for table in _TABLES:
        df = file_con.execute(f"SELECT * FROM {table}").df()
        mem_con.register(f"_src_{table}", df)
        mem_con.execute(f"CREATE TABLE {table} AS SELECT * FROM _src_{table}")
        mem_con.unregister(f"_src_{table}")

    file_con.close()

    mem_con.execute(V_CENSUS)
    mem_con.execute(V_MAP_METRICS)

    row_count = mem_con.execute("SELECT COUNT(*) FROM v_census").fetchone()[0]
    print(f"  In-memory DB ready — v_census: {row_count:,} rows")

    return mem_con


# Module-level singleton — runs once on first import, cached for app lifetime
_CON: ddb.DuckDBPyConnection = _init_memory_db()


def get_con() -> ddb.DuckDBPyConnection:
    """Return the shared in-memory DuckDB connection."""
    return _CON