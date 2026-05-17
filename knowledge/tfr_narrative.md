## Total Fertility Rate — Japan

### What TFR Measures

Total fertility rate is the average number of births per woman over a lifetime if
age-specific rates held constant throughout her reproductive years. A TFR of 2.07 is
the replacement level in low-mortality societies (slightly above 2.0 to account for
infant mortality and sex ratio at birth).

TFR is a period metric, not a cohort metric — it is a snapshot of a single calendar
year, not the actual completed fertility of any real generation of women. This matters
for interpretation: a declining TFR partly reflects tempo effects (women delaying
childbearing to later ages) in addition to genuine quantum decline (fewer births overall).

### Japan's TFR Trajectory

Note: `f_tfr` covers 1960–2024. The pre-1960 figures below come from MHLW vital
statistics and are not queryable from the dashboard's data.

- **1947:** ~4.54 — postwar baby boom peak, the highest recorded in the postwar era
- **1950:** ~3.65 — already declining sharply from the 1947 peak
- **1950s–60s:** Rapid decline driven by de facto legalization of abortion under the
  Eugenic Protection Law (優生保護法, 1948), with the 1949 amendment broadening access
  on economic grounds, combined with rapid urbanization and economic development
- **1957–1960:** TFR reaches ~2.0, approaching replacement level for the first time
- **1966:** 1.58 — 丙午 (hinoeuma) dip. Single-year anomaly; see `knowledge/historical_events.md`
- **1970–1972:** Brief plateau near 2.1 — the last period at or near replacement level
- **1973 onward:** Sustained decline below replacement, accelerating post-oil shock
- **1989:** 1.57 — the 1.57 ショック. Fell below the 1966 hinoeuma figure for the
  first time. Triggered national policy alarm. Marked the start of sustained government
  intervention: Angel Plan (1994), New Angel Plan (1999), successive childcare and
  parental leave expansions through the 2000s–2010s
- **1990s–2010s:** Low era, range of 1.2–1.4
- **2005:** 1.26 — historical national low (verifiable from `f_tfr`)
- **2005–2015:** Partial recovery attributed to tempo rebound (mean age at first birth
  stabilized) and modest policy effects
- **2016 onward:** Renewed decline
- **2023:** National TFR 1.20 — eighth consecutive year of decline. Tokyo fell below
  1.0 for the first time, recording 0.99

### Prefecture Variation

Okinawa has consistently held the highest prefectural TFR across all years in `f_tfr`
(1960–2024), remaining substantially above the national average at every point. Its
TFR has ranged ~1.6–1.9 across recent decades. Contributing factors include a younger
and more stable resident population, lower rates of delayed marriage, and lower
urbanization pressure relative to mainland prefectures.

Tokyo has held the lowest or near-lowest prefectural TFR across the same period,
ranging ~1.0–1.1 in recent decades and falling to 0.99 in 2023. The mechanism is
primarily compositional: Tokyo's in-migrant population skews heavily toward young adults
(20–34) who delay or forgo childbearing. This is a structural demographic feature of
the in-migration pattern, not evidence that Tokyo residents have different preferences.

The Okinawa–Tokyo gap is persistent and structural across decades, not cyclical.

### Why TFR Alone Does Not Explain Population Structure

**Cohort size effects.** A high TFR applied to a small cohort of women produces fewer
absolute births than a low TFR applied to a large cohort. Japan's 団塊ジュニア
(dankai junior) generation (1971–1974) produced a visible secondary bulge in the
population pyramid despite already-declining TFR, because their parent cohort (the
dankai generation) was enormous. Absolute birth counts matter as much as rates.

**Population momentum.** Even if TFR returned to replacement level today, Japan's
population would continue declining for decades. The current age structure — with a
small base of young women and a large elderly cohort — means that replacement-level
fertility produces far fewer births than deaths. Momentum is the reason that policy
interventions affecting TFR have limited near-term impact on total population size.

**Tempo vs. quantum.** Some portion of Japan's TFR decline reflects delay rather than
foregoing births entirely — women having the same number of children but later. Period
TFR understates eventual completed cohort fertility during periods of rising mean age
at first birth, and overstates it during periods of reversal.

### DB Table: `f_tfr`

Fields: `area_estat`, `year` (annual integer, not census-keyed), `tfr`.

- Join to `d_prefectures` on `area_estat`
- Coverage: 1960–2024. No data pre-1960.
- Annual grain — do not join directly to `f_census` without filtering to census years
- 3 suppressed values are excluded from source data (small prefecture/year combinations
  withheld for statistical privacy). Gaps in coverage are suppression, not missing ingestion.

### Sources

- **MHLW Vital Statistics — primary source for all TFR figures (annual, prefecture level):**
  https://www.mhlw.go.jp/english/database/db-hw/vs01.html
- **Pre-1960 TFR figures (4.54 in 1947, 3.65 in 1950) — academic confirmation:**
  IZA Discussion Paper No. 13885, "Japan's Demographic Transition and the Marriage Market"
  https://docs.iza.org/dp13885.pdf
- **Abortion legalization — Eugenic Protection Law (1948) and 1949 amendment:**
  Asia Safe Abortion Partnership, Japan country profile
  https://asap-asia.org/country-profile-japan/
- **Tokyo TFR 0.99 in 2023 (below 1.0 for first time), Okinawa 1.60:**
  Nippon.com, "Japan's Fertility Rate Drops to New Record Low"
  https://www.nippon.com/en/japan-data/h02015/
- **Angel Plan (1994) and New Angel Plan (1999):**
  Cabinet Office of Japan, Annual Report on the Declining Birthrate 2018 (English)
  https://www8.cao.go.jp/shoushi/shoushika/whitepaper/measures/english/w-2018/pdf/s1-2.pdf