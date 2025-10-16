import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")
initialize_state()

# Initialize session state for delete confirmation
if 'confirming_delete_id' not in st.session_state:
    st.session_state.confirming_delete_id = None

transactions = get_all_transactions()
st.title("📜 Transaction History")

# --- CONFIRMATION DIALOG LOGIC ---
if st.session_state.confirming_delete_id:
    try:
        transaction_to_delete = transactions[transactions['id'] == st.session_state.confirming_delete_id].iloc[0]
        
        st.warning(f"**Are you sure you want to delete this transaction?** This action cannot be undone.")
        
        with st.container(border=True):
            type_label = TRANSACTION_TYPE_LABELS.get(transaction_to_delete['transaction_type'], 'N/A')
            st.markdown(f"**{type_label}** by **{transaction_to_delete['person_name'].capitalize()}**")
            st.markdown(f"**Input:** {transaction_to_delete.get('input_amount', 0):,.6f} {transaction_to_delete['input_currency']}")
            st.markdown(f"**Output:** {transaction_to_delete.get('output_amount', 0):,.6f} {transaction_to_delete['output_currency']}")
            st.caption(f"Date: {transaction_to_delete['transaction_date'].strftime('%Y-%m-%d')}")

        col1, col2, _ = st.columns([1, 1, 5])
        with col1:
            if st.button("✅ Yes, permanently delete", type="primary"):
                delete_transaction(st.session_state.confirming_delete_id)
                st.session_state.confirming_delete_id = None
                st.success("Transaction deleted.")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirming_delete_id = None
                st.rerun()
                
    except (IndexError, KeyError):
        # If transaction is not found (e.g., already deleted in another tab), exit confirmation mode
        st.error("Transaction not found.")
        st.session_state.confirming_delete_id = None
        st.rerun()

# --- MAIN TRANSACTION LIST ---
else:
    st.markdown("View, filter, and manage all your transactions.")

    if transactions.empty:
        st.warning("No transactions found. Add a new one from the 'New Transaction' page.")
        st.stop()
        
    portfolio_df, _, _, _ = generate_financial_analysis(transactions, st.session_state.get('prices', {}))
    
    for index, row in transactions.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                type_label = TRANSACTION_TYPE_LABELS.get(row['transaction_type'], 'N/A')
                st.markdown(f"**{type_label}** by **{row['person_name'].capitalize()}**")
                st.caption(f"Date: {row['transaction_date'].strftime('%Y-%m-%d')}")
            
            with col2:
                in_amount = f"{row.get('input_amount', 0):,.6f}".rstrip('0').rstrip('.')
                out_amount = f"{row.get('output_amount', 0):,.6f}".rstrip('0').rstrip('.')
                st.markdown(f"**Input:** {in_amount} {row['input_currency']}")
                st.markdown(f"**Output:** {out_amount} {row['output_currency']}")

                if row['transaction_type'] == 'sell' and not portfolio_df.empty:
                    person_assets = portfolio_df[(portfolio_df['person_name'] == row['person_name']) & (portfolio_df['currency'] == row['input_currency'])]
                    if not person_assets.empty:
                        avg_buy_price = person_assets.iloc[0]['avg_buy_price']
                        if avg_buy_price > 0:
                            cost_of_goods = row['input_amount'] * avg_buy_price
                            fee = row.get('fee', 0)
                            pnl = row['output_amount'] - cost_of_goods - fee
                            pnl_color = "green" if pnl >= 0 else "red"
                            st.markdown(f"**<span style='color:{pnl_color};'>Realized P/L: ${pnl:,.2f}</span>**", unsafe_allow_html=True)

            with col3:
                # This button now SETS THE STATE to start the confirmation process
                if st.button("Delete", key=f"delete_{row['id']}"):
                    st.session_state.confirming_delete_id = row['id']
                    st.rerun()
