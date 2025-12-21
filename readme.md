# 🏦 Adaptive Loan Pricing Engine ("Project Dynamic")

### *A Dual-Model AI System for Real-Time Interest Rate Optimization*

**Status:** `Prototype Complete` | **Domain:** `FinTech / Credit Risk` | **Tech Stack:** `Python`, `XGBoost`, `Statsmodels`, `Scikit-Learn`

---

## 📖 Executive Summary

Traditional bank pricing is static riskier borrowers get higher rates based on rigid tiers. This approach fails to account for **Price Elasticity** (how likely a customer is to accept an offer).

**The Adaptive Loan Pricing Engine** solves this by combining two distinct AI models:

1. **Risk Engine (The Shield):** Predicts the probability of default (PD).
2. **Elasticity Engine (The Salesman):** Predicts the probability of acceptance based on price and market competition.

By merging these two signals, the system calculates the **Profit-Maximizing Interest Rate** for every single applicant, balancing Yield vs. Conversion vs. Risk.

---

## 🧠 The "Two-Brain" Architecture

This project moves beyond simple default prediction by introducing a second "Brain" for pricing.

### 🛡️ Brain 1: The Risk Model (Will they pay?)

* **Goal:** Estimate `P(Default)`.
* **Algorithm:** **XGBoost Classifier** with class weighting.
* **Data Source:** LendingClub (Post-origination performance).
* **Performance:**
    * **Recall (Defaulters):** 67% (Prioritizes catching bad loans).
    * **ROC-AUC:** ~0.72 (Strong rank-ordering capability).


* **Key Insight:** Uses `scale_pos_weight` to handle the heavy class imbalance (80% good / 20% bad).

### 🏷️ Brain 2: The Elasticity Model (Will they buy?)

* **Goal:** Estimate `P(Acceptance | Rate)`.
* **Algorithm:** **Segmented Logistic Regression** (White-box for compliance).
* **Data Source:** Prosper (Application data) + **Synthetic Rejection Generator**.
* **Innovation:**
    * **Synthetic Data Generation:** Fixed "Survival Bias" (where we only see accepted offers) by simulating rejected offers using a sigmoid decay function.
    * **Segmented Slopes:** Discovered that **Subprime** borrowers are *more* price-sensitive (slope: -5.56) due to affordability constraints compared to **Near-Prime** borrowers (slope: -4.14).



---

## 🏗️ Project Structure

The repository follows the **Cookiecutter Data Science** standard for production-grade ML projects.

```text
📂 Adaptive Loan Pricing Engine/
│
├── 📂 data/                           # (Ignored by Git)
│   ├── raw/                           # Original immutable data dumps
│   └── processed/                     # Cleaned Training/Testing tensors
│
├── 📂 docs/                           # Documentation
│   ├── business_requirements.docx     # The "Why" behind the code
│   └── data_dictionary.xlsx           # Feature definitions
│
├── 📂 models/                         # The Trained Brains
│   ├── risk_model_xgb.pkl             # Brain 1 (XGBoost)
│   └── elasticity_model_logit.pkl     # Brain 2 (Logistic Regression)
│
├── 📂 notebooks/                      # Experiments (Numbered sequence)
│   ├── 01_data_cleaning.ipynb         # Raw ingestion
│   ├── 02_eda_lending_club.ipynb      # Risk analysis & feature selection
│   ├── 03_prosper_data_eda.ipynb      # Elasticity analysis
│   ├── 04_feature_eng_lending_club.ipynb
│   ├── 05_feature_eng_prosper.ipynb
│   ├── 06_pd_model.ipynb              # Training the Risk Engine
│   └── 07_elasticity_model.ipynb      # Training the Pricing Engine
│
├── 📂 src/                            # Production Logic
│   ├── synthetic_data_generator.py    # Logic to fix survival bias
│   └── pricing_engine.py              # (Coming Soon) The final Optimizer function
│
└── requirements.txt                   # Dependency list

```

---

## ⚙️ How It Works (The Logic)

The system does not just predict; it **optimizes**. For every applicant, it runs a simulation:

1. **Input:** Applicant Data (Credit Score, Income, Loan Amount).
2. **Risk Check:** Brain 1 calculates `Expected Loss = Loan Amount * P(Default) * LGD`.
3. **Demand Check:** Brain 2 simulates `P(Accept)` for rates from 5% to 35%.
4. **Optimization:** It finds the specific interest rate  that maximizes:


*Visual from Notebook 07 showing how demand drops as rates rise.*

---

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* `pip` or `conda`

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/adaptive-pricing-engine.git
cd adaptive-pricing-engine

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Download Data:**
* Place `accepted_2007_to_2018Q4.csv` (LendingClub) and `prosperLoanData.csv` (Prosper) into `data/raw/`.



### Running the Pipeline

Follow the numbered notebooks to reproduce the results:

1. **`01_data_cleaning.ipynb`**: Prepares raw CSVs.
2. **`04_feature_eng...ipynb`**: Creates features like `relationship_depth` and `clv_segment`.
3. **`06_pd_model.ipynb`**: Trains the Risk Model.
4. **`07_elasticity_model.ipynb`**: Trains the Pricing Model and visualizes demand curves.

---

## 📊 Key Results

### Risk Model Performance

* **Confusion Matrix:** Successfully captured **67%** of actual defaults.


* **Trade-off:** Accepted lower precision (32%) to ensure high recall, prioritizing bank safety over aggressive lending.

### Elasticity Insights

* **The "Affordability Cliff":** Subprime borrowers showed the steepest demand drop-off (-5.56 coeff), proving they are price-sensitive due to DTI constraints, not just competitive shopping.


* **The "Sticky" Middle:** Near-Prime borrowers were the least sensitive (-4.14 coeff), representing the "Sweet Spot" for margin expansion.

---

## 🔮 Future Roadmap

* **Deployment:** Wrap `src/pricing_engine.py` in a **FastAPI** service.
* **Dashboard:** Build a **Streamlit** app for Loan Officers to simulate rate changes.
* **A/B Testing:** Design a framework to test the model against static pricing in a sandbox environment.

---

**Author:** Parth Mistry
**License:** MIT
