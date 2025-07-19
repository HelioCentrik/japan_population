# scripts/load_jp_census_csv.py
import pandas as pd
import duckdb as ddb



# Load historical CSV
df_ja = pd.read_csv("../docs/jp_census_historical_1920_2015.csv", encoding="cp932")
# print(f"\nColumns: {df_ja.columns}")
# for i, d in enumerate(df_ja.values):
#     if i < 10:
#         print(d)

column_map = {
    "都道府県コード": "prefecture_code",
    "都道府県名": "prefecture_name_ja",
    "年齢5歳階級": "age_group_ja",
    "元号": "era_name",
    "和暦（年）": "era_year",
    "西暦（年）": "year",
    "人口（総数）": "total_population",
    "人口（男）": "male_population",
    "人口（女）": "female_population"
}
df = df_ja.rename(columns=column_map)

prefecture_translation = {
    "北海道": "Hokkaido",
    "青森県": "Aomori",
    "岩手県": "Iwate",
    "宮城県": "Miyagi",
    "秋田県": "Akita",
    "山形県": "Yamagata",
    "福島県": "Fukushima",
    "茨城県": "Ibaraki",
    "栃木県": "Tochigi",
    "群馬県": "Gunma",
    "埼玉県": "Saitama",
    "千葉県": "Chiba",
    "東京都": "Tokyo",
    "神奈川県": "Kanagawa",
    "新潟県": "Niigata",
    "富山県": "Toyama",
    "石川県": "Ishikawa",
    "福井県": "Fukui",
    "山梨県": "Yamanashi",
    "長野県": "Nagano",
    "岐阜県": "Gifu",
    "静岡県": "Shizuoka",
    "愛知県": "Aichi",
    "三重県": "Mie",
    "滋賀県": "Shiga",
    "京都府": "Kyoto",
    "大阪府": "Osaka",
    "兵庫県": "Hyogo",
    "奈良県": "Nara",
    "和歌山県": "Wakayama",
    "鳥取県": "Tottori",
    "島根県": "Shimane",
    "岡山県": "Okayama",
    "広島県": "Hiroshima",
    "山口県": "Yamaguchi",
    "徳島県": "Tokushima",
    "香川県": "Kagawa",
    "愛媛県": "Ehime",
    "高知県": "Kochi",
    "福岡県": "Fukuoka",
    "佐賀県": "Saga",
    "長崎県": "Nagasaki",
    "熊本県": "Kumamoto",
    "大分県": "Oita",
    "宮崎県": "Miyazaki",
    "鹿児島県": "Kagoshima",
    "沖縄県": "Okinawa"
}

df["prefecture_name"] = df["prefecture_name_ja"].map(prefecture_translation)
df["area_estat"] = df["prefecture_code"].astype(int).mul(1000).astype(str).str.zfill(5)
# print(f"\nCensus columns:\n{df.columns}\n"
#       f"{len(df.values)} records.")
# for i, v in enumerate(df.values):
#     if i < 10:
#         print(v)

# Melt into fact table
fact_df = df.melt(
    id_vars=['area_estat', 'prefecture_code', 'prefecture_name_ja', 'prefecture_name', 'year', 'age_group_ja', 'era_name', 'era_year'],
    value_vars=["total_population", "male_population", "female_population"],
    var_name="sex",
    value_name="population"
)
# Clean sex names
fact_df['sex'] = fact_df['sex'].str.replace('_population', '')


# Build dimension tables (deduplicated)
dim_prefecture = df[['area_estat', 'prefecture_code', 'prefecture_name_ja', 'prefecture_name']].drop_duplicates()
dim_prefecture["prefecture_code"] = dim_prefecture["prefecture_code"].astype(str).str.zfill(2)
dim_prefecture["level"] = 2
dim_prefecture["parent_estat"] = '00000'
# print(f"\nPrefectures (en):\n{dim_prefecture.values}")

