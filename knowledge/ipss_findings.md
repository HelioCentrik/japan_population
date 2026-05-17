## IPSS Population Projections

**Source:** 日本の地域別将来推計人口 平成30年推計 (IPSS Regional Population Projections,
2018 edition). Based on the 2015 census. Published March 2018 by the National Institute
of Population and Social Security Research (国立社会保障・人口問題研究所).

A 2023 revision exists (令和5年推計), based on the 2020 census, covering 2020–2050.
This dashboard uses the 2018 edition. Findings are directionally consistent; prefecture
rankings are largely unchanged between editions.

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

The national-level figures below are from the companion IPSS national projections (2017
edition), which the 2018 regional report was designed to be consistent with. They are
not directly stored in `f_projections` (which is prefecture-level only) but are
verifiable by summing across all 47 prefectures.

- National population 2045: ~106M (down from ~127M in 2015)
- Elderly share (65+) nationally: ~36% by 2045
- Working-age share (15–64) nationally: ~52% by 2045

The prefecture-level figures below are directly computable from `f_projections`:

- Akita: projected ~50% elderly by 2045 — highest of any prefecture (verified against
  ingested data)
- Tokyo: projected elderly share remains below national average through 2045, reflecting
  sustained in-migration of young adults
- Okinawa: more gradual aging trajectory than peer prefectures, reflecting younger age
  structure and historically higher TFR

### Known Data Quirks

**2015 baseline divergence.** The 2015 rows in `f_projections` are IPSS projection
baseline figures, not census observations. IPSS uses imputed census figures that
supplement the raw census counts for individuals with unknown age, nationality, or
marital status — this is standard IPSS methodology and results in a starting population
approximately 1–2% above the raw `f_census` 2015 figures. Do not treat `f_projections`
2015 values as equivalent to `f_census` 2015. When asked to compare projection vs.
census at 2015, acknowledge this methodological gap.

**Do not extrapolate beyond 2045.** The dataset ends at 2045. Do not estimate or
project figures beyond that year.

**No sub-prefectural data.** `f_projections` is prefecture-level only. Municipal-level
projections (which underpin the Masuda analysis) are not in the DB.

### Sources

- **IPSS 2018 regional projections — English landing page:**
  https://www.ipss.go.jp/pp-shicyoson/e/shicyoson18/t-page.asp
- **IPSS 2018 regional projections — full report (Japanese, PDF, 256pp):**
  https://www.ipss.go.jp/pp-shicyoson/j/shicyoson18/6houkoku/houkoku.asp
- **IPSS 2017 national projections (source of 106M / 36% / 52% headline figures):**
  https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2017/pp_zenkoku2017.asp
- **IPSS 2023 regional projections revision (令和5年推計, 2020–2050):**
  https://www.ipss.go.jp/pp-shicyoson/j/shicyoson23/1kouhyo/top-01.asp
- **2015 baseline divergence methodology explanation (IPSS national projections FAQ):**
  https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2023/pp_zenkoku2023.asp