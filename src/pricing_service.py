import sys
sys.path.append('..')  # Ensure src/ is in the path

import argparse
import json
import sys
import pandas as pd
from src.pricing_engine import LoanPricingEngine


def initialize_engine():
    """
    Loads the heavy models only once at startup.
    """
    print("⏳ Initializing Adaptive Pricing Engine...")
    try:
        engine = LoanPricingEngine(
            risk_model_path='../models/risk_model_xgb.pkl',
            elasticity_model_path='../models/elasticity_model_logit.pkl',
            cost_of_funds=0.04
        )
        print("✅ Engine Loaded Successfully.")
        return engine
    except FileNotFoundError as e:
        print(f"❌ CRITICAL ERROR: Model files not found. {e}")
        sys.exit(1)


def parse_arguments():
    """
    Allows the script to be called from the Command Line (CLI).
    """
    parser = argparse.ArgumentParser(description='Adaptive Loan Pricing Engine V1.0')
    
    # Required Arguments
    parser.add_argument('--income', type=float, required=True, help='Annual Income ($)')
    parser.add_argument('--fico', type=float, required=True, help='FICO Score (300-850)')
    parser.add_argument('--amount', type=float, required=True, help='Loan Amount Requested ($)')
    parser.add_argument('--term', type=int, choices=[36, 60], required=True, help='Loan Term (Months)')
    
    # Optional Arguments (with Defaults)
    parser.add_argument('--dti', type=float, default=0.25, help='Debt-to-Income Ratio (0.0-1.0)')
    parser.add_argument('--util', type=float, default=30.0, help='Credit Utilization (%)')
    parser.add_argument('--inquiries', type=int, default=0, help='Recent Inquiries (Last 6m)')
    
    return parser.parse_args()


def main():
    engine = initialize_engine()
    
    args = parse_arguments()

    applicant_data = {
        'risk_score_norm': (args.fico - 300) / 550.0,
        'annual_inc': args.income,
        'LoanOriginalAmount': args.amount,
        'dti': args.dti,
        'revol_util': args.util,
        'inq_last_6mths': args.inquiries,
        'total_acc': 15,
        'term_years': args.term / 12,
        'emp_length': 5,
        'home_ownership_RENT': 1,
        'purpose_debt_consolidation': 1
    }
    
    print("\n--- Processing Application ---")
    print(f"Applicant: FICO {args.fico} | Income ${args.income:,.0f} | Loan ${args.amount:,.0f}")
    
 
    result = engine.get_optimal_rate(applicant_data)
    

    response = {
        "decision": result['decision'],
        "offered_rate": round(result['optimal_rate'], 4),
        "offered_rate_display": f"{result['optimal_rate']:.2%}",
        "risk_segment": result['risk_segment'],
        "probability_of_default": f"{result['prob_default']:.2%}",
        "expected_profit": round(result['max_profit'], 2),
        "policy_notes": result['policy_notes']
    }
    
    print("\n--- 📤 Engine Decision ---")
    print(json.dumps(response, indent=4))
    
    
    if result['decision'] == 'APPROVE':
        sys.exit(0)
    else:
        sys.exit(1) 

if __name__ == "__main__":
    main()