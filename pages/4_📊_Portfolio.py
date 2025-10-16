import streamlit as st
import pandas as pd
import time
from utils import initialize_state, get_all_transactions, get_full_portfolio_analysis, update_prices_in_state

st.set_page_config(page_title="Detailed Portfolio", layout="wide")

# Initialize state if not already done
initialize_state()
transactions = get_all_transactions()

st.title("📊 Detailed Portfolio View")
st.markdown("A detailed breakdown of assets, costs, and current market value for everyone.")

if transactions.empty:
    st.warning("No transactions recorded yet. Add a new transaction to see data.")
    st.stop()
    
# --- Price Update Section (Consistent with Dashboard) ---
all_symbols = transactions['input_currency'].unique().tolist() + transactions['output_currency'].unique().tolist()
unique_symbols = list(set(s for s in all_symbols if s not in ['IRR', None]))

update_prices_in_state(unique_symbols)
if st.button("🔄 Refresh Live Prices"):
    update_prices_in_state(unique_symbols, force_refresh=True)

last_update = st.session_state.get('last_price_fetch', 0)
if last_update > 0:
    st.caption(f"Prices last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_update))}")
    
st.caption("Price data provided by CoinGecko. There may be slight differences from exchange prices.")

# --- Perform Analysis with available prices ---
prices = st.session_state.get('prices', {})
analysis_df = get_full_portfolio_analysis(transactions, prices)

if analysis_df.empty:
    st.info("No assets with a positive balance to analyze.")
    st.stop()

people = analysis_df['person_name'].unique()
for person in people:
    with st.container(border=True):
        st.markdown(f"### {person.capitalize()}'s Portfolio")
        person_df = analysis_df[analysis_df['person_name'] == person].copy()
        person_crypto_df = person_df[person_df['currency'] != 'IRR']
        
        st.dataframe(
            person_crypto_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "currency": "Asset",
                "amount": st.column_config.NumberColumn("Balance", format="%.6f"),
                "avg_buy_price": st.column_config.NumberColumn("Avg. Buy Price", format="$%.2f"),
                "current_price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                "current_value_usd": st.column_config.NumberColumn("Market Value", format="$%.2f"),
                "pnl_usd": st.column_config.NumberColumn("Floating P/L", format="$%.2f"),
            },
            column_order=("currency", "amount", "current_value_usd", "pnl_usd", "avg_buy_price", "current_price")
        )
