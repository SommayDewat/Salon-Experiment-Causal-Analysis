
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"
OUTPUT = ROOT / "data" / "processed"

OUTPUT.mkdir(parents=True, exist_ok=True)

# Load data
appointments = pd.read_csv(
    DATA / "appointments.csv",
    parse_dates=["appointment_date"]
)

customers = pd.read_csv(DATA / "customers.csv")

# Keep completed appointments with identifiable customers.
completed = appointments[
    (appointments["appointment_status"] == "Completed")
    & appointments["customer_id"].notna()
].copy()

completed = completed.sort_values(
    ["customer_id", "appointment_date", "appointment_id"]
)

# First completed visit for each customer.
completed["visit_number"] = (
    completed.groupby("customer_id").cumcount() + 1
)

index_visits = completed[
    (completed["visit_number"] == 1)
    & (
        completed["appointment_date"]
        <= pd.Timestamp("2026-05-01")
    )
].copy()

# Find the next completed visit for each customer.
completed["next_visit_date"] = (
    completed.groupby("customer_id")["appointment_date"]
    .shift(-1)
)


# Find the next completed appointment for each customer.
completed["next_visit_date"] = (
    completed.groupby("customer_id")["appointment_date"]
    .shift(-1)
)

# Keep one record per customer: their first completed visit.
index_visits = completed[
    (completed["visit_number"] == 1)
    & (completed["appointment_date"] <= pd.Timestamp("2026-05-01"))
].copy()

# The next visit date is already available on the first visit row.
cohort = index_visits[
    [
        "customer_id",
        "appointment_id",
        "outlet_id",
        "appointment_date",
        "next_visit_date",
        "experiment_group",
        "experiment_treatment",
        "historical_treatment"
    ]
].copy()

# Calculate days until next completed visit.
cohort["days_to_next_visit"] = (
    cohort["next_visit_date"] - cohort["appointment_date"]
).dt.days

# Every index appointment has a complete 60-day observation window.
cohort["returned_within_60d"] = (
    cohort["days_to_next_visit"].between(0, 60)
).astype(int)

# Calculate days until the next completed appointment.
cohort["days_to_next_visit"] = (
    cohort["next_visit_date"] - cohort["appointment_date"]
).dt.days

# Every index appointment has a complete 60-day observation window.
cohort["returned_within_60d"] = (
    cohort["days_to_next_visit"].between(0, 60)
).astype(int)

# Add customer segment.
cohort = cohort.merge(
    customers[["customer_id", "customer_segment"]],
    on="customer_id",
    how="left",
    validate="one_to_one"
)

# Keep only randomized participants.
cohort = cohort[
    cohort["experiment_group"].isin(["Control", "Treatment"])
].copy()

# Validate uniqueness and assignment.
assert cohort["customer_id"].is_unique
assert cohort["returned_within_60d"].notna().all()
assert cohort["experiment_treatment"].isin([0, 1]).all()

cohort.to_csv(
    OUTPUT / "ab_test_customer_cohort.csv",
    index=False
)

print("\nCUSTOMER-LEVEL EXPERIMENT COHORT")
print("=" * 45)

print("Eligible customers:", len(cohort))
print("\nGroup counts:")
print(cohort["experiment_group"].value_counts())

print("\nRetention by group:")
print(
    cohort.groupby("experiment_group")["returned_within_60d"]
    .agg(["count", "mean", "sum"])
)

print("\nCustomer segment distribution:")
print(
    cohort.groupby(
        ["experiment_group", "customer_segment"]
    ).size().unstack(fill_value=0)
)

print("\nUnique customer check:", cohort["customer_id"].is_unique)
print("\nSaved:", OUTPUT / "ab_test_customer_cohort.csv")
