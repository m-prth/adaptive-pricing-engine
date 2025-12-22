import pandas as pd
import numpy as np
import joblib

class LoanPricingEngine:
    def __init__(self, risk_model_path, elasticity_model_path, cost_of_funds=0.04, lgd=0.6):
        """
        The Optimization Engine ("Brain 3").
        """
        self.risk_model = joblib.load(risk_model_path)
        self.elasticity_model = joblib.load(elasticity_model_path)
        self.cost_of_funds = cost_of_funds
        self.lgd = lgd
        
        # Governance: Hard Limits
        self.min_rate = 0.05  # Floor (5%)
        self.max_rate = 0.35  # Cap (35%)
        self.max_pd_threshold = 0.20 # Auto-reject if PD > 20%

    def _determine_segment(self, score):
        """Maps Risk Score to the segments used in training."""
        if score <= 0.4: return 'Subprime'
        if score <= 0.75: return 'NearPrime'
        return 'Prime'

    def get_optimal_rate(self, applicant_data, pd_multiplier=1.0):
        """
        Finds the profit-maximizing interest rate for a single applicant.
        """
        # -----------------------------------------------------------
        # STEP 1: PREDICT RISK (PD) - Brain 1
        # -----------------------------------------------------------
        risk_cols = self.risk_model.get_booster().feature_names
        
        # Safe input creation
        risk_input = pd.DataFrame([applicant_data])
        
        # 1. Fill missing columns with 0 (Standard Imputation)
        for col in risk_cols:
            if col not in risk_input.columns:
                risk_input[col] = 0
                
        # 2. 🛑 CRITICAL: Filter to ONLY the columns the model expects
        # This removes 'name', 'email', etc. so XGBoost doesn't crash
        risk_input = risk_input[risk_cols]
        
        pd_prob = self.risk_model.predict_proba(risk_input)[0][1]
        pd_prob = min(pd_prob * pd_multiplier, 1.0)  # Apply multiplier and cap at 1.0
        # Governance Check: Auto-Reject high risk
        if pd_prob > self.max_pd_threshold:
            return {
                'decision': 'REJECT_RISK',
                'optimal_rate': 0.0,
                'max_profit': -1.0,
                'prob_default': pd_prob,
                'risk_segment': 'High Risk',
                'curve_data': None
            }

        # -----------------------------------------------------------
        # STEP 2: GENERATE CANDIDATE GRID
        # -----------------------------------------------------------
        rate_grid = np.linspace(self.min_rate, self.max_rate, 61) # 0.5% steps
        loan_amt = applicant_data.get('LoanOriginalAmount', 15000)
        risk_score = applicant_data.get('risk_score_norm', 0.5)
        segment = self._determine_segment(risk_score)

        # -----------------------------------------------------------
        # STEP 3: SIMULATE ELASTICITY BATCH - Brain 2
        # -----------------------------------------------------------
        # Vectorized DataFrame construction
        elast_input = pd.DataFrame({
            'const': 1.0,
            'risk_score_norm': risk_score,
            'LoanOriginalAmount': loan_amt,
            'Rate_Subprime': 0.0,
            'Rate_NearPrime': 0.0,
            'Rate_Prime': 0.0
        }, index=range(len(rate_grid)))

        # Activate the correct segment column (One-Hot Logic)
        if segment == 'Subprime':
            elast_input['Rate_Subprime'] = rate_grid
        elif segment == 'NearPrime':
            elast_input['Rate_NearPrime'] = rate_grid
        else:
            elast_input['Rate_Prime'] = rate_grid
            
        # Predict Acceptance for ALL rates at once
        model_cols = ['const', 'risk_score_norm', 'Rate_Subprime', 'Rate_NearPrime', 'Rate_Prime', 'LoanOriginalAmount']
        accept_probs = self.elasticity_model.predict(elast_input[model_cols])

        # -----------------------------------------------------------
        # STEP 4: OPTIMIZE PROFIT
        # -----------------------------------------------------------
        # Profit = P(Accept) * [ (1-PD)*Income - PD*Loss ]
        
        profit_good = (rate_grid - self.cost_of_funds) * loan_amt
        loss_bad = self.lgd * loan_amt
        
        # Expected Margin = Weighted Average of Outcome
        expected_margin = ((1 - pd_prob) * profit_good) - (pd_prob * loss_bad)
        expected_profits = accept_probs * expected_margin
        
        # Create Result DataFrame
        results_df = pd.DataFrame({
            'Rate': rate_grid,
            'Prob_Accept': accept_probs,
            'Exp_Profit': expected_profits
        })

        # -----------------------------------------------------------
        # STEP 5: FINAL DECISION
        # -----------------------------------------------------------
        best_idx = results_df['Exp_Profit'].idxmax()
        best_offer = results_df.loc[best_idx]

        if best_offer['Exp_Profit'] < 0:
            decision = "REJECT_ECONOMICS" # Risk is fine, but price is too high for them to accept
        else:
            decision = "APPROVE"

        return {
            'optimal_rate': best_offer['Rate'],
            'max_profit': best_offer['Exp_Profit'],
            'decision': decision,
            'prob_default': pd_prob,
            'risk_segment': segment,
            'curve_data': results_df
        }