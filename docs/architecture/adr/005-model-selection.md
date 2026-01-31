# ADR-005: Model Selection Rationale

## Status
Accepted

## Date
2025-12-15

## Context

Choosing ML algorithms involves trade-offs between:
- Predictive performance
- Interpretability
- Regulatory acceptance
- Operational complexity
- Maintenance burden

For a loan pricing system, these trade-offs are particularly important because:
1. Regulators require model explainability
2. Wrong predictions have significant financial impact
3. Models must be stable over time
4. Different components have different requirements

## Decisions

### Risk Model: XGBoost

**Chosen for:**
- Strong performance on tabular credit data (AUC ~0.72)
- Handles non-linear interactions automatically
- Robust to feature scale differences
- Industry-standard for credit risk
- Native feature importance

**Trade-offs accepted:**
- Less interpretable than logistic regression
- Requires more careful hyperparameter tuning
- Larger model file size

**Alternatives rejected:**
- **Logistic Regression**: Lower AUC (~0.65), misses non-linear effects
- **Random Forest**: Similar performance, slower inference
- **Neural Network**: Overkill for tabular data, harder to explain
- **LightGBM/CatBoost**: Similar to XGBoost, XGBoost more widely adopted

### Elasticity Model: Logistic Regression (Statsmodels)

**Chosen for:**
- Direct interpretability of coefficients as elasticity measures
- Natural enforcement of monotonic price response
- Stability under large sample sizes
- Alignment with economic theory
- Regulatory acceptance

**Trade-offs accepted:**
- Lower pseudo R² than tree-based models
- Cannot capture complex non-linear effects
- Requires careful feature engineering

**Alternatives rejected:**
- **XGBoost**: Can create non-monotonic price responses
- **Neural Network**: Black box, no coefficient interpretation
- **GAM (Generalized Additive Model)**: More flexible but less interpretable
- **Scikit-learn Logistic**: Statsmodels provides better statistical output

### Optimization: Grid Search

**Chosen for:**
- Simple and reliable
- Guaranteed to find optimum within grid
- Easy to understand and debug
- Fast enough for real-time (61 points in <100ms)

**Trade-offs accepted:**
- Not continuous optimization
- Resolution limited by grid granularity
- Doesn't scale to many dimensions

**Alternatives rejected:**
- **Gradient Descent**: Elasticity function may not be smooth
- **Bayesian Optimization**: Overkill for 1D optimization
- **Analytical Solution**: No closed form for this objective

## Consequences

### Risk Model (XGBoost)
- Requires SHAP or similar for explanations
- Model files are larger (~10MB vs <1MB for logistic)
- Feature importance available but not coefficient-based

### Elasticity Model (Logistic Regression)
- Coefficients directly interpretable
- Easy to explain to regulators
- May underfit complex behaviors
- Stable predictions, no surprising non-monotonicities

### Optimization (Grid Search)
- Predictable performance
- Easy to parallelize if needed
- Resolution: 0.5% rate increments (61 points from 5% to 35%)

## Validation

Both model choices validated via:
1. **Integration Testing**: `notebooks/09_integration_validation.ipynb`
2. **Sensitivity Analysis**: `notebooks/10_sensitivity_analysis.ipynb`
3. **Backtesting**: `notebooks/12_backtesting.ipynb`

Key validation results:
- Risk monotonicity: Correlation(PD, Rate) > 0.9
- Demand monotonicity: All rate coefficients negative
- Governance layer prevents edge case issues

## References

- Risk Model Training: `notebooks/06_pd_model.ipynb`
- Elasticity Model Training: `notebooks/07_elasticity_model.ipynb`
- Optimization Engine: `src/pricing_engine.py`
