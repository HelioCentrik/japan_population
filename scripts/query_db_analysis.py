# scripts/query_db.py
import duckdb as ddb



con = ddb.connect("../data/japan_population.duckdb")

misc = con.execute("""
SELECT year, population, pop_delta, year_gap
FROM v_map_metrics
WHERE area_estat = '47000'
  AND year BETWEEN 1935 AND 1960
ORDER BY year;
""").df()
print(f"\nmisc:\n{misc.columns}\n"
      f"{len(misc.values)} records.\n"
      f"{misc}")

# row_counts = con.execute("""
#     -- === TABLE ROW COUNTS ===
#     SELECT 'f_census' as tbl, COUNT(*) as rows FROM f_census
#     UNION ALL SELECT 'd_prefectures', COUNT(*) FROM d_prefectures
#     UNION ALL SELECT 'd_age_groups', COUNT(*) FROM d_age_groups
#     UNION ALL SELECT 'd_sex', COUNT(*) FROM d_sex
#     UNION ALL SELECT 'd_years', COUNT(*) FROM d_years;
# """).df()
# print(f"\nrow counts:\n{row_counts.columns}\n"
#       f"{len(row_counts.values)} records.\n"
#       f"{row_counts}")
#
# year_coverage = con.execute("""
#     -- === YEAR COVERAGE ===
#     SELECT DISTINCT year FROM f_census ORDER BY year;
# """).df()
# print(f"\nyears:\n{year_coverage.columns}\n"
#       f"{len(year_coverage.values)} records.\n"
#       f"{year_coverage}")
#
# prefecture_coverage = con.execute("""
#     -- === PREFECTURE COVERAGE PER YEAR ===
#     SELECT year, COUNT(DISTINCT area_estat) as prefecture_count
#     FROM f_census
#     GROUP BY year ORDER BY year;
# """).df()
# print(f"\nprefectures:\n{prefecture_coverage.columns}\n"
#       f"{len(prefecture_coverage.values)} records.\n"
#       f"{prefecture_coverage}")
#
# age_coverage = con.execute("""
#     -- === AGE GROUP COVERAGE PER YEAR ===
#     SELECT year, COUNT(DISTINCT age_group_id) as age_group_count
#     FROM f_census
#     GROUP BY year ORDER BY year;
# """).df()
# print(f"\nages:\n{age_coverage.columns}\n"
#       f"{len(age_coverage.values)} records.\n"
#       f"{age_coverage}")
#
# missing_pop = con.execute("""
#     -- === NULL / MISSING POPULATION CHECK ===
#     SELECT year, COUNT(*) as null_population_rows
#     FROM f_census
#     WHERE population IS NULL
#     GROUP BY year ORDER BY year;
# """).df()
# print(f"\nmissing populations:\n{missing_pop.columns}\n"
#       f"{len(missing_pop.values)} records.\n"
#       f"{missing_pop}")
#
# completeness = con.execute("""
#     -- === COMPLETENESS CHECK: expected vs actual fact rows ===
#     -- Expected = prefectures × age_groups × sex × years
#     SELECT
#         (SELECT COUNT(*) FROM d_prefectures) *
#         (SELECT COUNT(*) FROM d_age_groups) *
#         (SELECT COUNT(*) FROM d_sex) *
#         (SELECT COUNT(*) FROM d_years) AS expected_rows,
#         (SELECT COUNT(*) FROM f_census) AS actual_rows;
# """).df()
# print(f"\ncompleteness:\n{completeness.columns}\n"
#       f"{len(completeness.values)} records.\n"
#       f"{completeness}")
#
# population_range = con.execute("""
#     -- === POPULATION RANGE SANITY CHECK ===
#     SELECT
#         MIN(population) as min_pop,
#         MAX(population) as max_pop,
#         AVG(population) as avg_pop,
#         COUNT(*) FILTER (WHERE population = 0) as zero_rows
#     FROM f_census;
# """).df()
# print(f"\npopulation range:\n{population_range.columns}\n"
#       f"{len(population_range.values)} records.\n"
#       f"{population_range}")
#
# v_census = con.execute("""
#     -- === v_census VIEW SPOT CHECK ===
#     SELECT year, sex, area_level, COUNT(*) as rows
#     FROM v_census
#     WHERE age_group = 'Total'
#     GROUP BY year, sex, area_level
#     ORDER BY year, sex, area_level;
# """).df()
# print(f"\ncensus view:\n{v_census.columns}\n"
#       f"{len(v_census.values)} records.\n"
#       f"{v_census}")

# okinawa_coverage = con.execute("""
#     SELECT year, population
#     FROM v_map_metrics
#     WHERE area_estat = '47000'
#     ORDER BY year
# """).df()
# print(f"\nOkinawa coverage:\n{okinawa_coverage}")
#
# completeness = con.execute("""
#     SELECT year, COUNT(DISTINCT area_estat) AS prefecture_count
#     FROM v_map_metrics
#     GROUP BY year ORDER BY year
# """).df()
# print(f"\nPrefecture count by year:\n{completeness}")

con.close()
