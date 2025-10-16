import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")

# --- NEW: CSS for the new design ---
st.markdown("""
<style>
/* A general class for the text with the color bar */
.tx-type-text {
    padding-left: 10px; /* Space between bar and text */
    border-left-width: 5px; /* Thickness of the bar */
    border-left-style: solid;
}
/* Specific color classes */
.buy-text { border-left-color: #28a745; } /* Green */
.sell-text { border-left-color: #dc3545; } /* Red */
.transfer-text { border-left-color: #ffc107; } /* Yellow */
.swap-text { border-left-color: #007bff; } /* Blue */
</style>
""", unsafe_allow_html=True)

TYPE_TO_CLASS = {
    "buy_usdt_with_toman": "buy-text", "buy_crypto_with_usdt": "buy-text",
    "sell": "sell-text", "transfer": "transfer-text", "swap": "swap-text"
}

initialize_state()
if 'confirming_delete_id' not in st.session_state: st.session_state.confirming_delete_id = None
transactions = get_all_transactions()
st.title("📜 Transaction History")

if st.session_state.confirming_delete_id:
    # ... (منطق تایید حذف بدون تغییر)
    try:
        tx_to_delete = transactions[transactions['id'] == st.session_state.confirming_delete_id].iloc[0]
        st.warning("Are you sure you want to permanently delete this transaction?")
        col1, col2, _ = st.columns([1,1,5])
        if col1.button("✅ Yes, delete", type="primary"):
            delete_transaction(st.session_state.confirming_delete_id); st.session_state.confirming_delete_id = None; st.success("Deleted."); st.rerun()
        if col2.button("❌ Cancel"):
            st.session_state.confirming_delete_id = None; st.rerun()
    except:
        st.session_state.confirming_delete_id = None; st.rerun()
else:
    st.markdown("View, filter, and manage all your transactions.")
    if transactions.empty:
        st.warning("No transactions found."); st.stop()
    
    portfolio_df, _, _, _ = generate_financial_analysis(transactions, st.session_state.get('prices', {}))
    
    for index, row in transactions.iterrows():
        # --- MODIFIED: Each transaction is now in its own clean container ---
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 4, 2])
            with c1:
                type_label = TRANSACTION_TYPE_LABELS.get(row['transaction_type'], 'N/A')
                css_class = f"tx-type-text {TYPE_TO_CLASS.get(row['transaction_type'], '')}"
                
                # Apply the CSS class to the title text
                st.markdown(f'<div class="{css_class}">**{type_label}** by **{row["person_name"].capitalize()}**</div>', unsafe_allow_html=True)
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
