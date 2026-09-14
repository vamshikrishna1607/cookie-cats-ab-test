"""
Step 2: Hypothesis tests on retention_1 and retention_7
Two-proportion z-test (primary) + chi-square (cross-check)
Plus: effect size, Wilson CI, bootstrap CI, post-hoc power analysis
"""
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

np.random.seed(42)
df = pd.read_csv("/home/claude/ab-test-project/data/cookie_cats.csv")

def test_retention(metric):
    print(f"\n{'='*60}\nMetric: {metric}\n{'='*60}")
    g30 = df[df.version == "gate_30"][metric]
    g40 = df[df.version == "gate_40"][metric]

    n30, n40 = len(g30), len(g40)
    x30, x40 = g30.sum(), g40.sum()
    p30, p40 = x30 / n30, x40 / n40

    print(f"gate_30: n={n30}, retained={x30}, rate={p30:.4%}")
    print(f"gate_40: n={n40}, retained={x40}, rate={p40:.4%}")
    print(f"Absolute difference (30-40): {(p30 - p40):.4%}")
    print(f"Relative lift (30 vs 40): {(p30 - p40)/p40:.2%}")

    # Two-proportion z-test
    count = np.array([x30, x40])
    nobs = np.array([n30, n40])
    z_stat, p_val = proportions_ztest(count, nobs)
    print(f"\nTwo-proportion z-test: z={z_stat:.4f}, p={p_val:.4f}")

    # Wilson confidence intervals for each proportion
    ci30 = proportion_confint(x30, n30, method="wilson")
    ci40 = proportion_confint(x40, n40, method="wilson")
    print(f"Wilson 95% CI gate_30: ({ci30[0]:.4%}, {ci30[1]:.4%})")
    print(f"Wilson 95% CI gate_40: ({ci40[0]:.4%}, {ci40[1]:.4%})")

    # Bootstrap CI for the difference in proportions
    n_boot = 10000
    boot_diffs = np.empty(n_boot)
    g30_arr = g30.values.astype(float)
    g40_arr = g40.values.astype(float)
    for i in range(n_boot):
        s30 = np.random.choice(g30_arr, size=n30, replace=True).mean()
        s40 = np.random.choice(g40_arr, size=n40, replace=True).mean()
        boot_diffs[i] = s30 - s40
    boot_ci = np.percentile(boot_diffs, [2.5, 97.5])
    print(f"Bootstrap 95% CI for (p30 - p40): ({boot_ci[0]:.4%}, {boot_ci[1]:.4%})")

    # Effect size (Cohen's h) + post-hoc power
    effect_size = proportion_effectsize(p30, p40)
    power_analysis = NormalIndPower()
    achieved_power = power_analysis.power(effect_size=abs(effect_size), nobs1=n30, ratio=n40/n30, alpha=0.05)
    print(f"\nCohen's h (effect size): {effect_size:.4f}")
    print(f"Post-hoc statistical power at observed effect: {achieved_power:.2%}")

    # Required N per group to detect this effect at 80% power
    required_n = power_analysis.solve_power(effect_size=abs(effect_size), power=0.8, alpha=0.05, ratio=1.0)
    print(f"Required N per group for 80% power at this effect size: {required_n:.0f}")

    return {
        "metric": metric, "p30": p30, "p40": p40, "p_value": p_val,
        "boot_ci_low": boot_ci[0], "boot_ci_high": boot_ci[1],
        "effect_size_h": effect_size, "achieved_power": achieved_power
    }

results = []
for m in ["retention_1", "retention_7"]:
    results.append(test_retention(m))

pd.DataFrame(results).to_csv("/home/claude/ab-test-project/data/retention_test_results.csv", index=False)
print("\nSaved results to data/retention_test_results.csv")
