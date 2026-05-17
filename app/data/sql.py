# app/data/sql.py
"""
Shared SQL view definitions.

Single source of truth for v_census and v_map_metrics. Imported by both
app/data/db.py (in-memory singleton) and scripts/build_db.py (file DB build).
Keeping definitions here ensures both consumers always run identical SQL.
"""

# v_census: row-level census data joined to all dimension tables.
#
# Two branches via UNION ALL:
#   1. Standard records — all years and schemes as stored in f_census.
#   2. 1945 kazoedoshi conversion — scheme_b bands remapped to scheme_a
#      equivalents via -1 label shift (e.g. 1-5 → 0-4). Self-join on
#      d_age_groups resolves the correct scheme_a label, age_start, age_end,
#      and is_open_ended for each converted band.
#
# Consumers that want standard scheme_a metrics should filter:
#   WHERE age_scheme = 'scheme_a' AND age_group != 'Total'
V_CENSUS = """
CREATE OR REPLACE VIEW v_census AS

-- Standard records: all years, all schemes, as stored
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

UNION ALL

-- 1945 kazoedoshi conversion: scheme_b bands remapped to scheme_a equivalents
-- via -1 label shift (e.g. 1-5 -> 0-4). Self-join on d_age_groups resolves
-- the correct scheme_a label, age_start, age_end, and is_open_ended.
SELECT
    f.year,
    p.area_estat,
    p.prefecture_name_ja,
    p.prefecture_name,
    p.level         AS area_level,
    p.parent_estat,
    a_mapped.age_group,
    a_mapped.age_start,
    a_mapped.age_end,
    a_mapped.is_open_ended,
    'scheme_a'      AS age_scheme,
    s.sex,
    s.sex_ja,
    f.population
FROM f_census      f
JOIN d_prefectures p        ON f.area_estat    = p.area_estat
JOIN d_age_groups  a_b      ON f.age_group_id  = a_b.age_group_id
JOIN d_age_groups  a_mapped ON a_mapped.source_scheme = 'scheme_a'
                           AND a_mapped.age_start     = a_b.age_start - 1
                           AND a_mapped.is_open_ended = a_b.is_open_ended
JOIN d_sex         s        ON f.sex_id        = s.sex_id
WHERE f.year            = 1945
  AND a_b.source_scheme = 'scheme_b'
"""

# v_map_metrics: one row per prefecture × year with pre-computed demographic
# metrics and period-over-period deltas via LAG() window functions.
#
# 1945 is present via the kazoedoshi conversion in v_census, so the LAG()
# window for 1950 correctly references 1945 as prev_year (year_gap = 5).
#
# Okinawa 1950/1955: pop_0_14 / pop_15_64 / pop_65_plus are understated
# because the 70+ band is scheme_b and excluded here. The choropleth
# grey-out in maps.py handles the display side.
V_MAP_METRICS = """
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
        ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14,   0), 1) AS aging_index,
        ROUND(pop_65_plus * 100.0 / NULLIF(pop_15_64,  0), 1) AS old_age_dep,
        ROUND(pop_15_64   * 100.0 / NULLIF(population, 0), 1) AS working_age_share
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
    (population   - prev_population)                     AS pop_delta,
    ROUND(aging_index       - prev_aging_index,       1) AS aging_index_delta,
    ROUND(old_age_dep       - prev_old_age_dep,       1) AS old_age_dep_delta,
    ROUND(working_age_share - prev_working_age_share, 1) AS working_age_share_delta,
    prev_year,
    (year - prev_year) AS year_gap
FROM with_prev
ORDER BY year, area_estat
"""
