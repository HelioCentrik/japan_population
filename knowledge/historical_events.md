## Demographic Inflection Points — Japan

Key events visible in the census data, ordered chronologically. Where an event
produces a visible artifact in the pyramid or timeseries, that artifact is described.

---

**1945 — Wartime census**
Conducted under wartime conditions. Uses kazoedoshi (数え年) age reckoning — ages are
one year higher than Western reckoning on average. Figures are provisional; wartime
displacement makes enumeration incomplete. Treat all 1945 values as approximate.
The 1945 data uses scheme_b age bands (1–5, 6–10...) rather than scheme_a (0–4,
5–9...) and is not directly comparable to other census years without remapping.
See `knowledge/census.md` for full detail on the 1945 quirks.

**1947–1949 — 団塊の世代 (dankai no sedai) baby boom**
Births exceeded 2.5 million per year across these three years, peaking at 2.69 million
in 1949 — the highest annual birth count in postwar statistics. Compare to ~730k births
in 2023. The largest single birth cohort in Japanese demographic history. Visible as a
pronounced bulge tracking upward through every subsequent pyramid — 0–4 in 1950,
20–24 in 1970, 65–69 in 2015, 70–74 in 2020. From 2012 onward, the dankai generation
began entering the 65+ bracket, driving the sharp acceleration in aging index and
old-age dependency ratio visible in the timeseries after 2010. Their exit from the
working-age bracket (15–64) is the primary structural driver of working-age share
decline post-2010.

**1950 — WWII male deficit**
The 25–29 age band shows a sex ratio of approximately 83.8 males per 100 females in
the 1950 census. This reflects combat casualties from WWII — young men who did not
return. The deficit is also visible in the 30–34 band in 1955 as the cohort ages. Not
a data error. See `knowledge/census.md`.

**1966 — 丙午 (hinoeuma, fire horse year)**
The traditional belief that daughters born in hinoeuma years bring misfortune to their
husbands caused many couples to delay or avoid births in 1966. National TFR dropped
to 1.58 — the lowest recorded to that point. The resulting cohort notch (a narrow
band of unusually few people born in 1966) is visible as:
- A thinning in the 20–24 band of the 1985 pyramid
- A thinning in the 25–29 band of the 1990 pyramid
- Continuing to track upward in subsequent censuses
This is a single-year anomaly, not a trend. The cohort notch has no causal relationship
to subsequent TFR decline.

**1971–1974 — 団塊ジュニア (dankai junior) secondary boom**
Children of the dankai generation. Birth counts exceeded 2 million per year, peaking
at 2.09 million in 1973. The 1973 peak is ~22% below the 1949 dankai peak of 2.69M —
reflecting already-declining TFR despite the large parent cohort. Visible as a secondary
bulge trailing the dankai bulge by ~25 years in every pyramid. As this generation ages
toward 65+ (beginning ~2036), a second wave of pressure on the aging index and
dependency ratio is projected. Their concentration in Tokyo metro during the 1990s
(for education and employment) is a key factor behind the persistent urban–rural
migration imbalance.

**1973 — End of high-growth era**
The first oil shock ends Japan's postwar high-growth period. TFR begins sustained
decline below replacement level from this point. The economic shift from manufacturing
to services accelerates urbanization and the structural conditions for delayed marriage
and lower fertility.

**1989 — 1.57 ショック (1.57 Shock)**
National TFR fell to 1.57, dropping below the 1966 hinoeuma figure for the first time.
This was symbolically significant — hinoeuma had been treated as a one-off anomaly, so
falling below it confirmed that low fertility was structural, not cyclical. Triggered
sustained national policy attention: Angel Plan (1994), New Angel Plan (1999), and
successive childcare and parental leave expansions through the 2000s–2010s.

**1995 — Working-age share peaks**
Working-age population (15–64) reaches its national peak share at approximately 69.5%
of total population (computable from `f_census`). Every subsequent census shows decline.
The 1995 census represents the demographic high-water mark for Japan's productive labor
capacity. Prefectures with high outmigration began their working-age decline earlier —
some rural prefectures peaked in 1985 or 1990, directly verifiable from `f_census`.

**~1997 — Aging index crosses 100 nationally**
Between the 1995 and 2000 censuses, Japan's aging index (elderly population 65+ divided
by child population 0–14, multiplied by 100) crossed 100 for the first time — meaning
elderly outnumbered children at the national level. The ~1997 figure is an interpolation;
the 1995 and 2000 census values bracketing the crossover are directly computable from
`f_census`. In prefectures with high outmigration, this crossover occurred earlier:
Shimane and Akita crossed 100 before 1990, verifiable from `f_census`.

**2005 — TFR historical low**
National TFR reaches 1.26 — the lowest recorded value in the dataset (verifiable from
`f_tfr`). Partial recovery followed through 2015, attributed to tempo rebound
(stabilization of mean age at first birth) and modest policy effects, before renewed
decline from 2016.

**2008 — National population peaks**
Japan's total population reaches its historical peak at 128.1 million in October 2008.
Every census after 2010 records a lower total than the previous one. Absolute population
decline — not just slower growth — becomes the defining condition from this point.

**2011 — Tōhoku earthquake and tsunami (3/11)**
Not a census year, but affects the 2010–2015 intercensal period. Iwate, Miyagi, and
Fukushima prefectures experienced direct population loss and prolonged displacement.
Fukushima's population decline in this period reflects both disaster impact and nuclear
evacuation — not purely demographic trend. Interpret 2015 figures for these three
prefectures with this context.

---

### Sources

- **Dankai baby boom birth counts (2.5M+/year, 2.69M peak in 1949):**
  Wikipedia, "Baby boom" — Japan section
  https://en.wikipedia.org/wiki/Baby_boom
- **Dankai junior peak births (2.09M in 1973):**
  Same source as above; also: Nippon.com, "Number of Japanese Births Falls for Tenth
  Successive Year in 2025"
  https://www.nippon.com/en/japan-data/h02717/
- **2023 birth count (~730k):**
  Nippon.com, "Japan's Fertility Rate Drops to New Record Low"
  https://www.nippon.com/en/japan-data/h02015/
- **~1997 aging index crossover (elderly > children nationally):**
  Wikipedia, "Aging of Japan"
  https://en.wikipedia.org/wiki/Aging_of_Japan
- **Japan population peak — 128.1 million in October 2008:**
  Wikipedia, "Aging of Japan"; primary source is Statistics Bureau population estimates
  https://en.wikipedia.org/wiki/Aging_of_Japan
- **3/11 earthquake demographic context:**
  Reconstruction Agency of Japan
  https://www.reconstruction.go.jp/english/