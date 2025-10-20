import streamlit as st
import pandas as pd
import time
from utils import initialize_state, get_all_transactions, update_prices_in_state, generate_financial_analysis, TRANSACTION_TYPE_LABELS

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
initialize_state()
transactions = get_all_transactions()
st.title("Crypto Financial Dashboard")

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
portfolio_df, toman_stats_df, realized_pnl_df, fee_summary_df = generate_financial_analysis(transactions, prices)

tab1, tab2, tab3, tab4 = st.tabs(["Floating P/L", "Realized P/L", "Toman Exchange", "Fee Analysis"])

with tab1:
    st.subheader("Current Portfolio & Floating Profit/Loss")
    if portfolio_df.empty: st.info("No current holdings to analyze.")
    else:
        pnl_summary = portfolio_df.groupby('person_name').agg(total_value=('current_value_usd', 'sum'), total_cost=('total_cost_of_holdings', 'sum')).reset_index()
        pnl_summary['floating_pnl'] = pnl_summary['total_value'] - pnl_summary['total_cost']
        for _, row in pnl_summary.iterrows():
            with st.container(border=True):
                st.markdown(f"#### {row['person_name'].capitalize()}")
                delta_percent = (row['floating_pnl'] / row['total_cost']) * 100 if row['total_cost'] > 0 else 0
                c1,c2,c3 = st.columns(3); c1.metric("Market Value", f"${row['total_value']:,.2f}"); c2.metric("Total Cost", f"${row['total_cost']:,.2f}"); c3.metric("Floating P/L", f"${row['floating_pnl']:,.2f}", f"{delta_percent:.2f}%")

with tab2:
    st.subheader("Realized Profit/Loss from Sales & Swaps")
    if realized_pnl_df.empty: st.info("No sales or swaps have been recorded yet.")
    else: st.dataframe(realized_pnl_df, column_config={"person_name": "Person", "realized_pnl": st.column_config.NumberColumn("Net Realized P/L (USD)", format="$%.2f")}, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Toman-to-USDT Exchange Statistics")
    if toman_stats_df.empty: st.info("No Toman-to-USDT transactions recorded.")
    else: st.dataframe(toman_stats_df, column_config={"person_name": "Person", "total_toman_paid": st.column_config.NumberColumn("Total Toman Paid", format="%,.0f Toman"), "total_usdt_received": st.column_config.NumberColumn("Total USDT Received", format="%.2f USDT"), "avg_usdt_cost": st.column_config.NumberColumn("Avg. Cost per USDT", format="%,.0f Toman")}, hide_index=True, use_container_width=True)

with tab4:
    st.subheader("Comprehensive Fee Breakdown (in USD)")
    if fee_summary_df.empty:
        st.info("No fees have been recorded.")
    else:
        total_fees_per_person = fee_summary_df.groupby('person_name')['fee'].sum().reset_index().rename(columns={'fee': 'total_fee'})
        st.markdown("#### Total Fees Per Person")
        st.dataframe(total_fees_per_person, column_config={"person_name": "Person", "total_fee": st.column_config.NumberColumn("Total Fees Paid (USD)", format="$%.2f")}, hide_index=True, use_container_width=True)
        with st.expander("See detailed breakdown"):
            display_fees = fee_summary_df.copy()
            display_fees['transaction_type'] = display_fees['transaction_type'].map(TRANSACTION_TYPE_LABELS).fillna(display_fees['transaction_type'])
            st.dataframe(display_fees, column_config={"person_name": "Person", "transaction_type": "Transaction Type", "fee": st.column_config.NumberColumn("Fee (USD)", format="$%.2f")}, hide_index=True, use_container_width=True)
