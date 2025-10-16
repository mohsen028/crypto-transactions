import streamlit as st
import pandas as pd
from utils import initialize_state, get_all_transactions, delete_transaction, TRANSACTION_TYPE_LABELS, generate_financial_analysis

st.set_page_config(page_title="Transaction History", layout="wide")

# --- NEW: Combined CSS for both the Card/Bar and the Badge ---
st.markdown("""
<style>
/* 1. The main container card with the vertical bar */
.transaction-card {
    position: relative;
    background-color: #262730;
    border-radius: 8px;
    padding: 1rem 1rem 1rem 2rem; /* Space on the left for the color bar */
    margin-bottom: 1rem;
    border: 1px solid #3a3a3a;
}
.transaction-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 8px; /* Thickness of the bar */
    height: 100%;
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}
/* Colors for the vertical bar */
.buy-card::before { background-color: #28a745; }
.sell-card::before { background-color: #dc3545; }
.transfer-card::before { background-color: #ffc107; }
.swap-card::before { background-color: #007bff; }

/* 2. The small badge for the transaction type */
.tx-badge {
    display: inline-block;
    padding: 0.25em 0.6em;
    font-size: 0.75em;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle; /* Aligns badge with the middle of the text */
    border-radius: 0.375rem;
    text-transform: uppercase;
}
/* Colors for the badge */
.buy-badge { background-color: rgba(40, 167, 69, 0.2); color: #28a745; }
.sell-badge { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; }
.transfer-badge { background-color: rgba(255, 193, 7, 0.2); color: #ffc107; }
.swap-badge { background-color: rgba(0, 123, 255, 0.2); color: #007bff; }
</style>
""", unsafe_allow_html=True)

# --- Two sets of maps: one for the card, one for the badge ---
TYPE_TO_CARD_CLASS = {
    "buy_usdt_with_toman": "buy-card", "buy_crypto_with_usdt": "buy-card",
    "sell": "sell-card", "transfer": "transfer-card", "swap": "swap-card"
}
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
        # --- MODIFIED: The final combined design ---
        card_class = f"transaction-card {TYPE_TO_CARD_CLASS.get(row['transaction_type'], '')}"
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([4, 4, 2])
        with c1:
            # Prepare the badge
            type_label = TRANSACTION_TYPE_LABELS.get(row['transaction_type'], 'N/A')
            badge_class = TYPE_TO_BADGE_CLASS.get(row['transaction_type'], '')
            badge_html = f'<span class="tx-badge {badge_class}">{type_label}</span>'
            
            # Display title and badge side-by-side
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px;">
                <h4>{row['person_name'].capitalize()}</h4>
                {badge_html}
            </div>
            """, unsafe_allow_html=True)
            
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
