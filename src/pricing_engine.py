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
        
        # ---------------------------------------------------------
        # Governance Policy Configuration 
        # ---------------------------------------------------------
        self.policy_config = {
            'GLOBAL_MIN_RATE': 0.05,   # 5%
            'GLOBAL_MAX_RATE': 0.35,   # 35%
            'MAX_PD_THRESHOLD': 0.20,  # HARD REJECT if PD > 20%
            'PRIME_MAX_RATE': 0.20,    # 20% max for Prime
            'MIN_PROFIT_MARGIN': 50   # 50$ minimum profit margin
        }

    def _determine_segment(self, score):
        """Maps Risk Score to the segments used in training."""
        if score <= 0.4: return 'Subprime'
        if score <= 0.75: return 'NearPrime'
        return 'Prime'
    
    def _apply_governance(self, proposed_rate, pd, segment, expected_profit):
        """
        The 'Compliance Officer' Function
        Reviews the ML's proposed rate and applies hard rules.
        """
        final_decision = 'APPROVE'
        final_rate = proposed_rate
        notes = []

        # Rule 1: Hard PD Cutoff
        if pd > self.policy_config['MAX_PD_THRESHOLD']:
            return 'REJECT_RISK', 0.0, ['PD exceeds maximum threshold']
        
        # Rule 2: Global Rate Cap
        if final_rate > self.policy_config['GLOBAL_MAX_RATE']:
            final_rate = self.policy_config['GLOBAL_MAX_RATE']
            notes.append('Capped to Global Max (36%)')

        # Rule 3: Segment-Specific Caps
        if segment == 'Prime' and final_rate > self.policy_config['PRIME_MAX_RATE']:
            final_rate = self.policy_config['PRIME_MAX_RATE']
            notes.append(f"Capped at Prime Max ({self.policy_config['PRIME_MAX_RATE']:.0%})")

        # Rule 4: Minimum Profit Margin
        if expected_profit < self.policy_config['MIN_PROFIT_MARGIN']:
            return 'REJECT_ECONOMICS', 0.0, ['Expected profit below minimum margin']
        
        return final_decision, final_rate, notes

    def get_optimal_rate(self, applicant_data, pd_multiplier=1.0):
        """
        Finds the profit-maximizing interest rate for a single applicant.
        """
        # -----------------------------------------------------------
        # STEP 1: PREDICT RISK (PD) - Brain 1
        # -----------------------------------------------------------
        risk_cols = self.risk_model.get_booster().feature_names
        risk_input = pd.DataFrame([applicant_data])
        for col in risk_cols:
            if col not in risk_input.columns:
                risk_input[col] = 0
        risk_input = risk_input[risk_cols]
        
        pd_prob = self.risk_model.predict_proba(risk_input)[0][1]
        pd_prob = min(pd_prob * pd_multiplier, 1.0)  
        if pd_prob > self.policy_config['MAX_PD_THRESHOLD']:
            return {
                'decision': 'REJECT_RISK',
                'optimal_rate': 0.0,
                'max_profit': 0.0,
                'prob_default': pd_prob,
                'risk_segment': 'High Risk',
                'curve_data': None,
                'policy_notes': ["Pre-optimization PD Check"]
            }

        rate_grid = np.linspace(self.policy_config['GLOBAL_MIN_RATE'], self.policy_config['GLOBAL_MAX_RATE'], 61) # 0.5% steps
        loan_amt = applicant_data.get('LoanOriginalAmount', 15000)
        risk_score = applicant_data.get('risk_score_norm', 0.5)
        segment = self._determine_segment(risk_score)

        elast_input = pd.DataFrame({
            'const': 1.0,
            'risk_score_norm': risk_score,
            'LoanOriginalAmount': loan_amt,
            'Rate_Subprime': 0.0,
            'Rate_NearPrime': 0.0,
            'Rate_Prime': 0.0
        }, index=range(len(rate_grid)))

        if segment == 'Subprime':
            elast_input['Rate_Subprime'] = rate_grid
        elif segment == 'NearPrime':
            elast_input['Rate_NearPrime'] = rate_grid
        else:
            elast_input['Rate_Prime'] = rate_grid
            

        model_cols = ['const', 'risk_score_norm', 'Rate_Subprime', 'Rate_NearPrime', 'Rate_Prime', 'LoanOriginalAmount']
        accept_probs = self.elasticity_model.predict(elast_input[model_cols])

        # Profit Calculation
        # Profit = P(Accept) * [ (1-PD)*Income - PD*Loss ]
        
        profit_good = (rate_grid - self.cost_of_funds) * loan_amt
        loss_bad = self.lgd * loan_amt
        expected_margin = ((1 - pd_prob) * profit_good) - (pd_prob * loss_bad)
        expected_profits = accept_probs * expected_margin

        results_df = pd.DataFrame({
            'Rate': rate_grid,
            'Prob_Accept': accept_probs,
            'Exp_Profit': expected_profits
        })

        best_idx = results_df['Exp_Profit'].idxmax()
        raw_optimal_rate = results_df.loc[best_idx, 'Rate']
        max_profit = results_df.loc[best_idx, 'Exp_Profit']


        decision, final_rate, notes = self._apply_governance(raw_optimal_rate, pd_prob, segment, max_profit)

      
        return {
            'optimal_rate': final_rate,
            'max_profit': max_profit,
            'decision': decision,
            'prob_default': pd_prob,
            'risk_segment': segment,
            'curve_data': results_df,
            'policy_notes': notes
        }