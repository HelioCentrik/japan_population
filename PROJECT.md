# A Century of Japan's Population (1920 - 2020)
### 少子高齢化

100 years of Japanese census data. Visualized across all 47 prefectures. Built as a full-stack portfolio piece targeting the Japanese market.

**[GitHub](https://github.com/HelioCentrik/japan_population)**

***Click the Gemini icon*** to query the dashboard with **Gemini 3.1 Flash Lite**.

---

## What It Shows

Japan has the most advanced aging crisis of any major economy. Every prefecture now has more elderly than children, the working-age population has been shrinking since 1995, and the dependency burden on working adults has nearly sextupled since 1920.

---

## The Visuals

**Population Pyramid** - Shows Japan's age and sex breakdown for any census year, nationally or by prefecture. The shift from a wide base in 1920 to an inverted barrel by 2020 tells the whole story at a glance. Key birth cohorts are annotated in the chart tooltips, including the post-war boom (団塊世代), its echo, the wartime generation's male deficit, and the low-fertility generations.

**Map of Japan** - Prefecture-level map switchable between total population, aging index, population change, and working-age share. Click a prefecture to filter the pyramid and overlay it on the time series.

**Time Series** - National trend across all 21 census years, switchable between raw population, total fertility rate (TFR), and the youth/working-age/elderly share breakdown. Population and share views include IPSS projection overlays from 2020, with high/low confidence bands.

**KPI Cards** - Six headline figures for the selected year: national population, period change, aging index, working-age share, TFR, and the most migrated-to prefecture.

The Gemini AI panel can answer questions across all four datasets — including historical birth rates and TFR trends by prefecture, internal migration patterns, and IPSS population projections through 2045.

---

## The Pipeline

Five government sources (e-Stat census API, MHLW vital statistics, IPSS prefectural projections, IPSS national projections, e-Stat migration reports)  
→ per-source ETL scripts with validation, deduplication, and schema alignment  
→ DuckDB star schema (5 fact tables · 4 dimension tables · 5 pre-aggregated views)  
→ two-layer figure cache (in-memory dict + disk store with DB fingerprint invalidation)  
→ Dash/Plotly frontend with a CSS custom property token pipeline for theming  
→ Gemini Flash AI side panel grounded in a structured domain knowledge base  
Self-hosted via Gunicorn behind Nginx.

---

## Stack

Python · JavaScript · Dash 4 · Plotly 6 · DuckDB · GeoPandas

---

## Data & Attribution

**Census data** - Statistics Bureau of Japan, 国勢調査 1920-2020, via [e-Stat](https://www.e-stat.go.jp/). Non-commercial use with attribution.

**TFR data** - Ministry of Health, Labour and Welfare, Vital Statistics (人口動態統計). Prefecture-level, 1960–2024, via [e-Stat](https://www.e-stat.go.jp/).

**Population projections** - National Institute of Population and Social Security Research (国立社会保障・人口問題研究所). Prefecture-level: 2018 edition, 2015–2045, from [ipss.go.jp](https://www.ipss.go.jp/pp-shicyoson/e/shicyoson18/t-page.asp). National: 2017 edition, 2015–2065 (medium/high/low variants), from [ipss.go.jp](https://www.ipss.go.jp/pp-zenkoku/e/zenkoku_e2017/pp_zenkoku2017e.asp).

**Internal migration** - Statistics Bureau of Japan, 住民基本台帳人口移動報告. Prefecture-level net migration, 1985–2020, via [e-Stat](https://www.e-stat.go.jp/).

**Boundary geometry** - [Geospatial Information Authority of Japan](https://www.gsi.go.jp/) (国土地理院), via [dataofjapan/land](https://github.com/dataofjapan/land). Simplified at tolerance=0.01 via Shapely.

**Header photo** - Okinawa, c. 1950-1954. Bert Mosher / The American Photo Service, archived by [Remembering Okinawa](https://www.rememberingokinawa.com/page/american_photo_2).