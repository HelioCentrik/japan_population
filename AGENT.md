# AGENT.md — Japan Population Dashboard

## What this model is

This semantic model covers Japan's national census data from 1920 to 2020,
structured as a star schema with prefecture-level granularity (47 prefectures,
`area_level = 2`). It answers questions about Japan's demographic trajectory —
aging, population decline, working-age contraction, and dependency burden — at
both national and prefecture level. All figures are sourced from Japan's official
decennial/quinquennial census via the e-Stat government statistics API.

---

## Response Guidance

- **Default:** 2–4 sentences. Get to the point, then stop.
- **List questions** ("what are the key takeaways", "what events happened"): up to 4
  bullets, one substantive sentence each. No nested bullets. No sub-sections.
- **Complex or multi-part questions:** up to 6 bullets if genuinely needed.
- **No preamble.** Don't open with "Great question" or "The dashboard shows that..."
  — start with the answer.
- **No closing summary.** Don't restate what you just said. End when the content ends.
- **Prefer concrete over abstract.** Name the year, the metric, the prefecture. Avoid
  vague qualifiers like "significantly" or "dramatically" unless the magnitude warrants it.
- If a question can't be answered from census, projections, TFR, or migration data — such as 
  economics, post-2045 forecasts, individual-level data — say so briefly and stop.

---

## Dashboard Visual Guide

### KPI Cards

Four metric cards displayed in the side panel. They update when the year slider moves
or a prefecture is selected via the map.

| Card | Metric | Notes |
|---|---|---|
| 人口 Population | Total population | Switches to prefecture total on map click |
| 高齢化指数 Aging Index | Elderly (65+) / Children (0–14) × 100 | >100 = more elderly than children |
| 老年従属人口指数 Old-Age Dependency Ratio | Elderly per 100 working-age adults | Primary economic burden metric |
| 生産年齢人口割合 Working-Age Share | % of population aged 15–64 | Peaked ~69.5% nationally in 1990–1995 |

---

### Map Panel

Choropleth of Japan's 47 prefectures. Click a prefecture to filter the pyramid and
time series to that region. Click the ocean or the active prefecture again to return
to the national view.

**Metric selector** (dropdown, top-left of panel):

| Metric | Colorscale | Notes |
|---|---|---|
| 人口 Population | Sequential (plasma, light = high) | Raw headcount; all census years |
| 人口増減 Population Change | Diverging red–yellow–white–blue–violet | Red = decline; violet = strong growth; all census years |
| 合計特殊出生率 TFR | Sequential (viridis) | Coverage: census years 1960–present. Slider snaps to min 1960 when active. NULL for pre-1960 years. |
| 純移動数 Net Migration | Diverging (green = net inflow; red = net outflow) | Coverage: census years 1985–2020. Slider snaps to that window when active. NULL outside range. 1985 is partial (4 of 5 years). |

**Year-snap behaviour:** When the metric selector changes, a dedicated callback in `callbacks/selection.py` updates the slider `min`, `max`, `marks`, and `value` to reflect the active metric's valid census-year window. The slider physically cannot land on an out-of-coverage year. Playback (`toggle_playback`, `advance_year`) filters `PLAYBACK_YEARS` through the same bounds via `MAP_METRICS[metric]["min_year"/"max_year"]`. The primary chart callback (`update_charts`) needs no awareness of coverage — it always receives a valid year as input.

**Okinawa note:** For 1950 and 1955, Okinawa's prefectural tile is visually greyed out
because those figures are methodologically suspect — Okinawa was under US administration
and was not enumerated as part of Japan's official census in those years.

---

### Population Pyramid

Horizontal bar chart showing age-sex distribution for the selected year and geography
(national by default; prefecture view when a prefecture is clicked on the map).

**Bars:**
- **Blue bars (left):** Male population. Displayed as negative values to push left.
- **Pink/red bars (right):** Female population.
- Y-axis: 5-year age bands (0–4 through 80+ or 85+, depending on census year).
- Band count varies by year — terminal band changed over time (80+ in earlier years,
  85+ in later ones).

**Cohort annotations** (not shown in legend — hover the markers to identify them):

| Visual | Color | Cohort | Birth years | Visible when |
|---|---|---|---|---|
| Outlined band (no fill) | Orange | 団塊の世代 Dankai | 1947–1949 | Year ≥ 1950 |
| Outlined band (no fill) | Green | 団塊ジュニア Dankai Junior | 1971–1974 | Year ≥ 1975 |
| Diamond markers on male bars | Amber | 戦中世代 Wartime Generation | 1910–1925 | National, 1950–2015 |
| Diamond markers at center | Sky blue | 少子化世代 Shoushika | 1986–1990 | National, year ≥ 1990 |

Hovering a diamond marker shows a tooltip card with the cohort name (Japanese), birth
year range, and the age band that cohort occupies in the selected year.

The dankai and dankai junior outlines are shapes drawn over the bars — they don't appear
in the legend and don't have hover behavior. They mark which age bands the cohort occupies
as the pyramid updates year by year.

