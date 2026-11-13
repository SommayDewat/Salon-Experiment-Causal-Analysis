
from pathlib import Path

import pandas as pd
from statsmodels.stats.proportion import (
    proportions_ztest,
    confint_proportions_2indep
)

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "synthetic_experiment_outcomes.csv"
OUTPUT = ROOT / "outputs" / "tables"

OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)

results = []

for segment in sorted(df["customer_segment"].unique()):

    subset = df[df["customer_segment"] == segment]

    control = subset[subset["experiment_group"] == "Control"]
    treatment = subset[subset["experiment_group"] == "Treatment"]

    control_n = len(control)
    treatment_n = len(treatment)

    control_success = int(control["returned_within_60d"].sum())
    treatment_success = int(treatment["returned_within_60d"].sum())

    control_rate = control_success / control_n
    treatment_rate = treatment_success / treatment_n

    effect = treatment_rate - control_rate

    ci_low, ci_high = confint_proportions_2indep(
        treatment_success,
        treatment_n,
        control_success,
        control_n,
        method="newcomb",
        compare="diff",
        alpha=0.05
    )

    z_stat, p_value = proportions_ztest(
        [treatment_success, control_success],
        [treatment_n, control_n]
    )

    results.append({
        "segment": segment,
        "control_customers": control_n,
        "treatment_customers": treatment_n,
        "control_retention": control_rate,
        "treatment_retention": treatment_rate,
        "absolute_effect": effect,
        "ci_95_lower": ci_low,
        "ci_95_upper": ci_high,
        "z_statistic": z_stat,
        "p_value": p_value
    })

results_df = pd.DataFrame(results)

results_df["nominal_significant"] = (
    results_df["p_value"] < 0.05
)

results_df.to_csv(
    OUTPUT / "segment_treatment_effects.csv",
    index=False
)

print("\nSEGMENT-LEVEL TREATMENT EFFECTS")
print("=" * 65)

for _, row in results_df.iterrows():
    print(f"\nSegment: {row['segment']}")
    print(f"Control retention: {row['control_retention']:.2%}")
    print(f"Treatment retention: {row['treatment_retention']:.2%}")
    print(f"Absolute effect: {row['absolute_effect']:.2%}")
    print(
        "95% CI:",
        f"[{row['ci_95_lower']:.2%}, {row['ci_95_upper']:.2%}]"
    )
    print(f"P-value: {row['p_value']:.6f}")
    print(
        "Nominally significant:",
        row["nominal_significant"]
    )

print("\nSaved:", OUTPUT / "segment_treatment_effects.csv")
