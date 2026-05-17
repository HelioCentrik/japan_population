## IPSS Population Projections

**Source:** 日本の地域別将来推計人口 平成30年推計 (IPSS Regional Population Projections,
2018 edition). Based on the 2015 census. Published March 2018 by the National Institute
of Population and Social Security Research (国立社会保障・人口問題研究所).

A 2023 revision exists, based on the 2020 census. This dashboard uses the 2018 edition.
Findings are directionally consistent; prefecture rankings are largely unchanged.

### Coverage

- Years: 2015–2045, 5-year intervals (2015, 2020, 2025, 2030, 2035, 2040, 2045)
- Geography: 47 prefectures only. No municipal or national aggregate rows.
- Breakdown: sex × scheme_a age bands (18 bands, 0–4 through 85+; 85+ is terminal)

### DB Table: `f_projections`

Fields: `projection_year`, `area_estat`, `age_group_id`, `sex_id`, `population`.

- Join to `d_prefectures` on `area_estat`
- Join to `d_age_groups` on `age_group_id`
- Filter by `sex_id` for sex-disaggregated queries; sum across sex for totals
- `projection_year` is the query field for year selection (not `year` or `census_year`)

### Key Headline Projections

- National population 2045: ~106M (down from ~127M in 2015)
- Elderly share (65+) nationally: ~36% by 2045
- Working-age share (15–64) nationally: ~52% by 2045
- Akita: projected ~50% elderly by 2045 — highest of any prefecture
- Tokyo: relatively younger due to sustained in-migration; projected elderly share
  remains below national average through 2045
- Okinawa: younger age structure and historically higher TFR produce a more gradual
  aging trajectory compared to peer prefectures

### Known Data Quirks

**2015 baseline divergence.** The 2015 rows in `f_projections` are IPSS projection
baseline figures, not census observations. IPSS adjusts the 2015 starting population
upward ~1–2% to account for census undercounting. Do not treat `f_projections` 2015
values as equivalent to `f_census` 2015. When asked to compare projection vs. census
at 2015, acknowledge this methodological gap.

**Do not extrapolate beyond 2045.** The dataset ends at 2045. Do not estimate or
project figures beyond that year.

**No sub-prefectural data.** `f_projections` is prefecture-level only. Municipal-level
projections (which underpin the Masuda analysis) are not in the DB.