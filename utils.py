import streamlit as st
import pandas as pd
import requests
import time

DATA_FILE = "transactions.csv"

def _ensure_data_types(df):
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
    if 'transactions' in st.session_state: return
    try:
        transactions_df = pd.read_csv(DATA_FILE); st.session_state.transactions = _ensure_data_types(transactions_df)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        st.session_state.transactions = _ensure_data_types(pd.DataFrame())
    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0
    if 'edit_transaction_id' not in st.session_state: st.session_state.edit_transaction_id = None

TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]; CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]; CURRENCIES = ["USDT"] + CRYPTOS

def get_all_transactions():
    if 'transactions' in st.session_state:
        df = _ensure_data_types(st.session_state.transactions.copy()); return df.sort_values(by="transaction_date", ascending=False)
    return _ensure_data_types(pd.DataFrame())

def add_transaction(data):
    df = get_all_transactions(); new_id = str(pd.Timestamp.now().timestamp())
    new_df = pd.concat([df, pd.DataFrame([{"id": new_id, **data}])], ignore_index=True)
    st.session_state.transactions = _ensure_data_types(new_df); _save_transactions()

def update_transaction(id, data):
    df = get_all_transactions(); idx = df.index[df['id'] == id]
    if not idx.empty:
        for key, value in data.items(): df.loc[idx, key] = value
    st.session_state.transactions = _ensure_data_types(df); _save_transactions()

def delete_transaction(transaction_id):
    df = get_all_transactions(); st.session_state.transactions = df[df['id'] != transaction_id]; _save_transactions()

def get_current_balance(person_name, currency_symbol, tx_id_to_exclude=None):
    transactions = get_all_transactions()
    if tx_id_to_exclude: transactions = transactions[transactions['id'] != tx_id_to_exclude]
    if transactions.empty: return 0.0
    person_tx = transactions[transactions['person_name'] == person_name]
    if person_tx.empty: return 0.0
    gains = person_tx[person_tx['output_currency'] == currency_symbol]['output_amount'].sum()
    losses = person_tx[person_tx['input_currency'] == currency_symbol]['input_amount'].sum()
    return gains - losses

def update_prices_in_state(symbols, force_refresh=False):
    # ... (This function is correct and remains unchanged)

# --- The Final, Truly Corrected Analysis Function ---
def generate_financial_analysis(transactions, prices):
    tx = _ensure_data_types(transactions.copy())
    empty_df = pd.DataFrame()
    if tx.empty: return empty_df, empty_df, empty_df, empty_df

    # --- STEP 1: Calculate all fees in USD and store in a new column ---
    tx['fee_usd'] = tx['fee'] # Start with explicit fees
    toman_mask = tx['transaction_type'] == 'buy_usdt_with_toman'
    if toman_mask.any():
        rate = tx.loc[toman_mask, 'rate']
        hidden_fee_usd = (tx.loc[toman_mask, 'input_amount'] / rate.replace(0, pd.NA)) - tx.loc[toman_mask, 'output_amount']
        tx.loc[toman_mask, 'fee_usd'] = hidden_fee_usd.fillna(0)
    transfer_mask = tx['transaction_type'] == 'transfer'
    if transfer_mask.any():
        fee_amount = tx.loc[transfer_mask, 'input_amount'] - tx.loc[transfer_mask, 'output_amount']
        fee_currency_price = tx.loc[transfer_mask, 'input_currency'].map(prices).fillna(1.0)
        tx.loc[transfer_mask, 'fee_usd'] = fee_amount * fee_currency_price

    # --- STEP 2: Create a cumulative fee pool for each person ---
    unallocated_fees = tx[tx['transaction_type'].isin(['buy_usdt_with_toman', 'transfer'])]
    fee_pool = unallocated_fees.groupby('person_name')['fee_usd'].sum().to_dict()

    # --- STEP 3: Calculate Cost Basis, now including a share of the fee pool ---
    acquisitions = tx[tx['transaction_type'].isin(['buy_crypto_with_usdt', 'swap'])].copy()
    if not acquisitions.empty:
        person_total_acquisition_cost = acquisitions.groupby('person_name')['input_amount'].sum().to_dict()
        def allocate_fees(row):
            person = row['person_name']
            total_cost = person_total_acquisition_cost.get(person, 0)
            if total_cost == 0: return 0
            prorated_fee = (fee_pool.get(person, 0) * row['input_amount']) / total_cost
            return prorated_fee
        
        acquisitions['allocated_fee'] = acquisitions.apply(allocate_fees, axis=1)
        acquisitions['total_cost'] = acquisitions['input_amount'] + acquisitions['fee_usd'] + acquisitions['allocated_fee']
        cost_basis_agg = acquisitions.groupby(['person_name', 'output_currency']).agg(total_cost_usd=('total_cost', 'sum'), total_amount_crypto=('output_amount', 'sum')).reset_index()
        cost_basis_agg['avg_buy_price'] = cost_basis_agg['total_cost_usd'] / cost_basis_agg['total_amount_crypto']
        cost_basis = cost_basis_agg.rename(columns={'output_currency': 'currency'})
    else:
        cost_basis = pd.DataFrame(columns=['person_name', 'currency', 'avg_buy_price'])

    # --- STEP 4: The rest of the analysis now uses the corrected cost basis ---
    portfolio = pd.concat([...]).groupby(['person_name', 'currency'])['amount'].sum().reset_index()
    portfolio_analysis = pd.merge(portfolio, cost_basis, on=['person_name', 'currency'], how='left')
    
    if prices and not portfolio_analysis.empty:
        portfolio_analysis['current_price'] = portfolio_analysis['currency'].map(prices)
        portfolio_analysis['current_value_usd'] = portfolio_analysis['amount'] * portfolio_analysis['current_price']
        portfolio_analysis['total_cost_of_holdings'] = portfolio_analysis['amount'] * portfolio_analysis['avg_buy_price']
        portfolio_analysis['floating_pnl_usd'] = portfolio_analysis['current_value_usd'] - portfolio_analysis['total_cost_of_holdings']

    # ... (The rest of the function for realized P/L and fee summary remains largely the same)
    
    return portfolio_analysis.fillna(0), toman_stats, realized_pnl_summary, fee_summary
