# app/kpi.py
from functools import lru_cache

from dash import html

from app.config import (
    ACCENT_DANKAI_JR, COLOR_WARNING,
    PYRAMID_MALE_COLOR, PYRAMID_FEMALE_COLOR,
)
from app.db import get_con


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
            ROUND(pop_0_14    * 100.0 / NULLIF(pop_total, 0), 1) AS children_share
        FROM age_buckets
    """).fetchone()

    # ── Most / least aged prefecture ─────────────────────────────────────────
    most = con.execute(f"""
        SELECT prefecture_name_ja, prefecture_name, aging_index
        FROM v_map_metrics WHERE year = {year}
        ORDER BY aging_index DESC LIMIT 1
    """).fetchone()

    least = con.execute(f"""
        SELECT prefecture_name_ja, prefecture_name, aging_index
        FROM v_map_metrics WHERE year = {year}
        ORDER BY aging_index ASC LIMIT 1
    """).fetchone()

    return {
        "national_pop":    national_pop,
        "pop_delta":       pop_delta,
        "prev_year":       prev_year,
        "aging_index":     float(row[0]) if row[0] is not None else None,
        "children_share":  float(row[1]) if row[1] is not None else None,
        "most_aged_ja":    most[0]  if most  else "—",
        "most_aged_en":    most[1]  if most  else "—",
        "most_aged_val":   float(most[2])  if most  and most[2]  is not None else None,
        "least_aged_ja":   least[0] if least else "—",
        "least_aged_en":   least[1] if least else "—",
        "least_aged_val":  float(least[2]) if least and least[2] is not None else None,
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
            "年少人口  Children 0–14",
            _fmt_one(kpi["children_share"], "%"),
        ),
        _card(
            "最高齢化  Most Aged Prefecture",
            kpi["most_aged_ja"],
            sub=html.Span([
                kpi["most_aged_en"],
                html.Span(f"  ·  {_fmt_one(kpi['most_aged_val'])}",
                          style={"color": "var(--color-text-hi)"}),
            ]),
        ),
        _card(
            "最少齢化  Least Aged Prefecture",
            kpi["least_aged_ja"],
            sub=html.Span([
                kpi["least_aged_en"],
                html.Span(f"  ·  {_fmt_one(kpi['least_aged_val'])}",
                          style={"color": "var(--color-text-hi)"}),
            ]),
        ),
    ]