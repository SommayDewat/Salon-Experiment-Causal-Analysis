# EXPERIMENT DESIGN DOCUMENT
## Salon Experiment & Causal Analysis

**Project:** Customer Retention Improvement Through Appointment Reminders  
**Industry:** Salon & Beauty Services  
**Analysis Type:** A/B Testing and Causal Inference  
**Dataset:** Synthetic Data (Simulated)  
**Status:** Design and analytical demonstration completed

---

## 1. Executive Summary

This project demonstrates how experimentation and causal inference techniques can be applied to evaluate the effectiveness of appointment reminders in improving customer retention for a fictional salon business operating 22 outlets.

The proposed experiment compares customers assigned to a reminder group against customers assigned to a control group that does not receive the experimental reminder.

The primary objective is to estimate whether appointment reminders improve the probability of a customer returning within 60 days.

The project demonstrates:

- Experimental design and hypothesis development.
- Sample-size and statistical power calculations.
- Randomization and Sample Ratio Mismatch (SRM) checks.
- A/B testing and confidence interval estimation.
- Customer segment-level analysis.
- Multiple-comparison correction.
- CUPED variance reduction.
- Historical Difference-in-Differences (DiD) analysis.

All datasets and reported outcomes are synthetic. Results demonstrate analytical methodology and must not be interpreted as actual business performance.

## 2. Business Problem

Customer retention is an important performance indicator for salon businesses. Customers who do not return after an appointment may reduce repeat revenue and increase customer acquisition requirements.

The business wants to understand whether sending appointment reminders can encourage customers to return within a defined period.

Without a controlled experiment, changes in retention could be influenced by seasonality, customer preferences, outlet performance or other external factors.

A randomized experiment provides a structured approach to estimating the incremental effect of the reminder intervention.

## 3. Business Objective

**Primary objective:**

Measure the impact of appointment reminders on customer retention within 60 days of an eligible index appointment.

**Secondary objectives:**

1. Evaluate retention effects across customer segments.
2. Determine the sample size required to detect a meaningful improvement.
3. Validate experimental randomization.
4. Assess the statistical significance and uncertainty of the estimated treatment effect.
5. Demonstrate variance reduction using CUPED.
6. Demonstrate historical causal analysis using Difference-in-Differences.

## 4. Experiment Hypothesis

**Null Hypothesis (H0):**

Appointment reminders do not improve 60-day customer retention.

The retention probability is equal between treatment and control groups.

**Alternative Hypothesis (H1):**

Appointment reminders improve 60-day customer retention.

The retention probability is higher in the treatment group.

The experiment uses a two-sided statistical significance level of 5% for sample-size planning.

## 5. Experimental Design

| Parameter | Design |
|---|---|
| Experiment type | Randomized Controlled A/B Test |
| Randomization unit | Customer |
| Treatment group | Customers assigned to receive reminders |
| Control group | Customers assigned to business-as-usual communication without the experimental reminder |
| Allocation | 50:50 |
| Primary outcome | Return within 60 days |
| Follow-up period | 60 days |
| Significance level | 5% |
| Statistical power | 80% |
| Minimum detectable effect | 3 percentage points |
| Baseline retention assumption | 50% |

### Treatment Group

Customers assigned to the treatment group are intended to receive the experimental appointment reminder.

### Control Group

Customers assigned to the control group continue without the experimental reminder.

Other customer communication policies should remain consistent across both groups wherever possible.

## 6. Target Population and Eligibility

The proposed target population consists of eligible salon customers with an identifiable customer record and a qualifying appointment.

Recommended eligibility criteria:

- Valid customer identifier.
- Eligible completed index appointment.
- Valid appointment date.
- No duplicate experiment assignment.
- Sufficient follow-up time to observe the 60-day retention outcome.

Walk-in appointments without a customer identifier should be excluded from customer-level randomization and retention analysis.

Each customer should enter the primary analysis once, using a clearly defined index appointment.

## 7. Randomization Strategy

Customers are allocated to treatment and control groups using a customer-level randomization process.

The intended allocation is:

- Treatment: 50%
- Control: 50%

Randomization should be performed using a reproducible process with a recorded random seed.

Randomization balance should be assessed using relevant pre-treatment characteristics:

- Customer segment.
- Home outlet.
- Previous visit frequency.
- Historical spending.
- Customer tenure.

### Sample Ratio Mismatch Validation

The synthetic customer roster contains:

| Group | Customers |
|---|---:|
| Control | 20,006 |
| Treatment | 19,994 |
| Total | 40,000 |

The SRM chi-square test returned a p-value of 0.952156.

No evidence of a sample allocation mismatch was detected.

This check validates the observed allocation balance; it does not independently establish the quality of the randomization process.

## 8. Sample Size and Statistical Power

The sample-size calculation uses the following planning assumptions:

| Parameter | Value |
|---|---:|
| Baseline retention | 50% |
| Expected treatment retention | 53% |
| Minimum detectable effect | 3 percentage points |
| Significance level | 0.05 |
| Statistical power | 80% |
| Allocation ratio | 1:1 |

The two-proportion power calculation estimated:

- Required control sample: 4,356 customers.
- Required treatment sample: 4,356 customers.
- Total sample: 8,712 customers.

Allowing an additional 10% for incomplete or unusable observations gives a target recruitment sample of approximately 9,680 customers.

