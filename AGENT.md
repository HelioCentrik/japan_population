# AGENT.md — Japan Population Dashboard

## What this model is

This semantic model covers Japan's national census data from 1920 to 2020,
structured as a star schema with prefecture-level granularity (47 prefectures,
area_level = 2). It is designed to answer questions about Japan's demographic
trajectory: aging, population decline, working-age contraction, and
dependency burden — at both national and prefecture level.

All population figures are sourced from Japan's official decennial/quinquennial
census via the e-Stat government statistics API.

---

## Core concepts and how to interpret them

### Aging Index (高齢化指数)
The headline metric. Ratio of elderly (65+) to children (0–14), multiplied
by 100. A value above 100 means there are more elderly than children —
Japan likely crossed this threshold around 1997, but the first census to
confirm it was 2000 (index ~119). It has not returned below it. Higher = more aged.
Prefecture rankings by aging index reveal which regions are aging fastest.

### Old-Age Dependency Ratio (老年従属人口指数)
How many elderly people (65+) exist per 100 working-age adults (15–64).
This is the primary economic burden metric. It was ~8.6 in 1920 and ~48.5
by 2020 — meaning the working-age population now supports roughly 5x more
elderly than a century ago.

### Working-Age Share (生産年齢人口割合)
The share of total population aged 15–64. Peaked at ~69.5% in 1990–1995.
Declining since. This is the core driver of Japan's economic output
constraint.

### Total Dependency Ratio (従属人口指数)
Combined burden: (children 0–14 + elderly 65+) / working-age (15–64) × 100.
U-shaped over the century: high in 1920 (youth-driven), minimum ~43.5 in
1990 (Japan's demographic dividend peak), rising again since (now
elderly-driven). The 1990 trough is Japan's highest-productivity window.

### Population Share View (人口割合)
A time series showing youth (0–14), working-age (15–64), and elderly (65+) as a
percentage of the classified population across all census years. The three shares
always sum to 100%. Note: the ~1.45M individuals with unknown age are excluded from
the denominator — they are a data quality artifact, not a demographic category.

