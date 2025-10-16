### **مرحله ۲: کد نهایی و کامل `pages/2_💸_New_Transaction.py` (با پیش‌نمایش کارمزد)**

این کد، کادر آبی رنگ پیش‌نمایش کارمزد را به تمام فرم‌های مربوطه بازمی‌گرداند.

```python
import streamlit as st
import pandas as pd
import datetime
from utils import add_transaction, get_current_balance, PEOPLE, CURRENCIES, CRYPTOS, update_prices_in_state

st.set_page_config(page_title="New Transaction", layout="centered")
st.title("💸 Record a New Transaction")
update_prices_in_state(CURRENCIES)

person_name = st.selectbox("Person", options=PEOPLE, format_func=lambda x: x.capitalize())
transaction_date = st.date_input("Transaction Date", datetime.date.today())
transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell", "Transfer", "Swap"])
st.markdown("---")

form_data = {"person_name": person_name, "transaction_date": pd.to_datetime(transaction_date)}

if transaction_type == "Buy":
    buy_type = st.radio("Buy with:", ["Toman (IRR)", "USDT"], horizontal=True, key="buy_type")
    if buy_type == "Toman (IRR)":
        with st.form("buy_usdt_form"):
            st.subheader("Buy USDT with Toman")
            amount_toman = st.number_input("Amount Toman (IRR)", min_value=0, format="%d")
            c1,c2 = st.columns(2)
            amount_usdt = c1.number_input("Amount USDT Received", min_value=0.0, format="%.8f")
            usdt_rate = c2.number_input("Stated USDT Rate", min_value=0, format="%d")
            notes = st.text_area("Notes (Optional)")
            if amount_toman > 0 and usdt_rate > 0 and amount_usdt > 0:
                fee_usd = (amount_toman / usdt_rate) - amount_usdt
                st.info(f"Calculated Hidden Fee: {fee_usd:,.4f} USDT")
            if st.form_submit_button("Save Transaction"):
                form_data.update({"transaction_type": "buy_usdt_with_toman", "input_currency": "IRR", "output_currency": "USDT", "input_amount": amount_toman, "output_amount": amount_usdt, "rate": usdt_rate, "notes": notes, "fee": 0})
                add_transaction(form_data); st.success("Transaction Saved!")
    else: # Buy Crypto with USDT
        with st.form("buy_crypto_form"):
            st.subheader("Buy Crypto with USDT")
            crypto_to_buy = st.selectbox("Crypto to Buy", CRYPTOS)
            c1, c2 = st.columns(2)
            amount_usdt = c1.number_input("Amount of USDT Spent", min_value=0.0, format="%.8f")
            amount_crypto = c2.number_input("Amount of Crypto Received", min_value=0.0, format="%.8f")
            fee = st.number_input("Explicit Fee (in USDT, if any)", min_value=0.0, format="%.8f")
            notes = st.text_area("Notes (Optional)")
            if st.form_submit_button("Save Transaction"):
                form_data.update({"transaction_type": "buy_crypto_with_usdt", "input_currency": "USDT", "output_currency": crypto_to_buy, "input_amount": amount_usdt, "output_amount": amount_crypto, "fee": fee, "notes": notes})
                add_transaction(form_data); st.success("Transaction Saved!")
else:
    form_key = f"{transaction_type.lower()}_form"
    with st.form(form_key):
        st.subheader(f"{transaction_type} Crypto")
        if transaction_type == "Transfer":
            input_currency = st.selectbox("Currency Transferred", CURRENCIES)
            output_currency = input_currency
        elif transaction_type == "Sell":
            input_currency = st.selectbox("Source Currency", CRYPTOS)
            output_currency = "USDT"
        else: # Swap
            c1, c2 = st.columns(2)
            input_currency = c1.selectbox("Source Currency", CURRENCIES)
            output_currency = c2.selectbox("Destination Currency", CURRENCIES)
        
        c1, c2 = st.columns(2)
        input_amount = c1.number_input("Amount Given / Sent", min_value=0.0, format="%.8f")
        output_amount = c2.number_input("Amount Received", min_value=0.0, format="%.8f")
        
        fee = 0
        if transaction_type in ["Sell", "Swap"]:
             fee = st.number_input("Explicit Fee (in USD, if any)", min_value=0.0, format="%.8f")
        
        prices = st.session_state.get('prices', {})
        if transaction_type == "Transfer" and input_amount > output_amount:
            st.info(f"Calculated Transfer Fee: {input_amount - output_amount:,.8f} {input_currency}")
        elif transaction_type in ["Sell", "Swap"] and input_amount > 0 and prices.get(input_currency, 0) > 0:
            value_given_usd = input_amount * prices[input_currency]
            value_received_usd = output_amount * prices.get(output_currency, 1.0)
            slippage_fee = value_given_usd - value_received_usd
            if slippage_fee > 0:
                st.info(f"Calculated Slippage/Fee: ${slippage_fee:,.4f}")

        notes = st.text_area("Notes (Optional)")

        if st.form_submit_button("Save Transaction"):
            current_balance = get_current_balance(person_name, input_currency)
            if round(input_amount, 8) > round(current_balance, 8):
                st.error(f"Insufficient balance. You have {current_balance:,.8f} {input_currency} but are trying to use {input_amount:,.8f}.")
            else:
                form_data.update({"transaction_type": transaction_type.lower(), "input_currency": input_currency, "output_currency": output_currency, "input_amount": input_amount, "output_amount": output_amount, "fee": fee, "notes": notes})
                add_transaction(form_data)
                st.success("Transaction Saved!")
