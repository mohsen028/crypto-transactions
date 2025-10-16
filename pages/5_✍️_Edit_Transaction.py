import streamlit as st
import pandas as pd
from utils import get_all_transactions, update_transaction, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="Edit Transaction", layout="centered")

if 'edit_transaction_id' not in st.session_state or not st.session_state.edit_transaction_id:
    st.warning("Please select a transaction to edit from the 'Transaction History' page.")
    st.stop()

transactions = get_all_transactions()
transaction_id = st.session_state.edit_transaction_id
try:
    tx_data = transactions[transactions['id'] == transaction_id].iloc[0].to_dict()
except IndexError:
    st.error("Transaction not found. It might have been deleted.")
    st.stop()

st.title(f"✍️ Editing Transaction")
st.markdown(f"**ID:** `{transaction_id}`")

# Use a simple form for editing. For a full-featured app, you would replicate the dynamic new transaction form.
with st.form("edit_form"):
    st.info("Note: For simplicity, this form allows editing core values. Be careful when changing types or currencies.")
    
    person_name = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']) if tx_data['person_name'] in PEOPLE else 0)
    transaction_date = st.date_input("Transaction Date", value=pd.to_datetime(tx_data['transaction_date']))
    
    c1, c2 = st.columns(2)
    input_currency = c1.selectbox("Input Currency", options=CURRENCIES, index=CURRENCIES.index(tx_data['input_currency']) if tx_data['input_currency'] in CURRENCIES else 0)
    output_currency = c2.selectbox("Output Currency", options=CURRENCIES, index=CURRENCIES.index(tx_data['output_currency']) if tx_data['output_currency'] in CURRENCIES else 0)
    
    c1, c2 = st.columns(2)
    input_amount = c1.number_input("Input Amount", value=tx_data.get('input_amount', 0.0), format="%.8f")
    output_amount = c2.number_input("Output Amount", value=tx_data.get('output_amount', 0.0), format="%.8f")
    
    fee = st.number_input("Fee (in USD)", value=tx_data.get('fee', 0.0), format="%.8f")
    notes = st.text_area("Notes", value=tx_data.get('notes', ''))
    
    if st.form_submit_button("Update Transaction"):
        updated_data = {
            "person_name": person_name, "transaction_date": pd.to_datetime(transaction_date),
            "input_currency": input_currency, "output_currency": output_currency,
            "input_amount": input_amount, "output_amount": output_amount,
            "fee": fee, "notes": notes
        }
        update_transaction(transaction_id, updated_data)
        st.success("Transaction updated successfully!")
        st.session_state.edit_transaction_id = None # Clear the edit state
