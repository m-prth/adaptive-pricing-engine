# Model Card: Risk Model (Probability of Default)

## Model Details

| Property | Value |
|----------|-------|
| Model Name | Risk Model (PD Model) |
| Version | 1.0 |
| Type | Binary Classifier |
| Algorithm | XGBoost |
| Framework | xgboost 3.1.2 |
| Output | Probability of Default (0-1) |
| File | `models/risk_model_xgb.pkl` |

## Intended Use

### Primary Use Case
Estimate the probability of loan default for use as an input to the Adaptive Loan Pricing Engine. The model provides risk scores that feed into the profit optimization calculation.

### Out of Scope
- Direct approval/rejection decisions (this is handled by the governance layer)
- Commercial or business loans
- Mortgage lending
- Non-US borrowers

## Training Data

### Data Source
- **Dataset**: LendingClub Loan Data (2007-2018 Q4)
- **Size**: ~1.2 million loans
- **Features**: 80 engineered features

### Target Variable
- `loan_status` mapped to binary:
  - `1` = Default / Charged Off
  - `0` = Fully Paid / Current

### Class Distribution
| Class | Count | Percentage |
|-------|-------|------------|
| Non-Default (0) | 646,051 | 80% |
| Default (1) | 161,159 | 20% |

### Data Split
| Split | Purpose |
|-------|---------|
| Train | Model training |
| Validation | Early stopping, hyperparameter tuning |
| Test | Final performance evaluation |

## Model Architecture

### Hyperparameters (Final Configuration)

```python
XGBClassifier(
    objective="binary:logistic",
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6,
    min_child_weight=1,
    subsample=0.8,
    colsample_bytree=1.0,
    scale_pos_weight=4.01,  # Class imbalance handling
    eval_metric="auc",
    early_stopping_rounds=20,
    random_state=42
)
```

### Class Imbalance Handling
- `scale_pos_weight = 4.01` (ratio of negatives to positives)
- No oversampling or synthetic balancing applied
- Preserves real-world class proportions and probability calibration

## Performance Metrics

### Primary Metric: ROC-AUC
| Dataset | AUC |
|---------|-----|
| Cross-Validation | 0.7178 |
| Validation | 0.7179 |
| Test | 0.7168 |

### Classification Report (Test Set)

| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| Non-Default (0) | 0.89 | 0.64 | 0.74 |
| Default (1) | 0.32 | 0.67 | 0.43 |

### Metric Interpretation

**Why these metrics are appropriate:**

1. **Recall for Defaults (67%)**: The model captures the majority of risky applicants. In credit risk, missing a defaulter (false negative) is significantly more costly than flagging a good borrower.

2. **Lower Precision on Defaults (32%)**: Expected and acceptable. The model is intentionally conservative, which protects capital in pricing applications.

3. **ROC-AUC (~0.72)**: Indicates strong rank-ordering capability. The model reliably distinguishes higher-risk from lower-risk borrowers.

4. **Accuracy (65%)**: Reported for completeness, not optimization. Accuracy is misleading for imbalanced datasets.

## Feature Importance

Top predictive features (by gain):
1. Credit utilization (`revol_util`)
2. Debt-to-income ratio (`dti`)
3. Annual income (`annual_inc`)
4. FICO score (via `risk_score_norm`)
5. Recent credit inquiries (`inq_last_6mths`)
6. Loan term (`term_years`)
7. Total accounts (`total_acc`)

## Limitations

### Data Limitations
- Trained on 2007-2018 data; may not reflect post-COVID lending patterns
- US-only borrowers from LendingClub platform
- Does not account for macroeconomic regime shifts

### Model Limitations
- Point-in-time prediction; does not model time-varying default risk
- Assumes feature distributions remain stable (requires PSI monitoring)
- XGBoost is less interpretable than logistic regression

### Known Failure Modes
- Performance may degrade for applicant profiles underrepresented in training data
- Extreme economic conditions (recession) may cause underestimation of PD
- Use `pd_multiplier` parameter for stress testing scenarios

## Ethical Considerations

### Protected Characteristics
- No protected class features (race, gender, age) are used directly
- FICO score is used as primary risk signal, which may have disparate impact
- Geographic features are not included

### Fair Lending Compliance
- Model should be monitored for disparate impact across protected groups
- Adverse action reasons can be derived from feature importance
- Governance layer enforces consistent treatment via policy rules

## Monitoring Requirements

### Drift Detection
- Monitor PSI (Population Stability Index) weekly on key features
- Thresholds:
  - PSI < 0.1: Safe
  - PSI 0.1-0.25: Warning
  - PSI > 0.25: Retrain required

### Performance Monitoring
- Track actual vs predicted default rates monthly
- Alert if actual default rate exceeds prediction by >20%

## Model Governance

### Retraining Triggers
1. PSI exceeds 0.25 on any key feature
2. AUC drops below 0.68 on production data
3. Actual default rate deviates >20% from predicted
4. Major economic regime change

### Approval Requirements
- Model Risk Management (MRM) sign-off required for production deployment
- Annual model review required

## References

- Training Notebook: `notebooks/06_pd_model.ipynb`
- Feature Engineering: `notebooks/03_feature_eng_lending_club.ipynb`
- Integration Validation: `notebooks/09_integration_validation.ipynb`
