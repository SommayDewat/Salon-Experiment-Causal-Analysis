
from pathlib import Path
import numpy as np
import pandas as pd

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

SEED = 20261112
BASELINE_RETENTION = 0.50
TREATMENT_EFFECT = 0.03

rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
OUTPUT = ROOT / "data" / "processed"

OUTPUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Load randomized customer roster
# --------------------------------------------------

customers = pd.read_csv(DATA / "customers.csv")

customers = customers[
    customers["experiment_group"].isin(["Control", "Treatment"])
].copy()

assert customers["customer_id"].is_unique

# --------------------------------------------------
# 3. Generate experiment index dates
# --------------------------------------------------

# Every customer must have a complete 60-day follow-up.
# Therefore, index dates must be on or before 2026-05-01.
start_date = pd.Timestamp("2025-01-01")
last_index_date = pd.Timestamp("2026-05-01")

date_range_days = (last_index_date - start_date).days

customers["index_date"] = (
    start_date
    + pd.to_timedelta(
        rng.integers(0, date_range_days + 1, len(customers)),
        unit="D"
    )
)

# --------------------------------------------------
# 4. Define reminder treatment
# --------------------------------------------------

customers["reminder_sent"] = (
    customers["experiment_group"] == "Treatment"
).astype(int)

# Control receives standard communication.
customers["communication_type"] = np.where(
    customers["reminder_sent"] == 1,
    "Personalized reminder",
    "Standard communication"
)

# --------------------------------------------------
# 5. Generate customer-level retention outcomes
# --------------------------------------------------

customers["baseline_probability"] = BASELINE_RETENTION

customers["retention_probability"] = (
    BASELINE_RETENTION
    + TREATMENT_EFFECT * customers["reminder_sent"]
)

# Generate one independent customer-level outcome.
customers["returned_within_60d"] = (
    rng.random(len(customers))
    < customers["retention_probability"]
).astype(int)

# --------------------------------------------------
# 6. Generate a synthetic follow-up date
# --------------------------------------------------

# These dates represent simulated outcomes, not observed
# appointments from the 300,000-row appointment dataset.
days_to_return = rng.integers(1, 61, len(customers))

customers["next_visit_date"] = pd.NaT

retained = customers["returned_within_60d"] == 1

customers.loc[retained, "next_visit_date"] = (
    customers.loc[retained, "index_date"]
    + pd.to_timedelta(days_to_return[retained], unit="D")
)

customers["days_to_next_visit"] = (
    customers["next_visit_date"] - customers["index_date"]
).dt.days

# --------------------------------------------------
# 7. Validation
# --------------------------------------------------

assert customers["customer_id"].is_unique
assert customers["returned_within_60d"].isin([0, 1]).all()

assert (
    customers.loc[retained, "days_to_next_visit"]
    .between(1, 60)
    .all()
)

assert (
    customers.loc[~retained, "next_visit_date"].isna().all()
)

# --------------------------------------------------
# 8. Save customer-level experiment outcomes
# --------------------------------------------------

experiment_outcomes = customers[
    [
        "customer_id",
        "home_outlet",
        "customer_segment",
        "experiment_group",
        "reminder_sent",
        "communication_type",
        "index_date",
        "next_visit_date",
        "days_to_next_visit",
        "baseline_probability",
        "retention_probability",
        "returned_within_60d"
    ]
].copy()

experiment_outcomes.to_csv(
    OUTPUT / "synthetic_experiment_outcomes.csv",
    index=False
)

# --------------------------------------------------
# 9. Summary
# --------------------------------------------------

print("\nSYNTHETIC EXPERIMENT OUTCOMES")
print("=" * 50)

print("Total randomized customers:", len(experiment_outcomes))

print("\nGroup counts:")
print(experiment_outcomes["experiment_group"].value_counts())

print("\nRetention summary:")
print(
    experiment_outcomes.groupby("experiment_group")[
        "returned_within_60d"
    ].agg(["count", "mean", "sum"])
)

print("\nConfigured treatment effect:", f"{TREATMENT_EFFECT:.1%}")

print(
    "\nObserved simulated difference:",
    f"{experiment_outcomes.groupby('experiment_group')['returned_within_60d'].mean()['Treatment'] - experiment_outcomes.groupby('experiment_group')['returned_within_60d'].mean()['Control']:.4f}"
)

print("\nSaved:", OUTPUT / "synthetic_experiment_outcomes.csv")
