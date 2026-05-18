# app/viz/kpi.py
from functools import lru_cache

from dash import html

from app.aesthetics.config import (
    ACCENT_DANKAI_JR, COLOR_WARNING,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
    TFR_CUTOFF_YEAR, MIGRATION_CUTOFF_YEAR,
)
from app.data.db import get_con


@lru_cache(maxsize=32)
def build_kpi_data(year: int) -> dict:
    con = get_con()

    # ── Previous census year ──────────────────────────────────────────────────
    prev_row = con.execute(f"""
        SELECT MAX(year) FROM d_years WHERE year < {year}
    """).fetchone()
    prev_year = int(prev_row[0]) if prev_row[0] is not None else None

    # ── National population (Total row) ──────────────────────────────────────
    pop_row = con.execute(f"""
        SELECT SUM(population)
        FROM v_census
        WHERE year = {year} AND age_group = 'Total'
          AND sex = 'total' AND area_level = 2
    """).fetchone()
    national_pop = int(pop_row[0]) if pop_row[0] is not None else None

    # ── Pop delta vs previous census ─────────────────────────────────────────
    pop_delta = None
    if prev_year is not None:
        prev_pop_row = con.execute(f"""
            SELECT SUM(population)
            FROM v_census
            WHERE year = {prev_year} AND age_group = 'Total'
              AND sex = 'total' AND area_level = 2
        """).fetchone()
        if prev_pop_row[0] is not None and national_pop is not None:
            pop_delta = national_pop - int(prev_pop_row[0])

    # ── Age bucket metrics ────────────────────────────────────────────────────
    row = con.execute(f"""
        WITH age_buckets AS (
            SELECT
                SUM(CASE WHEN age_start >= 0  AND age_end <= 14 THEN population ELSE 0 END) AS pop_0_14,
                SUM(CASE WHEN age_start >= 15 AND age_end <= 64 THEN population ELSE 0 END) AS pop_15_64,
                SUM(CASE WHEN age_start >= 65                   THEN population ELSE 0 END) AS pop_65_plus,
                SUM(population)                                                              AS pop_total
            FROM v_census
            WHERE year = {year} AND age_scheme = 'scheme_a'
              AND age_group != 'Total' AND sex = 'total' AND area_level = 2
        )
        SELECT
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14,  0), 1) AS aging_index,
            ROUND(pop_0_14    * 100.0 / NULLIF(pop_total, 0), 1) AS children_share,
            ROUND(pop_15_64   * 100.0 / NULLIF(pop_total, 0), 1) AS working_age_share
        FROM age_buckets
    """).fetchone()

    # ── TFR — national average of prefecture values for this census year ──────
    # f_tfr has no national aggregate row; average all prefectures.
    # Returns None pre-1960 (no coverage).
    tfr_val = None
    if year >= TFR_CUTOFF_YEAR:
        tfr_row = con.execute(f"""
            SELECT ROUND(AVG(tfr), 2)
            FROM f_tfr
            WHERE year = {year}
        """).fetchone()
        tfr_val = float(tfr_row[0]) if tfr_row[0] is not None else None

    # ── Most migrated-to prefecture ───────────────────────────────────────────
    # f_migration census_year coverage: 1985–2020. Returns None outside that.
    migrated_ja  = None
    migrated_en  = None
    migrated_net = None
    if year >= MIGRATION_CUTOFF_YEAR:
        mig_row = con.execute(f"""
            SELECT p.prefecture_name_ja, p.prefecture_name, m.net_migration
            FROM f_migration m
            JOIN d_prefectures p ON p.area_estat = m.area_estat
            WHERE m.census_year = {year}
              AND m.net_migration IS NOT NULL
            ORDER BY m.net_migration DESC
            LIMIT 1
        """).fetchone()
        if mig_row:
            migrated_ja  = mig_row[0]
            migrated_en  = mig_row[1]
            migrated_net = int(mig_row[2])

    return {
        "national_pop":       national_pop,
        "pop_delta":          pop_delta,
        "prev_year":          prev_year,
        "aging_index":        float(row[0]) if row[0] is not None else None,
        "working_age_share":  float(row[2]) if row[2] is not None else None,
        "tfr":                tfr_val,
        "migrated_ja":        migrated_ja,
        "migrated_en":        migrated_en,
        "migrated_net":       migrated_net,
    }


def _card(label: str, value, sub=None) -> html.Div:
    """
    Single KPI card.
    Always renders all 3 grid rows so the CSS grid anchor stays consistent.
    `value` may be a string or a Dash component (e.g. html.Span with color).
    """
    return html.Div([
        html.Div(label,                          className="kpi-label"),
        html.Div(value,                          className="kpi-value"),
        html.Div(sub if sub is not None else "", className="kpi-sub"),
    ], className="card")


def render_kpi_cards(kpi: dict, era_label: str = "") -> list:
    def _fmt_pop(v):
        return f"{v:,}" if v is not None else "—"

    def _fmt_one(v, suffix=""):
        return f"{v:.1f}{suffix}" if v is not None else "—"

    # Population delta — colored span, signed number
    if kpi["pop_delta"] is not None:
        delta      = kpi["pop_delta"]
        sign       = "+" if delta >= 0 else ""
        color      = ACCENT_DANKAI_JR if delta >= 0 else COLOR_WARNING
        delta_val  = html.Span(f"{sign}{delta:,}", style={"color": color})
        delta_sub  = f"from {kpi['prev_year']}" if kpi["prev_year"] else ""
    else:
        delta_val = "—"
        delta_sub = ""

    # ── Card 4: Working-Age Share ─────────────────────────────────────────────
    working_age_share = kpi["working_age_share"]

    # ── Card 5: TFR ───────────────────────────────────────────────────────────
    tfr = kpi["tfr"]
    tfr_val_str = f"{tfr:.2f}" if tfr is not None else "—"

    # ── Card 6: Most Migrated-To Prefecture ───────────────────────────────────
    mig_ja  = kpi["migrated_ja"]
    mig_en  = kpi["migrated_en"]
    mig_net = kpi["migrated_net"]

    if mig_ja is not None and mig_net is not None:
        sign = "+" if mig_net >= 0 else ""
        mig_sub = html.Span([
            mig_en,
            html.Span(f"  ·  {sign}{mig_net:,}", style={"color": "var(--color-text-hi)"}),
        ])
    else:
        mig_sub = None

    return [
        _card(
            "国民人口  National Population",
            _fmt_pop(kpi["national_pop"]),
            sub=era_label,
        ),
        _card(
            "人口増減  Population Change",
            delta_val,
            sub=delta_sub,
        ),
        _card(
            "高齢化指数  Aging Index",
            _fmt_one(kpi["aging_index"]),
        ),
        _card(
            "生産年齢人口  Working-Age Share",
            _fmt_one(working_age_share, "%"),
        ),
        _card(
            "合計特殊出生率  TFR",
            tfr_val_str,
            sub="replacement: 2.10" if tfr is not None else None,
        ),
        _card(
            "転入超過  Most Migrated-To",
            mig_ja if mig_ja is not None else "—",
            sub=mig_sub,
        ),
    ]
