# API Reference: Pricing Service

This document describes the interfaces for the Adaptive Loan Pricing Engine.

## Overview

The pricing engine exposes two interfaces:
1. **CLI** - Command-line interface for single predictions
2. **Python API** - Direct class usage for integration

A REST API (FastAPI) is planned but not yet implemented.

---

## CLI Interface

### Command

```bash
python src/pricing_service.py [OPTIONS]
```

### Required Arguments

| Argument | Type | Range | Description |
|----------|------|-------|-------------|
| `--income` | float | 10,000 - 500,000 | Annual income in USD |
| `--fico` | int | 300 - 850 | FICO credit score |
| `--amount` | float | 1,000 - 100,000 | Loan principal requested |
| `--term` | int | 36 or 60 | Loan term in months |

### Optional Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--dti` | float | 0.25 | Debt-to-income ratio (0.0 - 1.0) |
| `--util` | float | 30.0 | Credit utilization percentage (0 - 100) |
| `--inquiries` | int | 0 | Credit inquiries in last 6 months |

### Example Usage

```bash
# Basic request
python src/pricing_service.py --income 75000 --fico 720 --amount 15000 --term 36

# Full request with optional parameters
python src/pricing_service.py \
  --income 85000 \
  --fico 680 \
  --amount 20000 \
  --term 60 \
  --dti 0.35 \
  --util 45.0 \
  --inquiries 2
```

### Response Format

```json
{
    "decision": "APPROVE",
    "offered_rate": 0.1850,
    "offered_rate_display": "18.50%",
    "risk_segment": "NearPrime",
    "probability_of_default": "8.23%",
    "expected_profit": 847.52,
    "policy_notes": []
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `decision` | string | One of: `APPROVE`, `REJECT_RISK`, `REJECT_ECONOMICS` |
| `offered_rate` | float | Optimal interest rate (decimal, e.g., 0.185 = 18.5%) |
| `offered_rate_display` | string | Human-readable rate |
| `risk_segment` | string | One of: `Subprime`, `NearPrime`, `Prime`, `High Risk` |
| `probability_of_default` | string | Estimated PD as percentage |
| `expected_profit` | float | Expected profit in USD |
| `policy_notes` | array | List of governance rules applied |

### Decision Values

| Decision | Meaning | Exit Code |
|----------|---------|-----------|
| `APPROVE` | Loan approved at offered_rate | 0 |
| `REJECT_RISK` | PD exceeds 20% threshold | 1 |
| `REJECT_ECONOMICS` | Expected profit below $50 minimum | 1 |

### Policy Notes Examples

```json
["Capped at Prime Max (20%)"]
["Capped to Global Max (35%)"]
["PD exceeds maximum threshold"]
["Expected profit below minimum margin"]
["Pre-optimization PD Check"]
```

---

## Python API

### LoanPricingEngine Class

**Location:** `src/pricing_engine.py`

#### Initialization

```python
from src.pricing_engine import LoanPricingEngine

