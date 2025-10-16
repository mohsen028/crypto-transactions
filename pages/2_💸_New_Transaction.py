import streamlit as st
import pandas as pd
import datetime
from utils import add_transaction, get_current_balance, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="New Transaction", layout="centered")
st.title("💸 Record a New Transaction")
# ... (بخش اول فرم بدون تغییر)
person_name = st.selectbox("Person", options=PEOPLE, format_func=lambda x: x.capitalize())
transaction_date = st.date_input("Transaction Date", datetime.date.today())
transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell", "Transfer", "Swap"])
st.markdown("---")
form_data = {"person_name": person_name, "transaction_date": pd.to_datetime(transaction_date)}

# --- Buy Forms (No validation needed) ---
if transaction_type == "Buy":
    # ... (کد فرم‌های خرید بدون تغییر باقی می‌ماند)
    pass

# --- Transfer Form (WITH validation) ---
elif transaction_type == "Transfer":
    st.subheader("Transfer Currency")
    with st.form("transfer_form"):
        currency = st.selectbox("Currency Transferred", CURRENCIES)
        c1, c2 = st.columns(2)
        amount_sent = c1.number_input("Amount Sent", min_value=0.0, format="%.8f")
        amount_received = c2.number_input("Amount Received", min_value=0.0, format="%.8f")
        notes = st.text_area("Notes (Optional)")
        
        if st.form_submit_button("Save Transaction"):
            # --- VALIDATION LOGIC ---
            current_balance = get_current_balance(person_name, currency)
            if amount_sent > current_balance:
                st.error(f"Insufficient balance. You have {current_balance:,.8f} {currency} but are trying to transfer {amount_sent:,.8f}.")
            else:
                fee = amount_sent - amount_received if amount_sent > amount_received else 0
                form_data.update({"transaction_type": "transfer", "input_currency": currency, "output_currency": currency, "input_amount": amount_sent, "output_amount": amount_received, "notes": notes, "fee": fee})
                add_transaction(form_data); st.success("Transaction Saved!")

# --- Sell & Swap Forms (WITH validation) ---
else:
    form_data.update({"transaction_type": "sell" if transaction_type == "Sell" else "swap"})
    with st.form("sell_swap_form"):
        st.subheader(f"{transaction_type} Crypto")
        c1, c2 = st.columns(2)
        input_currency = c1.selectbox("Source Currency", CRYPTOS if transaction_type == "Sell" else CURRENCIES)
        output_currency = "USDT" if transaction_type == "Sell" else c2.selectbox("Destination Currency", CURRENCIES)
        c1, c2 = st.columns(2)
        input_amount = c1.number_input("Amount Given", min_value=0.0, format="%.8f")
        output_amount = c2.number_input("Amount Received", min_value=0.0, format="%.8f")
        fee = st.number_input("Explicit Fee (in USD, if any)", min_value=0.0, format="%.8f")
        notes = st.text_area("Notes (Optional)")

        if st.form_submit_button("Save Transaction"):
            # --- VALIDATION LOGIC ---
            current_balance = get_current_balance(person_name, input_currency)
            if input_amount > current_balance:
                st.error(f"Insufficient balance. You have {current_balance:,.8f} {input_currency} but are trying to spend {input_amount:,.8f}.")
            else:
                form_data.update({"input_currency": input_currency, "output_currency": output_currency, "input_amount": input_amount, "output_amount": output_amount, "fee": fee, "notes": notes})
                add_transaction(form_data); st.success("Transaction Saved!")
