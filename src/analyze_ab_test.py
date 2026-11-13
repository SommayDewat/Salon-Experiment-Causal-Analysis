
from pathlib import Path

import pandas as pd
from scipy.stats import norm
from statsmodels.stats.proportion import (
    proportions_ztest,
    confint_proportions_2indep
)

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "synthetic_experiment_outcomes.csv"
OUTPUT = ROOT / "outputs" / "tables"

OUTPUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 1. Load and validate experiment data
# --------------------------------------------------

df = pd.read_csv(INPUT)

assert df["customer_id"].is_unique
assert df["returned_within_60d"].notna().all()

summary = (
    df.groupby("experiment_group")["returned_within_60d"]
    .agg(["count", "sum", "mean"])
)

control_n = int(summary.loc["Control", "count"])
treatment_n = int(summary.loc["Treatment", "count"])

control_retained = int(summary.loc["Control", "sum"])
treatment_retained = int(summary.loc["Treatment", "sum"])

control_rate = control_retained / control_n
treatment_rate = treatment_retained / treatment_n

# --------------------------------------------------
# 2. Absolute treatment effect
# --------------------------------------------------

absolute_effect = treatment_rate - control_rate

# --------------------------------------------------
# 3. Relative retention lift
# --------------------------------------------------

relative_lift = absolute_effect / control_rate

# --------------------------------------------------
# 4. 95% confidence interval for risk difference
# --------------------------------------------------

ci_low, ci_high = confint_proportions_2indep(
    treatment_retained,
    treatment_n,
    control_retained,
    control_n,
    method="newcomb",
    compare="diff",
    alpha=0.05
)

# --------------------------------------------------
# 5. Two-proportion z-test
# --------------------------------------------------

z_stat, p_value = proportions_ztest(
    count=[treatment_retained, control_retained],
    nobs=[treatment_n, control_n],
    alternative="two-sided"
)

# --------------------------------------------------
# 6. Statistical decision
# --------------------------------------------------

statistically_significant = p_value < 0.05

if statistically_significant and ci_low > 0:
    decision = "GO - Positive retention effect detected"
elif statistically_significant and ci_high < 0:
    decision = "NO-GO - Negative retention effect detected"
else:
    decision = "EXTEND - Evidence is inconclusive"

# --------------------------------------------------
# 7. Print results
# --------------------------------------------------

print("\nA/B TEST STATISTICAL EVALUATION")
print("=" * 55)

print(f"Control customers: {control_n:,}")
print(f"Treatment customers: {treatment_n:,}")

print(f"\nControl retention: {control_rate:.4%}")
print(f"Treatment retention: {treatment_rate:.4%}")

print(f"\nAbsolute effect: {absolute_effect:.4%}")
print(f"Relative retention lift: {relative_lift:.4%}")

print(
    "\n95% Confidence Interval:",
    f"[{ci_low:.4%}, {ci_high:.4%}]"
)

print(f"\nZ statistic: {z_stat:.4f}")
print(f"P-value: {p_value:.8f}")

print("\nStatistical significance:", statistically_significant)
print("Preliminary statistical decision:", decision)

# --------------------------------------------------
# 8. Save results
# --------------------------------------------------

results = pd.DataFrame([{
    "control_customers": control_n,
    "treatment_customers": treatment_n,
    "control_retention": control_rate,
    "treatment_retention": treatment_rate,
    "absolute_effect": absolute_effect,
    "relative_lift": relative_lift,
    "ci_95_lower": ci_low,
    "ci_95_upper": ci_high,
    "z_statistic": z_stat,
    "p_value": p_value,
    "statistically_significant": statistically_significant,
    "preliminary_decision": decision
}])

results.to_csv(
    OUTPUT / "ab_test_statistical_results.csv",
    index=False
)

print(
    "\nResults saved:",
    OUTPUT / "ab_test_statistical_results.csv"
)
