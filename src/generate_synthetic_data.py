
from pathlib import Path
import numpy as np
import pandas as pd

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

SEED = 42
N_APPOINTMENTS = 300_000
N_CUSTOMERS = 40_000
N_OUTLETS = 22
N_STYLISTS = 110

rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "synthetic"
OUTPUT.mkdir(parents=True, exist_ok=True)

START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2026-06-30")

# --------------------------------------------------
# 2. Create outlet master data
# --------------------------------------------------

outlets = pd.DataFrame({
    "outlet_id": [f"O{i:02d}" for i in range(1, N_OUTLETS + 1)],
    "outlet_name": [f"Coimbatore Salon {i:02d}" for i in range(1, N_OUTLETS + 1)],
    "region": ["Treatment Region"] * 11 + ["Control Region"] * 11,
    "historical_treatment": [1] * 11 + [0] * 11
})

outlets.to_csv(OUTPUT / "outlets.csv", index=False)

# --------------------------------------------------
# 3. Create stylist master data
# --------------------------------------------------

stylists = pd.DataFrame({
    "stylist_id": [f"S{i:03d}" for i in range(1, N_STYLISTS + 1)],
    "outlet_id": [
        f"O{(i % N_OUTLETS) + 1:02d}"
        for i in range(N_STYLISTS)
    ],
    "experience_years": rng.integers(1, 16, N_STYLISTS),
    "skill_level": rng.choice(
        ["Junior", "Mid-level", "Senior"],
        N_STYLISTS,
        p=[0.25, 0.50, 0.25]
    )
})

stylists.to_csv(OUTPUT / "stylists.csv", index=False)

# --------------------------------------------------
# 4. Create service master data
# --------------------------------------------------

services = pd.DataFrame({
    "service_id": ["SV01", "SV02", "SV03", "SV04", "SV05", "SV06"],
    "standard_service_name": [
        "Haircut", "Hair Coloring", "Facial",
        "Manicure", "Pedicure", "Spa Therapy"
    ],
    "base_price": [500, 1800, 1200, 600, 700, 2000],
    "category": [
        "Hair", "Hair", "Skin",
        "Nails", "Nails", "Wellness"
    ]
})

services.to_csv(OUTPUT / "services.csv", index=False)

# Different outlets use different service names.
service_aliases = {
    "SV01": ["Haircut", "Hair Cut", "Cutting"],
    "SV02": ["Hair Coloring", "Hair Colour", "Color Service"],
    "SV03": ["Facial", "Face Clean Up", "Skin Facial"],
    "SV04": ["Manicure", "Nail Care", "Hand Care"],
    "SV05": ["Pedicure", "Foot Care", "Feet Treatment"],
    "SV06": ["Spa Therapy", "Body Spa", "Relaxation Therapy"]
}

# --------------------------------------------------
# 5. Create customer-level experiment assignments
# --------------------------------------------------

customers = pd.DataFrame({
    "customer_id": [f"C{i:05d}" for i in range(1, N_CUSTOMERS + 1)],
    "home_outlet": rng.choice(
        outlets["outlet_id"].to_numpy(),
        N_CUSTOMERS
    ),
    "customer_segment": rng.choice(
        ["New", "Regular", "Loyal"],
        N_CUSTOMERS,
        p=[0.35, 0.45, 0.20]
    )
})

# Randomized 50/50 assignment within each home outlet.
customers["experiment_group"] = (
    customers.groupby("home_outlet")["customer_id"]
    .transform(lambda x: rng.permutation(
        np.where(np.arange(len(x)) % 2 == 0, "Control", "Treatment")
    ))
)

customers["experiment_treatment"] = (
    customers["experiment_group"] == "Treatment"
).astype(int)

customer_lookup = customers.set_index("customer_id")

# --------------------------------------------------
# 6. Generate appointment records
# --------------------------------------------------

customer_ids = rng.choice(
    customers["customer_id"].to_numpy(),
    N_APPOINTMENTS
)

customer_data = customer_lookup.loc[customer_ids].reset_index()

# Simulate 8% walk-in appointments without customer IDs.
is_walk_in = rng.random(N_APPOINTMENTS) < 0.08