engine = LoanPricingEngine(
    risk_model_path='models/risk_model_xgb.pkl',
    elasticity_model_path='models/elasticity_model_logit.pkl',
    cost_of_funds=0.04,  # Optional, default 4%
    lgd=0.6              # Optional, default 60%
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `risk_model_path` | str | Required | Path to XGBoost risk model pickle |
| `elasticity_model_path` | str | Required | Path to statsmodels elasticity model pickle |
| `cost_of_funds` | float | 0.04 | Bank's borrowing cost (4%) |
| `lgd` | float | 0.6 | Loss Given Default (60%) |

#### get_optimal_rate Method

```python
result = engine.get_optimal_rate(applicant_data, pd_multiplier=1.0)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `applicant_data` | dict | Required | Applicant features (see below) |
| `pd_multiplier` | float | 1.0 | Stress testing multiplier for PD |

**Applicant Data Dictionary:**

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `risk_score_norm` | float | Yes | Normalized FICO: `(fico - 300) / 550` |
| `annual_inc` | float | Yes | Annual income in USD |
| `LoanOriginalAmount` | float | Yes | Loan principal |
| `term_years` | float | Yes | Loan term in years (3 or 5) |
| `dti` | float | No | Debt-to-income ratio |
| `revol_util` | float | No | Credit utilization |
| `inq_last_6mths` | int | No | Recent credit inquiries |
| `total_acc` | int | No | Total credit accounts |
| `emp_length` | int | No | Employment length in years |
| `home_ownership_RENT` | int | No | 1 if renting, 0 otherwise |
| `purpose_debt_consolidation` | int | No | 1 if debt consolidation, 0 otherwise |

**Return Value:**

```python
{
    'decision': str,           # 'APPROVE', 'REJECT_RISK', 'REJECT_ECONOMICS'
    'optimal_rate': float,     # Best rate (0.0 if rejected)
    'max_profit': float,       # Expected profit at optimal rate
    'prob_default': float,     # Probability of default
    'risk_segment': str,       # 'Subprime', 'NearPrime', 'Prime', 'High Risk'
    'curve_data': DataFrame,   # Rate vs Profit curve (None if rejected)
    'policy_notes': list       # Governance rules applied
}
```

#### Example: Python Integration

```python
from src.pricing_engine import LoanPricingEngine

# Initialize
engine = LoanPricingEngine(
    risk_model_path='models/risk_model_xgb.pkl',
    elasticity_model_path='models/elasticity_model_logit.pkl'
)

# Prepare applicant data
applicant = {
    'risk_score_norm': (720 - 300) / 550,  # FICO 720
    'annual_inc': 75000,
    'LoanOriginalAmount': 15000,
    'term_years': 3,
    'dti': 0.25,
    'revol_util': 30,
    'inq_last_6mths': 1
}

# Get optimal rate
result = engine.get_optimal_rate(applicant)

if result['decision'] == 'APPROVE':
    print(f"Approved at {result['optimal_rate']:.2%}")
    print(f"Expected profit: ${result['max_profit']:.2f}")
else:
    print(f"Rejected: {result['policy_notes']}")
```

#### Example: Stress Testing

```python
# Normal scenario
normal_result = engine.get_optimal_rate(applicant, pd_multiplier=1.0)

# Recession scenario (+30% PD)
recession_result = engine.get_optimal_rate(applicant, pd_multiplier=1.3)

# Severe stress (+50% PD)
stress_result = engine.get_optimal_rate(applicant, pd_multiplier=1.5)
```

---

## Policy Configuration

### Access Policy Config

```python
engine.policy_config
```

### Default Policy Values

| Parameter | Value | Description |
|-----------|-------|-------------|
| `GLOBAL_MIN_RATE` | 0.05 (5%) | Floor rate |
| `GLOBAL_MAX_RATE` | 0.35 (35%) | Regulatory usury cap |
| `MAX_PD_THRESHOLD` | 0.20 (20%) | Auto-reject if PD exceeds |
| `PRIME_MAX_RATE` | 0.20 (20%) | Cap for Prime segment |
| `MIN_PROFIT_MARGIN` | 50 | Minimum expected profit ($) |

### Modify Policy (Runtime)

```python
# Adjust for different markets
engine.policy_config['GLOBAL_MAX_RATE'] = 0.30  # 30% cap
engine.policy_config['MIN_PROFIT_MARGIN'] = 100  # Higher profit floor
```

---

## Error Handling

### FileNotFoundError

```python
try:
    engine = LoanPricingEngine(
        risk_model_path='models/risk_model_xgb.pkl',
        elasticity_model_path='models/elasticity_model_logit.pkl'
    )
except FileNotFoundError as e:
    print(f"Model files not found: {e}")
    print("Run notebooks 06 and 07 to generate models")
```

### Missing Features

If required features are missing from `applicant_data`, the risk model will use 0 as default. This may produce inaccurate results.

**Recommended:** Always provide all available features.

---

## Streamlit Dashboard

### Launch

```bash
streamlit run src/dashboard.py
```

### URL

```
http://localhost:8501
```

### Features

- Interactive sliders for applicant parameters
- Real-time rate optimization
- Profit curve visualization
- Stress testing controls (Cost of Funds, Recession Multiplier)
- Policy guardrails display

---

## Planned: REST API

Future implementation will provide:

```
POST /api/v1/price
GET  /api/v1/health
GET  /api/v1/config
```

See ADR-004 for planned REST API design.
