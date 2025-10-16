import streamlit as st
import pandas as pd
import time
from utils import initialize_state, get_all_transactions, update_prices_in_state, generate_financial_analysis

st.set_page_config(page_title="Detailed Portfolio", layout="wide")

def color_pnl(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    color = 'red' if val < 0 else '#28a745' if val > 0 else 'gray'
    return f'color: {color}'

initialize_state()
transactions = get_all_transactions()
st.title("📊 Detailed Portfolio Analysis")
st.markdown("A deep-dive into each person's holdings, costs, and performance.")

if transactions.empty:
    st.warning("No transactions recorded yet. Add a new transaction to see data.")
    st.stop()
    
# --- FIX: Handle empty transactions DataFrame ---
unique_symbols = []
if not transactions.empty:
    all_symbols = pd.concat([transactions['input_currency'], transactions['output_currency']]).dropna().unique()
    unique_symbols = [s for s in all_symbols if s != 'IRR']

update_prices_in_state(unique_symbols)
if st.button("🔄 Refresh Live Prices"): update_prices_in_state(unique_symbols, force_refresh=True)

# ... بقیه کد بدون تغییر باقی می‌ماند
last_update = st.session_state.get('last_price_fetch', 0)
if last_update > 0: st.caption(f"Prices last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_update))}")
st.caption("Price data provided by CoinGecko.")
st.markdown("---")

prices = st.session_state.get('prices', {})
portfolio_df, _, _, _ = generate_financial_analysis(transactions, prices)

if portfolio_df.empty or 'floating_pnl_usd' not in portfolio_df.columns:
    st.info("No current holdings with cost basis to analyze.")
    st.stop()

people = portfolio_df['person_name'].unique()
for person in people:
    with st.container(border=True):
        st.markdown(f"### {person.capitalize()}'s Portfolio")
        person_df = portfolio_df[portfolio_df['person_name'] == person].copy()
        person_df['floating_pnl_percent'] = (person_df['floating_pnl_usd'] / person_df['total_cost_of_holdings'].replace(0, pd.NA)) * 100
        styled_df = person_df.style.applymap(color_pnl, subset=['floating_pnl_usd', 'floating_pnl_percent'])
        st.dataframe(styled_df, hide_index=True, use_container_width=True,
            column_config={
                "currency": "Asset", "amount": st.column_config.NumberColumn("Balance", format="%.8f"),
                "avg_buy_price": st.column_config.NumberColumn("Avg. Cost Price (USD)", help="Average price paid per unit, including fees.", format="$%.2f"),
                "current_price": st.column_config.NumberColumn("Current Price (USD)", format="$%.2f"),
                "current_value_usd": st.column_config.NumberColumn("Market Value (USD)", format="$%.2f"),
                "floating_pnl_usd": st.column_config.NumberColumn("Floating P/L (USD)", help="Unrealized profit or loss based on current market price.", format="$%.2f"),
                "floating_pnl_percent": st.column_config.NumberColumn("Floating P/L (%)", format="%.2f%%"),
                "person_name": None, "total_cost_of_holdings": None,
            },
            column_order=("currency", "amount", "current_value_usd", "floating_pnl_usd", "floating_pnl_percent", "avg_buy_price", "current_price")
        )