The estimated enrollment period using the simulated enrollment rate was approximately 133 days.

Including a 60-day outcome follow-up period gives an estimated total duration of approximately 193 days.

These estimates assume independent customer-level observations. If randomization or implementation occurs at outlet level, clustering and design effects must be incorporated into the power calculation.

## 9. Success Metrics

### Primary Metric: 60-Day Customer Retention

The proportion of eligible customers who complete a qualifying return visit within 60 days of their index appointment.

### Secondary Metrics

- Repeat visit rate.
- Time to next completed visit.
- Customer retention by segment.
- Customer retention by outlet.

### Guardrail Metrics

The following should be monitored before making a real business rollout decision:

- Appointment cancellation rate.
- No-show rate.
- Revenue per completed visit.
- Customer complaints or opt-outs.
- Communication delivery and failure rates.

These guardrail outcomes were not included in the current synthetic A/B outcome ledger and therefore cannot be evaluated from the reported retention results.

## 10. Statistical Analysis Plan

The primary analysis compares 60-day retention between treatment and control groups.

The analysis includes:

1. Group-level retention calculations.
2. Absolute treatment effect in percentage points.
3. Relative retention lift.
4. Two-proportion statistical test.
5. 95% confidence interval estimation.
6. Statistical significance assessment.

The primary effect is calculated as the difference between treatment and control retention probabilities.

The primary analysis should follow the intention-to-treat principle, retaining customers in their originally assigned groups regardless of whether a reminder was successfully delivered.

### Customer Segment Analysis

Results are evaluated separately for:

- Loyal customers.
- Regular customers.
- New customers.

Holm correction is applied to the three subgroup comparisons to control the family-wise error rate.

A treatment-by-segment interaction test is used to assess whether the estimated treatment effects differ across segments.

### CUPED Analysis

CUPED is demonstrated using a simulated pre-experiment customer activity variable.

The objective is to reduce outcome variance using information measured before treatment assignment.

The revised synthetic CUPED scenario reported a 2.64% variance reduction.

### Historical Difference-in-Differences

A separate synthetic outlet-month dataset is used to demonstrate historical causal analysis.

It includes:

- 11 treatment outlets.
- 11 control outlets.
- 30 monthly observations.
- Intervention date: July 2025.

The analysis compares changes in retention between treatment and control outlets before and after intervention.

The historical DiD scenario is a separate simulation and is not linked to the customer-level A/B experiment.

## 11. Experiment Results Summary

The original synthetic A/B experiment produced:

| Metric | Result |
|---|---:|
| Control retention | 50.09% |
| Treatment retention | 52.55% |
| Absolute treatment effect | +2.46 pp |
| Relative retention lift | +4.90% |
| 95% confidence interval | +1.48 to +3.43 pp |
| P-value | Approximately 0.00000090 |

The treatment group showed a statistically significant positive retention difference in the simulated experiment.

Segment-level results remained significant after Holm correction. However, the joint treatment-by-segment interaction test was not statistically significant (p = 0.181031).

The separate historical DiD scenario estimated an effect of +5.8814 percentage points, compared with the six-percentage-point effect deliberately introduced into that simulation.

## 12. Risks and Limitations

The project uses synthetic data, and therefore its results cannot establish the effectiveness of appointment reminders in an actual salon business.

Additional limitations include:

- Simulated outcomes may not reflect actual customer behaviour.
- The main A/B, CUPED and DiD datasets represent separate simulation scenarios.
- The current CUPED covariate is simulated rather than derived from actual historical appointments.
- Guardrail metrics have not been validated through the experiment outcome ledger.
- Outlet-level DiD analysis uses only 22 clusters, limiting the reliability of conventional cluster-robust inference.
- A non-significant pre-trend test does not prove the parallel-trends assumption.
- Actual reminder delivery, contamination and customer opt-outs would require operational monitoring.

## 13. Business Recommendation

The simulated A/B experiment demonstrates a positive retention difference associated with the reminder intervention.

For a real business implementation, the recommended next step would be a controlled pilot using actual eligible salon customers.

The pilot should include:

1. Verified customer-level randomization.
2. Reliable reminder delivery tracking.
3. A predefined 60-day retention outcome.
4. Monitoring of cancellation, no-show and revenue guardrails.
5. Pre-specified statistical analysis.
6. Documentation of exclusions and missing outcomes.
7. A rollout decision based on both retention improvement and business impact.

Segment-specific reminder strategies should not be adopted solely on the basis of the current subgroup results because the interaction test did not demonstrate statistically significant treatment-effect heterogeneity.

## 14. Conclusion

This project demonstrates an end-to-end analytical framework for evaluating a customer retention intervention.

It combines experimental design, statistical power planning, randomization diagnostics, A/B testing, customer segmentation, CUPED and Difference-in-Differences.

The synthetic results demonstrate how these techniques can support structured business decisions while emphasizing the importance of experimental validity, statistical assumptions and transparent reporting.

**Final classification:** Synthetic analytical demonstration — not an actual salon business experiment.

---

**Prepared for:** Data Analytics Portfolio  
**Project:** Salon Experiment & Causal Analysis  
**Primary analytical tools:** Python, Pandas, NumPy, SciPy, Statsmodels, Matplotlib and Seaborn