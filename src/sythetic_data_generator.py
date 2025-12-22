import pandas as pd
import numpy as np
import tqdm  

try:
    prosper = pd.read_csv("data/prosperLoanData.csv")
except FileNotFoundError:
    prosper = pd.read_csv("ProsperLoanData.csv")

funded_loans = prosper[prosper['LoanStatus'].isin(['Completed', 'Current', 'Paid'])].copy()

def generate_rates():
    """Generates a fixed grid of interest rates from 5% to 40%."""
    return np.linspace(0.05, 0.40, 15)

def acceptance_probability(offered_rate, actual_rate, alpha=30):
    """Calculates probability of acceptance with strict price sensitivity."""
    if offered_rate <= actual_rate:
        return min(0.99, 0.95 + np.random.normal(0, 0.01))
    
    diff = offered_rate - actual_rate
    prob = 1.0 / (1.0 + np.exp(alpha * diff))
    return prob

print(f"Generating synthetic data for {len(funded_loans)} loans...")

synthetic_rows = []
iter_data = funded_loans


for idx, row in tqdm.tqdm(iter_data.iterrows(), total=iter_data.shape[0], desc="Simulating Loans"):
    actual_rate = row.get('BorrowerRate', row.get('InterestRate', 0.15))
    
    rates = generate_rates()
    
    for r in rates:
        prob_accept = acceptance_probability(r, actual_rate, alpha=30)
        accepted = np.random.binomial(1, prob_accept)
        
        new_row = row.copy()
        new_row['OfferedRate'] = r
        new_row['Accepted'] = accepted
        new_row['True_Prob_Accept'] = prob_accept 
        
        synthetic_rows.append(new_row)


synthetic_df = pd.DataFrame(synthetic_rows)
output_path = "data/Prosper_Synthetic_Elasticity.csv" 

synthetic_df.to_csv(output_path, index=False)

print(f"✅ Synthetic dataset created! Shape: {synthetic_df.shape}")
print(f"   Saved to: {output_path}")

print("\n--- Calibration Check ---")
print("Avg Acceptance at 5% Rate: ", synthetic_df[synthetic_df['OfferedRate'] <= 0.055]['Accepted'].mean())
print("Avg Acceptance at 35% Rate:", synthetic_df[synthetic_df['OfferedRate'] >= 0.35]['Accepted'].mean())
print("(Target: >90% at low rates, <10% at high rates)")