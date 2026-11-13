
from pathlib import Path

import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT / "data" / "processed"
    / "synthetic_cuped_scenario.csv"
)

OUTPUT = ROOT / "outputs" / "tables"
OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

# Validate input
required_columns = [
    "customer_id",
    "experiment_group",
    "pre_experiment_visits",
    "returned_within_60d"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(f"Missing columns: {missing}")

if df["customer_id"].duplicated().any():
    raise ValueError("Duplicate customer IDs detected.")

# Treatment indicator
df["treatment"] = (
    df["experiment_group"] == "Treatment"
).astype(int)

# Outcome and pre-treatment covariate
y = df["returned_within_60d"].astype(float)
x = df["pre_experiment_visits"].astype(float)

# CUPED coefficient
theta = x.cov(y) / x.var()

# CUPED-adjusted outcome
df["cuped_outcome"] = (
    y - theta * (x - x.mean())
)

# Unadjusted regression
X_unadjusted = sm.add_constant(df["treatment"])

model_unadjusted = sm.OLS(
    y, X_unadjusted
).fit(cov_type="HC2")

# CUPED-adjusted regression
X_adjusted = sm.add_constant(df["treatment"])

model_adjusted = sm.OLS(
    df["cuped_outcome"],
    X_adjusted
).fit(cov_type="HC2")

# Variance reduction
original_variance = y.var()
adjusted_variance = df["cuped_outcome"].var()

variance_reduction = (
    1 - adjusted_variance / original_variance
) * 100

# Comparison
results = pd.DataFrame([
    {
        "method": "Unadjusted",
        "treatment_effect": model_unadjusted.params["treatment"],
        "standard_error": model_unadjusted.bse["treatment"],
        "p_value": model_unadjusted.pvalues["treatment"]
    },
    {
        "method": "CUPED Adjusted",
        "treatment_effect": model_adjusted.params["treatment"],
        "standard_error": model_adjusted.bse["treatment"],
        "p_value": model_adjusted.pvalues["treatment"]
    }
])

results.to_csv(
    OUTPUT / "cuped_analysis_results.csv",
    index=False
)

print("\nCUPED ANALYSIS")
print("=" * 60)

print(f"Dataset: {INPUT.name}")
print(f"Customers: {len(df):,}")

print(
    "Covariate-outcome correlation:",
    round(x.corr(y), 4)
)

print(f"Theta: {theta:.6f}")
print(f"Original variance: {original_variance:.6f}")
print(f"Adjusted variance: {adjusted_variance:.6f}")
print(f"Variance reduction: {variance_reduction:.2f}%")

print("\nTREATMENT EFFECT COMPARISON")
print(results.to_string(index=False))

print(
    "\nSaved:",
    OUTPUT / "cuped_analysis_results.csv"
)
