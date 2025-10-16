import streamlit as st
import pandas as pd
import requests
import time

DATA_FILE = "transactions.csv"

# --- Data Sanitization and Saving (No change) ---
def _ensure_data_types(df):
    # ... (This function is correct and remains unchanged)
    expected_cols = {"id": "object", "transaction_type": "object", "person_name": "object", "transaction_date": "datetime64[ns]", "input_currency": "object", "output_currency": "object", "input_amount": "float64", "output_amount": "float64", "rate": "float64", "fee": "float64", "notes": "object"}
    for col, dtype in expected_cols.items():
        if col not in df.columns: df[col] = pd.Series(dtype=dtype)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    for col in ['input_amount', 'output_amount', 'rate', 'fee']: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    for col in ['id', 'transaction_type', 'person_name', 'input_currency', 'output_currency', 'notes']: df[col] = df[col].astype(str).fillna('')
    return df

def _save_transactions():
    if 'transactions' in st.session_state: st.session_state.transactions.to_csv(DATA_FILE, index=False)

def initialize_state():
    # ... (No change)
    if 'transactions' in st.session_state: return
    try:
        transactions_df = pd.read_csv(DATA_FILE)
        st.session_state.transactions = _ensure_data_types(transactions_df)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.session_state.transactions = _ensure_data_types(pd.DataFrame())
    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0
    if 'edit_transaction_id' not in st.session_state: st.session_state.edit_transaction_id = None

# --- Constants (No change) ---
TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

# --- CRUD Functions (No change) ---
def get_all_transactions():
    # ... (No change)
    if 'transactions' in st.session_state:
        df = _ensure_data_types(st.session_state.transactions.copy())
        return df.sort_values(by="transaction_date", ascending=False)
    return _ensure_data_types(pd.DataFrame())

def add_transaction(data):
    # ... (No change)
    df = get_all_transactions(); new_id = str(pd.Timestamp.now().timestamp())
    new_df = pd.concat([df, pd.DataFrame([{"id": new_id, **data}])], ignore_index=True)
    st.session_state.transactions = _ensure_data_types(new_df); _save_transactions()

def update_transaction(id, data):
    # ... (No change)
    df = get_all_transactions(); idx = df.index[df['id'] == id]
    if not idx.empty:
        for key, value in data.items(): df.loc[idx, key] = value
    st.session_state.transactions = _ensure_data_types(df); _save_transactions()

def delete_transaction(transaction_id):
    # ... (No change)
    df = get_all_transactions(); st.session_state.transactions = df[df['id'] != transaction_id]; _save_transactions()

# --- MODIFIED: Balance Checking Function ---
def get_current_balance(person_name, currency_symbol, tx_id_to_exclude=None):
    """Calculates balance, optionally excluding one transaction (for edit validation)."""
    transactions = get_all_transactions()
    if tx_id_to_exclude:
        transactions = transactions[transactions['id'] != tx_id_to_exclude]
    if transactions.empty: return 0.0
    person_tx = transactions[transactions['person_name'] == person_name]
    if person_tx.empty: return 0.0
    gains = person_tx[person_tx['output_currency'] == currency_symbol]['output_amount'].sum()
    losses = person_tx[person_tx['input_currency'] == currency_symbol]['input_amount'].sum()
    return gains - losses

# --- Price Fetching and Financial Analysis (No change) ---
def update_prices_in_state(symbols, force_refresh=False):
    # ... (No change)
    pass

def generate_financial_analysis(transactions, prices):
    # ... (This powerful function is correct and remains unchanged)
    pass
