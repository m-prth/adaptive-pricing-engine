### Documentation: Synthetic Data Generation Logic Update

**Date:** December 21, 2025
**Module:** `src/synthetic_data_generator.py`
**Objective:** Correct the "Optimization Floor" anomaly where the engine defaulted to the maximum rate (35%).

---

### **1. The Problem: The "Inelasticity Trap"**

During the validation of the Pricing Engine (Notebook 08), we observed that the optimizer consistently recommended the **maximum possible interest rate (35%)** for Prime borrowers, which is economically unrealistic.

#### **Diagnosis**

* **Symptom:** The Profit Curve was monotonically increasing, meaning the model calculated that profit *always* increased as rates went up, without a penalty for rejection.
* **Root Cause:** The Elasticity Model (Brain 2) was trained on synthetic data that was too "optimistic." The diagnostics showed it believed **~50% of Prime borrowers would accept a 35% interest rate**.
* **The Math:** If  at , the Expected Profit is massive. The penalty for high prices (rejection) was not severe enough to outweigh the margin gain.

### **2. The Solution: "High-Sensitivity" Synthetic Data**

We rewrote the data generation logic to strictly enforce the **Law of Demand**: *As price increases, demand must fall—and eventually hit zero.*

#### **Key Changes Implemented**

1. **Expanded Rate Spectrum (`generate_rates`)**
* **Before:** Tested rates only within  of the actual historical rate. The model never "saw" a rejection at 35%.
* **After:** Forces the model to see the entire grid from **5% to 40%**. This ensures the model learns the behavior at the extremes (Concept Learning).


2. **Increased Price Sensitivity (`alpha` parameter)**
* **Before:** `alpha ≈ 5-10`. The demand curve was a gentle slope.
* **After:** `alpha = 30`. This creates a steep "Demand Cliff." A rate increase of 5% above the market rate now slashes acceptance probability to .


3. **Asymmetric Logic**
* Added a rule: If `Offered Rate <= Actual Rate`, then . This anchors the model to reality—borrowers rarely reject a better deal than the one they actually signed.



### **3. The Result: "Economic Reality"**

After regenerating the data (Output verification), the calibration is now economically sound:

* **P(Accept) at 5% Rate:** **85.69%** (High conversion for cheap loans)
* **P(Accept) at 35% Rate:** **0.62%** (Near-zero conversion for expensive loans)

#### **Impact on Optimization**

* **Old Behavior:** Offer 35%  Profit $2,000  **Winner** (Incorrect).
* **New Behavior:** Offer 35%  Profit $2,000  0.6% prob = $12  **Loser**.
* **New Winner:** The optimizer will now hunt for the "Sweet Spot" (likely 8-12% for Prime), where probability is healthy (~60-80%) and margin is decent.

### **4. Next Steps**

1. **Retrain Brain 2:** Run `07_elasticity_model.ipynb` using the newly generated `Prosper_Synthetic_Elasticity.csv`.
2. **Verify Optimizer:** Re-run `08_optimization_engine.ipynb`. You should now see **bell-shaped (convex)** profit curves instead of straight lines.