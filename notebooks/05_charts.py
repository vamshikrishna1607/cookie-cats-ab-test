"""
Step 5: Remaining summary charts for the dashboard/README
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportion_confint

df = pd.read_csv("/home/claude/ab-test-project/data/cookie_cats.csv")
colors = {"gate_30": "#2E5EAA", "gate_40": "#D96C3F"}

# --- Chart 1: Retention rates with 95% Wilson CIs ---
fig, axes = plt.subplots(1, 2, figsize=(9, 4.5), sharey=False)
for ax, metric, title in zip(axes, ["retention_1", "retention_7"], ["Day-1 Retention", "Day-7 Retention"]):
    rates, lowers, uppers = [], [], []
    for v in ["gate_30", "gate_40"]:
        sub = df[df.version == v][metric]
        n, x = len(sub), sub.sum()
        p = x / n
        lo, hi = proportion_confint(x, n, method="wilson")
        rates.append(p * 100)
        lowers.append((p - lo) * 100)
        uppers.append((hi - p) * 100)
    bars = ax.bar(["gate_30", "gate_40"], rates, color=[colors["gate_30"], colors["gate_40"]],
                   yerr=[lowers, uppers], capsize=6, width=0.5)
    ax.set_title(title)
    ax.set_ylabel("Retention (%)")
    ax.spines[["top", "right"]].set_visible(False)
    for bar, r in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, r + 1.5, f"{r:.1f}%", ha="center", fontsize=9)
plt.suptitle("Retention by Variant (error bars = 95% Wilson CI)")
plt.tight_layout()
plt.savefig("/home/claude/ab-test-project/dashboard/retention_rates.png", dpi=150)
plt.close()

# --- Chart 2: Rounds played distribution (outlier excluded, log scale) ---
outlier_id = df.loc[df.sum_gamerounds.idxmax(), "userid"]
df_clean = df[df.userid != outlier_id]
fig, ax = plt.subplots(figsize=(8, 4.5))
for v in ["gate_30", "gate_40"]:
    sub = df_clean[df_clean.version == v]["sum_gamerounds"]
    sub = sub[sub > 0]  # log scale needs >0
    ax.hist(np.log10(sub), bins=40, alpha=0.55, label=v, color=colors[v])
ax.set_xlabel("log10(rounds played)")
ax.set_ylabel("Number of users")
ax.set_title("Engagement Distribution by Variant (outlier excluded, log scale)")
ax.legend()
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("/home/claude/ab-test-project/dashboard/rounds_distribution.png", dpi=150)
plt.close()

# --- Chart 3: SRM check ---
counts = df["version"].value_counts()
fig, ax = plt.subplots(figsize=(5, 4.5))
bars = ax.bar(["gate_30", "gate_40"], [counts["gate_30"], counts["gate_40"]],
              color=[colors["gate_30"], colors["gate_40"]], width=0.5)
ax.axhline(counts.sum()/2, color="gray", linestyle="--", linewidth=1, label="Expected (50/50)")
for bar, c in zip(bars, [counts["gate_30"], counts["gate_40"]]):
    ax.text(bar.get_x() + bar.get_width()/2, c + 300, f"{c:,}", ha="center", fontsize=9)
ax.set_title("Sample Size Check (SRM)")
ax.set_ylabel("Users")
ax.legend(fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("/home/claude/ab-test-project/dashboard/srm_check.png", dpi=150)
plt.close()

print("Saved 3 charts to dashboard/: retention_rates.png, rounds_distribution.png, srm_check.png")
