# Monitoring Plan

This document outlines the production monitoring strategy for the Adaptive Loan Pricing Engine (ALPE).

## Overview

The monitoring plan covers three categories:
1. **Data Drift Monitoring** - Detecting shifts in input feature distributions
2. **Model Performance Monitoring** - Tracking prediction accuracy over time
3. **Business Metrics Monitoring** - Ensuring business objectives are met

## 1. Data Drift Monitoring

### Method: Population Stability Index (PSI)

PSI measures the shift in feature distributions between training data and production data.

**Formula:**
```
PSI = Σ (Actual% - Expected%) × ln(Actual% / Expected%)
```

**Implementation:** `src/monitor_util.py`

### PSI Thresholds

| PSI Value | Status | Action |
|-----------|--------|--------|
| < 0.1 | Safe | No action required |
| 0.1 - 0.25 | Warning | Investigate root cause |
| > 0.25 | Critical | Initiate model retraining |

### Features to Monitor

#### Risk Model Features
| Feature | Priority | Frequency |
|---------|----------|-----------|
| `risk_score_norm` (FICO) | Critical | Weekly |
| `dti` | Critical | Weekly |
| `revol_util` | High | Weekly |
| `annual_inc` | High | Weekly |
| `inq_last_6mths` | Medium | Bi-weekly |
| `LoanOriginalAmount` | Medium | Bi-weekly |
| `term_years` | Low | Monthly |

#### Elasticity Model Features
| Feature | Priority | Frequency |
|---------|----------|-----------|
| `risk_score_norm` | Critical | Weekly |
| `LoanOriginalAmount` | High | Weekly |
| Segment distribution | High | Weekly |
| Rate distribution | Medium | Weekly |

### Drift Alert Process

```
1. Automated PSI calculation runs [weekly]
2. Results logged to monitoring dashboard
3. If PSI > 0.1 on any critical feature:
   - Alert sent to model owner
   - Root cause analysis within 48 hours
4. If PSI > 0.25 on any feature:
   - Escalate to Model Risk Management
   - Initiate retraining pipeline
   - Document in model governance log
```

## 2. Model Performance Monitoring

### Risk Model (PD) Metrics

| Metric | Baseline | Alert Threshold | Frequency |
|--------|----------|-----------------|-----------|
| AUC-ROC | 0.72 | < 0.68 | Monthly |
| Actual Default Rate | ~8% | > 12% or < 4% | Monthly |
| Brier Score | 0.15 | > 0.20 | Monthly |
| Calibration Slope | 1.0 | < 0.8 or > 1.2 | Quarterly |

### Elasticity Model Metrics

| Metric | Baseline | Alert Threshold | Frequency |
|--------|----------|-----------------|-----------|
| Predicted vs Actual Acceptance Rate | Within 5% | > 10% deviation | Weekly |
| Segment Distribution Shift | Stable | > 15% change | Weekly |
| Rate Coefficient Stability | Per training | Sign change | Quarterly |

### Performance Degradation Process

```
1. If AUC drops below 0.68:
   - Conduct segment-level analysis
   - Check for population shift
   - Evaluate retraining need

2. If actual default rate deviates > 20%:
   - Review economic conditions
   - Assess stress scenario applicability
   - Consider pd_multiplier adjustment

3. If acceptance rate deviates > 10%:
   - Analyze by segment
   - Check competitor rate environment
   - Review elasticity assumptions
```

## 3. Business Metrics Monitoring

### Operational Metrics

| Metric | Description | Frequency |
|--------|-------------|-----------|
| Decision Volume | Total pricing decisions per day | Daily |
| Approval Rate | APPROVE / Total decisions | Daily |
| Rejection Breakdown | REJECT_RISK vs REJECT_ECONOMICS | Daily |
| Average Offered Rate | Mean rate across approvals | Daily |
| Rate by Segment | Mean rate per Subprime/NearPrime/Prime | Daily |

### Profitability Metrics

| Metric | Description | Frequency |
|--------|-------------|-----------|
| Expected Profit (Predicted) | Sum of predicted E[Profit] | Daily |
| Actual Profit (Realized) | Observed profit on matured loans | Monthly |
| Profit Accuracy | Predicted vs Actual | Quarterly |
| Average Margin | (Rate - Cost of Funds) × Principal | Weekly |

### Policy Compliance Metrics

| Metric | Description | Alert Condition |
|--------|-------------|-----------------|
| Rate Cap Violations | Decisions capped by GLOBAL_MAX_RATE | > 5% of decisions |
| Prime Cap Applications | Decisions capped by PRIME_MAX_RATE | Informational |
| PD Rejections | REJECT_RISK decisions | > 25% of applications |
| Economics Rejections | REJECT_ECONOMICS decisions | > 10% of applications |

## 4. Monitoring Dashboard

### Recommended Visualizations

1. **PSI Trend Chart** - Line chart showing PSI values over time for each monitored feature

2. **AUC Trend** - Monthly AUC with confidence intervals

3. **Default Rate Comparison** - Predicted vs Actual default rate by cohort

4. **Acceptance Rate by Segment** - Stacked bar chart showing acceptance rates

5. **Rate Distribution** - Histogram of offered rates with segment overlay

6. **Decision Funnel** - Sankey diagram: Applications → Approvals → Acceptances

### Alert Channels

| Severity | Channel | Response Time |
|----------|---------|---------------|
| Critical | Email + Slack + PagerDuty | < 1 hour |
| Warning | Email + Slack | < 24 hours |
| Informational | Dashboard only | Next business day |

## 5. Governance Integration

### Model Review Cadence

| Review Type | Frequency | Participants |
|-------------|-----------|--------------|
| Monitoring Review | Weekly | Model Owner |
| Performance Review | Monthly | Model Owner + Data Science Lead |
| MRM Review | Quarterly | Model Risk Management |
| Full Validation | Annual | MRM + External Validator |

### Documentation Requirements

All monitoring results must be documented with:
- Date and time of analysis
- Data period covered
- Key findings
- Actions taken (if any)
- Sign-off by model owner

### Retraining Protocol

When retraining is triggered:

1. **Pre-Training**
   - Document trigger reason
   - Freeze production model version
   - Prepare updated training data

2. **Training**
   - Follow original training notebooks
   - Compare new model to champion
   - Validate on holdout data

3. **Validation**
   - Run integration tests (notebook 09)
   - Conduct sensitivity analysis (notebook 10)
   - Verify policy layer behavior (notebook 11)

4. **Deployment**
   - Shadow mode deployment (1 week minimum)
   - A/B test if possible
   - Full rollout with monitoring

## 6. Implementation Checklist

### Immediate (Pre-Production)
- [ ] Set up PSI calculation job (weekly cron)
- [ ] Create monitoring database/tables
- [ ] Configure alert channels
- [ ] Build initial dashboard

### Short-Term (First Month)
- [ ] Establish baseline metrics
- [ ] Tune alert thresholds based on initial data
- [ ] Document escalation procedures
- [ ] Train operations team

### Ongoing
- [ ] Weekly drift review
- [ ] Monthly performance review
- [ ] Quarterly governance review
- [ ] Annual full validation

## References

- PSI Implementation: `src/monitor_util.py`
- Validation Notebooks: `notebooks/09_integration_validation.ipynb`, `notebooks/10_sensitivity_analysis.ipynb`
- Model Cards: `docs/models/risk-model-card.md`, `docs/models/elasticity-model-card.md`
