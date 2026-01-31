# ADR-001: Dual-Model Architecture for Pricing

## Status
Accepted

## Date
2025-12-01

## Context

Traditional loan pricing uses static "rate cards" - lookup tables that map risk tiers to fixed interest rates. This approach has limitations:

1. **Under-pricing risk**: Low-risk, price-sensitive borrowers receive rates higher than necessary and leave for competitors
2. **Lost yield**: Inelastic borrowers (who would accept higher rates) are under-charged
3. **No optimization**: No mechanism to find the profit-maximizing rate for each applicant

We needed an architecture that could:
- Assess credit risk accurately
- Model borrower price sensitivity
- Optimize rates dynamically per applicant
- Maintain regulatory compliance

## Decision

We implemented a **Dual-Model + Optimizer** architecture:

### Brain 1: Risk Model (XGBoost)
- Predicts Probability of Default (PD)
- Trained on LendingClub historical loan performance
- Outputs calibrated default probabilities

### Brain 2: Elasticity Model (Logistic Regression)
- Predicts Probability of Acceptance given a rate
- Trained on Prosper data with synthetic rate scenarios
- Outputs acceptance probabilities across rate spectrum

### Brain 3: Optimization Engine
- Combines PD and P(Accept) to compute Expected Profit
- Grid search over rate space (5% to 35%, 61 points)
- Finds rate that maximizes: `E[Profit] = P(Accept) × [(1-PD) × Income - PD × Loss]`

## Alternatives Considered

### Single End-to-End Model
Train one model to directly predict optimal rate.

**Rejected because:**
- No interpretability of risk vs. elasticity components
- Harder to validate individual components
- Cannot explain decisions to regulators

### Reinforcement Learning
Learn optimal pricing through trial and error.

**Rejected because:**
- Requires live experimentation with real loans
- Long feedback loops (defaults take months to observe)
- Regulatory concerns about unexplainable pricing

### Rule-Based Pricing
Encode expert rules for rate adjustments.

**Rejected because:**
- Cannot adapt to changing market conditions
- Does not learn from data
- Misses non-linear interactions

## Consequences

### Positive
- Clear separation of concerns (risk vs. demand)
- Each model can be validated independently
- Explainable to regulators and internal stakeholders
- Governance layer can be applied consistently
- Stress testing is straightforward (adjust PD multiplier)

### Negative
- Two models to maintain and monitor
- Requires synthetic data for elasticity training
- Grid search is computationally simple but not optimal for very fine granularity

### Risks
- Models may drift at different rates
- Synthetic elasticity data may not match real behavior
- Correlation between risk and elasticity not fully captured

## References

- Architecture Notebook: `notebooks/00_project_architecture.ipynb`
- Risk Model: `notebooks/06_pd_model.ipynb`
- Elasticity Model: `notebooks/07_elasticity_model.ipynb`
- Optimization Engine: `src/pricing_engine.py`
