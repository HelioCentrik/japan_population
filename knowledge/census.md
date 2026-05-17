# Census Data — Japan Population Dashboard

## Source & Coverage

**Series:** 年齢（５歳階級），男女別人口－都道府県（大正９年～平成27年）  
**Publisher:** Statistics Bureau, Ministry of Internal Affairs (総務省統計局)  
**Stat ID:** `000031523105` (1920–2015 CSV) + e-Stat API `0003410381` (2020 added separately)  
**Years in DB:** 1920, 1925, 1930, 1935, 1940, 1945, 1947, 1950, 1955, 1960, 1965,
1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020  
**Geography:** 47 prefectures + national aggregate (`area_level = 1`)  
**Grain:** One row per `year × area_estat × age_group_id × sex_id`

---

## Primary Query Surface

All app queries go through `v_census` — a pre-joined view across all dimension tables.
Do not re-join `d_prefectures`, `d_age_groups`, or `d_sex` manually.

Key fields: `year`, `area_estat`, `prefecture_name`, `prefecture_name_ja`, `area_level`,
`age_group`, `age_start`, `age_end`, `is_open_ended`, `age_scheme`, `sex`, `population`

Always filter `age_scheme = 'scheme_a'` for derived metrics. Always filter
`area_level = 2` for prefecture-level queries.

---

## Age Band Schemes

**`scheme_a`** — Standard 5-year bands: 0–4, 5–9 … 80–84, 85+. Use for all derived
metrics. Consistent across all census years except 1945.

**`scheme_b`** — Kazoedoshi (数え年) bands: 1–5, 6–10 … 81–85, 86+. Present in
1945 source data only. Remapped to scheme_a via −1 label shift (1–5 → 0–4) in `v_census`.

---

## Known Data Quirks

### 1945 Census — Provisional

The 1945 figure was collected under wartime and immediate post-war conditions via a
separate survey (人口調査), not a standard census. Several compounding issues apply:

- **Kazoedoshi age reckoning (数え年):** Age was reported as kazoedoshi — 1 at birth,
  incrementing each New Year's Day — rather than completed years. Remapped to scheme_a
  via −1 label shift. This is an approximation, not a precise conversion.
- **0–4 band is absent** from the raw source data. The remapping cannot recover it.
- **Aging index is unreliable** for 1945 — the 0–14 denominator is distorted by the
  missing band and the scheme conversion.
- **Wartime displacement** means the population distribution reflects evacuation,
  mobilization, and death rather than normal residence patterns.

Treat 1945 as a continuity marker only. The time series renders it with a distinct red
marker as a visual warning. Do not present 1945 figures as ground truth.

### WWII Sex Ratio Scar

The 1950 census shows a male deficit in the 25–29 age band — sex ratio 83.8 against a
natural baseline of ~105 (normal range 103–107). This is a direct artifact of WWII
combat deaths among men born approximately 1921–1925 (prime conscription age). It is
not a data error.

The scar advances 5 years per census: 25–29 in 1950 → 30–34 in 1955 → … → 55–59 by
1975. By 1980 it has diffused into older bands and is no longer sharply visible. The
pyramid renders diamond markers on affected bands when the ratio drops below 90.

### Terminal Age Band Variation

Earlier census years use 80+ as the open-ended terminal band; later years use 85+.
The `age_start >= 65` filter handles this correctly for elderly population counts — do
not filter on `age_end` or `is_open_ended` directly when computing elderly totals.

### Okinawa 1950 and 1955

Okinawa was under US administration from 1945 until reversion to Japan on 15 May 1972,
and was not enumerated as part of Japan's official census methodology in 1950 and 1955.
The 1950 census was conducted by the US Military Government of the Ryukyu Islands; the
1955 census by the Government of the Ryukyu Islands. Both used the de jure population
concept and a reference date of December 1 (vs. October 1 for Japan proper). The
figures present in the DB for those years are drawn from these separate enumerations,
not from standard Statistics Bureau census methodology.

Two specific issues affect 1950 and 1955:

- The Statistics Bureau's own documentation notes that the 1950 and 1955 Okinawa
  results are tabulations of the population **aged 14 years and over only**. The
  under-14 population for those years is therefore incomplete or estimated.
- The 70–74 age band for these two years contains "70 years and older" open-ended
  values rather than a true 5-year band, confirmed in e-Stat footnotes. This inflates
  the 70–74 count relative to adjacent census years.
- These issues together produce an anomalous population trajectory:
  574k (1940) → 880k (1950) → 777k (1955) → 882k (1960).

The map greys out Okinawa for 1950 and 1955 with a tooltip explaining the data quality
issue. Do not present these figures as comparable to other prefectures in those years.

### Summing Prefecture Rows ≠ National Total

The national aggregate rows (`area_level = 1`) include ~1.45M individuals whose age
was unknown or unclassified at enumeration time. These individuals are not distributed
across prefecture rows. Always use `area_level = 1` rows for national figures — do not
sum prefecture rows to derive a national total.

---

## Sources

- **Primary census data (1920–2015):** e-Stat stat ID `000031523105`
  https://www.e-stat.go.jp/stat-search/files?tstat=000001011857
- **2020 census data:** e-Stat API, stat ID `0003410381`
  https://www.e-stat.go.jp/
- **Okinawa enumeration methodology and coverage gaps (1950–1970):** Statistics Bureau,
  2020 Population Census — Explanation of Terms (PDF), pp. covering Okinawa-ken
  https://www.stat.go.jp/english/data/kokusei/2020/pdf/exp.pdf
- **Okinawa pre-reversion census history:** Statistics Bureau, Outline of the 2010
  Population Census of Japan (PDF), Part 2
  https://www.stat.go.jp/english/data/kokusei/2010/final_en/pdf/02-01.pdf
- **Natural sex ratio at birth (103–107 range):** Hesketh & Xing (2006),
  "Abnormal sex ratios in human populations: Causes and consequences", PNAS
  https://www.pnas.org/doi/10.1073/pnas.0602203103