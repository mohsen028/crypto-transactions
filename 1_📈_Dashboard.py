import streamlit as st
import pandas as pd
from utils import initialize_transactions, get_all_transactions, format_currency

st.set_page_config(
    page_title="Crypto Tracker Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize data if not already done
initialize_transactions()

# Load transactions
transactions = get_all_transactions()

# --- Page Title ---
st.title("📈 Dashboard")
st.markdown("Overview of your crypto transactions.")

# --- Key Metrics (StatsCard) ---
st.markdown("### Key Statistics")

if transactions.empty:
    st.warning("No transactions recorded yet. Add a new transaction to see statistics.")
else:
    buy_transactions = transactions[transactions['transaction_type'].str.contains('buy')]
    sell_transactions = transactions[transactions['transaction_type'] == 'sell']

    total_transactions = len(transactions)
    buy_count = len(buy_transactions)
    sell_count = len(sell_transactions)
    
    # In a real scenario, fees would be in a consistent currency (e.g., USDT)
    # Here we just sum them up as a demo.
    total_fees = transactions['fee'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Transactions", value=total_transactions)
    with col2:
        st.metric(label="Buy Transactions", value=buy_count)
    with col3:
        st.metric(label="Sell Transactions", value=sell_count)
    with col4:
        st.metric(label="Total Fees (Mixed Currency)", value=f"{total_fees:,.2f}")

st.markdown("---")

# --- Charts and Recent Transactions ---
col1, col2 = st.columns([2, 1]) # Make chart column wider

with col1:
    st.subheader("📊 Transaction Activity (Last 7 Days)")
    if transactions.empty:
        st.info("Chart will be displayed here once you have transactions.")
    else:
        # Prepare data for the chart (TransactionChart)
        transactions['date_only'] = transactions['transaction_date'].dt.date
        
        # Get the last 7 days of data
        today = pd.to_datetime('today').date()
        seven_days_ago = today - pd.to_timedelta('6D')
        
        chart_data = transactions[transactions['date_only'] >= seven_days_ago]
        
        if chart_data.empty:
