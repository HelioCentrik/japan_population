## The Masuda Report and Municipal Extinction Risk

### Source and Background

Author: Masuda Hiroya (増田寛也), former Minister of Internal Affairs and Communications,
at the time a guest professor at the University of Tokyo's Graduate School of Public Policy.

Published: May 2014, under the Japan Policy Council (日本創成会議, JPC) — a private
research body whose membership included senior figures from government, industry, and
academia. Widely treated as quasi-official.

Full title: 「地方消滅 — 東京一極集中が招く人口急減」(Chihou Shometsu: Tokyo ikkkyoku
shuuchu ga maneku jinkou kyuugen). Published in book form by Chūō Kōron Shinsha.

A 10-year follow-up was published in April 2024 by the 人口戦略会議 (Population Strategy
Council, PSC) — a successor body — under the title "2024 Sustainability Analysis Report
in Local Municipalities." The 2024 report uses the same core methodology applied to the
2020 census baseline, with a 2020–2050 projection window.

### Core Claim

**2014 edition:** 896 of Japan's ~1,800 municipalities are projected to "disappear" by
2040. Defined as: losing ≥50% of their young female population (ages 20–39) between
2010 and 2040, assuming migration trends continue unchanged.

**2024 edition:** 744 of 1,729 municipalities meet the same extinction criterion over
the 2020–2050 window — a reduction of 152 from 2014. Of the 2014 cohort, 239
municipalities have since escaped extinction-risk classification.

Note: the 2014 count of 896 excluded Fukushima Prefecture municipalities due to
post-3/11 displacement distorting migration data. The 2024 count includes Fukushima;
excluding it yields 711, making the true like-for-like improvement larger than
the headline 896→744 comparison suggests.

### The Mechanism

The Masuda argument is not primarily about TFR. The mechanism is:

1. Rural outmigration drains the young female population (20–39)
2. With few potential mothers, the absolute number of births collapses regardless of TFR
3. Fewer births → accelerated population aging → further erosion of services and economic
   opportunity → accelerated outmigration
4. The spiral becomes self-reinforcing past a tipping point. The report argues that
   communities are often unaware the threshold has been crossed until it's too late to reverse.

This is why the dashboard's working-age share and aging index metrics — not TFR alone —
are the relevant diagnostic signals for extinction risk at the prefecture level.

### Prefectures That Consistently Appear at High Risk

Akita, Shimane, Kochi, Iwate. These prefectures show the highest aging index, lowest
working-age share, and highest projected elderly share in `f_projections` across
multiple census years. Their appearance on the Masuda high-risk list is directly
reflected in what the dashboard's map displays.

### Policy Response

The report's release in May 2014 triggered an immediate national response. Prime Minister
Abe announced a regional revitalization campaign within weeks. By September 2014, a new
ministerial post (Minister for Regional Revitalization) was created. The "Headquarters
for Population, Community, and Job Creation" (まち・ひと・しごと創生本部) was established
under the Cabinet Secretariat to formulate response strategies. The Masuda Report is the
direct policy origin of Japan's regional revitalization (地方創生) framework.

### Counter-Arguments and Limitations

- **Methodology critique:** Critics note that 879 municipalities had already seen their
  young female population halve between 1980–2020 — roughly the same number the 2014
  report predicted would disappear — yet none have formally "disappeared." The extinction
  criterion (loss of young women) is a leading indicator, not a sufficient condition.
  (Source: RIETI, June 2024)
- **Migration reversal:** The 2024 report's lower count (744 vs. 896) reflects partial
  recovery in some municipalities — attributed to remote-work structural shifts and
  targeted migration incentives post-2020. The direction of risk has not changed, but
  the pace is not uniformly worsening.
- **Aggregation level:** The report operates at the municipality level; the dashboard
  operates at the prefecture level. A prefecture can contain both high-risk and
  lower-risk municipalities. Treat prefecture-level metrics as averages that may mask
  acute intra-prefecture variation.
- **Masuda data is not in the DB.** The extinction-risk classifications are not stored
  in any dashboard table. This is reference context only — use it to explain *why*
  certain prefectural metrics matter, not to quote specific municipal risk counts.

### Sources

- Original report (book): Masuda Hiroya, 「地方消滅」, Chūō Kōron Shinsha, May 2014.
  ISBN 978-4-12-102950-5
- Japan Policy Council proposal document (PDF):
  http://www.policycouncil.jp/pdf/prop03/prop03.pdf
- 2024 Population Strategy Council report (PDF):
  https://www.hit-north.or.jp/cms/wp-content/uploads/2024/04/01_report-1.pdf
- Japan Times coverage of 2024 report (April 24, 2024):
  https://www.japantimes.co.jp/news/2024/04/24/japan/society/depopulation-municipalities-vanish/
- RIETI critique of extinction methodology (June 2024):
  https://www.rieti.go.jp/en/rieti_report/320.html
- Tokyo Foundation English summary of 2014 report:
  https://www.tokyofoundation.org/research/detail.php?id=589