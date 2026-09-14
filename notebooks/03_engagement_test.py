"""
Step 3: Engagement test — sum_gamerounds between gate_30 and gate_40
Outlier (49,854 rounds) excluded per project decision.
Distribution is heavily right-skewed -> use Mann-Whitney U (non-parametric).
"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("data/cookie_cats.csv")

# Exclude the extreme outlier (documented decision)
outlier_id = df.loc[df.sum_gamerounds.idxmax(), "userid"]
print(f"Excluding userid {outlier_id} (sum_gamerounds = {df.sum_gamerounds.max()}) as a data-quality outlier "
      f"(~17x the next-highest value of {df.sum_gamerounds.nlargest(2).iloc[1]}, consistent with a bot/QA account).")
df_clean = df[df.userid != outlier_id].copy()

g30 = df_clean[df_clean.version == "gate_30"]["sum_gamerounds"]
g40 = df_clean[df_clean.version == "gate_40"]["sum_gamerounds"]

print(f"\ngate_30: n={len(g30)}, mean={g30.mean():.2f}, median={g30.median():.1f}, std={g30.std():.2f}")
print(f"gate_40: n={len(g40)}, mean={g40.mean():.2f}, median={g40.median():.1f}, std={g40.std():.2f}")

# Skewness check to justify non-parametric test choice
print(f"\nSkewness gate_30: {stats.skew(g30):.2f}")
print(f"Skewness gate_40: {stats.skew(g40):.2f}")
print("-> Heavily right-skewed in both groups; a t-test's normality assumption doesn't hold well, "
      "so Mann-Whitney U (rank-based, robust to skew/outliers) is the appropriate test.")

# Mann-Whitney U test
u_stat, p_val = stats.mannwhitneyu(g30, g40, alternative="two-sided")
print(f"\nMann-Whitney U test: U={u_stat:.1f}, p={p_val:.4f}")

# Rank-biserial correlation as effect size for Mann-Whitney
n1, n2 = len(g30), len(g40)
rank_biserial = 1 - (2 * u_stat) / (n1 * n2)
print(f"Rank-biserial correlation (effect size): {rank_biserial:.4f}")

print("\nConclusion: " + (
    "No statistically significant difference in engagement (rounds played) between gates."
    if p_val >= 0.05 else
    "Statistically significant difference in engagement between gates."
))
