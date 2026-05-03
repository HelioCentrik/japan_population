# scripts/build_db.py
"""
Build japan_population.duckdb from scratch.

Run from the project root:
    python scripts/build_db.py

Loads source/jp_census_historical_1920_2015.csv
  → builds star schema (d_prefectures, d_age_groups, d_sex, d_years, f_census)
  → creates views  (v_census, v_map_metrics)

Idempotent — safe to re-run; all objects are CREATE OR REPLACE.
Called automatically by app.py on startup if the DB file is absent.
"""

import sys
from pathlib import Path

import pandas as pd
import duckdb as ddb

from app.utils import DB_PATH
from app.sql import V_CENSUS, V_MAP_METRICS



# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH     = PROJECT_ROOT / "source" / "jp_census_historical_1920_2015.csv"

# ── Column rename map ─────────────────────────────────────────────────────────
_COL_MAP = {
    "都道府県コード": "prefecture_code",
    "都道府県名":    "prefecture_name_ja",
    "年齢5歳階級":   "age_group_ja",
    "元号":         "era_name",
    "和暦（年）":    "era_year",
    "西暦（年）":    "year",
    "人口（総数）":  "total_population",
    "人口（男）":    "male_population",
    "人口（女）":    "female_population",
}

# ── Prefecture translation (JA → EN) ─────────────────────────────────────────
_PREF_EN = {
    "北海道": "Hokkaido",   "青森県": "Aomori",    "岩手県": "Iwate",
    "宮城県": "Miyagi",     "秋田県": "Akita",     "山形県": "Yamagata",
    "福島県": "Fukushima",  "茨城県": "Ibaraki",   "栃木県": "Tochigi",
    "群馬県": "Gunma",      "埼玉県": "Saitama",   "千葉県": "Chiba",
    "東京都": "Tokyo",      "神奈川県": "Kanagawa", "新潟県": "Niigata",
    "富山県": "Toyama",     "石川県": "Ishikawa",  "福井県": "Fukui",
    "山梨県": "Yamanashi",  "長野県": "Nagano",    "岐阜県": "Gifu",
    "静岡県": "Shizuoka",   "愛知県": "Aichi",     "三重県": "Mie",
    "滋賀県": "Shiga",      "京都府": "Kyoto",     "大阪府": "Osaka",
    "兵庫県": "Hyogo",      "奈良県": "Nara",      "和歌山県": "Wakayama",
    "鳥取県": "Tottori",    "島根県": "Shimane",   "岡山県": "Okayama",
    "広島県": "Hiroshima",  "山口県": "Yamaguchi", "徳島県": "Tokushima",
    "香川県": "Kagawa",     "愛媛県": "Ehime",     "高知県": "Kochi",
    "福岡県": "Fukuoka",    "佐賀県": "Saga",      "長崎県": "Nagasaki",
    "熊本県": "Kumamoto",   "大分県": "Oita",      "宮崎県": "Miyazaki",
    "鹿児島県": "Kagoshima", "沖縄県": "Okinawa",
}

