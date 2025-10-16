import streamlit as st
import pandas as pd
import datetime
from utils import get_all_transactions, update_transaction, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="Edit Transaction", layout="centered")

# --- Security check: ensure an edit is in progress ---
if 'edit_transaction_id' not in st.session_state or not st.session_state.edit_transaction_id:
    st.warning("Please select a transaction to edit from the 'Transaction History' page.")
    # Use st.page_link for modern Streamlit versions if available, otherwise use a markdown link
    st.page_link("pages/3_📜_Transaction_History.py", label="Go to Transaction History", icon="📜")
    st.stop()

# --- Load the specific transaction ---
transactions = get_all_transactions()
transaction_id = st.session_state.edit_transaction_id
try:
    tx_data = transactions[transactions['id'] == transaction_id].iloc[0].to_dict()
except IndexError:
    st.error("Transaction not found. It might have been deleted.")
    st.session_state.edit_transaction_id = None # Clear broken ID
    st.stop()

st.title(f"✍️ Editing Transaction")
st.caption(f"ID: `{transaction_id}`")
st.markdown("---")

# --- Render the correct form based on transaction type ---

form_data = tx_data.copy()

# --- FORM 1: Buy USDT with Toman ---
if tx_data['transaction_type'] == 'buy_usdt_with_toman':
    st.subheader("Edit: Buy USDT with Toman")
    with st.form("edit_buy_usdt_form"):
        form_data['person_name'] = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        form_data['transaction_date'] = st.date_input("Transaction Date", value=pd.to_datetime(tx_data['transaction_date']))
        
        amount_toman = st.number_input("Amount in Toman (IRR)", value=int(tx_data.get('input_amount', 0)), step=100000, format="%d")
        c1, c2 = st.columns(2)
        amount_usdt = c1.number_input("Amount of USDT Received", value=float(tx_data.get('output_amount', 0.0)), format="%.8f")
        usdt_rate = c2.number_input("Stated USDT Rate in Toman", value=int(tx_data.get('rate', 0)), step=500, format="%d")
        notes = st.text_area("Notes", value=tx_data.get('notes', ''))
        
        fee_usd = 0
        if amount_toman > 0 and usdt_rate > 0 and amount_usdt > 0:
            usdt_should_have_received = amount_toman / usdt_rate
            fee_usd = usdt_should_have_received - amount_usdt
            st.info(f"Calculated Hidden Fee: {fee_usd:,.4f} USDT")

        if st.form_submit_button("Update Transaction"):
            form_data.update({"input_amount": amount_toman, "output_amount": amount_usdt, "rate": usdt_rate, "notes": notes, "fee": fee_usd})
            update_transaction(transaction_id, form_data)
            st.success("Transaction updated!"); st.session_state.edit_transaction_id = None

# --- FORM 2: Buy Crypto with USDT ---
elif tx_data['transaction_type'] == 'buy_crypto_with_usdt':
    st.subheader("Edit: Buy Crypto with USDT")
    with st.form("edit_buy_crypto_form"):
        form_data['person_name'] = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        form_data['transaction_date'] = st.date_input("Transaction Date", value=pd.to_datetime(tx_data['transaction_date']))

        crypto_to_buy = st.selectbox("Crypto to Buy", CRYPTOS, index=CRYPTOS.index(tx_data['output_currency']))
        c1, c2 = st.columns(2)
        amount_usdt = c1.number_input("Amount of USDT Spent", value=float(tx_data.get('input_amount', 0.0)), format="%.8f")
        amount_crypto = c2.number_input("Amount of Crypto Received", value=float(tx_data.get('output_amount', 0.0)), format="%.8f")
        fee = st.number_input("Explicit Fee (in USDT, if any)", value=float(tx_data.get('fee', 0.0)), format="%.8f")
        notes = st.text_area("Notes", value=tx_data.get('notes', ''))

        if st.form_submit_button("Update Transaction"):
            form_data.update({"output_currency": crypto_to_buy, "input_amount": amount_usdt, "output_amount": amount_crypto, "fee": fee, "notes": notes})
            update_transaction(transaction_id, form_data)
            st.success("Transaction updated!"); st.session_state.edit_transaction_id = None

# --- FORM 3: Transfer ---
elif tx_data['transaction_type'] == 'transfer':
    st.subheader("Edit: Transfer Currency")
    with st.form("edit_transfer_form"):
        form_data['person_name'] = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        form_data['transaction_date'] = st.date_input("Transaction Date", value=pd.to_datetime(tx_data['transaction_date']))
        
        currency = st.selectbox("Currency Transferred", CURRENCIES, index=CURRENCIES.index(tx_data['input_currency']))
        c1, c2 = st.columns(2)
        amount_sent = c1.number_input("Amount Sent", value=float(tx_data.get('input_amount', 0.0)), format="%.8f")
        amount_received = c2.number_input("Amount Received", value=float(tx_data.get('output_amount', 0.0)), format="%.8f")
        notes = st.text_area("Notes", value=tx_data.get('notes', ''))

        if st.form_submit_button("Update Transaction"):
            form_data.update({"input_currency": currency, "output_currency": currency, "input_amount": amount_sent, "output_amount": amount_received, "notes": notes})
            update_transaction(transaction_id, form_data)
            st.success("Transaction updated!"); st.session_state.edit_transaction_id = None

# --- FORM 4: Sell or Swap ---
else:
    form_type = tx_data['transaction_type'].capitalize()
    st.subheader(f"Edit: {form_type} Crypto")
    with st.form("edit_sell_swap_form"):
        form_data['person_name'] = st.selectbox("Person", options=PEOPLE, index=PEOPLE.index(tx_data['person_name']))
        form_data['transaction_date'] = st.date_input("Transaction Date", value=pd.to_datetime(tx_data['transaction_date']))

        c1, c2 = st.columns(2)
        input_currency = c1.selectbox("Source Currency", CURRENCIES, index=CURRENCIES.index(tx_data['input_currency']))
        output_currency = c2.selectbox("Destination Currency", CURRENCIES, index=CURRENCIES.index(tx_data['output_currency']))
        c1, c2 = st.columns(2)
        input_amount = c1.number_input("Amount Given", value=float(tx_data.get('input_amount', 0.0)), format="%.8f")
        output_amount = c2.number_input("Amount Received", value=float(tx_data.get('output_amount', 0.0)), format="%.8f")
        fee = st.number_input("Explicit Fee (in USD, if any)", value=float(tx_data.get('fee', 0.0)), format="%.8f")
        notes = st.text_area("Notes", value=tx_data.get('notes', ''))

        if st.form_submit_button("Update Transaction"):
            form_data.update({"input_currency": input_currency, "output_currency": output_currency, "input_amount": input_amount, "output_amount": output_amount, "fee": fee, "notes": notes})
            update_transaction(transaction_id, form_data)
            st.success("Transaction updated!"); st.session_state.edit_transaction_id = None


if st.session_state.edit_transaction_id is None:
    st.info("Edit complete. You can now leave this page.")
    st.page_link("pages/3_📜_Transaction_History.py", label="Go back to Transaction History", icon="📜")
