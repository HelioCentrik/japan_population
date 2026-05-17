## Internal Migration — Japan

### Source

e-Stat 住民基本台帳人口移動報告 (Report on Internal Migration in Japan Derived from
the Basic Resident Registration). Publisher: Statistics Bureau, Ministry of Internal
Affairs and Communications (総務省統計局).

The report tracks inter-prefectural migration based on 住民票 (juuminhyou — resident
registration) address changes. Data is compiled from notifications submitted to
municipal governments under the Basic Resident Registration Act. Released monthly
(移動月報) and annually (年報); the dashboard ingestion uses annual figures.

The ingested dataset was stitched from 8 overlapping annual publications spanning
1982–2025. Where publications overlap, the earliest publication date takes precedence.

### DB Table: `f_migration`

Fields: `area_estat`, `census_year`, `net_migration`.

- Join to `d_prefectures` on `area_estat`
- 47 prefectures only. No national aggregate row — sum across all prefectures if needed,
  but note that inter-prefectural net migration sums to zero by definition (one
  prefecture's in-migrant is another's out-migrant). The sum will be zero or near-zero;
  any deviation reflects rounding or foreign resident movements.
- `net_migration` = total in-migrants minus total out-migrants for the rollup window

### Coverage and Grain

One row per `area_estat × census_year`. Each `census_year` value represents a 5-year
rollup: census year Y = sum of annual net migration for years (Y−4) through Y inclusive.
This aligns migration flows to census intervals, making `f_migration` joinable to
`f_census` on `census_year`.

**Available census years: 1985–2020.**

**NULL for census years 1960–1980.** No prefecture-level source data exists for this
period. Do not infer zero — NULL means no data, not zero net migration.

**1985 is a partial window.** Source data begins 1982, so the 1985 census year entry
covers 4 years (1982–1985) rather than the standard 5. Net migration figures for 1985
are slightly understated relative to a full window. Treat with caution when comparing
1985 to later census years.

### Key Patterns

**Tokyo metro dominance.** Tokyo, Kanagawa, Saitama, and Chiba consistently show net
positive migration across all covered census years. This four-prefecture cluster is the
dominant in-migration destination in the dataset. The concentration is stronger in
recent censuses than earlier ones — urban pull has intensified, not moderated.

**Age composition of migration flows.** The 20–24 age band drives the majority of
Tokyo metro inflow. Young adults relocating for university entry (18) and initial
employment (22–23) are the core migrating cohort. This is why Tokyo's demographic
profile skews young relative to its low TFR — it imports young adults continuously,
then sees partial return migration in the 30s as some residents move to suburban
prefectures for family formation.

**Outmigration concentration.** Prefectures with the highest sustained net outmigration
consistently overlap with the highest aging index on the map: Akita, Shimane, Kochi,
Iwate. The migration data provides the mechanistic link between what the map shows
(high aging index) and why it is that way (decades of youth drain).

**2024 snapshot.** In 2024, only 7 of 47 prefectures had net positive migration.
This figure reflects annual data, not a census-year rollup, but illustrates the
degree of geographic concentration in migration gains.

### Connection to Other Tables

**Migration and TFR divergence.** Prefecture-level TFR differences are partly a
compositional effect of migration patterns, not purely a behavioral difference between
residents. Tokyo's chronically low TFR reflects its in-migrant population skewing
heavily toward young adults in the delay-or-forgo childbearing phase of life. Okinawa's
persistently high TFR reflects a more stable resident population with less selective
outmigration of young women. When comparing TFR across prefectures, migration context
is essential for correct interpretation.

**Dankai junior and urban concentration.** The dankai junior generation's (1971–1974)
large cohort moved to Tokyo metro in large numbers during the 1990s for education and
employment. This is why that cohort's size did not translate into rural population
recovery — its most demographically productive years were spent in urban prefectures,
not in the home prefectures that needed the population most.

**Masuda mechanism.** The self-reinforcing spiral described in `knowledge/masuda_report.md`
operates through migration: youth drain → shrinking young female base → fewer births
→ accelerated aging → deteriorating services → accelerated youth drain. `f_migration`
provides the empirical data behind the first arrow in that chain.

### Known Data Quirks

**Registered address ≠ physical residence.** Net migration figures reflect 住民票
(juuminhyou) address changes, not actual physical movement. A proportion of residents —
particularly students and young workers — maintain registered addresses in their home
prefectures while living elsewhere. This causes minor undercounting of true urban
in-migration and overcounting of true rural population in prefecture-level figures. The
effect is most pronounced in rural prefectures with large universities or significant
commuter populations.

**No data pre-1982 at the prefecture level.** The 1960–1980 NULL values are a source
data limitation, not a processing gap. Prefecture-level migration data does not exist
in digitized form from this source for those years.

**Deduplication.** Where overlapping publications conflict on a given year, the earliest
publication date was used. Revised figures from later publications were not applied.

**Foreign residents (外国人).** The Basic Resident Registration Act was amended in July
2012 to include foreign residents in the registration network. Annual migration data
from 2013 onward includes foreign resident address changes; pre-2013 data covers
Japanese nationals only. For census-year rollups ending in 2015 and 2020, the window
partially includes foreign-resident migration. This introduces a minor inconsistency
in the 2015 census year entry (2011–2015 window straddles the 2013 coverage change).

### Sources

- Statistics Bureau official page for the report:
  https://www.stat.go.jp/data/idou/index.html
- e-Stat data portal (all annual publications):
  https://www.e-stat.go.jp/stat-search?toukei=00200523
- English-language overview of the survey methodology:
  https://www.stat.go.jp/english/data/idou/1.html