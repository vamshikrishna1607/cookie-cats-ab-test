import nbformat as nbf
import re

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(path, drop_prefix_lines=0):
    with open(path) as f:
        src = f.read()
    # strip the module docstring block at top (already covered by markdown)
    src = re.sub(r'^"""[\s\S]*?"""\n', '', src, count=1)
    cells.append(nbf.v4.new_code_cell(src.strip()))

md("""# A/B Test Analysis: Cookie Cats — Gate Placement & Player Retention

**Business question:** Cookie Cats is a mobile puzzle game with a progress gate (a forced wait/paywall) that
was originally placed at level 30. This analysis evaluates an experiment that moved the gate to level 40,
to determine whether the change should ship.

**Dataset:** [Cookie Cats A/B test](https://www.kaggle.com/datasets/arpitdw/cokie-cats) — 90,189 players randomly
assigned to `gate_30` (control) or `gate_40` (treatment), with Day-1 retention, Day-7 retention, and total
rounds played recorded per player.

**Methodology overview:**
1. Data validation + Sample Ratio Mismatch (SRM) check
2. Hypothesis tests on Day-1 and Day-7 retention (two-proportion z-test, Wilson CIs, bootstrap CI)
3. Effect size and post-hoc power analysis
4. Engagement test on rounds played (Mann-Whitney U, after outlier handling)
5. Retention-curve extrapolation to Day-14/Day-30 (mobile-analytics power-law model)
6. Business recommendation
""")

md("## 1. Data Validation & Sample Ratio Mismatch (SRM) Check\n\n"
   "Before trusting any test result, we confirm the data is clean and that randomization actually worked "
   "(an SRM — an unexpected imbalance in group sizes — can silently invalidate an entire experiment).")
code("notebooks/01_eda.py")
md("""**Findings:**
- No missing values, no duplicate users.
- Group sizes: `gate_30` = 44,700, `gate_40` = 45,489 (49.6% / 50.4% split).
- A naive chi-square SRM test flags this at p = 0.0086 — but at this sample size (90K+), chi-square is
  extremely sensitive to tiny imbalances. Standard practice (Kohavi et al., trustworthy online experiments)
  is to use a stricter SRM threshold of **p < 0.001** specifically to avoid false alarms at scale. At that
  threshold, this passes — randomization is sound.
- One extreme outlier: a single `gate_30` user logged 49,854 rounds vs. a next-highest value of 2,961
  (~17x higher) — almost certainly a bot/QA account, not a real player. Excluded from the engagement
  analysis below, with the exclusion documented rather than silently dropped.
""")

md("## 2. Retention Hypothesis Tests\n\n"
   "Primary metrics: Day-1 and Day-7 retention. Using a two-proportion z-test as the primary test, "
   "Wilson confidence intervals (better calibrated than the normal approximation for proportions), "
   "a bootstrap CI as an assumption-light cross-check, and a post-hoc power analysis to know whether "
   "a non-significant result actually means 'no effect' or just 'underpowered.'")
code("notebooks/02_hypothesis_tests.py")
md("""**Findings:**

| Metric | gate_30 | gate_40 | Abs. diff | p-value | Achieved power |
|---|---|---|---|---|---|
| Day-1 retention | 44.82% | 44.23% | +0.59pp | 0.074 (not significant) | 43% (underpowered) |
| Day-7 retention | 19.02% | 18.20% | +0.82pp | **0.0016 (significant)** | 89% (well-powered) |

Both metrics point the same direction — `gate_30` retains better — but only Day-7 clears both statistical
significance **and** adequate power. The Day-1 result should be read as directionally consistent, not as
independent evidence, since a 43%-powered test isn't reliable enough to lean on by itself.
""")

md("## 3. Engagement Test — Rounds Played\n\n"
   "Distribution is heavily right-skewed (most players churn early, a few play a lot), so a t-test's "
   "normality assumption doesn't hold. Mann-Whitney U (rank-based) is used instead.")
code("notebooks/03_engagement_test.py")
md("""**Finding:** No practically meaningful difference in engagement between gates (p = 0.051, effect size
≈ 0 at -0.0075). The gate placement affects *whether* players come back, not *how much* they play once
they're in.
""")

md("## 4. Retention Curve Forecast (Day-14 / Day-30)\n\n"
   "**Scope note:** the dataset only provides two retention anchor points per user (Day-1, Day-7) — there's "
   "no daily cohort panel to build a full time-series model from. Instead, this uses a standard mobile-game "
   "analytics technique: fitting a power-law retention decay curve `R(t) = a·t⁻ᵇ` through the two known points "
   "per variant, then extrapolating forward. This is the same family of model studios use for early-stage "
   "retention/LTV forecasting — but it **is an extrapolation, not a measurement**, and should be presented "
   "as directional only.")
code("notebooks/04_retention_curve_forecast.py")
md("""**Finding:** the projected gap widens slightly by Day-30 (10.0% vs. 9.4% projected retention),
consistent with — but not independent confirmation of — the Day-7 result above.
""")

md("## 5. Summary Charts")
code("notebooks/05_charts.py")
md("""![Retention rates](../dashboard/retention_rates.png)
![Rounds distribution](../dashboard/rounds_distribution.png)
![SRM check](../dashboard/srm_check.png)
![Retention curve forecast](../dashboard/retention_curve_forecast.png)
""")

md("""## 6. Business Recommendation

**Do not move the gate from level 30 to level 40.**

- Day-7 retention — the more reliable of the two retention metrics here, both statistically significant
  and adequately powered — is **0.82 percentage points (4.5% relative) higher** when the gate stays at
  level 30.
- Day-1 retention trends the same direction but isn't independently conclusive (underpowered).
- Engagement (rounds played) is unaffected either way, so there's no offsetting upside to moving the gate.
- The Day-14/Day-30 extrapolation is directionally consistent with keeping the gate at level 30, though it
  should be treated as a projection, not a guarantee.

**Practical significance check:** a 0.82pp absolute lift in Day-7 retention, at Cookie Cats' scale, compounds
into a meaningfully larger retained player base over time — this isn't just statistically real, it's large
enough to matter for the business.

**Caveats for a future re-run:** this experiment only measures short-term retention and engagement; it
doesn't capture monetization or long-term (Day-30+) *measured* retention. A follow-up test with a longer
observation window would close that gap.
""")

nb['cells'] = cells
with open('/home/claude/ab-test-project/notebooks/AB_Test_Cookie_Cats_Analysis.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook written.")
