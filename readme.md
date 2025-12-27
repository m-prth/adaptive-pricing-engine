
# 🏦 Adaptive Loan Pricing Engine (ALPE)

> **A "Self-Driving" Financial Model that optimizes loan interest rates to maximize profit while strictly adhering to risk and regulatory guardrails.**

---

## Business Value
Banks typically set interest rates using static "Rate Cards" (lookup tables). This leaves money on the table:
1.  **Low-Risk/Price-Sensitive** borrowers leave for competitors (Churn).
2.  **Inelastic** borrowers are under-charged (Lost Yield).

**ALPE** solves this by using a **Dual-Model Approach**:
* **Brain 1 (Risk):** Calculates the probability of default (XGBoost).
* **Brain 2 (Elasticity):** Calculates the probability of acceptance (Segmented Logistic Regression).
* **Brain 3 (Optimizer):** Finds the exact interest rate that maximizes *Expected Profit* ($E[P]$).

**Key Capabilities:**
*  **Yield Uplift:** +50bps average increase on inelastic segments.
*  **Risk Shield:** Automatically rejects applicants with Probability of Default (PD) > 20%.
*  **Stress Testing:** Simulates economic shocks (Recession/Rate Hikes) to ensure portfolio resilience.
*  **Compliance:** Automated adherence to regulatory caps and Fair Lending rules.

---

## Tech Stack
* **Core:** Python 3.10, Pandas, NumPy
* **Machine Learning:** XGBoost (Risk), Statsmodels (Elasticity/Econometrics)
* **Optimization:** Numerical Grid Search with Constraint Handling
* **App & Interface:** Streamlit (Dashboard), Argparse (CLI)
* **Deployment:** Docker (Containerization)
* **Monitoring:** Population Stability Index (PSI) for Data Drift

---

## Architecture

### 1. The Risk Model (XGBoost)
Predicts `P(Default)`.
* **Inputs:** FICO, Income, DTI, Utilization, Inquiries, **Loan Term**.
* **Performance:** AUC ~0.72 (Stable across time).

### 2. The Elasticity Model (Econometrics)
Predicts `P(Accept | Rate)`.
* **Methodology:** Segmented Logistic Regression (Price Sensitivity Curves).
* **Insight:** Subprime borrowers are significantly more sensitive to rate hikes than Prime borrowers.

### 3. The Optimization Engine
Calculates Expected Profit and enforces the following **Active Policy Limits**:
* **Global Rate Cap:** 35% (Regulatory Hard Limit).
* **Prime Rate Cap:** 20% (Brand Protection for Low-Risk Borrowers).
* **Risk Appetite:** Reject if PD > 20%.
* **Profit Floor:** Reject if Expected Profit < $50.

---

## How to Run

### Option A: Docker (Recommended)
Run the full dashboard in an isolated container.

```bash
# 1. Build the image
docker build -t pricing-engine .

# 2. Run the container
docker run -p 8501:8501 pricing-engine

```

Access the dashboard at `http://localhost:8501`.

### Option B: Local Installation

```
git clone https://github.com/m-prth/adaptive-pricing-engine.git
cd adaptive-pricing-engine
pip install -r requirements.txt
```

#### 1. Run the Dashboard

Simulate loan offers and stress tests in real-time.

```
streamlit run src/dashboard.py
```

#### 2. Run via Command Line (CLI)

Generate a single loan offer for integration testing.

```
python src/pricing_service.py --income 75000 --fico 720 --amount 15000 --term 36
```

#### 3. Run the Backtest

Validate performance on historical data.

```bash
jupyter notebook notebooks/12_backtesting.ipynb

```

## Project Structure

```text
├── models/                 # Pre-trained ML models (Pickle)
├── src/
│   ├── pricing_engine.py   # The Core Logic Class (Optimization & Policy)
│   ├── pricing_service.py  # CLI Entry Point for Single Predictions
│   ├── dashboard.py        # Streamlit Front-End
│   ├── monitor_util.py     # Drift Detection (PSI)
│   └── synthetic_data_generator.py
├── notebooks/              # Research, Training & Validation
├── Dockerfile              # Container Configuration
└── monitoring_plan.md      # Governance Documentation

```

## License

MIT License - Free for educational use.

