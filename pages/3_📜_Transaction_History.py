import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")

# --- NEW: CSS for the new Badge design ---
st.markdown("""
<style>
/* Style for the small transaction type badge */
.tx-badge {
    display: inline-block;
    padding: 0.25em 0.6em;
    font-size: 0.75em;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.375rem; /* More rounded corners */
    text-transform: uppercase;
}
/* Color variations for the badge */
.buy-badge { background-color: rgba(40, 167, 69, 0.2); color: #28a745; }
.sell-badge { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; }
.transfer-badge { background-color: rgba(255, 193, 7, 0.2); color: #ffc107; }
.swap-badge { background-color: rgba(0, 123, 255, 0.2); color: #007bff; }
</style>
""", unsafe_allow_html=True)

# Map transaction types to the new badge CSS classes
TYPE_TO_BADGE_CLASS = {
    "buy_usdt_with_toman": "buy-badge", "buy_crypto_with_usdt": "buy-badge",
    "sell": "sell-badge", "transfer": "transfer-badge", "swap": "swap-badge"
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
        # Each transaction is now in its own clean container
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 4, 2])
            
            # --- MODIFIED: New title layout in the first column ---
            with c1:
                # Prepare the badge
                type_label = TRANSACTION_TYPE_LABELS.get(row['transaction_type'], 'N/A')
                badge_class = TYPE_TO_BADGE_CLASS.get(row['transaction_type'], '')
                badge_html = f'<span class="tx-badge {badge_class}">{type_label}</span>'
                
                # Use columns for alignment
                title_col, badge_col = st.columns([2, 3])
                with title_col:
                    st.markdown(f"#### {row['person_name'].capitalize()}")
                with badge_col:
                    st.markdown(badge_html, unsafe_allow_html=True)

                st.caption(f"Date: {pd.to_datetime(row['transaction_date']).strftime('%Y-%m-%d')}")
            
            # --- Second and third columns remain the same ---
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
