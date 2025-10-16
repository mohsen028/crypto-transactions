import streamlit as st
import pandas as pd
import datetime
from utils import add_transaction, get_current_balance, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="New Transaction", layout="centered")
st.title("💸 Record a New Transaction")

person_name = st.selectbox("Person", options=PEOPLE, format_func=lambda x: x.capitalize())
transaction_date = st.date_input("Transaction Date", datetime.date.today())
transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell", "Transfer", "Swap"])
st.markdown("---")

form_data = {"person_name": person_name, "transaction_date": pd.to_datetime(transaction_date)}

# --- Buy Forms (No changes needed here) ---
if transaction_type == "Buy":
    # ... (This entire section is correct and remains unchanged)
    buy_type = st.radio("What are you buying with?", ["Toman (IRR)", "USDT"], horizontal=True)
    if buy_type == "Toman (IRR)":
        # ... form for buying with Toman
    else:
        # ... form for buying with USDT

# --- Transfer, Sell, Swap Forms (WITH THE FIX) ---
else:
    form_key = f"{transaction_type.lower()}_form"
    with st.form(form_key):
        st.subheader(f"{transaction_type} Crypto")
        
        if transaction_type in ["Sell", "Swap", "Transfer"]:
            source_currency_options = CRYPTOS if transaction_type == "Sell" else CURRENCIES
            if transaction_type == "Transfer":
                input_currency = st.selectbox("Currency Transferred", source_currency_options)
                output_currency = input_currency
            else:
                c1, c2 = st.columns(2)
                input_currency = c1.selectbox("Source Currency", source_currency_options)
                output_currency = "USDT" if transaction_type == "Sell" else c2.selectbox("Destination Currency", CURRENCIES)

            c1, c2 = st.columns(2)
            input_amount = c1.number_input("Amount Given / Sent", min_value=0.0, format="%.8f")
            output_amount = c2.number_input("Amount Received", min_value=0.0, format="%.8f")
            
            fee = 0
            if transaction_type not in ["Transfer"]:
                 fee = st.number_input("Explicit Fee (in USD, if any)", min_value=0.0, format="%.8f")

            notes = st.text_area("Notes (Optional)")

            if st.form_submit_button("Save Transaction"):
                # --- THE CRITICAL FIX IS HERE ---
                current_balance = get_current_balance(person_name, input_currency)
                # Compare after rounding to 8 decimal places to avoid float errors
                if round(input_amount, 8) > round(current_balance, 8):
                    st.error(f"Insufficient balance. You have {current_balance:,.8f} {input_currency} but are trying to use {input_amount:,.8f}.")
                else:
                    form_data.update({
                        "transaction_type": transaction_type.lower(),
                        "input_currency": input_currency, "output_currency": output_currency,
                        "input_amount": input_amount, "output_amount": output_amount,
                        "fee": fee, "notes": notes
                    })
                    add_transaction(form_data)
                    st.success("Transaction Saved!")
