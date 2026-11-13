
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT / "data" / "processed"
    / "synthetic_experiment_outcomes.csv"
)

OUTPUT = (
    ROOT / "data" / "processed"
    / "synthetic_cuped_scenario.csv"
)

df = pd.read_csv(INPUT)

rng = np.random.default_rng(20261113)

# Simulated pre-experiment customer activity
segment_activity = {
    "New": 1.0,
    "Regular": 3.0,
    "Loyal": 5.0
}

df["pre_experiment_visits"] = (
    df["customer_segment"].map(segment_activity)
    + rng.normal(0, 1.0, len(df))
).clip(lower=0)

# Standardize historical activity
x = df["pre_experiment_visits"]

x_standardized = (
    x - x.mean()
) / x.std()

# Create numeric treatment indicator
df["treatment"] = (
    df["experiment_group"] == "Treatment"
).astype(int)

# Introduce relationship between historical activity
# and future retention probability.
baseline_probability = (
    0.50 + 0.08 * x_standardized
).clip(0.10, 0.90)

treatment_effect = 0.03

df["retention_probability"] = (
    baseline_probability
    + treatment_effect * df["treatment"]
).clip(0.01, 0.99)

# Generate a new simulated binary outcome
df["returned_within_60d"] = rng.binomial(
    1,
    df["retention_probability"]
)

df.to_csv(OUTPUT, index=False)

print("\nREVISED CUPED SIMULATION")
print("=" * 55)

print(f"Total customers: {len(df):,}")
print(
    "Correlation between historical activity and retention:",
    round(
        df["pre_experiment_visits"].corr(
            df["returned_within_60d"]
        ),
        4
    )
)

print("\nRetention by group:")
print(
    df.groupby("experiment_group")[
        "returned_within_60d"
    ].mean()
)

print(f"\nSaved: {OUTPUT}")
