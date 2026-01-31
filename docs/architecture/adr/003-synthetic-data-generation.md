# ADR-003: Synthetic Data for Elasticity Training

## Status
Accepted

## Date
2025-12-10

## Context

Training an elasticity model requires knowing how borrowers would respond to different rate offers. This presents a fundamental challenge:

**The Counterfactual Problem**: In historical data, we only observe the rate that was actually offered and whether the borrower accepted. We don't know what would have happened at different rates.

For example, if a borrower accepted a 15% rate, we don't know if they would have:
- Accepted at 18%? (lost yield opportunity)
- Rejected at 12%? (unlikely but possible)

Without counterfactual data, we cannot estimate price elasticity.

## Decision

Generate **synthetic acceptance outcomes** for each loan in the Prosper dataset:

### Methodology

1. For each historical loan, create 15 rate scenarios (5% to 40%)

2. Calculate acceptance probability using a logistic function:
   ```
   P(Accept) = 1 / (1 + exp(α × (OfferedRate - ObservedRate)))
   ```
   Where:
   - `α = 30` (steepness parameter)
   - `ObservedRate` = the rate at which the loan was actually booked

3. Generate binary acceptance outcome by sampling from Bernoulli(P(Accept))

4. Apply noise and segment-specific adjustments

### Assumptions

- Borrowers who accepted at the observed rate would have higher acceptance at lower rates
- Borrowers who accepted at the observed rate would have lower acceptance at higher rates
- The relationship follows a logistic (S-curve) pattern
- Different segments may have different sensitivities (captured by segment-specific coefficients)

### Output

- File: `data/Prosper_Synthetic_Elasticity.csv` (~786 MB)
- ~850,000 training observations (multiple scenarios per loan)

## Alternatives Considered

### Use Only Historical Data
Train on actual acceptance/rejection at observed rates only.

**Rejected because:**
- Only one data point per loan (no rate variation)
- Cannot estimate sensitivity to rate changes
- Selection bias: observed rates were already optimized

### Randomized Controlled Trial
Run experiments with randomized rate offers.

**Rejected because:**
- Ethically questionable (different rates for similar borrowers)
- Expensive (lost revenue from suboptimal rates)
- Time-consuming (need to wait for outcomes)
- Not feasible for portfolio project

### Use Published Elasticity Estimates
Apply elasticity values from academic literature.

**Rejected because:**
- May not match specific population
- Less flexible for segment-specific effects
- No learning from our data

### Causal Inference Methods
Use instrumental variables or regression discontinuity.

**Rejected because:**
- Requires specific data structures we don't have
- Complex methodology with strong assumptions
- Less transparent for governance

## Consequences

### Positive
- Enables elasticity estimation without experiments
- Creates sufficient data for segment-specific coefficients
- Reproducible and documented methodology
- Can be regenerated with different assumptions

### Negative
- Synthetic data may not match real behavior
- Steepness parameter (α=30) is assumed, not estimated
- No ground truth to validate against
- Requires careful documentation for regulators

### Mitigations

1. **Sensitivity Analysis**: Test with different α values (20, 30, 40)
2. **Shadow Mode**: Compare predicted vs. actual acceptance in production
3. **Calibration Monitoring**: Track acceptance rate deviations over time
4. **Documentation**: Clear disclosure in model governance

## The "Optimization Floor" Fix

Initial synthetic data generation had an issue where the optimization engine consistently hit the rate floor (5%) because synthetic acceptance probabilities were too high at all rates.

**Root Cause**: Insufficient penalty for high rates in synthetic generation.

**Fix**: Increased steepness parameter and added segment-specific adjustments.

See `docs/synthetic_data_logic.md` for detailed explanation.

## References

- Generator Code: `src/sythetic_data_generator.py`
- Methodology Documentation: `docs/synthetic_data_logic.md`
- Elasticity Training: `notebooks/07_elasticity_model.ipynb`
