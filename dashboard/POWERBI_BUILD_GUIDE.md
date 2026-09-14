# Power BI Dashboard — Build Guide
### Cookie Cats A/B Test: Gate Placement & Retention

This turns the Python analysis into an interactive Power BI dashboard. The statistical
tests (z-tests, bootstrap CIs, power analysis) stay in Python — that's the right tool for
them — and their *results* get imported into Power BI for presentation and exploration.
That split (Python for rigor, Power BI for the story) is exactly how this works in a real
analytics team, and it's worth saying explicitly if you're asked about it in an interview.

## 1. Files you need

All in the `data/` folder:
- `cookie_cats.csv` — raw data, for a drill-down table and DAX measures
- `powerbi_kpi_cards.csv` — headline numbers for the top KPI row
- `powerbi_retention_summary.csv` — retention rate, p-value, power, CI by metric/version
- `powerbi_retention_curve.csv` — measured (Day 1/7) + projected (Day 14/30) retention
- `powerbi_engagement_bins.csv` — rounds-played, bucketed, by version

Plus `dashboard/CookieCats_PowerBI_Theme.json` — a custom theme with the same two colors
used in the Python charts, so the whole project looks like one consistent piece of work.

## 2. Import

1. Power BI Desktop → **Get Data → Text/CSV** → import all five CSVs above (one at a time,
   or select all five in one Get Data dialog since they're in the same folder).
2. In Power Query, confirm `retention_1`/`retention_7` on `cookie_cats.csv` are typed as
   **True/False**, and `Version`/`version` columns are **Text**. Click **Close & Apply**.
3. **View → Themes → Browse for themes** → select `CookieCats_PowerBI_Theme.json`.
4. **Model view**: these tables are independent (each is already a finished summary, not
   a fact table needing joins) — you don't need relationships between them. If Power BI
   auto-detects a relationship on a shared column name like "Version," that's fine to
   leave, but nothing in this guide depends on it.

## 3. DAX measures (on the `cookie_cats` table)

```
Total Users = COUNTROWS(cookie_cats)

Day1 Retention % =
DIVIDE(
    CALCULATE(COUNTROWS(cookie_cats), cookie_cats[retention_1] = TRUE),
    [Total Users]
)

Day7 Retention % =
DIVIDE(
    CALCULATE(COUNTROWS(cookie_cats), cookie_cats[retention_7] = TRUE),
    [Total Users]
)

Median Rounds Played = MEDIAN(cookie_cats[sum_gamerounds])

Avg Rounds Played (excl. outlier) =
CALCULATE(
    AVERAGE(cookie_cats[sum_gamerounds]),
    cookie_cats[userid] <> 6390605
)
```

Format the two retention measures as **Percentage, 2 decimals**.

## 4. Page 1 — Experiment Overview

**KPI card row** (top of page, 5 cards side by side), from `powerbi_kpi_cards.csv`:
Total Users · gate_30 Users · gate_40 Users · Day-7 Lift (pp) · Day-7 p-value.
Use a plain **Card** visual for each — no colored background, just the number and label,
per the theme (avoid decorating a number that doesn't need it).

**Recommendation banner** below the cards: a text box, not a visual — "Recommendation:
Keep the gate at level 30" in the theme's `good` color (#1A7F37), since this is a
status/decision, not a data series. Don't reuse the categorical blue/orange for this —
status color is reserved for state, never for "another series."

**SRM check** (small multiple, bottom-left): Clustered column, `Version` on axis,
`Total Users` (or a `Count of userid`) as value, with a constant reference line at 45,094.5
(Format pane → Analytics → Constant line) labeled "Expected (50/50)."

## 5. Page 2 — Retention Results

Source: `powerbi_retention_summary.csv`.

**Main visual**: Clustered column chart. Axis = `Metric` (Day-1 Retention, Day-7
Retention), Legend = `Version`, Values = `Retention Rate` (format as %). This is the one
chart on the dashboard doing the real work, so give it the most space.

- **One axis only** — don't add p-value as a second y-axis on this chart. It lives in the
  table below instead.
- **Fixed color order**: gate_30 = #2E5EAA (blue), gate_40 = #D96C3F (orange) — set this
  explicitly in Format → Data colors rather than letting Power BI auto-assign, so the
  mapping never flips if you reorder or filter.
- Turn on **Data labels** (both series, since there are only two — direct labels beat
  forcing someone to read the axis).

**Supporting table** below/beside it: columns `Metric`, `Version`, `Retention Rate`,
`P-Value`, `Significant (p<0.05)`, `Achieved Power`. This is where the statistical rigor
actually shows — conditional formatting on `Significant (p<0.05)` (green text for "Yes")
makes it scannable.

**Slicer**: `Version`, so a viewer can isolate one arm — but keep both selected by default
so the comparison is visible on load.

## 6. Page 3 — Engagement

Source: `powerbi_engagement_bins.csv`.

Clustered column: Axis = `Rounds Played Bucket` (this column is already ordered low→high
in the CSV — in Power Query, right-click the column → **Sort by Column** isn't needed
since it's categorical text; instead set **Column tools → Sort by Column** to a hidden
numeric rank if the buckets render out of order), Legend = `Version`, Values = `Users`.
Same two colors, same legend, for visual consistency with Page 2.

Add two cards above it: `Median Rounds Played` and `Avg Rounds Played (excl. outlier)`
from your DAX measures, one per version (use a small matrix/table instead of cards if you
want both versions visible at once without a slicer).

## 7. Page 4 — Retention Forecast

Source: `powerbi_retention_curve.csv`.

Line chart: Axis = `Day`, Legend = `Version`, Values = `Retention` (format as %). To show
measured-vs-projected without a second axis: add `Type` to a **small multiples** field (or
use the `Type` column to set line style — solid for Measured, dashed for Projected, via
Format → this requires either two overlapping line visuals filtered by Type, or a
conditional formatting workaround; simplest is two visuals stacked with matching axes and
a shared legend, with a text annotation "Day 7 → dashed = projected").
Add a text callout near Day 7: "Measured range ends here — Day 14/30 are extrapolated,
not observed" so nobody reads the projection as a measurement.

## 8. Final pass (do this before calling it done)

- Every chart with 2+ series has a visible legend; gate_30/gate_40 use the *same* two
  colors on every page (Format → Data colors, matched to the theme, not re-picked per page).
- No dual-axis charts anywhere.
- Status color (green/red) appears only on the recommendation banner and the
  "Significant" column — never as a third data series color.
- Click through as a viewer: do the cards, chart, and table on each page agree with each
  other and with the README's numbers?

## 9. Ship it

- **File → Export → Export to PDF** for a static copy to attach alongside the notebook.
- If you have a Power BI Service account (free tier works), **Publish** it and grab the
  shareable link — put that link in your GitHub README and resume bullet instead of just
  a screenshot, so it's interactive.
- Screenshot Page 1 for the GitHub README's top (a picture people actually look at before
  reading further).
