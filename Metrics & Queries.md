# Metrics & Queries — Japan Population Dashboard

How to derive demographic metrics from the census star schema. All queries run against `v_census` unless otherwise noted. Always use `age_scheme = 'scheme_a'` for derived metrics. Never use the `Total` age group row in arithmetic — sum individual bands instead.

---

## Derived Metrics

### Aging Index (高齢化指数)

The headline metric. Captures Japan's inversion from child-dominated to elderly-dominated society with an intuitive threshold at 100.

**Formula:** `SUM(pop where age_start >= 65) / SUM(pop where age_end <= 14) × 100`

**National trajectory:** 14.4 (1920) → 13.9 (1950) → 29.4 (1970) → 66.2 (1990) → 91.2 (1995) → 119.1 (2000, first crossing of 100) → ~174 (2010) → ~211 (2015)
```sql
SELECT area_estat, prefecture_name, prefecture_name_ja,
    ROUND(
        SUM(CASE WHEN age_start >= 65 THEN population ELSE 0 END) * 100.0 /
        NULLIF(SUM(CASE WHEN age_start <= 10 AND age_end <= 14 THEN population ELSE 0 END), 0)
    , 1) AS aging_index
FROM v_census
WHERE year = {year}
  AND age_scheme = 'scheme_a'
  AND age_group != 'Total'
  AND sex = 'total'
  AND area_level = 2
GROUP BY area_estat, prefecture_name, prefecture_name_ja
ORDER BY aging_index DESC
```

---

### Old-Age Dependency Ratio (老年従属人口指数)

Quantifies the economic burden shift. Crossed youth dependency between 1995 and 2000.

**Formula:** `SUM(pop 65+) / SUM(pop 15–64) × 100`

**National trajectory:** ~8.6 (1920) → ~8.3 (1950) → ~10.3 (1970) → ~17.1 (1990) → 25.5 (2000) → ~43.5 (2015)

This metric is computed in `v_map_metrics` and used in KPI cards, but is **not** a selectable map metric — replaced by Population Change (`pop_delta`). Do not add it back to `MAP_METRICS` in `config.py`.

---

### Youth Dependency Ratio (年少従属人口指数)

**Formula:** `SUM(pop 0–14) / SUM(pop 15–64) × 100`

**National trajectory:** ~63.0 (1920) → ~59.3 (1950) → ~35.2 (1970) → 21.4 (2000) → ~20.6 (2015)

---

### Total Dependency Ratio (従属人口指数)

U-shaped curve: high in 1920 (driven by youth), minimum ~43.5 in 1990, rising again by 2015 (driven by elderly). The trough is Japan's demographic dividend period.

**Formula:** `(SUM(pop 0–14) + SUM(pop 65+)) / SUM(pop 15–64) × 100`

---

### Working-Age Share (生産年齢人口割合)

**Formula:** `SUM(pop 15–64) / SUM(total pop) × 100`

**National trajectory:** Peaked at ~69.5% in 1990–1995, declining since.

---

### Children 0–14 Share (年少人口割合)

Share of the population in the youngest cohort. Used in KPI cards.

**Formula:** `SUM(pop 0–14) / total pop × 100`

**National trajectory:** ~36.5% (1920) → ~35.4% (1950) → ~24.0% (1970) → ~14.6% (2000) → ~12.9% (2015)

---

### Sex Ratio by Age Band (性比)

**Formula:** `male_pop / female_pop × 100` per age band

In 1950, the 25–29 band had a sex ratio of 83.8 (vs. natural ~103). The WWII notch walks up the pyramid at 5 years per census, reaching 55–59 by 1975 (ratio 79.7 — the dataset minimum). See `Annotations.md` for UI treatment.
```sql
SELECT age_group, age_start,
    SUM(CASE WHEN sex = 'male'   THEN population END) AS male_pop,
    SUM(CASE WHEN sex = 'female' THEN population END) AS female_pop,
    ROUND(
        SUM(CASE WHEN sex = 'male' THEN population END) * 100.0 /
        NULLIF(SUM(CASE WHEN sex = 'female' THEN population END), 0)
    , 1) AS sex_ratio
FROM v_census
WHERE year = {year}
  AND age_scheme = 'scheme_a'
  AND age_group != 'Total'
  AND sex != 'total'
  AND area_level = 2
GROUP BY age_group, age_start
ORDER BY age_start
```

---

## Reusable CTE — Age Bucket Aggregation

Base pattern for computing all dependency ratios in a single pass. Use this for KPI cards and time series.
```sql
WITH age_buckets AS (
    SELECT year, area_estat, prefecture_name, prefecture_name_ja,
        SUM(CASE WHEN age_start >= 0  AND age_end <= 14 THEN population ELSE 0 END) AS pop_0_14,
        SUM(CASE WHEN age_start >= 15 AND age_end <= 64 THEN population ELSE 0 END) AS pop_15_64,
        SUM(CASE WHEN age_start >= 65                   THEN population ELSE 0 END) AS pop_65_plus,
        SUM(population) AS pop_total
    FROM v_census
    WHERE age_scheme = 'scheme_a'
      AND age_group != 'Total'
      AND sex = 'total'
      AND area_level = 2
    GROUP BY year, area_estat, prefecture_name, prefecture_name_ja
)
SELECT *,
    ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14, 0), 1)                  AS aging_index,
    ROUND(pop_65_plus * 100.0 / NULLIF(pop_15_64, 0), 1)                 AS old_age_dep,
    ROUND(pop_0_14 * 100.0 / NULLIF(pop_15_64, 0), 1)                    AS youth_dep,
    ROUND((pop_0_14 + pop_65_plus) * 100.0 / NULLIF(pop_15_64, 0), 1)    AS total_dep,
    ROUND(pop_15_64 * 100.0 / NULLIF(pop_total, 0), 1)                   AS working_age_share
FROM age_buckets
ORDER BY year, area_estat
```