# ── Age group definitions ─────────────────────────────────────────────────────
# [age_group_ja, age_group_en, age_start, age_end, is_open_ended, source_scheme]
# source_scheme values:
#   scheme_a — standard 5-year bands (0-4, 5-9 … 80-84, 85+). Used for all metrics.
#   scheme_b — offset bands (1-5, 6-10 … 81-85, 86+). Present in CSV for 1945.
#   base     — the Total aggregate row only.
_AGE_GROUP_ROWS = [
    ["総数",    "Total",                 0,   None, True,  "base"],
    ["0～4歳",  "0–4 years old",         0,   4,    False, "scheme_a"],
    ["5～9歳",  "5–9 years old",         5,   9,    False, "scheme_a"],
    ["10～14歳","10–14 years old",        10,  14,   False, "scheme_a"],
    ["15～19歳","15–19 years old",        15,  19,   False, "scheme_a"],
    ["20～24歳","20–24 years old",        20,  24,   False, "scheme_a"],
    ["25～29歳","25–29 years old",        25,  29,   False, "scheme_a"],
    ["30～34歳","30–34 years old",        30,  34,   False, "scheme_a"],
    ["35～39歳","35–39 years old",        35,  39,   False, "scheme_a"],
    ["40～44歳","40–44 years old",        40,  44,   False, "scheme_a"],
    ["45～49歳","45–49 years old",        45,  49,   False, "scheme_a"],
    ["50～54歳","50–54 years old",        50,  54,   False, "scheme_a"],
    ["55～59歳","55–59 years old",        55,  59,   False, "scheme_a"],
    ["60～64歳","60–64 years old",        60,  64,   False, "scheme_a"],
    ["65～69歳","65–69 years old",        65,  69,   False, "scheme_a"],
    ["70～74歳","70–74 years old",        70,  74,   False, "scheme_a"],
    ["75～79歳","75–79 years old",        75,  79,   False, "scheme_a"],
    ["80歳以上","80 years and older",     80,  None, True,  "scheme_a"],
    ["80～84歳","80–84 years old",        80,  84,   False, "scheme_a"],
    ["85歳以上","85 years and older",     85,  None, True,  "scheme_a"],
    ["1～5歳",  "1–5 years old",          1,   5,    False, "scheme_b"],
    ["6～10歳", "6–10 years old",         6,   10,   False, "scheme_b"],
    ["11～15歳","11–15 years old",        11,  15,   False, "scheme_b"],
    ["16～20歳","16–20 years old",        16,  20,   False, "scheme_b"],
    ["21～25歳","21–25 years old",        21,  25,   False, "scheme_b"],
    ["26～30歳","26–30 years old",        26,  30,   False, "scheme_b"],
    ["31～35歳","31–35 years old",        31,  35,   False, "scheme_b"],
    ["36～40歳","36–40 years old",        36,  40,   False, "scheme_b"],
    ["41～45歳","41–45 years old",        41,  45,   False, "scheme_b"],
    ["46～50歳","46–50 years old",        46,  50,   False, "scheme_b"],
    ["51～55歳","51–55 years old",        51,  55,   False, "scheme_b"],
    ["56～60歳","56–60 years old",        56,  60,   False, "scheme_b"],
    ["61～65歳","61–65 years old",        61,  65,   False, "scheme_b"],
    ["66～70歳","66–70 years old",        66,  70,   False, "scheme_b"],
    ["71～75歳","71–75 years old",        71,  75,   False, "scheme_b"],
    ["76～80歳","76–80 years old",        76,  80,   False, "scheme_b"],
    ["81～85歳","81–85 years old",        81,  85,   False, "scheme_b"],
    ["86歳以上","86 years and older",     86,  None, True,  "scheme_b"],
    # Okinawa 1950/1955 anomaly: US-administration methodology used open-ended 70+
    # band instead of the standard 70-74 band. Classified scheme_b so it's excluded
    # from scheme_a metrics and doesn't inflate prefecture-level aggregates.
    ["70歳以上","70 years and older",     70,  None, True,  "scheme_b"],
]


# ── Build functions ───────────────────────────────────────────────────────────

def _load_csv() -> pd.DataFrame:
    print(f"  Reading {CSV_PATH.name} ...")
    df = pd.read_csv(CSV_PATH, encoding="cp932")
    df = df.rename(columns=_COL_MAP)
    df["area_estat"]       = df["prefecture_code"].astype(int).mul(1000).astype(str).str.zfill(5)
    df["prefecture_name"]  = df["prefecture_name_ja"].map(_PREF_EN)
    return df


def _build_dim_prefectures(df: pd.DataFrame) -> pd.DataFrame:
    pref = (
        df[["area_estat", "prefecture_code", "prefecture_name_ja", "prefecture_name"]]
        .drop_duplicates()
        .copy()
    )
    pref["prefecture_code"] = pref["prefecture_code"].astype(str).str.zfill(2)
    pref["level"]           = 2
    pref["parent_estat"]    = "00000"

    # Synthetic national aggregate row — not in the CSV (prefecture-only source),
    # but documented in the data dictionary. No f_census rows reference it,
    # so it's reference-only and doesn't affect any metric queries.
    national = pd.DataFrame([{
        "area_estat":         "00000",
        "prefecture_code":    "00",
        "prefecture_name_ja": "全国",
        "prefecture_name":    "Japan",
        "level":              1,
        "parent_estat":       None,
    }])
    return pd.concat([national, pref], ignore_index=True)


