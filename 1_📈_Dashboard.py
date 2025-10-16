import streamlit as st
import pandas as pd
from utils import initialize_transactions, get_all_transactions, get_full_portfolio_analysis

st.set_page_config(page_title="Crypto Dashboard", icon=":chart_with_upwards_trend:", layout="wide")

# Initialize and load data
initialize_transactions()
transactions = get_all_transactions()
analysis_df = get_full_portfolio_analysis(transactions)

# --- Header ---
st.title("📈 Crypto Portfolio Dashboard")
st.markdown("An overview of your collective crypto investments.")

# --- Top Level Metrics (StatsCards) ---
total_investment_usd = 0
if not analysis_df.empty:
    # Sum of what was spent on currently held assets
    total_investment_usd = analysis_df['total_cost_of_current_holdings'].sum()
    
total_market_value = analysis_df['current_value_usd'].sum() if not analysis_df.empty else 0
total_pnl = analysis_df['pnl_usd'].sum() if not analysis_df.empty else 0

col1, col2, col3 = st.columns(3)
col1.metric(label="Total Market Value", value=f"${total_market_value:,.2f}")
col2.metric(label="Total Investment (Cost Basis)", value=f"${total_investment_usd:,.2f}")
col3.metric(
    label="Total Floating P/L",
    value=f"${total_pnl:,.2f}",
    delta=f"{((total_pnl / total_investment_usd) * 100):.2f}%" if total_investment_usd > 0 else "0.00%"
)

st.markdown("---")

# --- NEW: P/L Summary per Person ---
st.subheader("Profit & Loss Summary")

if analysis_df.empty:
    st.info("No portfolio data to analyze. Add some 'Buy Crypto' transactions.")
else:
    # Group by person to get their total P/L
    pnl_summary = analysis_df.groupby('person_name').agg(
        total_value=('current_value_usd', 'sum'),
        total_cost=('total_cost_of_current_holdings', 'sum')
    ).reset_index()
    
    pnl_summary['pnl_usd'] = pnl_summary['total_value'] - pnl_summary['total_cost']
    
    # Determine number of columns based on number of people
    num_people = len(pnl_summary)
    if num_people > 0:
        cols = st.columns(num_people)
        for i, row in pnl_summary.iterrows():
            with cols[i]:
                delta_percent = (row['pnl_usd'] / row['total_cost']) * 100 if row['total_cost'] > 0 else 0
                st.metric(
                    label=f"{row['person_name'].capitalize()}'s Portfolio",
                    value=f"${row['total_value']:,.2f}",
                    delta=f"${row['pnl_usd']:,.2f} ({delta_percent:.2f}%)"
                )
