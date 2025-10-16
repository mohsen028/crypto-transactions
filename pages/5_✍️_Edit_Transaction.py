import streamlit as st
import pandas as pd
from utils import get_all_transactions, update_transaction, get_current_balance, PEOPLE, CURRENCIES, CRYPTOS

# ... (بخش اول صفحه ویرایش بدون تغییر)
st.set_page_config(page_title="Edit Transaction", layout="centered")
if 'edit_transaction_id' not in st.session_state or not st.session_state.edit_transaction_id:
    st.warning("Please select a transaction to edit from the 'Transaction History' page.")
    st.stop()
transactions = get_all_transactions()
transaction_id = st.session_state.edit_transaction_id
try:
    tx_data = transactions[transactions['id'] == transaction_id].iloc[0].to_dict()
except IndexError:
    st.error("Transaction not found."); st.stop()
st.title(f"✍️ Editing Transaction")

# --- Render the correct form based on transaction type ---

# --- FORM 1 & 2: Buy Forms (No validation needed) ---
if tx_data['transaction_type'].startswith('buy'):
    # ... (کد فرم‌های ویرایش خرید بدون تغییر باقی می‌ماند)
    pass

# --- FORM 3, 4: Transfer, Sell, Swap (WITH validation) ---
else:
    form_type = tx_data['transaction_type'].capitalize()
    st.subheader(f"Edit: {form_type} Crypto")
    with st.form("edit_disposal_form"):
        person_name = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        # ... (بقیه فیلدهای فرم)
        input_currency = st.selectbox("Input/Source Currency", CURRENCIES, index=CURRENCIES.index(tx_data['input_currency']))
        input_amount = st.number_input("Input/Given Amount", value=float(tx_data.get('input_amount', 0.0)), format="%.8f")
        # ... (سایر فیلدها)

        if st.form_submit_button("Update Transaction"):
            # --- VALIDATION LOGIC FOR EDITS ---
            original_amount = float(tx_data.get('input_amount', 0.0))
            amount_difference = input_amount - original_amount
            
            # We only need to check if the user is trying to spend *more* than before
            if amount_difference > 0:
                # The balance check needs to account for the original transaction amount
                current_balance = get_current_balance(person_name, input_currency)
                if amount_difference > current_balance:
                    st.error(f"Insufficient balance for this edit. You are trying to spend an additional {amount_difference:,.8f} {input_currency}, but you only have {current_balance:,.8f} available.")
                else:
                    # Update logic here
                    # ...
                    st.success("Transaction updated!")
            else:
                # Spending less or the same is always valid
                # Update logic here
                # ...
                st.success("Transaction updated!")