**WWII sex ratio scar:** When the male-to-female ratio in any age band drops below 90,
a subtle marker appears. In 1950, the 25–29 band shows a ratio of 83.8 — a direct
artifact of WWII combat deaths. This notch advances 5 years with each census and reaches
the 55–59 band by 1975.

**1945 note:** The pyramid for 1945 uses kazoedoshi (数え年) age data remapped to
standard 5-year bands via a −1 label shift. Age band 0–4 is absent. Treat it as
approximate, not ground truth.

---

### Time Series

Line chart covering all census years 1920–2020. The metric selector (top-left of panel)
controls what is plotted.

**Metric selector options:**

| Option | What it shows |
|---|---|
| 人口 Population | Total population over time |
| 高齢化指数 Aging Index | Ratio of elderly to children × 100; dashed threshold line at 100 |
| 人口割合 Population Share | Three lines — youth (0–14), working-age (15–64), elderly (65+) — always summing to 100% |

**Prefecture overlay:** When a prefecture is selected via the map, a dotted prefecture
line is added to the chart. In Population Share view, national lines fade to 25% opacity
to make the prefecture lines readable.

**Year marker:** A vertical line marks the currently selected year across all metrics.

**1945 data point:** The 1945 observation is rendered with a distinct red marker on all
time series views. The red color signals that the data is provisional and should be
interpreted with caution — it uses kazoedoshi age counting and was collected under
wartime/immediate post-war conditions. It is accessible via the slider but excluded from
automated playback.

**Aging Index threshold line:** A horizontal dashed line at 100 marks the structural
inversion point — the level at which elderly outnumber children. Japan crossed this
around 1997; the 2000 census (aging index ~119) is the first census to confirm it.

---

## Core Metrics & Concepts

### Aging Index (高齢化指数)
Elderly (65+) / Children (0–14) × 100. Above 100 means more elderly than children.
Japan likely crossed 100 around 1997; confirmed by the 2000 census (~119). Has not
returned below it. Higher = more aged. Prefecture rankings reveal regional variation.

### Old-Age Dependency Ratio (老年従属人口指数)
Elderly (65+) per 100 working-age adults (15–64). Was ~8.6 in 1920; ~48.5 by 2020.
The working-age population now supports roughly 5× more elderly than a century ago.

### Working-Age Share (生産年齢人口割合)
Share of total population aged 15–64. Peaked ~69.5% in 1990–1995. Declining since.
Core driver of Japan's economic output constraint.

### Total Dependency Ratio (従属人口指数)
(Children 0–14 + Elderly 65+) / Working-age (15–64) × 100. U-shaped over the century:
high in 1920 (youth-driven), minimum ~43.5 in 1990 (demographic dividend peak), rising
since (now elderly-driven). The 1990 trough is Japan's highest-productivity window.

### Population Share View (人口割合)
Youth (0–14), working-age (15–64), and elderly (65+) as a percentage of the classified
population. Always sums to 100%. The ~1.45M individuals with unknown age are excluded
from the denominator — they are a data quality artifact. Key inflection: elderly share
crossed youth share around 1997 (same event as the aging index crossing 100).

---

## Cohort Reference

### 団塊の世代 — Dankai no Sedai (Baby Boomers)
Born 1947–1949. Japan's post-WWII birth surge. The largest single cohort in the pyramid
for most of the 20th century. Their entry into the 65+ bracket in the 2010s drove a sharp
acceleration in the aging index and old-age dependency ratio. Marked with **orange outlines**
on the pyramid bars.

### 団塊ジュニア — Dankai Junior
Born 1971–1974. Children of the dankai generation. A secondary bulge visible in the
pyramid. Their working-age peak corresponded with the late-1990s economic stagnation.
As they age toward 65+ (from 2036), another wave of dependency burden is expected.
Marked with **green outlines** on the pyramid bars.

### 戦中世代 — Wartime Generation
Born 1910–1925. Came of age during WWII. The male deficit in this cohort's age bands is
the source of the sex ratio scar visible in the 1950 pyramid (25–29 band, ratio 83.8).
Tracked via **amber diamond markers** on the male (left) side of the pyramid. National
view only; visible for census years 1950–2015.

### 少子化世代 — Shoushika (Low Birth Rate Generation)
Born 1986–1990. The cohort born into Japan's sustained low-birth-rate era. Their small
size relative to preceding cohorts signals the long-term contraction of the youth base.
Tracked via **sky blue diamond markers** at the pyramid's center axis. National view
only; visible from 1990 onward.

---

## Census Data

Japan's official decennial/quinquennial census, 1920–2020. Grain: one row per
`year × area_estat × age_group_id × sex_id`. Primary query surface is `v_census`.
47 prefectures (`area_level = 2`) plus national aggregate (`area_level = 1`).

See `knowledge/census.md` for full source details, age band schemes, and known
data quirks.

---

## Supplementary Data