def _build_dim_age_groups() -> pd.DataFrame:
    dim = pd.DataFrame(
        _AGE_GROUP_ROWS,
        columns=["age_group_ja", "age_group", "age_start", "age_end",
                 "is_open_ended", "source_scheme"],
    )
    dim["age_group_id"] = dim.index
    return dim


def _build_dim_sex() -> pd.DataFrame:
    return pd.DataFrame({
        "sex_id": [0, 1, 2],
        "sex":    ["total", "male", "female"],
        "sex_ja": ["総数",   "男",   "女"],
    })


def _build_dim_years(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[["year", "era_name", "era_year"]]
        .drop_duplicates()
        .sort_values("year")
        .reset_index(drop=True)
    )


def _build_fact_census(
    df: pd.DataFrame,
    dim_age_groups: pd.DataFrame,
    dim_sex: pd.DataFrame,
) -> pd.DataFrame:
    # Melt total/male/female into a single population column
    melted = df.melt(
        id_vars=["area_estat", "age_group_ja", "year"],
        value_vars=["total_population", "male_population", "female_population"],
        var_name="sex",
        value_name="population",
    )
    melted["sex"] = melted["sex"].str.replace("_population", "", regex=False)

    # Resolve foreign keys
    melted = melted.merge(dim_age_groups[["age_group_id", "age_group_ja"]], on="age_group_ja", how="left")
    melted = melted.merge(dim_sex[["sex_id", "sex"]], on="sex", how="left")

    unmatched = melted["age_group_id"].isna().sum()
    if unmatched:
        raise ValueError(f"{unmatched} rows could not be matched to d_age_groups — check _AGE_GROUP_ROWS")

    return melted[["year", "area_estat", "age_group_id", "sex_id", "population"]].copy()


def _write_tables(con: ddb.DuckDBPyConnection, tables: dict[str, pd.DataFrame]) -> None:
    for name, df in tables.items():
        # Register the DataFrame so DuckDB can reference it in a SELECT
        con.register(f"_df_{name}", df)
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM _df_{name}")
        con.unregister(f"_df_{name}")
        count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"    {name}: {count:,} rows")


def _create_views(con: ddb.DuckDBPyConnection) -> None:
    con.execute(V_CENSUS)
    row_count = con.execute("SELECT COUNT(*) FROM v_census").fetchone()[0]
    print(f"    v_census: {row_count:,} rows")

    con.execute(V_MAP_METRICS)
    row_count = con.execute("SELECT COUNT(*) FROM v_map_metrics").fetchone()[0]
    print(f"    v_map_metrics: {row_count:,} rows")


# ── Entry point ───────────────────────────────────────────────────────────────

def build():
    """
    Full build: CSV → star schema → views.
    Called directly or from app.py on first startup.
    """
    if not CSV_PATH.exists():
        sys.exit(
            f"ERROR: source CSV not found at {CSV_PATH}\n"
            "Download it from e-Stat (stat ID 000031523105) and place it at that path."
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Building japan_population.duckdb ...")

    print("  Loading CSV ...")
    df = _load_csv()

    print("  Building dimension tables ...")
    dim_age_groups  = _build_dim_age_groups()
    dim_sex         = _build_dim_sex()
    dim_prefectures = _build_dim_prefectures(df)
    dim_years       = _build_dim_years(df)

    print("  Building fact table ...")
    fact_census = _build_fact_census(df, dim_age_groups, dim_sex)

    print("  Writing to DuckDB ...")
    con = ddb.connect(str(DB_PATH))
    _write_tables(con, {
        "d_prefectures": dim_prefectures,
        "d_age_groups":  dim_age_groups,
        "d_sex":         dim_sex,
        "d_years":       dim_years,
        "f_census":      fact_census,
    })

    print("  Creating views ...")
    _create_views(con)

    con.close()
    print(f"Done. DB written to {DB_PATH}")


if __name__ == "__main__":
    build()