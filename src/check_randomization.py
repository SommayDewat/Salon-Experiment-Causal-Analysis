
from pathlib import Path

import pandas as pd
import numpy as np
from scipy.stats import chisquare, chi2_contingency, binomtest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
OUTPUT = ROOT / "outputs" / "tables"
OUTPUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 1. Load the original randomized customer roster
# --------------------------------------------------

customers = pd.read_csv(DATA / "customers.csv")

assert customers["customer_id"].is_unique

experiment = customers[
    customers["experiment_group"].isin(["Control", "Treatment"])
].copy()

n = len(experiment)

group_counts = (
    experiment["experiment_group"]
    .value_counts()
    .reindex(["Control", "Treatment"], fill_value=0)
)

# --------------------------------------------------
# 2. Sample Ratio Mismatch (SRM)
# --------------------------------------------------

observed = group_counts.to_numpy()
expected = np.array([n / 2, n / 2])

srm_stat, srm_p = chisquare(
    f_obs=observed,
    f_exp=expected
)

# Exact binomial test as a second check.
binomial_result = binomtest(
    int(group_counts["Treatment"]),
    n=n,
    p=0.5,
    alternative="two-sided"
)

print("\nSAMPLE RATIO MISMATCH CHECK")
print("=" * 50)
print("Total randomized customers:", n)
print("Control:", group_counts["Control"])
print("Treatment:", group_counts["Treatment"])
print("Observed allocation:")
print(group_counts / n)

print(f"\nChi-square statistic: {srm_stat:.4f}")
print(f"Chi-square p-value: {srm_p:.6f}")
print(f"Exact binomial p-value: {binomial_result.pvalue:.6f}")

if srm_p < 0.001:
    print("SRM WARNING: Significant allocation mismatch detected.")
else:
    print("No strong evidence of sample ratio mismatch.")

# --------------------------------------------------
# 3. Baseline categorical balance
# --------------------------------------------------

def categorical_balance(data, column):
    table = pd.crosstab(
        data[column],
        data["experiment_group"]
    ).reindex(columns=["Control", "Treatment"], fill_value=0)

    chi2, p_value, dof, expected = chi2_contingency(table)

    proportions = table.div(table.sum(axis=0), axis=1)

    # Maximum absolute category-level difference.
    max_difference = (
        proportions["Treatment"] - proportions["Control"]
    ).abs().max()

    return table, p_value, max_difference


balance_results = []

for variable in ["customer_segment", "home_outlet"]:
    table, p_value, max_difference = categorical_balance(
        experiment, variable
    )

    balance_results.append({
        "variable": variable,
        "chi_square_p_value": p_value,
        "max_absolute_proportion_difference": max_difference
    })

    print(f"\nBALANCE CHECK: {variable.upper()}")
    print(table)
    print(f"Chi-square p-value: {p_value:.6f}")
    print(
        "Maximum absolute proportion difference:",
        f"{max_difference:.4f}"
    )

# --------------------------------------------------
# 4. Save results
# --------------------------------------------------

results = pd.DataFrame(balance_results)

results.loc[len(results)] = {
    "variable": "sample_ratio_mismatch",
    "chi_square_p_value": srm_p,
    "max_absolute_proportion_difference": abs(
        group_counts["Treatment"] / n - 0.5
    )
}

results.to_csv(
    OUTPUT / "randomization_balance_results.csv",
    index=False
)

print("\nSaved:", OUTPUT / "randomization_balance_results.csv")
