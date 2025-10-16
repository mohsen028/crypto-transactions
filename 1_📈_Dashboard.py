import streamlit as st
import pandas as pd
import time
from utils import initialize_state, get_all_transactions, get_full_portfolio_analysis, update_prices_in_state

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

# Initialize data and prices state
initialize_state()
transactions = get_all_transactions()

# --- Header ---
st.title("📈 Crypto Portfolio Dashboard")
st.markdown("An overview of your collective crypto investments.")

# --- Price Update Section ---
# Get all unique symbols from portfolio to update their prices
all_symbols = transactions['input_currency'].unique().tolist() + transactions['output_currency'].unique().tolist()
unique_symbols = list(set(s for s in all_symbols if s not in ['IRR', None]))

# Trigger price update automatically (if needed) or manually
update_prices_in_state(unique_symbols)
if st.button("🔄 Refresh Live Prices"):
    update_prices_in_state(unique_symbols, force_refresh=True)

# Display last update time
last_update = st.session_state.get('last_price_fetch', 0)
if last_update > 0:
    st.caption(f"Prices last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_update))}")

# --- Perform Analysis with available prices ---
prices = st.session_state.get('prices', {})
analysis_df = get_full_portfolio_analysis(transactions, prices)

# --- Top Level Metrics (StatsCards) ---
total_investment_usd = 0
if not analysis_df.empty:
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

# --- P/L Summary per Person ---
st.subheader("Profit & Loss Summary")
if analysis_df.empty or 'pnl_usd' not in analysis_df.columns:
    st.info("No portfolio data to analyze. Add some 'Buy Crypto' transactions.")
else:
    pnl_summary = analysis_df.groupby('person_name').agg(
        total_value=('current_value_usd', 'sum'),
        total_cost=('total_cost_of_current_holdings', 'sum')
    ).reset_index()
    
    pnl_summary['pnl_usd'] = pnl_summary['total_value'] - pnl_summary['total_cost']
    
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
