import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")

# --- NEW: Define CSS styles for containers ---
st.markdown("""
<style>
.st-emotion-cache-16txtl3 {
    padding-top: 1rem; /* Adjust this value as needed */
    padding-bottom: 1rem; /* Adjust this value as needed */
}
.buy-container {
    background-color: rgba(40, 167, 69, 0.1);
    border: 1px solid rgba(40, 167, 69, 0.4);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.sell-container {
    background-color: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220, 53, 69, 0.4);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.transfer-container {
    background-color: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.4);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.swap-container {
    background-color: rgba(0, 123, 255, 0.1);
    border: 1px solid rgba(0, 123, 255, 0.4);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# --- NEW: Map transaction types to CSS classes ---
TYPE_TO_CLASS = {
    "buy_usdt_with_toman": "buy-container",
    "buy_crypto_with_usdt": "buy-container",
    "sell": "sell-container",
    "transfer": "transfer-container",
    "swap": "swap-container"
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
        # ...
        col1, col2, _ = st.columns([1,1,5])
        if col1.button("✅ Yes, delete", type="primary"):
            delete_transaction(st.session_state.confirming_delete_id); st.session_state.confirming_delete_id = None; st.success("Deleted."); st.rerun()
        if col2.button("❌ Cancel"):
            st.session_state.confirming_delete_id = None; st.rerun()
    except:
        st.session_state.confirming_delete_id = None; st.rerun()
else:
    st.markdown("View, filter, and manage all your transactions.")
    if transactions.empty: st.warning("No transactions found."); st.stop()
    
    portfolio_df, _, _, _ = generate_financial_analysis(transactions, st.session_state.get('prices', {}))
    
    for index, row in transactions.iterrows():
        # --- MODIFIED: Use markdown to wrap content in a colored div ---
        css_class = TYPE_TO_CLASS.get(row['transaction_type'], "") # Get the CSS class
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
        
        # --- Display Realized P/L at the bottom of the container ---
        if row['transaction_type'] in ['sell', 'swap'] and not portfolio_df.empty:
            # This logic could be more complex, for now we just show a placeholder if needed
            # The full P/L logic is in the dashboard
            pass # You can add a simplified P/L note here if desired

        st.markdown('</div>', unsafe_allow_html=True)
