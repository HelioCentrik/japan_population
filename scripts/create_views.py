# scripts/create_views.py
import duckdb as ddb



con = ddb.connect("../data/japan_population.duckdb")

con.execute("""
    CREATE OR REPLACE VIEW v_map_metrics AS
    WITH age_buckets AS (
        SELECT
            area_estat,
            prefecture_name,
            prefecture_name_ja,
            year,
            SUM(population)                                                             AS population,
            SUM(CASE WHEN age_start >= 65           THEN population ELSE 0 END)         AS pop_65_plus,
            SUM(CASE WHEN age_start <= 10
                      AND age_end   <= 14           THEN population ELSE 0 END)         AS pop_0_14,
            SUM(CASE WHEN age_start >= 15
                      AND age_end   <= 64           THEN population ELSE 0 END)         AS pop_15_64
        FROM v_census
        WHERE age_scheme  = 'scheme_a'
          AND age_group   != 'Total'
          AND sex         = 'total'
          AND area_level  = 2
        GROUP BY area_estat, prefecture_name, prefecture_name_ja, year
    ),
    with_metrics AS (
        SELECT *,
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14,    0), 1) AS aging_index,
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_15_64,   0), 1) AS old_age_dep,
            ROUND(pop_15_64   * 100.0 / NULLIF(population,  0), 1) AS working_age_share
        FROM age_buckets
    ),
    with_lag AS (
        SELECT *,
            LAG(population)         OVER (PARTITION BY area_estat ORDER BY year) AS prev_population,
            LAG(aging_index)        OVER (PARTITION BY area_estat ORDER BY year) AS prev_aging_index,
            LAG(old_age_dep)        OVER (PARTITION BY area_estat ORDER BY year) AS prev_old_age_dep,
            LAG(working_age_share)  OVER (PARTITION BY area_estat ORDER BY year) AS prev_working_age_share,
            LAG(year)               OVER (PARTITION BY area_estat ORDER BY year) AS prev_year
        FROM with_metrics
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
        (population - prev_population)                       AS pop_delta,
        ROUND(aging_index       - prev_aging_index,       1) AS aging_index_delta,
        ROUND(old_age_dep       - prev_old_age_dep,       1) AS old_age_dep_delta,
        ROUND(working_age_share - prev_working_age_share, 1) AS working_age_share_delta,
        prev_year,
        (year - prev_year)                                   AS year_gap
    FROM with_lag
""")

# Sanity check
result = con.execute("""
    SELECT year, prefecture_name, population, aging_index, old_age_dep, working_age_share
    FROM v_map_metrics
    WHERE year = 2015
    ORDER BY aging_index DESC
    LIMIT 5
""").df()
print(f"\nv_map_metrics spot check (2015, top 5 by aging index):\n{result}")

con.close()
print("\nDone. v_map_metrics rebuilt.")