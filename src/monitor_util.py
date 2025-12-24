import numpy as np
import pandas as pd

def calculate_psi(expected, actual, buckettype='bins', buckets=10, axis=0):
    """
    Calculate the Population Stability Index (PSI) - The Industry Standard for Drift.
    
    Args:
        expected (array-like): The distribution from Training Data (Benchmark).
        actual (array-like): The distribution from Production Data (Current).
        buckets (int): Number of bins to split data into.
        
    Returns:
        psi_value (float): 
            < 0.1: No change (Safe)
            0.1 - 0.25: Slight change (Warning)
            > 0.25: Major shift (Action Required)
    """
    def scale_range(input, min, max):
        input += -(np.min(input))
        input /= np.max(input) / (max - min)
        input += min
        return input

    breakpoints = np.arange(0, buckets + 1) / (buckets) * 100

    if buckettype == 'bins':
        breakpoints = np.stack([np.percentile(expected, b) for b in breakpoints])


    expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)


    expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
    actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)


    psi_value = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))

    return psi_value

def check_drift(train_df, prod_df, features):
    """
    Runs PSI check on specific features.
    """
    alerts = []
    for feat in features:
        if feat in train_df.columns and feat in prod_df.columns:
            psi = calculate_psi(train_df[feat], prod_df[feat])
            status = "🟢 Safe"
            if psi > 0.1: status = "🟡 Warning"
            if psi > 0.25: status = "🔴 CRITICAL"
            
            alerts.append({
                'Feature': feat,
                'PSI': round(psi, 4),
                'Status': status
            })
    
    return pd.DataFrame(alerts)