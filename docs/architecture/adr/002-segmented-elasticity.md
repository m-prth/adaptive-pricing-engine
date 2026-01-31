# ADR-002: Segmented Elasticity Model

## Status
Accepted

## Date
2025-12-15

## Context

The initial elasticity model used a single rate coefficient for all borrowers:

```
P(Accept) = logistic(β₀ + β₁×Rate + β₂×RiskScore + β₃×Rate×RiskScore + ...)
```

The interaction term `Rate × RiskScore` allowed price sensitivity to vary linearly with risk score. However, this approach had limitations:

1. **Linear assumption**: Forced the difference in sensitivity between Score 0.2→0.3 to be the same as 0.8→0.9
2. **Reality**: Behavioral research shows consumers often fall into distinct segments with different behaviors
3. **Business need**: Pricing strategies differ by segment (Subprime vs. Prime)

## Decision

Replace the continuous interaction term with **segment-specific rate coefficients**:

```
P(Accept) = logistic(β₀ + β₁×RiskScore + β₂×Rate_Subprime + β₃×Rate_NearPrime + β₄×Rate_Prime + ...)
```

Where:
- `Rate_Subprime = Rate × I(Segment = Subprime)`
- `Rate_NearPrime = Rate × I(Segment = NearPrime)`
- `Rate_Prime = Rate × I(Segment = Prime)`

### Segmentation Boundaries

Based on normalized risk score `(FICO - 300) / 550`:
- **Subprime**: risk_score_norm ≤ 0.4 (FICO ≤ 520)
- **NearPrime**: 0.4 < risk_score_norm ≤ 0.75 (FICO 520-713)
- **Prime**: risk_score_norm > 0.75 (FICO > 713)

### Resulting Coefficients

| Segment | Rate Coefficient | Interpretation |
|---------|------------------|----------------|
| Subprime | -26.55 | Most price sensitive |
| Prime | -22.87 | Moderate sensitivity |
| NearPrime | -19.91 | Least price sensitive |

## Alternatives Considered

### Keep Continuous Interaction
Continue using `Rate × RiskScore`.

**Rejected because:**
- Forces linear relationship that may not match behavior
- Less interpretable for business users
- Cannot capture segment-specific dynamics

### Learn Segments with Clustering
Use k-means or similar to discover segments from data.

**Rejected because:**
- Learned segments may not be business-meaningful
- Harder to explain to regulators
- May change on retraining, causing instability

### More Granular Segments (5+)
Create more segments for finer granularity.

**Rejected because:**
- Insufficient data per segment
- Increased model complexity
- Diminishing returns on interpretability

## Consequences

### Positive
- Each segment has its own demand curve
- Captures real behavioral differences (Subprime 33% more sensitive than NearPrime)
- Interpretable for business and compliance
- Model pseudo R² improved from baseline

### Negative
- Segment boundaries are fixed, not learned
- Discontinuity at segment boundaries
- Requires segment determination before elasticity prediction

### Validation
- Risk monotonicity confirmed: higher PD correlates with higher rates (>0.9 correlation)
- Demand curves are monotonically decreasing in rate
- No sign inversions in coefficients

## References

- Implementation: `notebooks/07_elasticity_model.ipynb` (Section 5: Feature Tuning)
- Demand Curves Chart: `docs/Segmented Demand Curves.png`
- Integration Validation: `notebooks/09_integration_validation.ipynb`
