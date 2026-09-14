"""
Step 1: EDA + Sample Ratio Mismatch (SRM) check
Cookie Cats A/B test — gate_30 vs gate_40
"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("/home/claude/ab-test-project/data/cookie_cats.csv")

print("=== Shape & dtypes ===")
print(df.shape)
print(df.dtypes)

print("\n=== Nulls ===")
print(df.isnull().sum())

print("\n=== Duplicate userids ===")
print(df['userid'].duplicated().sum())

print("\n=== Group sizes ===")
counts = df['version'].value_counts()
print(counts)

# --- Sample Ratio Mismatch check ---
# Expected: 50/50 split. Chi-square goodness-of-fit test.
n_total = counts.sum()
expected = [n_total / 2, n_total / 2]
observed = [counts['gate_30'], counts['gate_40']]
chi2, p_srm = stats.chisquare(f_obs=observed, f_exp=expected)
print(f"\n=== SRM check ===")
print(f"Observed: {observed}, Expected: {expected}")
print(f"Chi2 = {chi2:.4f}, p-value = {p_srm:.4f}")
print("PASS: randomization looks fine (p > 0.01)" if p_srm > 0.01 else "WARNING: possible sample ratio mismatch (p <= 0.01)")

print("\n=== sum_gamerounds distribution ===")
print(df['sum_gamerounds'].describe())
print("Max value (check for outlier):", df['sum_gamerounds'].max())
print("Top 5 highest:")
print(df.nlargest(5, 'sum_gamerounds')[['userid', 'version', 'sum_gamerounds']])

print("\n=== Retention rates (raw) ===")
print(df.groupby('version')[['retention_1', 'retention_7']].mean())
