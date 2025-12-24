# 🏦 Adaptive Loan Pricing Engine (ALPE)

> **A "Self-Driving" Financial Model that optimizes loan interest rates to maximize profit while strictly adhering to risk and regulatory guardrails.**



---

## 🚀 Business Value
Banks typically set interest rates using static "Rate Cards" (lookup tables). This leaves money on the table:
1.  **Low-Risk/Price-Sensitive** borrowers leave for competitors (Churn).
2.  **Inelastic** borrowers are under-charged (Lost Yield).

**ALPE** solves this by using a **Dual-Model Approach**:
* **Brain 1 (Risk):** Calculates the probability of default (XGBoost).
* **Brain 2 (Elasticity):** Calculates the probability of acceptance (Logistic Regression).
* **Brain 3 (Optimizer):** Finds the exact interest rate that maximizes *Expected Profit* ($E[P]$).

**Impact (Backtest Results):**
* 💰 **Yield Uplift:** +50bps average increase on inelastic segments.
* 🛡️ **Risk Shield:** Avoided ~12% of defaults by pricing risk correctly.
* ⚖️ **Compliance:** Automated adherence to 36% APR caps and Fair Lending rules.

---

## 🛠️ Tech Stack
* **Core:** Python, Pandas, NumPy
* **Machine Learning:** XGBoost (Risk), Statsmodels (Elasticity/Econometrics)
* **Optimization:** Numerical Grid Search with Constraint Handling
* **App:** Streamlit (Interactive Dashboard)

---

## 🧩 Architecture

### 1. The Risk Model (XGBoost)
Predicts `P(Default)`.
* **Features:** FICO, DTI, Income, Utilization, Inquiries.
* **Performance:** AUC 0.72 (Stable across time).

### 2. The Elasticity Model (Econometrics)
Predicts `P(Accept | Rate)`.
* **Methodology:** Segmented Logistic Regression (Price Sensitivity Curves).
* **Insight:** Subprime borrowers are 3x more sensitive to rate hikes than Prime borrowers.

### 3. The Optimization Engine
$$
\mathbb{E}[\text{Profit}_i(r)] = P(\text{Accept}_i(r)) \times \Big[ (1 - PD_i) \cdot \text{Income}(r) - PD_i \cdot \text{Loss} \Big]
$$
*Subject to:*
* Max Rate <= 36% (Regulatory)
* Max Rate <= 18% (For Prime Segment Strategy)
* PD <= 20% (Risk Appetite)

---

## 💻 How to Run

### 1. Installation
```bash
git clone [https://github.com/yourusername/adaptive-pricing-engine.git](https://github.com/yourusername/adaptive-pricing-engine.git)
cd adaptive-pricing-engine
pip install -r requirements.txt