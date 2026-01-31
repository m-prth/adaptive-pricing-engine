# Model Card: Elasticity Model (Price Sensitivity)

## Model Details

| Property | Value |
|----------|-------|
| Model Name | Elasticity Model |
| Version | 1.0 |
| Type | Binary Classifier (Demand Model) |
| Algorithm | Logistic Regression |
| Framework | statsmodels 0.14.6 |
| Output | Probability of Acceptance (0-1) |
| File | `models/elasticity_model_logit.pkl` |

## Intended Use

### Primary Use Case
Estimate the probability that a borrower accepts a loan offer at a given interest rate. This model captures **price sensitivity** (elasticity) across different borrower segments to enable profit-maximizing rate optimization.

### Out of Scope
- Credit risk assessment (handled by Risk Model)
- Approval/rejection decisions
- Post-origination behavior prediction

## Training Data

### Data Source
- **Dataset**: Prosper Loan Data with synthetic rate scenarios
- **Size**: 851,850 observations (multiple rate scenarios per borrower)
- **Synthetic Data**: Generated to simulate borrower acceptance decisions across rate ranges 5%-40%

### Target Variable
- `Accepted`: Binary indicator of loan acceptance
  - `1` = Borrower accepts the offer
  - `0` = Borrower rejects the offer

### Why Synthetic Data?
Real counterfactual pricing outcomes (what would happen at different rates) are not observable. Synthetic scenarios approximate borrower decision behavior based on observed acceptance patterns and economic theory.

See `docs/synthetic_data_logic.md` for detailed methodology.

## Model Architecture

### Feature Set

| Feature | Description | Coefficient |
|---------|-------------|-------------|
| `const` | Intercept | 7.3417 |
| `risk_score_norm` | Normalized FICO score (0-1) | -3.9051 |
| `Rate_Subprime` | Rate × Subprime segment indicator | -26.5541 |
| `Rate_NearPrime` | Rate × NearPrime segment indicator | -19.9071 |
| `Rate_Prime` | Rate × Prime segment indicator | -22.8656 |
| `LoanOriginalAmount` | Loan principal | -4.66e-05 |

### Segmented Price Sensitivity

The model uses **segment-specific rate coefficients** instead of a single interaction term, allowing distinct demand curves per segment:

| Segment | Rate Coefficient | Interpretation |
|---------|------------------|----------------|
| Subprime | -26.55 | Most price sensitive |
| Prime | -22.87 | Moderate sensitivity |
| NearPrime | -19.91 | Least price sensitive |

**Key Insight**: Subprime borrowers are ~33% more price-sensitive than NearPrime borrowers, likely due to tighter budget constraints.

### Segmentation Logic
Based on `risk_score_norm = (FICO - 300) / 550`:
- **Subprime**: risk_score_norm <= 0.4
- **NearPrime**: 0.4 < risk_score_norm <= 0.75
- **Prime**: risk_score_norm > 0.75

## Performance Metrics

### Model Fit Statistics

| Metric | Value |
|--------|-------|
| Pseudo R-squared | 0.4440 |
| Log-Likelihood | -324,110 |
| LL-Null | -582,910 |
| LLR p-value | 0.000 |

### Why These Metrics Matter

1. **Pseudo R² = 0.44**: Strong for a behavioral choice model. Acceptance decisions are influenced by unobserved factors (urgency, alternatives, preferences).

2. **LLR p-value = 0**: Confirms that pricing and risk variables meaningfully explain acceptance behavior beyond chance.

3. **All coefficients statistically significant** (p < 0.001): Each variable contributes meaningfully to the prediction.

### Coefficient Validation

| Validation Check | Status |
|------------------|--------|
| Rate coefficients negative | Pass (higher rates reduce acceptance) |
| Monotonic price response | Pass |
| Segment differentiation | Pass (distinct elasticities) |
| No sign inversions | Pass |

## Economic Interpretation

### Demand Curve Behavior

For a **10% increase in offered rate**:
- Subprime acceptance drops by ~93% (log-odds: -2.65)
- NearPrime acceptance drops by ~86% (log-odds: -1.99)
- Prime acceptance drops by ~90% (log-odds: -2.29)

### Marginal Effects

At the median acceptance probability (50%):
- Each 1% rate increase reduces Subprime acceptance by ~6.6%
- Each 1% rate increase reduces NearPrime acceptance by ~5.0%
- Each 1% rate increase reduces Prime acceptance by ~5.7%

## Limitations

### Data Limitations
- Based on synthetic acceptance scenarios, not observed counterfactuals
- Prosper platform borrowers may not represent all consumer lending
- Does not capture competitor rate effects

### Model Limitations
- Assumes linear log-odds relationship with rate
- Does not model time-varying preferences
- Segment boundaries are fixed (not learned)

### Known Failure Modes
- May underestimate sensitivity during economic stress
- Extreme rates (>35%) are extrapolated beyond training data
- New borrower profiles may have different elasticity patterns

## Ethical Considerations

### Fair Pricing
- Segment-based pricing must comply with fair lending regulations
- Different rates by segment are based on risk characteristics, not protected classes
- Rate caps in governance layer prevent exploitative pricing

### Transparency
- Logistic regression provides interpretable coefficients
- Easy to explain rate decisions to borrowers and regulators
- No "black box" concerns

## Monitoring Requirements

### Drift Detection
- Monitor acceptance rate by segment weekly
- Track rate distribution of accepted loans
- PSI on `risk_score_norm` and `LoanOriginalAmount`

### Calibration Monitoring
- Compare predicted vs actual acceptance rates monthly
- Alert if deviation exceeds 10 percentage points

## Model Governance

### Why Logistic Regression?

Advanced ML models (XGBoost, neural networks) were deliberately avoided:
- They can create non-monotonic price responses
- They obscure elasticity interpretation
- They complicate regulatory approval

Logistic regression provides:
- Stable gradients for optimization
- Clear elasticity estimates
- Safe deployment in pricing engines

### Retraining Triggers
1. Acceptance rates deviate >10% from predictions
2. New competitor enters market
3. Significant change in borrower demographics
4. Annual scheduled review

## References

- Training Notebook: `notebooks/07_elasticity_model.ipynb`
- Feature Engineering: `notebooks/04_feature_eng_prosper.ipynb`
- Synthetic Data Logic: `docs/synthetic_data_logic.md`
- Integration Validation: `notebooks/09_integration_validation.ipynb`
