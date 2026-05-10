# A Century of Japan's Population (1920 - 2020)
### 少子高齢化

100 years of Japanese census data. Visualized across all 47 prefectures. Built as a full-stack portfolio piece targeting the Japanese market.

**[GitHub](https://github.com/HelioCentrik/japan_population)**

---

## What It Shows

Japan has the most advanced aging crisis of any major economy. Every prefecture now has more elderly than children, the working-age population has been shrinking since 1995, and the dependency burden on working adults has nearly sextupled since 1920 — all of it visible in the data.

---

## The Visuals

**Population Pyramid** — The anchor chart. Shows Japan's age and sex breakdown for any census year, nationally or by prefecture. The shift from a wide base in 1920 to an inverted barrel by 2020 tells the whole story at a glance. Key birth cohorts — the post-war boom (団塊世代), its echo, the wartime generation's male deficit, and the low-fertility generations — are annotated directly on the chart.

**Choropleth Map** — Prefecture-level map switchable between total population, aging index, population change, and working-age share. Click a prefecture to filter the pyramid and overlay it on the time series.

**Time Series** — National trend across all 21 census years, switchable between raw population, aging index, and the youth/working-age/elderly share breakdown.

**KPI Cards** — Six headline figures for the selected year: population, change, aging index, children's share, and the most- and least-aged prefectures.

---

## The Pipeline

Raw government data from Japan's e-Stat API  
→ ETL and schema validation  
→ DuckDB star schema (fact + 4 dimension tables, 2 pre-aggregated views)  
→ in-memory load at runtime  
→ two-layer figure cache → Dash/Plotly frontend with a CSS token pipeline for theming. Deployed on Render via Gunicorn.

---

## Stack

Python · JavaScript · Dash 4 · Plotly 6 · DuckDB · GeoPandas · Render

---

## Data & Attribution

**Census data** — Statistics Bureau of Japan, 国勢調査 1920–2020, via
[e-Stat](https://www.e-stat.go.jp/). Non-commercial use with attribution.

**Boundary geometry** — [Geospatial Information Authority of Japan](https://www.gsi.go.jp/)
(国土地理院), via [dataofjapan/land](https://github.com/dataofjapan/land).
Simplified at tolerance=0.001 via Shapely.

**Header photo** — Okinawa, c. 1950–1954. Bert Mosher / The American Photo Service,
archived by [Remembering Okinawa](https://www.rememberingokinawa.com/page/american_photo_2).