customer_ids = customer_ids.astype(object)
customer_ids[is_walk_in] = None

customer_data.loc[is_walk_in, "customer_id"] = None
customer_data.loc[is_walk_in, "experiment_group"] = "Not randomized"
customer_data.loc[is_walk_in, "experiment_treatment"] = 0

appointment_dates = (
    START_DATE
    + pd.to_timedelta(
        rng.integers(
            0,
            (END_DATE - START_DATE).days + 1,
            N_APPOINTMENTS
        ),
        unit="D"
    )
)

outlet_ids = customer_data["home_outlet"].to_numpy().copy()

# Some customers visit a different outlet.
switch_outlet = rng.random(N_APPOINTMENTS) < 0.15
outlet_ids[switch_outlet] = rng.choice(
    outlets["outlet_id"].to_numpy(),
    switch_outlet.sum()
)

service_ids = rng.choice(
    services["service_id"].to_numpy(),
    N_APPOINTMENTS,
    p=[0.30, 0.15, 0.20, 0.12, 0.10, 0.13]
)

service_price = services.set_index("service_id")["base_price"]
base_prices = pd.Series(service_ids).map(service_price).to_numpy()

# Customer-level experiment treatment effect:
# synthetic improvement in return probability.
is_treated = (
    customer_data["experiment_treatment"].to_numpy() == 1
)

return_probability = (
    0.30
    + 0.10 * (customer_data["customer_segment"].to_numpy() == "Regular")
    + 0.20 * (customer_data["customer_segment"].to_numpy() == "Loyal")
    + 0.05 * is_treated
)

return_probability = np.clip(return_probability, 0, 1)

returned_60d = (
    rng.random(N_APPOINTMENTS) < return_probability
).astype(int)

# Retention cannot be attributed to unidentified walk-in customers.
returned_60d = returned_60d.astype(float)
returned_60d[is_walk_in] = np.nan

# Treatment modestly reduces no-show probability.
no_show_probability = np.where(is_treated, 0.075, 0.10)

no_show = rng.random(N_APPOINTMENTS) < no_show_probability

# Some no-shows are recorded as cancellations.
cancellation = no_show & (rng.random(N_APPOINTMENTS) < 0.65)

status = np.where(
    no_show,
    np.where(cancellation, "Cancelled", "No-show"),
    "Completed"
)

# Revenue for completed appointments only.
treatment_revenue_uplift = np.where(is_treated, 1.03, 1.00)

revenue = np.where(
    status == "Completed",
    base_prices * rng.normal(1.0, 0.12, N_APPOINTMENTS)
    * treatment_revenue_uplift,
    0
)

revenue = np.maximum(revenue, 0).round(2)

# Stylist must belong to the appointment outlet.
stylist_map = stylists.groupby("outlet_id")["stylist_id"].apply(list).to_dict()

stylist_ids = [
    rng.choice(stylist_map[outlet])
    for outlet in outlet_ids
]

# Outlet-specific raw service names.
raw_service_names = [
    rng.choice(service_aliases[service_id])
    for service_id in service_ids
]

appointments = pd.DataFrame({
    "appointment_id": [
        f"A{i:06d}" for i in range(1, N_APPOINTMENTS + 1)
    ],
    "is_walk_in": is_walk_in.astype(int),
    "customer_id": customer_ids,
    "outlet_id": outlet_ids,
    "stylist_id": stylist_ids,
    "appointment_date": appointment_dates,
    "service_id": service_ids,
    "raw_service_name": raw_service_names,
    "appointment_status": status,
    "is_no_show": no_show.astype(int),
    "is_cancellation": cancellation.astype(int),
    "revenue": revenue,
    "experiment_group": customer_data["experiment_group"].to_numpy(),
    "experiment_treatment": customer_data["experiment_treatment"].to_numpy(),
    "returned_within_60d": returned_60d,
    "historical_treatment": pd.Series(outlet_ids).map(
        outlets.set_index("outlet_id")["historical_treatment"]
    ).to_numpy()
})


# --------------------------------------------------
# Calculate actual 60-day customer retention
# --------------------------------------------------

# Start with unknown retention.
appointments["returned_within_60d"] = np.nan

