# Japan Population Dashboard
### 日本の人口ダッシュボード

An interactive visualization of Japanese census data (1920–2020) across all 47 prefectures.

**Live:** [deanallton.com/japan-population](https://deanallton.com/japan-population)

---

## Setup

### Requirements

Python 3.12+

```bash
pip install -r requirements.txt
```

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

**KPI cards** — National population, period-over-period population change, aging index, children 0–14 share, and the most- and least-aged prefectures for the selected year.

**Choropleth map** — Prefecture-level choropleth with per-metric colour scales. Hover for prefecture name, population, aging index, and period-over-period delta. Aging index is defined as `population 65+ / population 0–14 × 100` (高齢化指数); values above 100 indicate the elderly population exceeds the child population. Okinawa is greyed out for 1950 and 1955 (see Limitations).

**Population pyramid** — Age/sex butterfly chart for the selected year and geography. Cohort annotations mark the 団塊世代 (dankai), 団塊ジュニア, 戦中世代 (wartime generation), and 少子化世代 birth cohorts. Hover tooltips show cohort context and population figures. The wartime generation's male deficit is visible walking up the pyramid across years.

**Time series** — Switchable between two views via a dropdown selector. The default population view shows national total, male, and female population trends in millions. The aging index view shows national 高齢化指数 (1920–2020) with a reference line at 100 — the crossover point where the elderly population exceeds the child population. Prefecture overlay shown on map selection. The 1945 data point is rendered as a distinct open-circle marker in red, matching the year slider.

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

## Data

### Coverage

21 census years, 1920–2020. 1920–2015 sourced from the e-Stat bulk CSV (`000031523105`); 2020 sourced via the e-Stat API (`0003410381`). The repository includes a pre-built `data/japan_population.duckdb` (2MB) — no data pipeline setup is required.

### 1945 Provisional Census (臨時国勢調査)

The 1945 data point is real official census data, not a gap or estimate. It was conducted November 1, 1945 — 78 days after surrender — and excludes Okinawa, which was under US administration. Age was recorded as kazoedoshi (数え年), a traditional counting system that produces bands offset by one year from completed age. These are converted to standard 5-year bands in the data pipeline. The 1945 marker is visually distinguished on the year slider and time series.

### Okinawa 1950 & 1955

Greyed out on the choropleth. During this period Okinawa remained under US administration and its census used an open-ended 70+ age band, causing the aging index to be overstated relative to other prefectures. Population figures are included; derived metrics are suppressed.

### Sources

**Census data** — Statistics Bureau of Japan, Population Census (国勢調査), 1920–2020. Retrieved via [e-Stat](https://www.e-stat.go.jp/) under the [e-Stat Terms of Use](https://www.e-stat.go.jp/terms-of-use). Redistribution of the derived database is permitted for non-commercial use with attribution.

**Prefecture boundary geometry** — GeoJSON sourced from [dataofjapan/land](https://github.com/dataofjapan/land), converted from Shapefiles published by the [Geospatial Information Authority of Japan](https://www.gsi.go.jp/) (国土地理院). Simplified at `tolerance=0.001` via Shapely for web rendering.

**Header photo** — Okinawa, c. 1950–1954. Original photo by Bert Mosher / The American Photo Service. Archived by [Remembering Okinawa](https://www.rememberingokinawa.com/page/american_photo_2).

---

## Limitations

**Geography** — Boundary geometry reflects modern prefecture definitions. Minor historical boundary changes prior to 1960 are not accounted for.

**1945 census** — The kazoedoshi-to-standard-band remapping introduces a one-year shift across all age groups. The 1945 year is excluded from choropleth metrics where this offset would produce misleading comparisons.

---

## Deployment

The app exposes `server = app.server` for WSGI. Deploy with Gunicorn:

```bash
gunicorn app:server
```

**Render settings:**
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:server`
- Python version: 3.11

**Cold start note:** On first request, all figures are built from the committed database into an in-memory cache (~30–60s on a standard instance). Subsequent requests are served from memory.