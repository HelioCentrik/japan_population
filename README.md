# Japan Population Dashboard
### 日本の人口ダッシュボード

An interactive visualization of Japanese census data (1920–2020) across all 47 prefectures.

**Live:** [deanallton.com/japan-population](https://deanallton.com/japan-population)

---

## Setup

### Requirements

Python 3.11+

```bash
pip install -r requirements.txt
```

### Data pipeline

Source files (`source/jp_census_historical_1920_2015.csv` and `source/japan_prefectures.geojson`) are included in the repository. To build the database:

```bash
python scripts/build_db.py
```

This script is idempotent and safe to re-run. It also executes automatically on startup if `data/japan_population.duckdb` is absent.

### Run

```bash
python app.py
```

---

## Dashboard

A single-page application with four linked panels driven by a shared year control.

### Controls

| Control | Effect |
|---|---|
| Year slider | Updates all panels simultaneously across 21 census years (1920–2020). |
| Play button | Autoplays through census years at a fixed interval. |
| Prefecture click (map) | Filters the pyramid and overlays a prefecture line on the time series. |
| Re-click / Reset | Clears prefecture selection and returns all panels to the national view. |
| Map metric selector | Switches the choropleth between total population, aging index, population change, and working-age share. |
| Time series selector | Switches the time series between population (default) and aging index views. |

### Panels

**Choropleth map** — Prefecture-level choropleth with per-metric colour scales. Hover for prefecture name, population, aging index, and period-over-period delta. Aging index is defined as `population 65+ / population 0–14 × 100` (高齢化指数); values above 100 indicate the elderly population exceeds the child population. Okinawa is greyed out for 1950 and 1955 (see Limitations).

**Population pyramid** — Age/sex butterfly chart for the selected year and geography. Cohort annotations mark the 団塊世代 (dankai), 団塊ジュニア, 戦中世代 (wartime generation), and 少子化世代 birth cohorts. Hover tooltips show cohort context and population figures. The wartime generation's male deficit is visible walking up the pyramid across years.

**Time series** — Switchable between two views via a dropdown selector. The default population view shows national total, male, and female population trends in millions. The aging index view shows national 高齢化指数 (1920–2020) with a reference line at 100 — the crossover point where the elderly population exceeds the child population. Prefecture overlay shown on map selection. The 1945 data point is rendered as a distinct open-circle marker in red, matching the year slider. See Data Notes for 1945 provenance.

**KPI cards** — National population, period-over-period population change, aging index, children 0–14 share, and the most- and least-aged prefectures for the selected year.

---

## Stack

| Library | Role |
|---|---|
| [Dash](https://dash.plotly.com/) | Application framework. Callback-driven interactivity without JavaScript. |
| [Plotly](https://plotly.com/python/) | Chart rendering — choropleth, pyramid, time series. |
| [DuckDB](https://duckdb.org/) | Analytical query engine. Census data stored in a star schema; derived metrics computed via SQL views. |
| [GeoPandas](https://geopandas.org/) | Prefecture geometry — reads the simplified Parquet file and joins to census data for map rendering. |
| [Shapely](https://shapely.readthedocs.io/) | Geometry operations underlying GeoPandas. |
| [Pandas](https://pandas.pydata.org/) | DataFrames for passing query results to Plotly. |
| [NumPy](https://numpy.org/) | Axis scaling utilities. |

---

## Data Notes

**Coverage:** 21 census years, 1920–2020. 1920–2015 sourced from CSV (`000031523105`); 2020 sourced via the e-Stat API (`0003410381`).

**1945 Provisional Census (臨時国勢調査):** The 1945 data point is real official census data, not a gap or estimate. It was conducted November 1, 1945 — 78 days after surrender — and excludes Okinawa, which was under US administration. Age was recorded as kazoedoshi (数え年), a traditional counting system that produces bands offset by one year from completed age. These are converted to standard 5-year bands in the data pipeline. The 1945 marker is visually distinguished on the year slider and time series.

**Okinawa 1950 & 1955:** Greyed out on the choropleth. During this period Okinawa remained under US administration and its census used an open-ended 70+ age band, causing the aging index to be overstated relative to other prefectures. Population figures are included; derived metrics are suppressed.

---

## Limitations

**1945 census (臨時国勢調査)**
The 1945 census was a provisional wartime survey. Age was recorded using the kazoedoshi (数え年) counting convention, producing age bands offset by one year from the standard scheme and no age-0 band. The data is remapped to standard age bands for display. The 1945 data point appears in all panels with a tooltip noting its wartime provenance; it is excluded from choropleth metrics where the remapping introduces unacceptable error.

**Okinawa 1950 & 1955**
Okinawa was under U.S. administration from 1945 until 1972 and was not surveyed under Japanese census methodology for this period. The 1950 and 1955 figures use an open-ended 70+ age band without granular breakdown, which inflates the aging index relative to all other prefectures and years. Okinawa is greyed out on the choropleth for these two years with an explanatory tooltip.

**Geography**
Boundary geometry reflects modern prefecture definitions. Minor historical boundary changes prior to 1960 are not accounted for.

---

## Data Sources

**Census data**
Statistics Bureau of Japan — Population Census (国勢調査), 1920–2020.
Retrieved via [e-Stat](https://www.e-stat.go.jp/). Provided under the [e-Stat Terms of Use](https://www.e-stat.go.jp/terms-of-use). Redistribution of the derived CSV is permitted for non-commercial use with attribution.

**Prefecture boundary geometry**
GeoJSON sourced from [dataofjapan/land](https://github.com/dataofjapan/land), converted from Shapefiles published by the [Geospatial Information Authority of Japan](https://www.gsi.go.jp/) (国土地理院). Simplified at `tolerance=0.001` via Shapely for web rendering.