### `f_projections` — IPSS Prefectural Projections
Grain: `projection_year × area_estat × age_group_id × sex_id`. Join to `d_prefectures`
on `area_estat`; join to `d_age_groups` on `age_group_id` (scheme_a, 18 bands).
Coverage: 2015–2045, 5-year intervals, 47 prefectures. 2015 rows are projection
baseline — not census observations. Do not extrapolate beyond 2045.

See `knowledge/ipss_findings.md`.

### `f_tfr` — Prefecture-Level Total Fertility Rate
Grain: `area_estat × year` (annual). Join to `d_prefectures` on `area_estat`.
Coverage: 1960–2024. No data pre-1960. Filter to census years when joining to `f_census`.

See `knowledge/tfr_narrative.md`.

### `f_migration` — Net Internal Migration
Grain: `area_estat × census_year`. Join to `d_prefectures` on `area_estat`.
Coverage: census years 1985–2020. NULL for 1960–1980 — no source data, do not infer
zero. Figures represent 5-year cumulative net migration ending on the census year.

See `knowledge/migration.md`.

### Masuda Report — Extinction-Risk Municipalities (Tertiary Reference)
Not a DB table. Policy context for the aging and working-age share metrics. Provides
the 消滅可能性都市 framing behind prefecture-level risk patterns visible in the map.

See `knowledge/masuda_report.md`.

---

## Rules the Agent Must Follow

- **Always filter `age_scheme = 'scheme_a'`** — standardized age grouping, consistent
  across all census years. Do not use other schemes for derived metrics.
- **Never mix the 'Total' age group row with band-level arithmetic.** When computing
  derived metrics, sum individual age bands only. Exception: to retrieve total population,
  query `WHERE age_group = 'Total'` directly — summing bands undercounts by ~1.45M.
- **The 65+ bucket uses `age_start >= 65`** — do not filter on `age_end`, as terminal
  bands vary by census year (80+, 85+, etc.).
- **Growth rates are annualized.** Formula: `(pop_b / pop_a) ^ (1 / (year_b - year_a)) - 1`.
  Do not assume 5-year periods even though most intervals are 5 years.
- **Use `area_level = 2` for prefecture queries, `area_level = 1` for national.** Do not
  sum prefecture rows to derive national figures.
- **Old-Age Dependency Ratio is NOT a selectable map metric.**

---

## Synonyms & Terminology

| Term the user might use | Resolves to |
|---|---|
| Elderly population | pop_65_plus / age_start >= 65 |
| Children / youth / young population | pop_0_14 / age_start <= 14 |
| Working age / economically active | pop_15_64 / age_start 15–64 |
| Aging rate / aging ratio | aging_index (高齢化指数) |
| Dependency burden | old_age_dep or total_dep depending on context |
| Prefecture | area_estat / prefecture_name |
| Population change | pop_delta (in v_map_metrics) |
| Youth share / 年少割合 | youth_share — pop_0_14 / classified pop × 100 |
| Working-age share / 生産割合 | working_share — pop_15_64 / classified pop × 100 |
| Elderly share / 老年割合 | old_share — pop_65_plus / classified pop × 100 |
| Old-age dependency ratio / 老年従属比 | old_share / working_share × 100 |
| Baby boomers / boomers | 団塊の世代 (Dankai), born 1947–1949 |
| Orange band / outline on pyramid | 団塊の世代 (Dankai) cohort |
| Green band / outline on pyramid | 団塊ジュニア (Dankai Junior) cohort |
| Amber / orange diamonds on pyramid | 戦中世代 (Wartime Generation) markers |
| Blue / sky blue diamonds on pyramid | 少子化世代 (Shoushika) markers |
| Red dot / marker on time series | 1945 provisional data point |
| Dashed line on aging index chart | Threshold at aging index = 100 |
| Grey prefecture on map | Okinawa 1950 or 1955 (suspect data) |
| Projection year / forecast year | projection_year (field in f_projections) |

---

## Known Data Quirks

See `knowledge/census.md` for full detail on all quirks.

- **1945 is provisional.** Kazoedoshi age reckoning, 0–4 band absent, aging index
  unreliable. Use for continuity only.
- **WWII sex ratio scar.** Male deficit in 25–29 band (1950, ratio 83.8). Advances 5
  years per census. Not a data error.
- **Terminal age band varies.** Use `age_start >= 65` for elderly counts, not `age_end`.
- **Okinawa 1950 and 1955 are estimates.** Not standard census enumeration. Treat with
  caution.
- **Summing prefectures ≠ national total.** Always use `area_level = 1` for national
  figures.

---

## What this model does NOT cover

- Individual-level data. All data is aggregated at prefecture or national level.
- Foreign resident population as a distinct category. Census includes all residents
  regardless of nationality; no foreign/domestic breakdown available.
- Birth rates, death rates, or migration flows. This model covers stock (population at
  a point in time), not flows.
- Economic indicators. Dependency ratios describe demographic burden, not GDP, labor
  productivity, or fiscal impact directly.