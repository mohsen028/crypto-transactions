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
            st.info("No transactions in the last 7 days.")
        else:
            # Group by date and transaction type
            daily_counts = chart_data.groupby(['date_only', 'transaction_type']).size().unstack(fill_value=0)
            
            # Create 'buy' and 'other' categories
            daily_counts['buy'] = daily_counts.get('buy_usdt_with_toman', 0) + daily_counts.get('buy_crypto_with_usdt', 0)
            daily_counts['other'] = daily_counts.get('transfer', 0) + daily_counts.get('swap', 0)
            
            # Ensure all required columns exist
            for col in ['buy', 'sell', 'other']:
                if col not in daily_counts.columns:
                    daily_counts[col] = 0
                    
            # Keep only relevant columns and re-index for all 7 days
            final_chart_data = daily_counts[['buy', 'sell', 'other']]
            all_days = pd.date_range(start=seven_days_ago, end=today, freq='D').date
            final_chart_data = final_chart_data.reindex(all_days, fill_value=0)
            final_chart_data.index.name = "date"
            
            st.bar_chart(final_chart_data, color=["#10b981", "#f59e0b", "#8b5cf6"]) # Green, Orange, Purple

with col2:
    st.subheader("🕒 Recent Transactions")
    if transactions.empty:
        st.info("Your latest transactions will appear here.")
    else:
        # Display recent transactions (RecentTransactions)
        recent = transactions.head(5)
        for _, row in recent.iterrows():
            with st.container(border=True):
                col_type, col_date = st.columns([3, 1])
                
                # Transaction Type Badge
                type_label = {
                    "buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto",
                    "sell": "Sell", "transfer": "Transfer", "swap": "Swap"
                }.get(row['transaction_type'], 'N/A')
                col_type.markdown(f"**{type_label}**")
                
                # Date
                col_date.markdown(f"<p style='text-align: right; color: grey;'>{row['transaction_date'].strftime('%b %d')}</p>", unsafe_allow_html=True)
                
                # Person and currency flow
                st.text(f"{row['person_name'].capitalize()} • {row['input_currency']} → {row['output_currency']}")
                
                # Amounts
                in_amount = format_currency(row['input_amount'], row['input_currency'])
                out_amount = format_currency(row['output_amount'], row['output_currency'])
                st.markdown(f"**{in_amount} → {out_amount}**")

```5.  روی دکمه **Commit new file** کلیک کنید.
