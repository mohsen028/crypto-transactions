import streamlit as st
import pandas as pd
import requests
import time

DATA_FILE = "transactions.csv"

def _ensure_data_types(df):
    if df.empty: return df
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    for col in ['input_amount', 'output_amount', 'rate', 'fee']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def _save_transactions():
    if 'transactions' in st.session_state:
        st.session_state.transactions.to_csv(DATA_FILE, index=False)

def initialize_state():
    if 'transactions' in st.session_state: return
    try:
        transactions_df = pd.read_csv(DATA_FILE)
        st.session_state.transactions = _ensure_data_types(transactions_df)
    except FileNotFoundError:
        st.session_state.transactions = pd.DataFrame(columns=["id", "transaction_type", "person_name", "transaction_date", "input_currency", "output_currency", "input_amount", "output_amount", "rate", "fee", "notes"])
    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0
    if 'edit_transaction_id' not in st.session_state: st.session_state.edit_transaction_id = None

TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

def get_all_transactions(): 
    if 'transactions' in st.session_state and not st.session_state.transactions.empty:
        df = _ensure_data_types(st.session_state.transactions)
        return df.sort_values(by="transaction_date", ascending=False)
    return pd.DataFrame()

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
    # ... (این تابع بدون تغییر باقی می‌ماند)
    now = time.time()
    if not force_refresh and (now - st.session_state.last_price_fetch) < 300: return
    if not symbols: return
    symbol_to_id = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin', 'SOL': 'solana', 'XRP': 'ripple', 'USDC': 'usd-coin', 'ADA': 'cardano', 'DOGE': 'dogecoin', 'DOT': 'polkadot', 'PAXG': 'pax-gold', 'USDT': 'tether'}
    ids = [symbol_to_id[s] for s in symbols if s in symbol_to_id]
    if not ids: return
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        prices = {symbol: data[id]['usd'] for symbol, id in symbol_to_id.items() if id in data}
        prices['USDT'] = 1.0
        st.session_state.prices.update(prices)
        st.session_state.last_price_fetch = now
        if force_refresh: st.toast("Prices updated!", icon="✅")
    except requests.exceptions.RequestException:
        if force_refresh: st.toast("Failed to update prices.", icon="❌")

