# A/B Test Analysis: Cookie Cats — Gate Placement & Player Retention

**Author:** Gundapaneni Vamshi Krishna
**Tools:** Python (Pandas, SciPy, statsmodels, Matplotlib), Jupyter

## Business Question

Cookie Cats is a mobile puzzle game with a progress gate — a forced wait before continuing — originally
placed at level 30. The product team ran an A/B test moving the gate to level 40 to see whether delaying
it would improve or hurt player retention. **Should the gate move to level 40, stay at level 30, or is the
result inconclusive?**

## Dataset

[Cookie Cats A/B test](https://www.kaggle.com/datasets/arpitdw/cokie-cats) — 90,189 players randomly split
between `gate_30` (control) and `gate_40` (treatment), with Day-1 retention, Day-7 retention, and total
rounds played recorded per player.

## Approach

1. **Data validation + Sample Ratio Mismatch (SRM) check** — confirm the randomization actually worked
   before trusting any downstream result.
2. **Retention hypothesis tests** — two-proportion z-test, Wilson confidence intervals, and a bootstrap CI
   as a cross-check, for both Day-1 and Day-7 retention.
3. **Effect size + post-hoc power analysis** — so a non-significant result can be read correctly as either
   "no effect" or "underpowered test," which are very different conclusions.
4. **Engagement test** — Mann-Whitney U test on rounds played, after documenting and excluding one extreme
   outlier user.
5. **Retention curve extrapolation** — a power-law decay model projecting Day-14/Day-30 retention from the
   two measured anchor points, clearly labeled as a directional projection rather than a measurement.

## Key Findings

| Metric | gate_30 | gate_40 | Difference | Statistical significance | Power |
|---|---|---|---|---|---|
| Day-1 retention | 44.82% | 44.23% | +0.59pp | Not significant (p = 0.074) | 43% (underpowered) |
| Day-7 retention | 19.02% | 18.20% | **+0.82pp** | **Significant (p = 0.0016)** | 89% (well-powered) |
| Rounds played | median 17 | median 16 | ~0 | Not significant (p = 0.051) | — |

- The sample split (44,700 vs. 45,489) triggers a naive SRM alarm, but clears the stricter p < 0.001
  threshold used in practice for large-sample experiments — randomization is sound.
- One user with 49,854 rounds (vs. a next-highest of 2,961) was excluded from the engagement analysis as a
  data-quality outlier.
- Both retention metrics point the same direction, but only Day-7 is both significant and adequately
  powered — that's the result this recommendation leans on.
- A power-law extrapolation to Day-14/Day-30 projects the gap widening slightly further, consistent with
  (not independent confirmation of) the Day-7 result.

## Recommendation

**Keep the gate at level 30. Do not ship the move to level 40.**

Day-7 retention — the most reliable metric in this test — is 4.5% relatively higher (0.82 percentage
points) when the gate stays at level 30, a difference that is both statistically significant and large
enough, at Cookie Cats' scale, to meaningfully affect the retained player base over time. There is no
offsetting engagement benefit to moving the gate later. A follow-up test with a longer observation window
(Day-14/Day-30 *measured*, not projected) would further de-risk this decision before a permanent rollout.

## Power BI Dashboard

The Python analysis feeds a companion Power BI dashboard (4 pages: Overview, Retention
Results, Engagement, Retention Forecast) — statistical rigor stays in Python, Power BI
handles the interactive presentation layer. See `dashboard/POWERBI_BUILD_GUIDE.md` for
the full build steps, DAX measures, and layout, and `dashboard/CookieCats_PowerBI_Theme.json`
for the matching color theme.

## Repo Structure

```
notebooks/
  AB_Test_Cookie_Cats_Analysis.ipynb   <- full analysis, run this one
  01_eda.py ... 05_charts.py           <- source scripts the notebook is built from
dashboard/
  retention_rates.png / rounds_distribution.png / srm_check.png / retention_curve_forecast.png
  POWERBI_BUILD_GUIDE.md               <- step-by-step Power BI build guide
  CookieCats_PowerBI_Theme.json        <- Power BI custom theme (matches chart colors)
data/
  cookie_cats.csv
  retention_test_results.csv / retention_curve_results.csv
  powerbi_kpi_cards.csv / powerbi_retention_summary.csv
  powerbi_retention_curve.csv / powerbi_engagement_bins.csv
```

## How to Run

```bash
pip install pandas numpy scipy statsmodels matplotlib jupyter
jupyter notebook notebooks/AB_Test_Cookie_Cats_Analysis.ipynb
```
