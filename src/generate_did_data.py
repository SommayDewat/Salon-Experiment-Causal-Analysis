
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

OUTPUT = (
    ROOT / "data" / "processed"
    / "synthetic_outlet_monthly_did.csv"
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(20261114)

outlets = pd.read_csv(
    ROOT / "data" / "synthetic" / "outlets.csv"
)

# Select 11 treatment and 11 control outlets
outlets = outlets.sort_values("outlet_id").copy()

outlets["group"] = [
    "Treatment" if i < 11 else "Control"
    for i in range(len(outlets))
]

# Monthly observation period
months = pd.date_range(
    start="2024-01-01",
    end="2026-06-01",
    freq="MS"
)

intervention_date = pd.Timestamp("2025-07-01")

rows = []

for _, outlet in outlets.iterrows():

    outlet_id = outlet["outlet_id"]
    group = outlet["group"]

    # Outlet-specific baseline performance
    outlet_effect = rng.normal(0, 8, 1)[0]

    for month_index, month in enumerate(months):

        post = int(month >= intervention_date)

        # Common monthly trend for both groups
        common_trend = month_index * 0.35

        # Shared seasonality
        seasonality = (
            5 * np.sin(2 * np.pi * month.month / 12)
        )

        # Random monthly variation
        noise = rng.normal(0, 5)

        # Treatment effect starts after intervention
        treatment_effect = (
            6 if group == "Treatment" and post == 1
            else 0
        )

        retention_rate = (
            50
            + outlet_effect
            + common_trend
            + seasonality
            + treatment_effect
            + noise
        )

        retention_rate = np.clip(
            retention_rate, 5, 95
        )

        rows.append({
            "outlet_id": outlet_id,
            "group": group,
            "month": month,
            "post": post,
            "retention_rate": retention_rate
        })

df = pd.DataFrame(rows)

df.to_csv(OUTPUT, index=False)

print("\nSYNTHETIC DiD DATASET")
print("=" * 55)

print(f"Total records: {len(df):,}")
print(f"Unique outlets: {df['outlet_id'].nunique()}")
print(f"Treatment outlets: {df[df['group'] == 'Treatment']['outlet_id'].nunique()}")
print(f"Control outlets: {df[df['group'] == 'Control']['outlet_id'].nunique()}")
print(f"Monthly period: {df['month'].min().date()} to {df['month'].max().date()}")
print(f"Intervention date: {intervention_date.date()}")

print("\nGroup distribution:")
print(df.groupby("group")["outlet_id"].nunique())

print("\nSaved:", OUTPUT)
