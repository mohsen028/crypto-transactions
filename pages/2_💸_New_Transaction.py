import streamlit as st
import pandas as pd
import datetime
from utils import add_transaction, get_current_balance, PEOPLE, CURRENCIES, CRYPTOS, update_prices_in_state

st.set_page_config(page_title="New Transaction", layout="centered")
st.title("💸 Record a New Transaction")
update_prices_in_state(CURRENCIES) # Update prices on page load for fee previews

# --- Shared Form Fields ---
person_name = st.selectbox("Person", options=PEOPLE, format_func=lambda x: x.capitalize())
transaction_date = st.date_input("Transaction Date", datetime.date.today())
transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell", "Transfer", "Swap"])
st.markdown("---")

form_data = {"person_name": person_name, "transaction_date": pd.to_datetime(transaction_date)}

# --- Buy USDT with Toman ---
if transaction_type == "Buy" and st.radio("Buy with:", ["Toman (IRR)", "USDT"]) == "Toman (IRR)":
    with st.form("buy_usdt_form"):
        st.subheader("Buy USDT with Toman")
        amount_toman = st.number_input("Amount Toman (IRR)", format="%d")
        c1,c2 = st.columns(2)
        amount_usdt = c1.number_input("Amount USDT Received", format="%.8f")
        usdt_rate = c2.number_input("Stated USDT Rate", format="%d")
        notes = st.text_area("Notes")
        if amount_toman > 0 and usdt_rate > 0 and amount_usdt > 0:
            fee_usd = (amount_toman / usdt_rate) - amount_usdt
            st.info(f"Calculated Hidden Fee: {fee_usd:,.4f} USDT")
        if st.form_submit_button("Save Transaction"):
            # ... save logic

# --- Other forms ---
else:
    # This part will now contain all other forms (Buy with USDT, Sell, Swap, Transfer)
    # Each will have its own st.form and logic, including the st.info for fee preview where applicable.
    
    if transaction_type == "Transfer":
         with st.form("transfer_form"):
            st.subheader("Transfer Currency")
            #... form fields ...
            amount_sent = st.number_input("Amount Sent", format="%.8f")
            amount_received = st.number_input("Amount Received", format="%.8f")
            if amount_sent > amount_received:
                fee = amount_sent - amount_received
                st.info(f"Calculated Transfer Fee: {fee:,.8f} {currency}")
            if st.form_submit_button("Save"):
                #... save logic with validation
    
    elif transaction_type == "Sell":
         with st.form("sell_form"):
            st.subheader("Sell Crypto for USDT")
            #... form fields ...
            input_amount = st.number_input("Amount Given", format="%.8f")
            output_amount = st.number_input("Amount Received (USDT)", format="%.8f")
            prices = st.session_state.get('prices', {})
            if input_amount > 0 and prices.get(input_currency, 0) > 0:
                value_given_usd = input_amount * prices[input_currency]
                fee = value_given_usd - output_amount
                if fee > 0: st.info(f"Calculated Slippage/Fee: ${fee:,.4f}")
            if st.form_submit_button("Save"):
                #... save logic with validation

    # ... and so on for Buy with USDT and Swap
