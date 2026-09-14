"""
Step 4: Retention curve forecast (the time-series component)

IMPORTANT SCOPE NOTE (for the write-up):
The dataset only gives two retention anchor points per user: Day-1 and Day-7
(no daily cohort panel / timestamps). So a full daily time-series model isn't
possible with this data. Instead we use a standard technique from mobile-game
analytics: fit a power-law retention decay curve R(t) = a * t^-b through the
two known anchor points per variant, then extrapolate to Day-14 and Day-30.
This is the same family of model studios use for retention/LTV forecasting
when they only have early-game data -- it's a legitimate, named technique,
but it IS an extrapolation, not a measurement, and that distinction should be
stated explicitly in the README/notebook.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/cookie_cats.csv")

def fit_power_law(r1, r7):
    a = r1
    b = -np.log(r7 / a) / np.log(7)
    return a, b

def project(a, b, t):
    return a * np.power(t, -b)

results = {}
for version in ["gate_30", "gate_40"]:
    sub = df[df.version == version]
    r1 = sub["retention_1"].mean()
    r7 = sub["retention_7"].mean()
    a, b = fit_power_law(r1, r7)
    r14 = project(a, b, 14)
    r30 = project(a, b, 30)
    results[version] = dict(r1=r1, r7=r7, a=a, b=b, r14=r14, r30=r30)
    print(f"{version}: R1={r1:.2%}  R7={r7:.2%}  ->  R14(proj)={r14:.2%}  R30(proj)={r30:.2%}  (decay exponent b={b:.3f})")

print(f"\nProjected Day-30 gap (gate_30 - gate_40): {(results['gate_30']['r30'] - results['gate_40']['r30']):.2%}")
print("Caveat: this is an extrapolation from 2 anchor points using an assumed power-law shape, "
      "not a measured outcome -- presented as a directional forecast only.")

# --- Chart ---
t_range = np.arange(1, 31)
fig, ax = plt.subplots(figsize=(8, 5))
colors = {"gate_30": "#2E5EAA", "gate_40": "#D96C3F"}
for version, r in results.items():
    curve = project(r["a"], r["b"], t_range)
    ax.plot(t_range, curve * 100, label=f"{version} (projected)", color=colors[version], linewidth=2)
    ax.scatter([1, 7], [r["r1"] * 100, r["r7"] * 100], color=colors[version], zorder=5, s=50,
               label=f"{version} (measured)")
ax.axvline(7, color="gray", linestyle=":", linewidth=1)
ax.text(7.3, ax.get_ylim()[1]*0.92, "measured range ends", fontsize=8, color="gray")
ax.set_xlabel("Days since install")
ax.set_ylabel("Retention (%)")
ax.set_title("Retention Curve: Measured (Day 1, 7) vs. Projected (power-law extrapolation)")
ax.legend(fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("dashboard/retention_curve_forecast.png", dpi=150)
print("\nSaved chart to dashboard/retention_curve_forecast.png")

pd.DataFrame(results).T.to_csv("data/retention_curve_results.csv")
