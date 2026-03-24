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
            SUM(population)                                                         AS population,
            SUM(CASE WHEN age_start >= 65           THEN population ELSE 0 END)     AS pop_65_plus,
            SUM(CASE WHEN age_start <= 10
                      AND age_end   <= 14           THEN population ELSE 0 END)     AS pop_0_14
        FROM v_census
        WHERE age_scheme  = 'scheme_a'
          AND age_group   != 'Total'
          AND sex         = 'total'
          AND area_level  = 2
        GROUP BY area_estat, prefecture_name, prefecture_name_ja, year
    ),
    with_index AS (
        SELECT *,
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14, 0), 1) AS aging_index
        FROM age_buckets
    ),
    with_lag AS (
        SELECT *,
            LAG(population)     OVER (PARTITION BY area_estat ORDER BY year) AS prev_population,
            LAG(aging_index)    OVER (PARTITION BY area_estat ORDER BY year) AS prev_aging_index,
            LAG(year)           OVER (PARTITION BY area_estat ORDER BY year) AS prev_year
        FROM with_index
    )
    SELECT
        area_estat,
        prefecture_name,
        prefecture_name_ja,
        year,
        population,
        aging_index,
        (population - prev_population)          AS pop_delta,
        ROUND(aging_index - prev_aging_index, 1) AS aging_index_delta,
        prev_year,
        (year - prev_year)                      AS year_gap
    FROM with_lag
""")

# Sanity check
result = con.execute("""
    SELECT year, prefecture_name, population, aging_index, pop_delta, aging_index_delta, prev_year, year_gap
    FROM v_map_metrics
    WHERE year = 2015
    ORDER BY aging_index DESC
    LIMIT 10
""").df()
print(f"\nv_map_metrics spot check (2015, top 10 by aging index):\n{result}")

# Check 1920 NULLs are behaving
nullcheck = con.execute("""
    SELECT year, COUNT(*) as rows, COUNT(pop_delta) as non_null_deltas
    FROM v_map_metrics
    GROUP BY year ORDER BY year
""").df()
print(f"\nNULL check by year:\n{nullcheck}")

con.close()
print("\nDone. v_map_metrics created.")
