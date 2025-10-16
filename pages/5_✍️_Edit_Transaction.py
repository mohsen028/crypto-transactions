import streamlit as st
import pandas as pd
from utils import get_all_transactions, update_transaction, get_current_balance, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="Edit Transaction", layout="centered")

if 'edit_transaction_id' not in st.session_state or not st.session_state.edit_transaction_id:
    st.warning("Please select a transaction to edit.")
    st.page_link("pages/3_📜_Transaction_History.py", label="Go to Transaction History", icon="📜")
    st.stop()

# ... (The rest of the edit page remains the same, but we apply the fix in the validation logic)

# In the "else" block for Transfer, Sell, Swap:
else:
    # ... form fields
    if st.form_submit_button("Update Transaction"):
        # --- THE CRITICAL FIX IS HERE ---
        balance_without_this_tx = get_current_balance(person_name, input_currency, tx_id_to_exclude=transaction_id)
        total_available_funds = balance_without_this_tx + float(tx_data['input_amount'])
        
        # Compare after rounding
        if round(input_amount, 8) > round(total_available_funds, 8):
            st.error(f"Insufficient balance for this edit. You only have {total_available_funds:,.8f} {input_currency} available.")
        else:
            # ... update logic
            st.success("Transaction updated!")
