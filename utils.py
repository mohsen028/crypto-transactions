import streamlit as st
import pandas as pd
import requests
import time

DATA_FILE = "transactions.csv"

# --- The Ultimate Data Sanitization Function ---
def _ensure_data_types(df):
    """This function is the ultimate safeguard. It ensures the DataFrame has the correct columns and data types, no matter what."""
    expected_cols = {
        "id": "object", "transaction_type": "object", "person_name": "object",
        "transaction_date": "datetime64[ns]", "input_currency": "object", "output_currency": "object",
        "input_amount": "float64", "output_amount": "float64", "rate": "float64",
        "fee": "float64", "notes": "object"
    }
    
    # Ensure all columns exist, fill missing ones with empty typed Series
    for col, dtype in expected_cols.items():
        if col not in df.columns:
            df[col] = pd.Series(dtype=dtype)

    # Coerce data types for existing columns
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    
    numeric_cols = ['input_amount', 'output_amount', 'rate', 'fee']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    string_cols = ['id', 'transaction_type', 'person_name', 'input_currency', 'output_currency', 'notes']
    for col in string_cols:
        df[col] = df[col].astype(str).fillna('')

    return df

def _save_transactions():
    if 'transactions' in st.session_state:
        st.session_state.transactions.to_csv(DATA_FILE, index=False)

def initialize_state():
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

# --- CRUD functions now use the sanitizer on retrieval ---
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
        for key, value in data.items():
            df.loc[idx, key] = value
    st.session_state.transactions = _ensure_data_types(df)
    _save_transactions()

def delete_transaction(transaction_id):
    df = st.session_state.transactions
    st.session_state.transactions = df[df['id'] != transaction_id]
    _save_transactions()

def update_prices_in_state(symbols, force_refresh=False):
    # ... (This function remains unchanged)
    pass

def generate_financial_analysis(transactions, prices):
    # As the final safeguard, sanitize the data one more time.
    tx = _ensure_data_types(transactions.copy())
    if tx.empty: 
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # The rest of this powerful function remains unchanged as it now trusts the data it receives.
    # ...
    return portfolio_analysis.fillna(0), toman_stats, realized_pnl_summary, fee_summary