Key inflection points:
- Working-age share peaked ~69.5% around 1990–1995 (Japan's demographic dividend peak).
- Elderly share crossed youth share around 1997 (same event as aging index crossing 100).
- The old-age dependency ratio (`老年従属比`) — elderly share / working-age share × 100
  — is derived from this view and shown in hover tooltips.

Prefecture overlay available: prefecture lines rendered as dotted, national lines
faded to 25% opacity when a prefecture is selected.

### Population Pyramid
Visualizes age-sex distribution for a given year and geography. The national
pyramid shifted from a classic triangular base (1920s, many young) to a
barrel/inverted shape (2020, many elderly). The WWII cohort notch
(male deficit in the 25–29 band in 1950, sex ratio 83.8) moves up the
pyramid 5 years per census.

---

## Rules the agent must follow

- **Always filter `age_scheme = 'scheme_a'`** — this is the standardized
  age grouping that is consistent across all census years. Do not use
  other schemes for derived metrics.
- **Never mix the 'Total' age group row with band-level arithmetic.** When
  computing derived metrics (aging index, dependency ratios, shares), sum
  individual age bands only — mixing Total with bands causes double-counting.
  Exception: to retrieve total population for a geography/year, query
  `WHERE age_group = 'Total'` directly. Summing bands will undercount by
  ~1.45M people with unknown age.
- **The 65+ bucket uses `age_start >= 65`** — do not filter on `age_end`
  for this group, as terminal bands vary by census year (80+, 85+, etc.).
- **Growth rates are annualized**, not period-aggregated. Formula:
  `(pop_b / pop_a) ^ (1 / (year_b - year_a)) - 1`. Do not assume 5-year
  periods even though most intervals are 5 years.
- **Use `area_level = 2` for prefecture-level queries, `area_level = 1` for
  national-level queries.** Do not sum prefecture rows to derive national
  figures — use the dedicated national rows.
- **Old-Age Dependency Ratio is NOT a selectable map metric.**

---

## Questions this model is designed to answer

- Which prefectures have the highest / lowest aging index in [year]?
- How has Japan's working-age population share changed since [year]?
- What is the old-age dependency ratio nationally / in [prefecture]?
- How does [prefecture]'s aging trajectory compare to the national average?
- What does the population pyramid look like for [year] nationally or in
  [prefecture]?
- In which census year did Japan's aging index first exceed 100?
- Which regions are aging fastest / slowest?
- What is the total dependency ratio trend over time?
- How has the share of youth / working-age / elderly population changed since [year]?
- When did the elderly share first exceed the youth share nationally?
- What is the old-age dependency ratio (老年従属比) in [year] nationally or for [prefecture]

---

## Synonyms and terminology

| Term the user might use | Resolves to |
|---|---|
| Elderly population | pop_65_plus / age_start >= 65 |
| Children / youth / young population | pop_0_14 / age_start <= 14 |
| Working age / economically active | pop_15_64 / age_start 15–64 |
| Aging rate / aging ratio | aging_index (高齢化指数) |
| Dependency burden | old_age_dep or total_dep depending on context |
| Prefecture | area_estat / prefecture_name |
| Region | area_level grouping of prefectures |
| Population change          | pop_delta (in v_map_metrics)                              |
| Youth share / 年少割合     | youth_share — pop_0_14 / classified pop × 100             |
| Working-age share / 生産割合 | working_share — pop_15_64 / classified pop × 100         |
| Elderly share / 老年割合   | old_share — pop_65_plus / classified pop × 100            |
| Old-age dependency ratio / 老年従属比 | old_share / working_share × 100 (= pop_65+ / pop_15–64 × 100) 

---

## What this model does NOT cover

- Population projections or forecasts beyond 2020 (all data is historical
  census). Do not extrapolate or estimate future values.
- Individual-level data. All data is aggregated at prefecture level
  (area_level = 2) or national level (area_level = 1).
- Foreign resident population as a distinct category. Census data includes
  all residents regardless of nationality; no foreign/domestic breakdown
  is available in this schema.
- Birth rates, death rates, or migration flows. This model covers stock
  (population at a point in time), not flows.
- Economic indicators. Dependency ratios describe demographic burden, not
  GDP, labor productivity, or fiscal impact directly.

---

## Known data quirks to surface when relevant

- **WWII cohort notch:** The 1950 census shows a male deficit in the 25–29
  age band (sex ratio 83.8, well below the natural ~103). This notch
  advances 5 years per subsequent census and reaches 55–59 by 1975.
  It is a historical artifact, not a data error.
- **Terminal age band varies by census year** (some use 80+, later censuses
  use 85+). The `age_start >= 65` filter handles this correctly without
  needing adjustment.
- **1945 census is provisional.** The 1945 data was collected under wartime
  and immediate post-war conditions and is not fully accurate. It is included
  for continuity but figures should be interpreted with caution. Do not treat
  1945 values as ground truth for precise trend analysis.
- **1945 age bands use kazoedoshi (数え年) counting**, where age at birth is
  1, not 0. The raw data (scheme_b) has been remapped onto standard 5-year
  bands (scheme_a) via a −1 label shift (e.g. the 1–5 band becomes 0–4).
  This is an approximation — not a perfect conversion — and contributes to
  the imprecision noted above. Querying `age_scheme = 'scheme_a'` via
  v_census returns the remapped values automatically.
- **Okinawa 1950 and 1955 data is methodologically suspect.** Okinawa was
  under US administration from 1945 until 1972 and was not enumerated as
  part of Japan's official census in those years. The 1950 and 1955 figures
  for Okinawa should be treated as estimates and interpreted with caution.
- **Terminal age band varies by census year**