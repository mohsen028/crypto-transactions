import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")

# This CSS block is crucial. Please ensure it's exactly like this.
st.markdown("""
<style>
.transaction-card {
    position: relative;
    background-color: #262730; /* Dark background for the card */
    border-radius: 8px;
    padding: 1rem 1rem 1rem 2rem; /* Make space on the left for the color bar */
    margin-bottom: 1rem;
    border: 1px solid #3a3a3a; /* A subtle border */
}
.transaction-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 8px; /* The thickness of the color bar */
    height: 100%;
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}
.buy::before { background-color: #28a745 !important; } /* Green */
.sell::before { background-color: #dc3545 !important; } /* Red */
.transfer::before { background-color: #ffc107 !important; } /* Yellow */
.swap::before { background-color: #007bff !important; } /* Blue */
</style>
""", unsafe_allow_html=True)

TYPE_TO_CLASS = {
    "buy_usdt_with_toman": "buy", "buy_crypto_with_usdt": "buy",
    "sell": "sell", "transfer": "transfer", "swap": "swap"
}

initialize_state()
if 'confirming_delete_id' not in st.session_state: st.session_state.confirming_delete_id = None
transactions = get_all_transactions()
st.title("📜 Transaction History")

if st.session_state.confirming_delete_id:
    try:
        tx_to_delete = transactions[transactions['id'] == st.session_state.confirming_delete_id].iloc[0]
        st.warning("Are you sure you want to permanently delete this transaction?")
        col1, col2, _ = st.columns([1,1,5])
        if col1.button("✅ Yes, delete", type="primary"):
            delete_transaction(st.session_state.confirming_delete_id)
            st.session_state.confirming_delete_id = None
            st.success("Deleted.")
            st.rerun()
        if col2.button("❌ Cancel"):
            st.session_state.confirming_delete_id = None
            st.rerun()
    except:
        st.session_state.confirming_delete_id = None
        st.rerun()
else:
    st.markdown("View, filter, and manage all your transactions.")
    if transactions.empty:
        st.warning("No transactions found.")
        st.stop()
    
    portfolio_df, _, _, _ = generate_financial_analysis(transactions, st.session_state.get('prices', {}))
    
    for index, row in transactions.iterrows():
        css_class = f"transaction-card {TYPE_TO_CLASS.get(row['transaction_type'], '')}"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([4, 4, 2])
        with c1:
            type_label = TRANSACTION_TYPE_LABELS.get(row['transaction_type'], 'N/A')
            st.markdown(f"**{type_label}** by **{row['person_name'].capitalize()}**")
            st.caption(f"Date: {pd.to_datetime(row['transaction_date']).strftime('%Y-%m-%d')}")
        with c2:
            st.markdown(f"**Input:** {row.get('input_amount', 0):,.8f} {row['input_currency']}")
            st.markdown(f"**Output:** {row.get('output_amount', 0):,.8f} {row['output_currency']}")
        with c3:
            if st.button("✍️ Edit", key=f"edit_{row['id']}"):
                st.session_state.edit_transaction_id = row['id']
                st.switch_page("pages/5_✍️_Edit_Transaction.py")
            if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                st.session_state.confirming_delete_id = row['id']
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
