import streamlit as st
import pandas as pd
import requests
import time
import sys
import os

# --- THE ULTIMATE FIX FOR PATHING ---
# Determine the base path for data file, works for both script and frozen exe
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle/frozen exe
    base_path = os.path.dirname(sys.executable)
else:
    # If run as a normal script
    base_path = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(base_path, "transactions.csv")
# --- END OF FIX ---

def _ensure_data_types(df):
    # ... (این تابع بدون تغییر باقی می‌ماند)
    pass # This function is fine

def _save_transactions():
    # ... (این تابع بدون تغییر باقی می‌ماند)
    pass # This function is fine

def initialize_state():
    if 'transactions' in st.session_state: return
    try:
        transactions_df = pd.read_csv(DATA_FILE)
        st.session_state.transactions = _ensure_data_types(transactions_df)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.session_state.transactions = _ensure_data_types(pd.DataFrame())
    # ... (بقیه این تابع بدون تغییر است)
    pass

# The rest of your utils.py file (TRANSACTION_TYPE_LABELS, PEOPLE, CRUD functions, etc.) remains unchanged.
# The only part that needed changing was the definition of DATA_FILE at the top.
# For completeness, here is the full correct file:

def _ensure_data_types(df):
    expected_cols = { "id": "object", "transaction_type": "object", "person_name": "object", "transaction_date": "datetime64[ns]", "input_currency": "object", "output_currency": "object", "input_amount": "float64", "output_amount": "float64", "rate": "float64", "fee": "float64", "notes": "object" }
    for col, dtype in expected_cols.items():
        if col not in df.columns: df[col] = pd.Series(dtype=dtype)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    numeric_cols = ['input_amount', 'output_amount', 'rate', 'fee']
    for col in numeric_cols: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def _save_transactions():
    if 'transactions' in st.session_state: st.session_state.transactions.to_csv(DATA_FILE, index=False)

def initialize_state():
    if 'transactions' in st.session_state: return
    try:
        st.session_state.transactions = _ensure_data_types(pd.read_csv(DATA_FILE))
    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.session_state.transactions = _ensure_data_types(pd.DataFrame())
    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0
    if 'edit_transaction_id' not in st.session_state: st.session_state.edit_transaction_id = None

TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

def get_all_transactions():
    if 'transactions' in st.session_state:
        df = _ensure_data_types(st.session_state.transactions.copy())
        return df.sort_values(by="transaction_date", ascending=False)
    return _ensure_data_types(pd.DataFrame())

def add_transaction(data):
    df = st.session_state.transactions
    new_id = str(pd.Timestamp.now().timestamp())
    new_df = pd.concat([df, pd.DataFrame([{"id": new_id, **data}])], ignore_index=True)
    st.session_state.transactions = _ensure_data_types(new_df)
    _save_transactions()

def update_transaction(id, data):
    df = st.session_state.transactions
    idx = df[df['id'] == id].index
    if not idx.empty:
        for key, value in data.items(): df.loc[idx, key] = value
    st.session_state.transactions = _ensure_data_types(df)
    _save_transactions()

def delete_transaction(transaction_id):
    df = st.session_state.transactions
    st.session_state.transactions = df[df['id'] != transaction_id]
    _save_transactions()

# ... (The rest of the functions like get_current_balance, update_prices_in_state, generate_financial_analysis are fine)