**65+ bucket:** Filter on `age_start >= 65` — this captures both closed bands and any open-ended terminal band (80+, 85+) regardless of which terminal band a given year uses. Don't filter on `age_end` for the 65+ side.

### Growth Rate Calculation

Intervals are uniform 5-year steps (1920–2020). Always compute annualized growth as:

```
rate = (pop_b / pop_a) ^ (1 / (year_b - year_a)) - 1
```

Never hardcode a 5-year denominator.

---

## Query Cookbook

### Map
```sql
-- Population + aging metrics by prefecture for a given year
-- Use v_map_metrics — pre-aggregated with deltas
SELECT area_estat, population, aging_index, pop_delta, aging_index_delta, prev_year, year_gap
FROM v_map_metrics
WHERE year = {year}
```

### Pyramid — National
```sql
SELECT age_group, age_start, sex, SUM(population) AS population
FROM (
    SELECT
        CASE WHEN age_start >= 80 THEN '80+' ELSE age_group END AS age_group,
        CASE WHEN age_start >= 80 THEN 80    ELSE age_start END AS age_start,
        sex,
        population
    FROM v_census
    WHERE year      = {year}
      AND age_scheme = 'scheme_a'
      AND age_group != 'Total'
      AND sex       != 'total'
      AND area_level = 2
)
GROUP BY age_group, age_start, sex
ORDER BY age_start
```

### Pyramid — Single Prefecture
```sql
SELECT age_group, age_start, sex, SUM(population) AS population
FROM (
    SELECT
        CASE WHEN age_start >= 80 THEN '80+' ELSE age_group END AS age_group,
        CASE WHEN age_start >= 80 THEN 80    ELSE age_start END AS age_start,
        sex,
        population
    FROM v_census
    WHERE year       = {year}
      AND age_scheme  = 'scheme_a'
      AND age_group  != 'Total'
      AND sex        != 'total'
      AND area_estat  = '{area_estat}'
)
GROUP BY age_group, age_start, sex
ORDER BY age_start
```

### Time Series — National Population
```sql
SELECT year, SUM(population) AS total_pop
FROM v_census
WHERE age_group = 'Total'
  AND sex = 'total'
  AND area_level = 2
GROUP BY year
ORDER BY year
```

### Time Series — Aging Index
```sql
WITH age_buckets AS (
    SELECT year,
        SUM(CASE WHEN age_start >= 65                                                THEN population ELSE 0 END) AS pop_65_plus,
        SUM(CASE WHEN age_start <= 10 AND age_end <= 14 THEN population ELSE 0 END) AS pop_0_14
    FROM v_census
    WHERE age_scheme = 'scheme_a'
      AND age_group  != 'Total'
      AND sex         = 'total'
      AND area_level  = 2   -- swap for AND area_estat = '{area_estat}' for prefecture overlay
    GROUP BY year
)
SELECT year,
    ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14, 0), 1) AS aging_index
FROM age_buckets
ORDER BY year
```

### Time Series — Population Share (年少 / 生産 / 老年)
**Denominator note:** Uses `pop_0_14 + pop_15_64 + pop_65_plus` as the denominator, not the `Total` row. This intentionally excludes the ~1.45M individuals with unknown age — they are a data quality artifact, not a meaningful demographic category. The three shares always sum to 100%.

```sql
WITH age_buckets AS (
    SELECT year,
        SUM(CASE WHEN age_start <= 10 AND age_end <= 14 THEN population ELSE 0 END) AS pop_0_14,
        SUM(CASE WHEN age_start >= 15 AND age_end <= 64 THEN population ELSE 0 END) AS pop_15_64,
        SUM(CASE WHEN age_start >= 65                   THEN population ELSE 0 END) AS pop_65_plus
    FROM v_census
    WHERE age_scheme = 'scheme_a'
      AND age_group  != 'Total'
      AND sex         = 'total'
      AND area_level  = 2   -- swap for AND area_estat = '{area_estat}' for prefecture overlay
    GROUP BY year
)
SELECT year,
    ROUND(pop_0_14    * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS youth_share,
    ROUND(pop_15_64   * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS working_share,
    ROUND(pop_65_plus * 100.0 / NULLIF(pop_0_14 + pop_15_64 + pop_65_plus, 0), 1) AS old_share,
    pop_0_14,
    pop_15_64,
    pop_65_plus
FROM age_buckets
ORDER BY year
```

### Available Census Years
```sql
SELECT DISTINCT year, era_name, era_year FROM d_years ORDER BY year
```