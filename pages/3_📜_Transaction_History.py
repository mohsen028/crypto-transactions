import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")

# --- NEW: Modern CSS for the card with a left colored bar ---
st.markdown("""
<style>
.transaction-card {
    position: relative; /* Needed for the pseudo-element */
    background-color: #262730; /* Dark background for the card */
    border-radius: 8px;
    padding: 1rem 1rem 1rem 2rem; /* Add left padding to make space for the bar */
    margin-bottom: 1rem;
    border: 1px solid #333;
}
.transaction-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 8px; /* Thickness of the colored bar */
    height: 100%;
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}
.buy::before { background-color: #28a745; }
.sell::before { background-color: #dc3545; }
.transfer::before { background-color: #ffc107; }
.swap::before { background-color: #007bff; }
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
    # ... (منطق تایید حذف بدون تغییر)
    try:
        # ...
    except:
        st.session_state.confirming_delete_id = None; st.rerun()
else:
    st.markdown("View, filter, and manage all your transactions.")
    if transactions.empty: st.warning("No transactions found."); st.stop()
    
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
