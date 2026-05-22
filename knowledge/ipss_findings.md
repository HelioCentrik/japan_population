## IPSS Population Projections

**Source:** 日本の地域別将来推計人口 平成30年推計 (IPSS Regional Population Projections,
2018 edition). Based on the 2015 census. Published March 2018 by the National Institute
of Population and Social Security Research (国立社会保障・人口問題研究所).

A 2023 revision exists (令和5年推計), based on the 2020 census, covering 2020–2050.
The dashboard uses the 2023 edition for national projections (`f_national_projections`).
Prefecture-level projection figures below are from the 2018 edition and are reference
context only — not stored in the DB. Findings are directionally consistent; prefecture
rankings are largely unchanged between editions.

### Coverage (2018 Regional Edition — Reference Only)

- Years: 2015–2045, 5-year intervals (2015, 2020, 2025, 2030, 2035, 2040, 2045)
- Geography: 47 prefectures only. No municipal or national aggregate rows.
- Breakdown: sex × scheme_a age bands (18 bands, 0–4 through 85+; 85+ is terminal)

### Key Headline Projections

The national-level figures below are from the IPSS national projections (2017 edition),
included here as reference benchmarks. The dashboard's `f_national_projections` table
uses the 2023 edition (2021–2070, annual); figures will differ slightly.

- National population 2045: ~106M (down from ~127M in 2015)
- Elderly share (65+) nationally: ~36% by 2045
- Working-age share (15–64) nationally: ~52% by 2045

The prefecture-level figures below are from the 2018 regional edition:

- Akita: projected ~50% elderly by 2045 — highest of any prefecture
- Tokyo: projected elderly share remains below national average through 2045, reflecting
  sustained in-migration of young adults
- Okinawa: more gradual aging trajectory than peer prefectures, reflecting younger age
  structure and historically higher TFR

### Known Data Quirks

**No sub-prefectural data.** Municipal-level projections (which underpin the Masuda
analysis) are not in the DB.

### Sources

- **IPSS 2018 regional projections — English landing page:**
  https://www.ipss.go.jp/pp-shicyoson/e/shicyoson18/t-page.asp
- **IPSS 2018 regional projections — full report (Japanese, PDF, 256pp):**
  https://www.ipss.go.jp/pp-shicyoson/j/shicyoson18/6houkoku/houkoku.asp
- **IPSS 2023 national projections (source of `f_national_projections`):**
  https://www.ipss.go.jp/pp-zenkoku/j/zenkoku2023/pp_zenkoku2023.asp
- **IPSS 2023 regional projections revision (令和5年推計, 2020–2050):**
  https://www.ipss.go.jp/pp-shicyoson/j/shicyoson23/1kouhyo/top-01.asp