# Define age group mapping with start/end, open-endedness, and source scheme
age_group_data = [
    ["総数", "Total", 0, None, True, "base"],
    ["0～4歳", "0–4 years old", 0, 4, False, "scheme_a"],
    ["5～9歳", "5–9 years old", 5, 9, False, "scheme_a"],
    ["10～14歳", "10–14 years old", 10, 14, False, "scheme_a"],
    ["15～19歳", "15–19 years old", 15, 19, False, "scheme_a"],
    ["20～24歳", "20–24 years old", 20, 24, False, "scheme_a"],
    ["25～29歳", "25–29 years old", 25, 29, False, "scheme_a"],
    ["30～34歳", "30–34 years old", 30, 34, False, "scheme_a"],
    ["35～39歳", "35–39 years old", 35, 39, False, "scheme_a"],
    ["40～44歳", "40–44 years old", 40, 44, False, "scheme_a"],
    ["45～49歳", "45–49 years old", 45, 49, False, "scheme_a"],
    ["50～54歳", "50–54 years old", 50, 54, False, "scheme_a"],
    ["55～59歳", "55–59 years old", 55, 59, False, "scheme_a"],
    ["60～64歳", "60–64 years old", 60, 64, False, "scheme_a"],
    ["65～69歳", "65–69 years old", 65, 69, False, "scheme_a"],
    ["70～74歳", "70–74 years old", 70, 74, False, "scheme_a"],
    ["75～79歳", "75–79 years old", 75, 79, False, "scheme_a"],
    ["80歳以上", "80 years and older", 80, None, True, "scheme_a"],
    ["80～84歳", "80–84 years old", 80, 84, False, "scheme_a"],
    ["85歳以上", "85 years and older", 85, None, True, "scheme_a"],
    ["1～5歳", "1–5 years old", 1, 5, False, "scheme_b"],
    ["6～10歳", "6–10 years old", 6, 10, False, "scheme_b"],
    ["11～15歳", "11–15 years old", 11, 15, False, "scheme_b"],
    ["16～20歳", "16–20 years old", 16, 20, False, "scheme_b"],
    ["21～25歳", "21–25 years old", 21, 25, False, "scheme_b"],
    ["26～30歳", "26–30 years old", 26, 30, False, "scheme_b"],
    ["31～35歳", "31–35 years old", 31, 35, False, "scheme_b"],
    ["36～40歳", "36–40 years old", 36, 40, False, "scheme_b"],
    ["41～45歳", "41–45 years old", 41, 45, False, "scheme_b"],
    ["46～50歳", "46–50 years old", 46, 50, False, "scheme_b"],
    ["51～55歳", "51–55 years old", 51, 55, False, "scheme_b"],
    ["56～60歳", "56–60 years old", 56, 60, False, "scheme_b"],
    ["61～65歳", "61–65 years old", 61, 65, False, "scheme_b"],
    ["66～70歳", "66–70 years old", 66, 70, False, "scheme_b"],
    ["71～75歳", "71–75 years old", 71, 75, False, "scheme_b"],
    ["76～80歳", "76–80 years old", 76, 80, False, "scheme_b"],
    ["81～85歳", "81–85 years old", 81, 85, False, "scheme_b"],
    ["86歳以上", "86 years and older", 86, None, True, "scheme_b"],
    ["70歳以上", "70 years and older", 70, None, True, "scheme_b"]
]

dim_age_group = pd.DataFrame(age_group_data, columns=[
    "age_group_ja", "age_group", "age_start", "age_end", "is_open_ended", "source_scheme"
])
dim_age_group['age_group_id'] = dim_age_group.reset_index().index
# print(f"\nAge group Columns:\n{dim_age_group.columns}\n"
#       f"{dim_age_group.values}")

fact_df = fact_df.merge(dim_age_group[['age_group_id', 'age_group_ja']], on='age_group_ja', how='left')

dim_sex = pd.DataFrame({
    "sex_id": [0, 1, 2],
    "sex": ["total", "male", "female"],
    "sex_ja": ["総数", "男", "女"]
})
# print(f"\nSex:\n{dim_sex.values}")

fact_df = fact_df.merge(dim_sex, on='sex', how='left')
# print(f"\nfact columns:\n{fact_df.columns}\n"
#       f"{len(fact_df.values)} records.")
# for i, v in enumerate(fact_df.values):
#     if i < 10:
#         print(v)

dim_years = df[["year", "era_name", "era_year"]].drop_duplicates()
# print(f"\nSex:\n{dim_years.values}")

fact_census = fact_df[[
    'year',
    'area_estat',
    'age_group_id',
    'sex_id',
    'population'
]].copy()
print(f"\ncensus columns:\n{fact_census.columns}\n"
      f"{len(fact_census.values)} records.")
for i, v in enumerate(fact_census.values):
    if i < 10:
        print(v)

# Load into DuckDB
con = ddb.connect("../data/japan_population.duckdb")

# con.execute("CREATE OR REPLACE TABLE census_jp_raw AS SELECT * FROM df_ja")

# con.execute("CREATE OR REPLACE TABLE f_census AS SELECT * FROM fact_census")
# con.execute("CREATE OR REPLACE TABLE d_prefectures AS SELECT area_estat, prefecture_code, prefecture_name_ja, prefecture_name, level, parent_estat FROM dim_prefecture")
# con.execute("CREATE OR REPLACE TABLE d_age_groups AS SELECT age_group_id, age_group_ja, age_group, age_start, age_end, is_open_ended, source_scheme FROM dim_age_group")
# con.execute("CREATE OR REPLACE TABLE d_sex AS SELECT * FROM dim_sex")
# con.execute("CREATE OR REPLACE TABLE d_years AS SELECT * FROM dim_years")

con.close()
