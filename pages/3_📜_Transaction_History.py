import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")
initialize_state()
# ... (بقیه کد تا بخش دکمه‌ها بدون تغییر است)
if 'confirming_delete_id' not in st.session_state: st.session_state.confirming_delete_id = None
transactions = get_all_transactions()
st.title("📜 Transaction History")

if st.session_state.confirming_delete_id:
    # ... (منطق تایید حذف بدون تغییر)
    try:
        tx_to_delete = transactions[transactions['id'] == st.session_state.confirming_delete_id].iloc[0]
        st.warning("Are you sure you want to permanently delete this transaction?")
        # ... (بقیه کد تایید حذف)
        col1, col2, _ = st.columns([1,1,5])
        if col1.button("✅ Yes, delete", type="primary"):
            delete_transaction(st.session_state.confirming_delete_id)
            st.session_state.confirming_delete_id = None
            st.success("Deleted."); st.rerun()
        if col2.button("❌ Cancel"):
            st.session_state.confirming_delete_id = None; st.rerun()
    except:
        st.session_state.confirming_delete_id = None; st.rerun()
else:
    st.markdown("View, filter, and manage all your transactions.")
    if transactions.empty: st.warning("No transactions found."); st.stop()
    
    portfolio_df, _, _, _ = generate_financial_analysis(transactions, st.session_state.get('prices', {}))
    
    for index, row in transactions.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 4, 2])
            # ... (نمایش اطلاعات تراکنش بدون تغییر)
            with c1:
                type_label = TRANSACTION_TYPE_LABELS.get(row['transaction_type'], 'N/A')
                st.markdown(f"**{type_label}** by **{row['person_name'].capitalize()}**")
                st.caption(f"Date: {pd.to_datetime(row['transaction_date']).strftime('%Y-%m-%d')}")
            with c2:
                st.markdown(f"**Input:** {row.get('input_amount', 0):,.8f} {row['input_currency']}")
                st.markdown(f"**Output:** {row.get('output_amount', 0):,.8f} {row['output_currency']}")
            
            # --- NEW: Action Buttons ---
            with c3:
                if st.button("✍️ Edit", key=f"edit_{row['id']}"):
                    st.session_state.edit_transaction_id = row['id']
                    st.switch_page("pages/5_✍️_Edit_Transaction.py") # Requires Streamlit 1.28+
                if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                    st.session_state.confirming_delete_id = row['id']
                    st.rerun()
