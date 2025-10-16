import streamlit as st
import pandas as pd
import datetime
from utils import add_transaction, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="New Transaction", layout="centered")

st.title("💸 Record a New Transaction")

# --- Shared Form Fields ---
person_name = st.selectbox("Person", options=PEOPLE, format_func=lambda x: x.capitalize())
transaction_date = st.date_input("Transaction Date", datetime.date.today())

transaction_type = st.selectbox(
    "Transaction Type",
    ["Buy", "Sell", "Transfer", "Swap"]
)

st.markdown("---")

# --- Dynamic Form Based on Transaction Type ---

# Use a dictionary to hold form data temporarily
form_data = {
    "person_name": person_name,
    "transaction_date": pd.to_datetime(transaction_date)
}

# --- BUY FORM ---
if transaction_type == "Buy":
    buy_type = st.radio("What are you buying with?", ["Toman (IRR)", "USDT"], horizontal=True)
    
    if buy_type == "Toman (IRR)": # BuyUSDTForm
        st.subheader("Buy USDT with Toman")
        form_data["transaction_type"] = "buy_usdt_with_toman"
        form_data["input_currency"] = "IRR"
        form_data["output_currency"] = "USDT"
        
        with st.form("buy_usdt_form"):
            c1, c2 = st.columns(2)
            amount_toman = c1.number_input("Amount in Toman (IRR)", min_value=0, step=100000, format="%d")
            amount_usdt = c2.number_input("Amount of USDT Received", min_value=0.0, step=0.01, format="%.2f")
            usdt_rate = st.number_input("Stated USDT Rate in Toman (for reference)", min_value=0, step=500, format="%d")
            notes = st.text_area("Notes (Optional)")

            # --- AUTO FEE CALCULATION ---
            fee = 0
            if amount_toman > 0 and amount_usdt > 0 and usdt_rate > 0:
                actual_value = amount_usdt * usdt_rate
                fee = amount_toman - actual_value
                st.info(f"Calculated Hidden Fee: {fee:,.0f} Toman")
            
            submitted = st.form_submit_button("Save Transaction")
            if submitted:
                form_data.update({
                    "input_amount": amount_toman, "output_amount": amount_usdt,
                    "rate": usdt_rate, "notes": notes, "fee": fee
                })
                add_transaction(form_data)
                st.success("Transaction Saved!")
    else: # BuyCryptoForm
        st.subheader("Buy Crypto with USDT")
        form_data["transaction_type"] = "buy_crypto_with_usdt"
        form_data["input_currency"] = "USDT"
        
        with st.form("buy_crypto_form"):
            crypto_to_buy = st.selectbox("Crypto to Buy", CRYPTOS)
            c1, c2 = st.columns(2)
            amount_usdt = c1.number_input("Amount of USDT Spent", min_value=0.0, step=0.01, format="%.2f")
            amount_crypto = c2.number_input("Amount of Crypto Received", min_value=0.0, step=0.000001, format="%.6f")
            fee = st.number_input("Explicit Fee (in USDT, if any)", min_value=0.0, step=0.01, format="%.2f")
            notes = st.text_area("Notes (Optional)")

            submitted = st.form_submit_button("Save Transaction")
            if submitted:
                form_data.update({
                    "output_currency": crypto_to_buy, "input_amount": amount_usdt,
                    "output_amount": amount_crypto, "fee": fee, "notes": notes
                })
                add_transaction(form_data)
                st.success("Transaction Saved!")

# --- TRANSFER FORM ---
elif transaction_type == "Transfer":
    st.subheader("Transfer Currency")
    st.markdown("Enter the amount you sent and the final amount that arrived in the destination wallet.")
    form_data["transaction_type"] = "transfer"
    
    with st.form("transfer_form"):
        currency = st.selectbox("Currency Transferred", CURRENCIES)
        c1, c2 = st.columns(2)
        amount_sent = c1.number_input("Amount Sent", min_value=0.0, step=0.000001, format="%.6f")
        amount_received = c2.number_input("Amount Received", min_value=0.0, step=0.000001, format="%.6f")
        notes = st.text_area("Notes (Optional)")
        
        # --- AUTO FEE CALCULATION ---
        fee = 0
        if amount_sent > 0 and amount_received > 0:
            fee = amount_sent - amount_received
            st.info(f"Calculated Transfer Fee: {fee:,.6f} {currency}")

        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            form_data.update({
                "input_currency": currency, "output_currency": currency,
                "input_amount": amount_sent, "output_amount": amount_received,
                "fee": fee, "notes": notes
            })
            add_transaction(form_data)
            st.success("Transaction Saved!")
            
# --- SELL & SWAP Forms (with optional explicit fee) ---
else: # Sell or Swap
    if transaction_type == "Sell":
        st.subheader("Sell Crypto for USDT")
        form_data.update({"transaction_type": "sell", "output_currency": "USDT"})
        form_key = "sell_form"
    else: # Swap
        st.subheader("Swap Currency")
        form_data.update({"transaction_type": "swap"})
        form_key = "swap_form"

    with st.form(form_key):
        c1, c2 = st.columns(2)
        input_currency = c1.selectbox("Source Currency", CRYPTOS if transaction_type == "Sell" else CURRENCIES)
        output_currency = "USDT" if transaction_type == "Sell" else c2.selectbox("Destination Currency", CURRENCIES)
        
        c1, c2 = st.columns(2)
        input_amount = c1.number_input("Amount Given", min_value=0.0, step=0.000001, format="%.6f")
        output_amount = c2.number_input("Amount Received", min_value=0.0, step=0.000001, format="%.6f")
        
        # For these types, the fee is often hidden in the rate. We allow an optional explicit fee.
        fee = st.number_input("Explicit Fee (in source currency, if any)", min_value=0.0, format="%.6f")
        notes = st.text_area("Notes (Optional)")

        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            form_data.update({
                "input_currency": input_currency, "output_currency": output_currency,
                "input_amount": input_amount, "output_amount": output_amount,
                "fee": fee, "notes": notes
            })
            add_transaction(form_data)
            st.success("Transaction Saved!")
