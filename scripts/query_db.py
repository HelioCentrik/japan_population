# scripts/query_db.py
import duckdb as ddb



con = ddb.connect("../data/japan_population.duckdb")

# ---- UPDATE RECORDS -----------------------------
view_census = con.execute("""
    CREATE OR REPLACE VIEW v_census AS
    SELECT cen.year,
        pref.area_estat,
        pref.prefecture_name_ja,
        pref.prefecture_name,
        pref.level AS area_level,
        pref.parent_estat,
        age.age_group,
        age.age_start,
        age.age_end,
        age.is_open_ended,
        age.source_scheme AS age_scheme,
        sex.sex,
        sex.sex_ja,
        cen.population
    FROM f_census cen
        INNER JOIN d_prefectures pref
            ON cen.area_estat = pref.area_estat
        INNER JOIN d_age_groups age
            ON cen.age_group_id = age.age_group_id
        INNER JOIN d_sex sex
            ON cen.sex_id = sex.sex_id
""").df()
print(f"\nCensus view columns:\n{view_census.columns}\n"
      f"{len(view_census.values)} records.")
for i, v in enumerate(view_census.values):
    if i < 20:
        print(v)

# con.execute("""
#       ALTER TABLE d_prefectures
#       ADD PRIMARY KEY (area_estat);
# """)




# ---- SELECT DB OBJECTS --------------------------
# # -- Constraints --
# cons = con.execute("""
#     SELECT constraint_name,
#         table_name,
#         constraint_column_names
#     FROM duckdb_constraints;
# """).fetchdf()
# print(f"\nconstraints:\n"
#       f"Columns: {cons.columns}")
# for c in list(cons.values):
#     print(c)

# # -- Indexes --
# idxs = con.execute("""
#       SELECT index_name,
#             table_name,
#             expressions
#       FROM duckdb_indexes;
# """).fetchdf()
# print(f"\nindexes:\n"
#       f"Columns: {idxs.columns}")
# for i in list(idxs.values):
#     print(i)

# -- Tables --
tbls = con.execute("""
      SELECT table_name,
            estimated_size,
            column_count,
            index_count
      FROM duckdb_tables;
""").fetchdf()
print(f"\ntables:\n"
      f"Columns: {tbls.columns}")
for t in list(tbls.values):
    print(t)

# -- Views --
views = con.execute("""
    SELECT view_name,
        column_count
    FROM duckdb_views;
""").fetchdf()
print(f"\nviews:\n"
      f"Columns: {views.columns}")
for v in list(views.values):
    print(v)




# ---- SELECT DATA -----------------------------
# census_ja_raw = con.execute("SELECT * FROM census_jp_raw").df()
# print(f"\nJapanese census columns: {census_ja_raw.columns}\n"
#       f"{len(census_ja_raw.values)} records.")
# print(census_ja_raw.values)

# fact_census = con.execute("SELECT * FROM f_census").df()
# print(f"\nJapanese census columns: {fact_census.columns}\n"
#       f"{len(fact_census.values)} records.")
# for i, v in enumerate(fact_census.values):
#     if i < 20:
#         print(v)

view_census = con.execute("SELECT * FROM v_census").df()
print(f"\ncensus view columns: {view_census.columns}\n"
      f"{len(view_census.values)} records.")
for i, v in enumerate(view_census.values):
    if i < 20:
        print(v)

# area = con.execute("SELECT * FROM area_dim").df()
# print(f"\nArea columns: {area.columns}\n"
#       f"{len(area.values)} records.")
# print(area.head())

tbl_prefecture = con.execute("SELECT * FROM d_prefectures").df()
print(f"\nPrefecture columns: {tbl_prefecture.columns}\n"
      f"{len(tbl_prefecture.values)} records.")
for v in list(tbl_prefecture.values):
    print(v)

# tbl_age_group = con.execute("SELECT * FROM d_age_groups").df()
# print(f"\nAge group columns: {tbl_age_group.columns}\n"
#       f"{len(tbl_age_group.values)} records.")
# for i, v in enumerate(tbl_age_group.values):
#     if i < 5:
#         print(v)
#
# tbl_sex = con.execute("SELECT * FROM d_sex").df()
# print(f"\nSex columns: {tbl_sex.columns}\n"
#       f"{len(tbl_sex.values)} records.")
# print(tbl_sex.head())
#
# tbl_years = con.execute("SELECT * FROM d_years").df()
# print(f"\nSex columns: {tbl_years.columns}\n"
#       f"{len(tbl_years.values)} records.")
# print(tbl_years.head())

con.close()
