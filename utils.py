import streamlit as st
import pandas as pd
import requests
import time
import sys
import os
import sqlite3 # --- NEW: Import the SQLite library ---

# --- DATABASE SETUP ---
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(base_path, "crypto_transactions.db")

def get_db_connection():
    """Creates a connection to the SQLite database and the transactions table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        transaction_type TEXT,
        person_name TEXT,
        transaction_date TEXT,
        input_currency TEXT,
        output_currency TEXT,
        input_amount REAL,
        output_amount REAL,
        rate REAL,
        fee REAL,
        notes TEXT
    )
    ''')
    return conn

# --- MODIFIED: This function now loads from the database ---
def initialize_state():
    if 'transactions' in st.session_state: return
    
    conn = get_db_connection()
    # Use pandas to read the entire SQL table into a DataFrame on startup
    st.session_state.transactions = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    
    # Ensure data types are correct after loading from DB
    st.session_state.transactions = _ensure_data_types(st.session_state.transactions)

    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0
    if 'edit_transaction_id' not in st.session_state: st.session_state.edit_transaction_id = None

# --- MODIFIED: All CRUD functions now talk to the database AND update the session state ---
def add_transaction(data):
    # 1. Update the database
    conn = get_db_connection()
    # Create a DataFrame from the new data to easily insert
    new_tx_df = pd.DataFrame([data])
    new_tx_df['id'] = str(pd.Timestamp.now().timestamp()) # Assign ID here
    new_tx_df.to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()
    
    # 2. Update the session state DataFrame for immediate UI refresh
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_tx_df], ignore_index=True)
    st.session_state.transactions = _ensure_data_types(st.session_state.transactions)

def update_transaction(id, data):
    # 1. Update the database
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create the SET part of the SQL query dynamically
    set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
    values = list(data.values()) + [id]
    cursor.execute(f"UPDATE transactions SET {set_clause} WHERE id = ?", tuple(values))
    conn.commit()
    conn.close()

    # 2. Update the session state DataFrame
    idx = st.session_state.transactions[st.session_state.transactions['id'] == id].index
    if not idx.empty:
        for key, value in data.items():
            st.session_state.transactions.loc[idx, key] = value
    st.session_state.transactions = _ensure_data_types(st.session_state.transactions)

def delete_transaction(transaction_id):
    # 1. Update the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()

    # 2. Update the session state DataFrame
    st.session_state.transactions = st.session_state.transactions[st.session_state.transactions['id'] != transaction_id]

# --- ALL OTHER FUNCTIONS BELOW THIS LINE REMAIN UNCHANGED ---
# They don't care where the data comes from; they just operate on the DataFrame.

def _ensure_data_types(df):
    # ... (This function is still needed and remains unchanged)
    expected_cols = { "id": "object", "transaction_type": "object", "person_name": "object", "transaction_date": "datetime64[ns]", "input_currency": "object", "output_currency": "object", "input_amount": "float64", "output_amount": "float64", "rate": "float64", "fee": "float64", "notes": "object" }
    for col, dtype in expected_cols.items():
        if col not in df.columns: df[col] = pd.Series(dtype=dtype)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    numeric_cols = ['input_amount', 'output_amount', 'rate', 'fee']
    for col in numeric_cols: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

def get_all_transactions():
    if 'transactions' in st.session_state:
        return _ensure_data_types(st.session_state.transactions.copy()).sort_values(by="transaction_date", ascending=False)
    return _ensure_data_types(pd.DataFrame())

def get_current_balance(person_name, currency_symbol, transactions_df=None):
    # ... (Unchanged)
    if transactions_df is None: transactions_df = get_all_transactions()
    if transactions_df.empty: return 0.0
    person_tx = transactions_df[transactions_df['person_name'] == person_name]
    gains = person_tx[person_tx['output_currency'] == currency_symbol]['output_amount'].sum()
    losses = person_tx[person_tx['input_currency'] == currency_symbol]['input_amount'].sum()
    return gains - losses

def update_prices_in_state(symbols, force_refresh=False):
    # ... (Unchanged)
    pass

def generate_financial_analysis(transactions, prices):
    # ... (Unchanged - The Brain of the app still works perfectly!)
    pass
