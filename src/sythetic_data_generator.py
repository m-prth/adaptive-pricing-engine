import pandas as pd
import numpy as np


prosper = pd.read_csv("ProsperLoanData.csv")

funded_loans = prosper[prosper['LoanStatus'].isin(['Completed', 'Current', 'Paid'])].copy()


def generate_rates(actual_rate, lower=1.0, upper=1.0, step=0.25):
    """
    Generate rates around the actual funded rate.
    lower, upper: percentage points below/above actual rate
    step: increment in percentage points
    """
    return np.round(np.arange(actual_rate - lower, actual_rate + upper + 0.01, step), 2)


alpha = 2  # higher alpha = more rate-sensitive applicants

def acceptance_probability(synthetic_rate, actual_rate, alpha=2):
    """
    Compute probability of acceptance for synthetic rate
    using a sigmoid function.
    """
    return 1 / (1 + np.exp(alpha * (synthetic_rate - actual_rate)))


synthetic_rows = []

for idx, row in funded_loans.iterrows():
    actual_rate = row['InterestRate']
    rates = generate_rates(actual_rate)
    
    for r in rates:
        prob_accept = acceptance_probability(r, actual_rate, alpha)
        accepted = np.random.binomial(1, prob_accept)
        
        new_row = row.copy()
        new_row['OfferedRate'] = r
        new_row['Accepted'] = accepted
        synthetic_rows.append(new_row)

synthetic_df = pd.DataFrame(synthetic_rows)


synthetic_df.to_csv("Prosper_Synthetic_Elasticity.csv", index=False)

print("Synthetic dataset created with shape:", synthetic_df.shape)
