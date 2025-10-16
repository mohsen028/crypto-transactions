import streamlit as st
import pandas as pd
import datetime
from utils import add_transaction, PEOPLE, CURRENCIES, CRYPTOS

st.set_page_config(page_title="New Transaction", page_icon="💸", layout="centered")

st.title("💸 Record a New Transaction")

# --- Shared Form Fields ---
person_name = st.selectbox("Person", options=PEOPLE, format_func=lambda x: x.capitalize())
transaction_date = st.date_input("Transaction Date", datetime.date.today())
notes = st.text_area("Notes (Optional)")

# --- Transaction Type Selection ---
transaction_type = st.selectbox(
    "Transaction Type",
    ["Buy", "Sell", "Transfer", "Swap"]
)

# --- Dynamic Form Based on Transaction Type ---

form_data = {
    "person_name": person_name,
    "transaction_date": pd.to_datetime(transaction_date),
    "notes": notes
}

is_valid = False

# --- BUY FORM ---
if transaction_type == "Buy":
    buy_type = st.radio("What are you buying with?", ["Toman (IRR)", "USDT"], horizontal=True)
    
    if buy_type == "Toman (IRR)": # BuyUSDTForm
        st.subheader("Buy USDT with Toman")
        form_data["transaction_type"] = "buy_usdt_with_toman"
        form_data["input_currency"] = "IRR"
        form_data["output_currency"] = "USDT"
        
        with st.form("buy_usdt_form"):
            col1, col2 = st.columns(2)
            form_data["input_amount"] = col1.number_input("Amount in Toman (IRR)", min_value=0, step=100000, format="%d")
            form_data["output_amount"] = col2.number_input("Amount of USDT Received", min_value=0.0, step=0.01, format="%.2f")
            form_data["rate"] = st.number_input("USDT Rate in Toman", min_value=0, step=500, format="%d")
            
            # Calculation
            if form_data["input_amount"] and form_data["output_amount"]:
                effective_cost = form_data["input_amount"] / form_data["output_amount"]
                form_data["fee"] = form_data["input_amount"] - (form_data["output_amount"] * form_data["rate"])
                st.success(f"Effective Cost per USDT: {effective_cost:,.2f} Toman")
            
            submitted = st.form_submit_button("Save Transaction")
            if submitted:
                is_valid = all([form_data["input_amount"], form_data["output_amount"], form_data["rate"]])

    else: # BuyCryptoForm
        st.subheader("Buy Crypto with USDT")
        form_data["transaction_type"] = "buy_crypto_with_usdt"
        form_data["input_currency"] = "USDT"
        
        with st.form("buy_crypto_form"):
            form_data["output_currency"] = st.selectbox("Crypto to Buy", CRYPTOS)
            col1, col2 = st.columns(2)
            form_data["input_amount"] = col1.number_input("Amount of USDT Spent", min_value=0.0, step=0.01, format="%.2f")
            form_data["output_amount"] = col2.number_input("Amount of Crypto Received", min_value=0.0, step=0.000001, format="%.6f")

            submitted = st.form_submit_button("Save Transaction")
            if submitted:
                is_valid = all([form_data["input_amount"], form_data["output_amount"], form_data["output_currency"]])

# --- SELL FORM ---
elif transaction_type == "Sell":
    st.subheader("Sell Crypto for USDT")
    form_data["transaction_type"] = "sell"
    form_data["output_currency"] = "USDT"

    with st.form("sell_form"):
        form_data["input_currency"] = st.selectbox("Crypto to Sell", CRYPTOS)
        col1, col2 = st.columns(2)
        form_data["input_amount"] = col1.number_input("Amount of Crypto Sold", min_value=0.0, step=0.000001, format="%.6f")
        form_data["output_amount"] = col2.number_input("Amount of USDT Received", min_value=0.0, step=0.01, format="%.2f")

        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            is_valid = all([form_data["input_amount"], form_data["output_amount"], form_data["input_currency"]])

# --- TRANSFER FORM ---
elif transaction_type == "Transfer":
    st.subheader("Transfer Currency")
    form_data["transaction_type"] = "transfer"

    with st.form("transfer_form"):
        currency = st.selectbox("Currency Transferred", CURRENCIES)
        form_data["input_currency"] = currency
        form_data["output_currency"] = currency
        col1, col2 = st.columns(2)
        form_data["input_amount"] = col1.number_input("Amount Sent", min_value=0.0, step=0.000001, format="%.6f")
        form_data["output_amount"] = col2.number_input("Amount Received", min_value=0.0, step=0.000001, format="%.6f")
        
        if form_data["input_amount"] and form_data["output_amount"]:
            fee = form_data["input_amount"] - form_data["output_amount"]
            form_data["fee"] = fee
            st.info(f"Transfer Fee: {fee:,.6f} {currency}")

        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            is_valid = all([form_data["input_amount"], form_data["output_amount"], currency])

# --- SWAP FORM ---
elif transaction_type == "Swap":
    st.subheader("Swap Currency")
    form_data["transaction_type"] = "swap"
    
    with st.form("swap_form"):
        col1, col2 = st.columns(2)
        form_data["input_currency"] = col1.selectbox("Source Currency", CURRENCIES)
        form_data["output_currency"] = col2.selectbox("Destination Currency", CURRENCIES)
        col1, col2 = st.columns(2)
        form_data["input_amount"] = col1.number_input("Amount Swapped", min_value=0.0, step=0.000001, format="%.6f")
        form_data["output_amount"] = col2.number_input("Amount Received", min_value=0.0, step=0.000001, format="%.6f")

        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            is_valid = all([
                form_data["input_amount"], form_data["output_amount"],
                form_data["input_currency"], form_data["output_currency"],
                form_data["input_currency"] != form_data["output_currency"]
            ])
            if form_data["input_currency"] == form_data["output_currency"]:
                st.error("Source and destination currency cannot be the same.")


# --- Submission Logic ---
if is_valid:
    # Clean up data before saving
    data_to_save = {k: v for k, v in form_data.items() if v is not None}
    if "rate" not in data_to_save: data_to_save["rate"] = None
    if "fee" not in data_to_save: data_to_save["fee"] = None
    
    add_transaction(data_to_save)
    st.success("Transaction saved successfully!")
    st.balloons()
elif submitted: # 'submitted' is True but 'is_valid' is False
    st.error("Please fill in all required fields correctly.")
