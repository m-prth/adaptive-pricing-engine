# ADR-004: Governance Layer Design

## Status
Accepted

## Date
2025-12-20

## Context

ML-based pricing introduces risks that pure optimization doesn't address:

1. **Regulatory Risk**: Usury laws cap maximum rates (varies by state, typically 30-36%)
2. **Reputational Risk**: Charging high rates to low-risk customers damages brand
3. **Economic Risk**: Approving loans with negative expected value
4. **Fair Lending Risk**: Disparate impact on protected classes

The optimization engine maximizes expected profit, but profit maximization alone can lead to:
- Rates exceeding legal limits
- Predatory pricing on captive segments
- Approving unprofitable high-risk loans
- Inconsistent treatment of similar applicants

## Decision

Implement a **governance layer** that reviews and constrains ML-proposed rates before final decision.

### Implementation

The `_apply_governance()` method in `LoanPricingEngine` acts as a "Compliance Officer":

```python
def _apply_governance(self, proposed_rate, pd, segment, expected_profit):
    # Rule 1: Hard PD Cutoff
    if pd > MAX_PD_THRESHOLD:  # 20%
        return 'REJECT_RISK', 0.0, ['PD exceeds maximum threshold']

    # Rule 2: Global Rate Cap
    if rate > GLOBAL_MAX_RATE:  # 35%
        rate = GLOBAL_MAX_RATE
        notes.append('Capped to Global Max')

    # Rule 3: Segment-Specific Caps
    if segment == 'Prime' and rate > PRIME_MAX_RATE:  # 20%
        rate = PRIME_MAX_RATE
        notes.append('Capped at Prime Max')

    # Rule 4: Minimum Profit Margin
    if expected_profit < MIN_PROFIT_MARGIN:  # $50
        return 'REJECT_ECONOMICS', 0.0, ['Expected profit below minimum']

    return 'APPROVE', rate, notes
```

### Policy Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `MAX_PD_THRESHOLD` | 20% | Risk appetite limit; higher PD = unacceptable loss exposure |
| `GLOBAL_MAX_RATE` | 35% | Regulatory usury cap (conservative) |
| `PRIME_MAX_RATE` | 20% | Brand protection; low-risk customers expect competitive rates |
| `MIN_PROFIT_MARGIN` | $50 | Economic floor; covers operational costs |
| `GLOBAL_MIN_RATE` | 5% | Floor rate; below this is unprofitable |

### Execution Order

1. **Pre-Optimization PD Check**: Reject immediately if PD > 20%
2. **Optimization**: Find profit-maximizing rate
3. **Post-Optimization Governance**: Apply caps and checks
4. **Final Decision**: Return approved rate or rejection

## Alternatives Considered

### Constrained Optimization
Build constraints into the optimization objective.

**Rejected because:**
- Mixes business logic with ML logic
- Harder to audit and explain
- Constraints may conflict

### Soft Penalties
Add penalty terms for high rates or high PD.

**Rejected because:**
- Penalty weights are arbitrary
- May still violate hard constraints
- Less transparent

### ML-Based Governance
Train a model to predict "appropriate" rates.

**Rejected because:**
- Requires labeled "appropriate" data
- Black box on top of black box
- Regulatory concerns

## Consequences

### Positive
- Clear separation: ML proposes, governance disposes
- Auditable decision trail via `policy_notes`
- Easy to modify thresholds without retraining models
- Consistent treatment via deterministic rules
- Explainable rejections

### Negative
- Rate caps may reduce theoretical profit
- Fixed thresholds may not adapt to market conditions
- Segment boundaries are hard-coded

### Governance Benefits

1. **Regulatory Compliance**: Never exceed usury limits
2. **Risk Management**: Auto-reject high-risk applicants
3. **Brand Protection**: Competitive rates for Prime customers
4. **Economic Viability**: Reject unprofitable loans
5. **Audit Trail**: Every decision has documented reasoning

## Future Enhancements

1. **State-Specific Caps**: Different usury limits by state
2. **Dynamic Thresholds**: Adjust based on portfolio composition
3. **Fair Lending Checks**: Disparate impact monitoring
4. **Override Workflow**: Human-in-the-loop for edge cases

## References

- Implementation: `src/pricing_engine.py` (`_apply_governance` method)
- Policy Demonstration: `notebooks/11_pricing_policy_layer.ipynb`
- Governance Summary: `notebooks/13_model_governance_summary.ipynb`
