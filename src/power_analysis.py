
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
import math

# Experiment planning assumptions
baseline_rate = 0.50
expected_treatment_rate = 0.53

alpha = 0.05
power = 0.80
allocation_ratio = 1.0

# Calculate standardized effect size
effect_size = proportion_effectsize(
    baseline_rate,
    expected_treatment_rate
)

# Calculate required sample size
analysis = NormalIndPower()

required_per_group = analysis.solve_power(
    effect_size=effect_size,
    power=power,
    alpha=alpha,
    ratio=allocation_ratio,
    alternative="two-sided"
)

required_per_group = math.ceil(required_per_group)
total_required = required_per_group * 2

# Allow for 10% unusable or ineligible participants
adjusted_total = math.ceil(total_required / 0.90)

print("\nA/B TEST POWER ANALYSIS")
print("=" * 45)

print(f"Baseline retention: {baseline_rate:.1%}")
print(f"Expected treatment retention: {expected_treatment_rate:.1%}")
print(f"Minimum detectable effect: {expected_treatment_rate-baseline_rate:.1%}")
print(f"Significance level: {alpha:.0%}")
print(f"Statistical power: {power:.0%}")

print(f"\nRequired customers per group: {required_per_group:,}")
print(f"Total required customers: {total_required:,}")
print(f"Total with 10% allowance: {adjusted_total:,}")

# Approximate enrollment duration using observed cohort size
daily_enrollment = 39872 / 547

estimated_days = math.ceil(adjusted_total / daily_enrollment)

print(f"\nEstimated daily enrollment: {daily_enrollment:.1f}")
print(f"Estimated enrollment days: {estimated_days}")
print("\nNote: This is a planning estimate, not a measured live-business duration.")
