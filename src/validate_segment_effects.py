
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT / "data" / "processed"
    / "synthetic_experiment_outcomes.csv"
)

OUTPUT = ROOT / "outputs" / "tables"
OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

df["treatment"] = (
    df["experiment_group"] == "Treatment"
).astype(int)

df["returned_within_60d"] = (
    df["returned_within_60d"].astype(int)
)

# 1. Multiple-testing correction
segment_results = pd.read_csv(
    OUTPUT / "segment_treatment_effects.csv"
)

segment_results["holm_adjusted_p"] = multipletests(
    segment_results["p_value"],
    method="holm"
)[1]

segment_results["holm_significant"] = (
    segment_results["holm_adjusted_p"] < 0.05
)

segment_results.to_csv(
    OUTPUT / "segment_effects_holm_adjusted.csv",
    index=False
)

# 2. Treatment-by-segment interaction
model = smf.ols(
    "returned_within_60d ~ treatment * C(customer_segment)",
    data=df
).fit(cov_type="HC2")

interaction_terms = [
    term for term in model.params.index
    if ":" in term
]

print("\nSEGMENT MULTIPLE-TESTING VALIDATION")
print("=" * 60)

print(
    segment_results[
        [
            "segment",
            "p_value",
            "holm_adjusted_p",
            "holm_significant"
        ]
    ].to_string(index=False)
)

print("\nTREATMENT-BY-SEGMENT INTERACTION")
print("=" * 60)

for term in interaction_terms:
    print(
        f"{term}: coefficient={model.params[term]:.6f}, "
        f"p-value={model.pvalues[term]:.6f}"
    )

# Joint test of all interaction terms
if interaction_terms:
    hypothesis = ", ".join(
        f"{term} = 0" for term in interaction_terms
    )
    joint_test = model.f_test(hypothesis)

    print("\nJoint interaction test:")
    print(f"F-statistic: {float(joint_test.fvalue):.6f}")
    print(f"P-value: {float(joint_test.pvalue):.6f}")

print("\nSaved:")
print(OUTPUT / "segment_effects_holm_adjusted.csv")
