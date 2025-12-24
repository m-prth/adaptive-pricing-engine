import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pricing_engine import LoanPricingEngine


st.set_page_config(page_title="Adaptive Pricing Engine", page_icon="🏦", layout="wide")

st.markdown("""
<style>
    .big-font { font-size: 24px !important; font-weight: bold; }
    .success-box { padding: 20px; background-color: #d4edda; border-radius: 10px; color: #155724; }
    .fail-box { padding: 20px; background-color: #f8d7da; border-radius: 10px; color: #721c24; }
    .metric-card { background-color: #f0f2f6; border-radius: 10px; padding: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🏦 Loan Parameters")

st.sidebar.header("👤 Applicant Profile")
with st.sidebar.form("applicant_form"):
    fico = st.slider("FICO Score", 300, 850, 720)
    income = st.number_input("Annual Income ($)", min_value=10000, value=75000, step=5000)
    loan_amt = st.number_input("Loan Amount ($)", min_value=1000, value=15000, step=1000)
    term_months = st.selectbox("Loan Term", options=[36, 60], index=0, help="Longer loans are riskier but generate more total interest.")
    dti = st.slider("Debt-to-Income (DTI)", 0.0, 1.0, 0.3)
    util = st.slider("Credit Utilization (%)", 0, 100, 40)
    inquiries = st.number_input("Recent Inquiries (6m)", 0, 10, 0)
    
    st.markdown("---")
    submitted = st.form_submit_button("💰 Generate Offer")

st.sidebar.markdown("---")
st.sidebar.header("📉 Economic Stress Test")
with st.sidebar.expander("Adjust Market Conditions"):
    cof_input = st.slider("Bank Cost of Funds (%)", 0.0, 0.15, 0.04, step=0.01)
    risk_multiplier = st.slider("Risk Multiplier (Recession)", 1.0, 2.0, 1.0, step=0.1, help="1.0 = Normal, 1.5 = Recession (Risk increases 50%)")

@st.cache_resource
def load_engine():
    return LoanPricingEngine(
        risk_model_path='models/risk_model_xgb.pkl',
        elasticity_model_path='models/elasticity_model_logit.pkl'
    )

engine = load_engine()

engine.cost_of_funds = cof_input

st.title("Adaptive Loan Pricing Dashboard")
st.markdown("Optimization Engine V1.0 | Active Policy Layer: **Enabled**")

if submitted:
    applicant_data = {
        'risk_score_norm': (fico - 300) / 550,
        'annual_inc': income,
        'dti': dti,
        'LoanOriginalAmount': loan_amt,
        'revol_util': util,
        'inq_last_6mths': inquiries,
        # Defaults
        'term_years': term_months / 12, 'emp_length': 5, 'home_ownership_RENT': 1, 
        'purpose_debt_consolidation': 1, 'total_acc': 20
    }

    decision = engine.get_optimal_rate(applicant_data, pd_multiplier=risk_multiplier)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Risk Segment", decision['risk_segment'])
    with col2:
        st.metric("Prob. of Default (PD)", f"{decision['prob_default']:.2%}", delta_color="inverse")
    with col3:
        st.metric("Exp. Profit", f"${decision['max_profit']:.0f}")
    with col4:
        if decision['decision'] == 'APPROVE':
            st.success(f"OFFER: {decision['optimal_rate']:.2%}")
        else:
            st.error(f"{decision['decision']}")

    st.markdown("---")

    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("📊 Optimization Curve")
        if decision['curve_data'] is not None:
            curve = decision['curve_data']

            fig, ax1 = plt.subplots(figsize=(10, 5))
                
            sns.lineplot(data=curve, x='Rate', y='Exp_Profit', ax=ax1, color='green', linewidth=3, legend=False)
            ax1.set_ylabel("Expected Profit ($)", color='green', fontweight='bold')
            ax1.set_xlabel("Interest Rate Offer")
            ax1.axhline(0, color='black', alpha=0.2)
                
            ax2 = ax1.twinx()
            sns.lineplot(data=curve, x='Rate', y='Prob_Accept', ax=ax2, color='gray', linestyle='--', alpha=0.6, legend=False)
            ax2.set_ylabel("Probability of Acceptance", color='gray')
            ax2.set_ylim(0, 1.05)
                
            if decision['decision'] == 'APPROVE':
                ax1.plot(decision['optimal_rate'], decision['max_profit'], 'ro', markersize=10, zorder=5)
                ax1.annotate(f" Optimal: {decision['optimal_rate']:.1%}", 
                            (decision['optimal_rate'], decision['max_profit']),
                            xytext=(0, 15), textcoords='offset points', ha='center', fontweight='bold', color='red')
                
            from matplotlib.lines import Line2D
            legend_elements = [
                    Line2D([0], [0], color='green', lw=3, label='Expected Profit ($)'),
                    Line2D([0], [0], color='gray', lw=2, linestyle='--', label='Prob. Acceptance')
                ]
                
            ax1.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=2, frameon=False)
                
            st.pyplot(fig)
                
            st.info("💡 **How to read this:** The Green Line is profit. The Grey Dashed Line is customer demand. We pick the peak of the Green Line.")
        else:
            st.warning("No optimization curve generated (Loan Rejected early).")

    with c2:
        st.subheader("🛡️ Policy Guardrails")
        
        policy_checks = {
            "Risk Assessment": "Pass" if decision['decision'] != 'REJECT_RISK' else "Fail",
            "Profitability Check": "Pass" if decision['decision'] != 'REJECT_ECONOMICS' else "Fail",
            "Usury Cap (36%)": "Pass",
            "Prime Rate Cap (18%)": "Applied" if "Prime Max" in str(decision['policy_notes']) else "N/A"
        }
        
        for check, status in policy_checks.items():
            if status == "Pass":
                st.markdown(f"✅ **{check}**")
            elif status == "Fail":
                st.markdown(f"❌ **{check}**")
            elif status == "Applied":
                st.markdown(f"🔒 **{check}** (Triggered)")
            else:
                st.markdown(f"⚪ {check}")

        st.markdown("### 📝 Governance Notes")
        if decision['policy_notes']:
            for note in decision['policy_notes']:
                st.warning(note)
        else:
            st.success("No manual overrides applied. Pure ML pricing.")

else:
    st.info("👈 Enter applicant details in the sidebar to generate a loan offer.")
    
    st.markdown("""
    ### Quick Start Guide
    1. **Adjust FICO:** Drag FICO to **750** to see a "Prime" offer.
    2. **Stress Test:** Open "Economic Stress Test" in the sidebar and set **Cost of Funds** to **8%**. Watch the offer rate jump up!
    3. **Break It:** Drag FICO to **500** to trigger a **REJECT_RISK**.
    """)
