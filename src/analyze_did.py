
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT / "data" / "processed"
    / "synthetic_outlet_monthly_did.csv"
)

TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT, parse_dates=["month"])

# Basic validation
assert df["outlet_id"].nunique() == 22
assert df.groupby("outlet_id")["group"].nunique().max() == 1

df["treatment"] = (
    df["group"] == "Treatment"
).astype(int)

df["did"] = df["treatment"] * df["post"]

# ------------------------------------------------
# 1. PRE- AND POST-INTERVENTION GROUP COMPARISON
# ------------------------------------------------

summary = (
    df.groupby(["group", "post"])["retention_rate"]
    .agg(["mean", "count", "std"])
    .reset_index()
)

print("\nPRE/POST RETENTION SUMMARY")
print("=" * 65)
print(summary.to_string(index=False))

means = df.groupby(
    ["group", "post"]
)["retention_rate"].mean()

control_pre = means.loc[("Control", 0)]
control_post = means.loc[("Control", 1)]

treatment_pre = means.loc[("Treatment", 0)]
treatment_post = means.loc[("Treatment", 1)]

did_estimate = (
    (treatment_post - treatment_pre)
    - (control_post - control_pre)
)

print("\nMANUAL DIFFERENCE-IN-DIFFERENCES")
print(f"Control change: {control_post - control_pre:.4f}")
print(f"Treatment change: {treatment_post - treatment_pre:.4f}")
print(f"DiD estimate: {did_estimate:.4f} percentage points")

# ------------------------------------------------
# 2. FIXED-EFFECTS REGRESSION
# ------------------------------------------------

model = smf.ols(
    "retention_rate ~ did + C(outlet_id) + C(month)",
    data=df
).fit(
    cov_type="cluster",
    cov_kwds={"groups": df["outlet_id"]}
)

effect = model.params["did"]
ci_low, ci_high = model.conf_int().loc["did"]

print("\nFIXED-EFFECTS DiD REGRESSION")
print("=" * 65)
print(f"DiD coefficient: {effect:.4f} percentage points")
print(f"95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
print(f"P-value: {model.pvalues['did']:.6f}")

# ------------------------------------------------
# 3. PARALLEL TRENDS VISUALIZATION
# ------------------------------------------------

trend = (
    df.groupby(["month", "group"])["retention_rate"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(12, 6))

for group in ["Control", "Treatment"]:
    subset = trend[trend["group"] == group]

    plt.plot(
        subset["month"],
        subset["retention_rate"],
        marker="o",
        markersize=3,
        label=group
    )

plt.axvline(
    pd.Timestamp("2025-07-01"),
    linestyle="--",
    label="Intervention"
)

plt.title("Difference-in-Differences: Monthly Retention Trends")
plt.xlabel("Month")
plt.ylabel("Retention Rate (%)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    FIGURES / "did_parallel_trends.png",
    dpi=300
)

plt.close()

# ------------------------------------------------
# 4. PRE-TREATMENT TREND CHECK
# ------------------------------------------------

pre = df[df["post"] == 0].copy()

pre["time_index"] = (
    (pre["month"] - pre["month"].min()).dt.days / 30.44
)

pre["treatment_time"] = (
    pre["treatment"] * pre["time_index"]
)

pretrend_model = smf.ols(
    "retention_rate ~ time_index + treatment_time + C(outlet_id)",
    data=pre
).fit(
    cov_type="cluster",
    cov_kwds={"groups": pre["outlet_id"]}
)

pretrend_effect = pretrend_model.params["treatment_time"]
pretrend_p = pretrend_model.pvalues["treatment_time"]

print("\nPRE-TREATMENT TREND CHECK")
print(f"Treatment trend difference: {pretrend_effect:.6f}")
print(f"P-value: {pretrend_p:.6f}")

# ------------------------------------------------
# 5. EXPORT RESULTS
# ------------------------------------------------

results = pd.DataFrame([
    {
        "metric": "Manual DiD estimate",
        "value": did_estimate
    },
    {
        "metric": "Fixed-effects DiD estimate",
        "value": effect
    },
    {
        "metric": "95% CI lower",
        "value": ci_low
    },
    {
        "metric": "95% CI upper",
        "value": ci_high
    },
    {
        "metric": "DiD p-value",
        "value": model.pvalues["did"]
    },
    {
        "metric": "Pre-trend interaction coefficient",
        "value": pretrend_effect
    },
    {
        "metric": "Pre-trend p-value",
        "value": pretrend_p
    }
])

results.to_csv(
    TABLES / "did_analysis_results.csv",
    index=False
)

summary.to_csv(
    TABLES / "did_group_summary.csv",
    index=False
)

print("\nFILES SAVED")
print(TABLES / "did_analysis_results.csv")
print(TABLES / "did_group_summary.csv")
print(FIGURES / "did_parallel_trends.png")
