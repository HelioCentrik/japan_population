# startup.py
import duckdb as ddb

con = ddb.connect("data/japan_population.duckdb", read_only=True)
years_df = con.execute(
    "SELECT DISTINCT year, era_name, era_year FROM d_years ORDER BY year"
).df()
PREFECTURE_LOOKUP = {
    row.area_estat: (row.prefecture_name_ja, row.prefecture_name)
    for row in con.execute(
        "SELECT area_estat, prefecture_name_ja, prefecture_name FROM d_prefectures WHERE level = 2"
    ).df().itertuples()
}
con.close()

CENSUS_YEARS = years_df["year"].tolist()
YEAR_LABELS = {
    int(row.year): f"{row.year} ({row.era_name}{row.era_year})"
    for row in years_df.itertuples()
}
YEAR_MIN = min(CENSUS_YEARS)
PLAYBACK_YEARS = [yr for yr in CENSUS_YEARS]
