import streamlit as st
import pandas as pd
from utils import get_all_transactions, update_transaction, get_current_balance, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="Edit Transaction", layout="centered")

if 'edit_transaction_id' not in st.session_state or not st.session_state.edit_transaction_id:
    st.warning("Please select a transaction to edit from the 'Transaction History' page.")
    st.page_link("pages/3_Transaction_History.py", label="Go to Transaction History")
    st.stop()

transaction_id = st.session_state.edit_transaction_id
try:
    tx_data = get_all_transactions().loc[lambda df: df['id'] == transaction_id].iloc[0].to_dict()
except IndexError:
    st.error("Transaction not found. It might have been deleted.")
    st.session_state.edit_transaction_id = None
    st.stop()

st.title("Editing Transaction")
st.caption(f"ID: `{transaction_id}`")
st.markdown("---")

tx_type = tx_data['transaction_type']

# --- FORM 1: Buy USDT with Toman ---
if tx_type == 'buy_usdt_with_toman':
    with st.form("edit_buy_usdt_form"):
        st.subheader("Edit: Buy USDT with Toman")
        person_name = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        transaction_date = st.date_input("Date", value=pd.to_datetime(tx_data['transaction_date']))
        amount_toman = st.number_input("Amount Toman (IRR)", value=int(tx_data.get('input_amount', 0)), format="%d")
        c1, c2 = st.columns(2)
        amount_usdt = c1.number_input("Amount USDT Received", value=float(tx_data.get('output_amount', 0.0)), format="%.8f")
        usdt_rate = c2.number_input("USDT Rate", value=int(tx_data.get('rate', 0)), format="%d")
        notes = st.text_area("Notes", value=tx_data.get('notes', ''))
        
        if st.form_submit_button("Update Transaction"):
            form_data = tx_data.copy()
            form_data.update({"person_name": person_name, "transaction_date": pd.to_datetime(transaction_date), "input_amount": amount_toman, "output_amount": amount_usdt, "rate": usdt_rate, "notes": notes})
            update_transaction(transaction_id, form_data)
            st.success("Transaction updated!"); st.session_state.edit_transaction_id = None

# --- FORM 2: Buy Crypto with USDT ---
elif tx_type == 'buy_crypto_with_usdt':
    with st.form("edit_buy_crypto_form"):
        st.subheader("Edit: Buy Crypto with USDT")
        person_name = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        transaction_date = st.date_input("Date", value=pd.to_datetime(tx_data['transaction_date']))
        
        output_currency = st.selectbox("Crypto to Buy", options=CRYPTOS, index=CRYPTOS.index(tx_data['output_currency']))
        c1, c2 = st.columns(2)
        input_amount = c1.number_input("Amount USDT Spent", value=float(tx_data.get('input_amount', 0.0)), format="%.8f")
        output_amount = c2.number_input("Amount Crypto Received", value=float(tx_data.get('output_amount', 0.0)), format="%.8f")
        fee = st.number_input("Explicit Fee (in USDT)", value=float(tx_data.get('fee', 0.0)), format="%.8f")
        notes = st.text_area("Notes", value=tx_data.get('notes', ''))
        
        if st.form_submit_button("Update Transaction"):
            form_data = tx_data.copy()
            form_data.update({
                "person_name": person_name, "transaction_date": pd.to_datetime(transaction_date),
                "output_currency": output_currency, "input_amount": input_amount,
                "output_amount": output_amount, "fee": fee, "notes": notes
            })
            update_transaction(transaction_id, form_data)
            st.success("Transaction updated!"); st.session_state.edit_transaction_id = None

# --- FORM 3, 4, 5: Transfer, Sell, Swap (WITH validation) ---
else:
    with st.form("edit_disposal_form"):
        st.subheader(f"Edit: {tx_type.replace('_', ' ').capitalize()}")
        person_name = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        transaction_date = st.date_input("Date", value=pd.to_datetime(tx_data['transaction_date']))
        
        input_currency = st.selectbox("Input/Source Currency", options=CURRENCIES, index=CURRENCIES.index(tx_data['input_currency']))
        input_amount = st.number_input("Input/Given Amount", value=float(tx_data.get('input_amount', 0.0)), format="%.8f")
        
        if tx_type != 'transfer':
            output_currency = st.selectbox("Output/Destination Currency", options=CURRENCIES, index=CURRENCIES.index(tx_data['output_currency']))
        else:
            output_currency = input_currency

        output_amount = st.number_input("Output/Received Amount", value=float(tx_data.get('output_amount', 0.0)), format="%.8f")
        notes = st.text_area("Notes", value=tx_data.get('notes', ''))
        fee = st.number_input("Explicit Fee (in USD, if any)", value=float(tx_data.get('fee', 0.0)), format="%.8f")


        if st.form_submit_button("Update Transaction"):
            balance_without_this_tx = get_current_balance(person_name, input_currency, tx_id_to_exclude=transaction_id)
            total_available_funds = balance_without_this_tx + float(tx_data['input_amount'])
            
            if round(input_amount, 8) > round(total_available_funds, 8):
                st.error(f"Insufficient balance. You only have {total_available_funds:,.8f} {input_currency} available for this transaction.")
            else:
                form_data = tx_data.copy()
                form_data.update({
                    "person_name": person_name, "transaction_date": pd.to_datetime(transaction_date),
                    "input_currency": input_currency, "output_currency": output_currency,
                    "input_amount": input_amount, "output_amount": output_amount, "fee": fee, "notes": notes
                })
                update_transaction(transaction_id, form_data)
                st.success("Transaction updated!"); st.session_state.edit_transaction_id = None

if st.session_state.edit_transaction_id is None:
    st.info("Edit complete. You can now leave this page.")
    st.page_link("pages/3_Transaction_History.py", label="Go back to Transaction History")