# Only completed appointments with identifiable customers
# can be used for customer-level retention.
completed_visits = appointments[
    (appointments["appointment_status"] == "Completed")
    & (appointments["customer_id"].notna())
].copy()

completed_visits = completed_visits.sort_values(
    ["customer_id", "appointment_date"]
)

# Find each customer's next completed appointment.
completed_visits["next_appointment_date"] = (
    completed_visits.groupby("customer_id")["appointment_date"]
    .shift(-1)
)

# A full 60-day observation window must be available.
cutoff_date = END_DATE - pd.Timedelta(days=60)

observable_visits = completed_visits[
    completed_visits["appointment_date"] <= cutoff_date
]

# Retained = next completed appointment within 60 days.
days_to_next_visit = (
    observable_visits["next_appointment_date"]
    - observable_visits["appointment_date"]
).dt.days

appointments.loc[
    observable_visits.index,
    "returned_within_60d"
] = (
    days_to_next_visit.between(0, 60)
).astype(int)

print(
    "\nRetention measurement:",
    appointments["returned_within_60d"].notna().sum(),
    "observable customer appointments"
)


# Historical intervention starts on 2025-10-01.
appointments["historical_post"] = (
    appointments["appointment_date"] >= pd.Timestamp("2025-10-01")
).astype(int)

# Synthetic historical intervention effect.
# Applied to treatment-region outlets after the intervention date.
historical_effect = (
    (appointments["historical_treatment"] == 1)
    & (appointments["historical_post"] == 1)
)

appointments.loc[historical_effect, "revenue"] *= 1.06
appointments["revenue"] = appointments["revenue"].round(2)

# --------------------------------------------------
# 7. Create product sales records
# --------------------------------------------------

completed = appointments[
    appointments["appointment_status"] == "Completed"
]

product_rows = completed.sample(
    frac=0.35,
    random_state=SEED
).copy()

product_catalog = pd.DataFrame({
    "product_id": ["P01", "P02", "P03", "P04", "P05"],
    "product_name": [
        "Shampoo", "Conditioner", "Hair Serum",
        "Face Cream", "Spa Oil"
    ],
    "unit_price": [450, 500, 650, 700, 900]
})

product_index = rng.integers(
    0, len(product_catalog),
    len(product_rows)
)

product_sales = pd.DataFrame({
    "sale_id": [
        f"PS{i:06d}" for i in range(1, len(product_rows) + 1)
    ],
    "appointment_id": product_rows["appointment_id"].to_numpy(),
    "customer_id": product_rows["customer_id"].to_numpy(),
    "outlet_id": product_rows["outlet_id"].to_numpy(),
    "product_id": product_catalog.iloc[product_index]["product_id"].to_numpy(),
    "quantity": rng.integers(1, 4, len(product_rows)),
    "unit_price": product_catalog.iloc[product_index]["unit_price"].to_numpy()
})

product_sales["sales_amount"] = (
    product_sales["quantity"] * product_sales["unit_price"]
)

# --------------------------------------------------
# 8. Save datasets
# --------------------------------------------------

appointments.to_csv(
    OUTPUT / "appointments.csv", index=False
)

product_sales.to_csv(
    OUTPUT / "product_sales.csv", index=False
)

product_catalog.to_csv(
    OUTPUT / "product_catalog.csv", index=False
)

customers.to_csv(
    OUTPUT / "customers.csv", index=False
)

# --------------------------------------------------
# 9. Print generation summary
# --------------------------------------------------

print("\nSYNTHETIC SALON DATA GENERATION COMPLETE")
print("=" * 50)

print(f"Appointments: {len(appointments):,}")
print(f"Customers: {customers['customer_id'].nunique():,}")
print(f"Outlets: {outlets['outlet_id'].nunique():,}")
print(f"Stylists: {stylists['stylist_id'].nunique():,}")
print(f"Product sales: {len(product_sales):,}")

print("\nAppointment status:")
print(appointments["appointment_status"].value_counts())

print("\nExperiment assignment:")
print(appointments.groupby("experiment_group")["customer_id"].nunique())

print("\nHistorical treatment outlets:")
print(outlets["historical_treatment"].value_counts())

print("\nFiles saved to:", OUTPUT)
        