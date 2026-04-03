# app/kpi.py
from functools import lru_cache

from dash import html

from app.db import get_con



@lru_cache(maxsize=32)
def build_kpi_data(year: int) -> dict:
    """
    Computes the six KPI values for a given census year.
    Cached on year — queries only run once per year per session.
    """
    con = get_con()

    # ── National population — from pre-stored Total row ───────────────────────
    pop_row = con.execute(f"""
        SELECT SUM(population) AS national_pop
        FROM v_census
        WHERE year       = {year}
          AND age_group  = 'Total'
          AND sex        = 'total'
          AND area_level = 2
    """).fetchone()

    # ── Four scalar national metrics via age_buckets CTE ─────────────────────
    row = con.execute(f"""
        WITH age_buckets AS (
            SELECT
                SUM(CASE WHEN age_start >= 0  AND age_end <= 14 THEN population ELSE 0 END)  AS pop_0_14,
                SUM(CASE WHEN age_start >= 15 AND age_end <= 64 THEN population ELSE 0 END)  AS pop_15_64,
                SUM(CASE WHEN age_start >= 65                   THEN population ELSE 0 END)  AS pop_65_plus,
                SUM(population)                                                               AS pop_total
            FROM v_census
            WHERE year       = {year}
              AND age_scheme  = 'scheme_a'
              AND age_group  != 'Total'
              AND sex         = 'total'
              AND area_level  = 2
        )
        SELECT
            pop_total,
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14,   0), 1)  AS aging_index,
            ROUND(pop_65_plus * 100.0 / NULLIF(pop_15_64,  0), 1)  AS old_age_dep,
            ROUND(pop_15_64   * 100.0 / NULLIF(pop_total,  0), 1)  AS working_age_share
        FROM age_buckets
    """).fetchone()

    # ── Most/least aged prefecture — reuse v_map_metrics ─────────────────────
    most = con.execute(f"""
        SELECT prefecture_name_ja, prefecture_name, aging_index
        FROM v_map_metrics
        WHERE year = {year}
        ORDER BY aging_index DESC
        LIMIT 1
    """).fetchone()

    least = con.execute(f"""
        SELECT prefecture_name_ja, prefecture_name, aging_index
        FROM v_map_metrics
        WHERE year = {year}
        ORDER BY aging_index ASC
        LIMIT 1
    """).fetchone()

    return {
        "national_pop":      int(pop_row[0]) if pop_row[0] is not None else None,
        "aging_index":       float(row[0])   if row[0]     is not None else None,
        "old_age_dep":       float(row[1])   if row[1]     is not None else None,
        "working_age_share": float(row[2])   if row[2]     is not None else None,
        "most_aged_ja":      most[0]  if most  else "—",
        "most_aged_en":      most[1]  if most  else "—",
        "most_aged_val":     float(most[2])  if most  and most[2]  is not None else None,
        "least_aged_ja":     least[0] if least else "—",
        "least_aged_en":     least[1] if least else "—",
        "least_aged_val":    float(least[2]) if least and least[2] is not None else None,
    }


def _card(label: str, value: str, sub: str | None = None) -> html.Div:
    """Single KPI card — label / value / optional sub-label."""
    children = [
        html.Div(label, className="kpi-label"),
        html.Div(value, className="kpi-value"),
    ]
    if sub:
        children.append(html.Div(sub, className="kpi-sub"))
    return html.Div(children, className="card")


def render_kpi_cards(kpi: dict) -> list:
    """
    Returns a list of six html.Div cards.
    Pass directly as children of the KPI row container in app.py.
    """
    def _fmt_pop(v):
        return f"{v:,}" if v is not None else "—"

    def _fmt_one(v, suffix=""):
        return f"{v:.1f}{suffix}" if v is not None else "—"

    return [
        _card(
            "国民人口  National Population",
            _fmt_pop(kpi["national_pop"]),
        ),
        _card(
            "高齢化指数  Aging Index",
            _fmt_one(kpi["aging_index"]),
        ),
        _card(
            "老年従属人口指数  Old-Age Dependency",
            _fmt_one(kpi["old_age_dep"], "%"),
        ),
        _card(
            "生産年齢人口割合  Working-Age Share",
            _fmt_one(kpi["working_age_share"], "%"),
        ),
        _card(
            "最高齢化  Most Aged Prefecture",
            kpi["most_aged_ja"],
            sub=f"{kpi['most_aged_en']}  ·  {_fmt_one(kpi['most_aged_val'])}",
        ),
        _card(
            "最少齢化  Least Aged Prefecture",
            kpi["least_aged_ja"],
            sub=f"{kpi['least_aged_en']}  ·  {_fmt_one(kpi['least_aged_val'])}",
        ),
    ]