# app/db.py
"""
In-memory DuckDB singleton.

Loads all tables from the file DB into an in-memory DuckDB instance at import
time, then creates v_census and v_map_metrics on top. All figure builders query
the in-memory connection via get_con() — no file I/O on any subsequent call.

Startup cost: ~1-2s on first import. All queries after that run against RAM.
"""

import duckdb as ddb
from app.config import DB_PATH



_DB_FILE = DB_PATH

_TABLES = [
    "d_prefectures",
    "d_age_groups",
    "d_sex",
    "d_years",
    "f_census",
]

_V_CENSUS = """
CREATE OR REPLACE VIEW v_census AS
SELECT
    f.year,
    p.area_estat,
    p.prefecture_name_ja,
    p.prefecture_name,
    p.level         AS area_level,
    p.parent_estat,
    a.age_group,
    a.age_start,
    a.age_end,
    a.is_open_ended,
    a.source_scheme AS age_scheme,
    s.sex,
    s.sex_ja,
    f.population
FROM f_census f
JOIN d_prefectures p ON f.area_estat    = p.area_estat
JOIN d_age_groups  a ON f.age_group_id  = a.age_group_id
JOIN d_sex         s ON f.sex_id        = s.sex_id
"""

_V_MAP_METRICS = """
CREATE OR REPLACE VIEW v_map_metrics AS
WITH age_buckets AS (
    SELECT
        year,
        area_estat,
        prefecture_name,
        prefecture_name_ja,
        SUM(CASE WHEN age_start >= 0  AND age_end <= 14 THEN population ELSE 0 END) AS pop_0_14,
        SUM(CASE WHEN age_start >= 15 AND age_end <= 64 THEN population ELSE 0 END) AS pop_15_64,
        SUM(CASE WHEN age_start >= 65                   THEN population ELSE 0 END) AS pop_65_plus,
        SUM(population)                                                              AS population
    FROM v_census
    WHERE age_scheme  = 'scheme_a'
      AND age_group  != 'Total'
      AND sex         = 'total'
      AND area_level  = 2
    GROUP BY year, area_estat, prefecture_name, prefecture_name_ja
),
metrics AS (
    SELECT *,
        ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14,    0), 1) AS aging_index,
        ROUND(pop_65_plus * 100.0 / NULLIF(pop_15_64,   0), 1) AS old_age_dep,
        ROUND(pop_15_64   * 100.0 / NULLIF(population,  0), 1) AS working_age_share
    FROM age_buckets
),
with_prev AS (
    SELECT
        m.*,
        LAG(m.year)              OVER (PARTITION BY m.area_estat ORDER BY m.year) AS prev_year,
        LAG(m.population)        OVER (PARTITION BY m.area_estat ORDER BY m.year) AS prev_population,
        LAG(m.aging_index)       OVER (PARTITION BY m.area_estat ORDER BY m.year) AS prev_aging_index,
        LAG(m.old_age_dep)       OVER (PARTITION BY m.area_estat ORDER BY m.year) AS prev_old_age_dep,
        LAG(m.working_age_share) OVER (PARTITION BY m.area_estat ORDER BY m.year) AS prev_working_age_share
    FROM metrics m
)
SELECT
    area_estat,
    prefecture_name,
    prefecture_name_ja,
    year,
    population,
    aging_index,
    old_age_dep,
    working_age_share,
    (population   - prev_population)                       AS pop_delta,
    ROUND(aging_index       - prev_aging_index,       1)   AS aging_index_delta,
    ROUND(old_age_dep       - prev_old_age_dep,       1)   AS old_age_dep_delta,
    ROUND(working_age_share - prev_working_age_share, 1)   AS working_age_share_delta,
    prev_year,
    (year - prev_year) AS year_gap
FROM with_prev
ORDER BY year, area_estat
"""


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

    mem_con.execute(_V_CENSUS)
    mem_con.execute(_V_MAP_METRICS)

    row_count = mem_con.execute("SELECT COUNT(*) FROM v_census").fetchone()[0]
    print(f"  In-memory DB ready — v_census: {row_count:,} rows")

    return mem_con


# Module-level singleton — runs once on first import, cached for app lifetime
_CON: ddb.DuckDBPyConnection = _init_memory_db()


def get_con() -> ddb.DuckDBPyConnection:
    """Return the shared in-memory DuckDB connection."""
    return _CON