# --- The Final, Corrected Analysis Function ---
def generate_financial_analysis(transactions, prices):
    if transactions.empty: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    tx = _ensure_data_types(transactions.copy())
    
    # --- Fee Calculation Stage ---
    # We create a new column `calculated_fee` to avoid overwriting user's explicit fee
    tx['calculated_fee'] = tx['fee'] # Start with the explicit fee

    # 1. Toman Buy Fee (in USD)
    toman_mask = tx['transaction_type'] == 'buy_usdt_with_toman'
    if toman_mask.any():
        rate = tx.loc[toman_mask, 'rate']
        hidden_fee_usd = (tx.loc[toman_mask, 'input_amount'] / rate.replace(0, pd.NA)) - tx.loc[toman_mask, 'output_amount']
        tx.loc[toman_mask, 'calculated_fee'] = hidden_fee_usd.fillna(0)

    # 2. Transfer Fee (in USD)
    transfer_mask = tx['transaction_type'] == 'transfer'
    if transfer_mask.any():
        fee_amount = tx.loc[transfer_mask, 'input_amount'] - tx.loc[transfer_mask, 'output_amount']
        fee_currency_price = tx.loc[transfer_mask, 'input_currency'].map(prices).fillna(1.0)
        tx.loc[transfer_mask, 'calculated_fee'] = fee_amount * fee_currency_price

    # 3. *** NEW: Swap Fee/Slippage Calculation (in USD) ***
    swap_mask = tx['transaction_type'] == 'swap'
    if swap_mask.any() and prices:
        value_given_usd = tx.loc[swap_mask, 'input_amount'] * tx.loc[swap_mask, 'input_currency'].map(prices).fillna(0)
        value_received_usd = tx.loc[swap_mask, 'output_amount'] * tx.loc[swap_mask, 'output_currency'].map(prices).fillna(0)
        slippage_fee = value_given_usd - value_received_usd
        # Add slippage to any explicit fee the user might have entered
        tx.loc[swap_mask, 'calculated_fee'] = tx.loc[swap_mask, 'calculated_fee'] + slippage_fee

    # --- Analysis Stage (using the new `calculated_fee` column) ---
    # (The rest of the function proceeds as before, but uses the corrected fees)
    
    toman_stats = tx[toman_mask].groupby('person_name').agg(total_toman_paid=('input_amount', 'sum'), total_usdt_received=('output_amount', 'sum')).reset_index()
    if not toman_stats.empty: toman_stats['avg_usdt_cost'] = toman_stats['total_toman_paid'] / toman_stats['total_usdt_received']
    
    acquisitions = tx[tx['transaction_type'].isin(['buy_crypto_with_usdt', 'swap'])].copy()
    if not acquisitions.empty:
        acquisitions['cost_in_usd'] = acquisitions.apply(lambda row: row['input_amount'] * prices.get(row['input_currency'], 1.0), axis=1)
        acquisitions['total_cost'] = acquisitions['cost_in_usd'] + acquisitions['calculated_fee']
        cost_basis_agg = acquisitions.groupby(['person_name', 'output_currency']).agg(total_cost_usd=('total_cost', 'sum'), total_amount_crypto=('output_amount', 'sum')).reset_index()
        cost_basis_agg['avg_buy_price'] = cost_basis_agg['total_cost_usd'] / cost_basis_agg['total_amount_crypto']
        cost_basis = cost_basis_agg.rename(columns={'output_currency': 'currency'})
    else: cost_basis = pd.DataFrame(columns=['person_name', 'currency', 'avg_buy_price'])
    
    portfolio = pd.concat([tx.rename(columns={'output_currency': 'currency', 'output_amount': 'amount'})[['person_name', 'currency', 'amount']], tx.rename(columns={'input_currency': 'currency', 'input_amount': 'amount'})[['person_name', 'currency', 'amount']].assign(amount=lambda df: -df['amount'])]).groupby(['person_name', 'currency'])['amount'].sum().reset_index()
    portfolio = portfolio[portfolio['amount'] > 1e-9]
    portfolio_analysis = pd.merge(portfolio, cost_basis, on=['person_name', 'currency'], how='left')
    
    if prices and not portfolio_analysis.empty:
        portfolio_analysis['current_price'] = portfolio_analysis['currency'].map(prices)
        portfolio_analysis['current_value_usd'] = portfolio_analysis['amount'] * portfolio_analysis['current_price']
        portfolio_analysis['total_cost_of_holdings'] = portfolio_analysis['amount'] * portfolio_analysis['avg_buy_price']
        portfolio_analysis['floating_pnl_usd'] = portfolio_analysis['current_value_usd'] - portfolio_analysis['total_cost_of_holdings']
    
    disposals = tx[tx['transaction_type'].isin(['sell', 'swap'])].copy()
    if not disposals.empty and not cost_basis.empty:
        disposals = pd.merge(disposals, cost_basis, left_on=['person_name', 'input_currency'], right_on=['person_name', 'currency'], how='left')
        disposals['value_received_usd'] = disposals.apply(lambda row: row['output_amount'] * prices.get(row['output_currency'], 1.0), axis=1)
        disposals['cost_of_goods_sold'] = disposals['input_amount'] * disposals['avg_buy_price']
        disposals['realized_pnl'] = disposals['value_received_usd'] - disposals['cost_of_goods_sold'] - disposals['calculated_fee']
        realized_pnl_summary = disposals.groupby('person_name')['realized_pnl'].sum().reset_index()
    else: realized_pnl_summary = pd.DataFrame(columns=['person_name', 'realized_pnl'])
    
    fee_summary = tx[tx['calculated_fee'] > 0].groupby(['person_name', 'transaction_type'])['calculated_fee'].sum().reset_index().rename(columns={'calculated_fee': 'fee'})
    
    return portfolio_analysis.fillna(0), toman_stats, realized_pnl_summary, fee_summary
