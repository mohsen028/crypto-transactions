import streamlit as st
import pandas as pd
import requests
import time

DATA_FILE = "transactions.csv"

# --- Helper functions for data consistency and saving ---
def _ensure_data_types(df):
    # ... (این بخش بدون تغییر باقی می‌ماند)
    if df.empty: return df
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    for col in ['input_amount', 'output_amount', 'rate', 'fee']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def _save_transactions():
    if 'transactions' in st.session_state:
        st.session_state.transactions.to_csv(DATA_FILE, index=False)

# --- Main state and data functions ---
def initialize_state():
    # ... (بدون تغییر)
    if 'transactions' in st.session_state: return
    try:
        transactions_df = pd.read_csv(DATA_FILE)
        st.session_state.transactions = _ensure_data_types(transactions_df)
    except FileNotFoundError:
        st.session_state.transactions = pd.DataFrame(columns=["id", "transaction_type", "person_name", "transaction_date", "input_currency", "output_currency", "input_amount", "output_amount", "rate", "fee", "notes"])
    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0
    if 'edit_transaction_id' not in st.session_state: st.session_state.edit_transaction_id = None

# --- Constants (No change) ---
TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

# --- CRUD functions with save hooks (No change) ---
def get_all_transactions(): 
    # ... (بدون تغییر)
    if 'transactions' in st.session_state and not st.session_state.transactions.empty:
        df = _ensure_data_types(st.session_state.transactions)
        return df.sort_values(by="transaction_date", ascending=False)
    return pd.DataFrame()

def add_transaction(data):
    # ... (بدون تغییر)
    df = st.session_state.transactions
    new_id = str(pd.Timestamp.now().timestamp())
    new_df = pd.concat([df, pd.DataFrame([{"id": new_id, **data}])], ignore_index=True)
    st.session_state.transactions = _ensure_data_types(new_df)
    _save_transactions()

def update_transaction(id, data):
    # ... (بدون تغییر)
    df = st.session_state.transactions
    idx = df[df['id'] == id].index
    if not idx.empty:
        for key, value in data.items():
            df.loc[idx, key] = value
    st.session_state.transactions = _ensure_data_types(df)
    _save_transactions()

def delete_transaction(transaction_id):
    # ... (بدون تغییر)
    df = st.session_state.transactions
    st.session_state.transactions = df[df['id'] != transaction_id]
    _save_transactions()

# --- NEW: Balance Checking Function ---
def get_current_balance(person_name, currency_symbol):
    """Calculates the current balance of a specific currency for a specific person."""
    transactions = st.session_state.get('transactions', pd.DataFrame())
    if transactions.empty:
        return 0.0

    person_tx = transactions[transactions['person_name'] == person_name]
    if person_tx.empty:
        return 0.0

    gains = person_tx[person_tx['output_currency'] == currency_symbol]['output_amount'].sum()
    losses = person_tx[person_tx['input_currency'] == currency_symbol]['input_amount'].sum()
    
    return gains - losses

# --- Price Fetching and Financial Analysis (No change) ---
def update_prices_in_state(symbols, force_refresh=False):
    # ... (بدون تغییر)
    pass

def generate_financial_analysis(transactions, prices):
    # ... (این تابع جامع و قدرتمند بدون تغییر باقی می‌ماند)
    pass
