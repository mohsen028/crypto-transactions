import streamlit as st
import pandas as pd
import time
from utils import initialize_state, get_all_transactions, update_prices_in_state, generate_financial_analysis, TRANSACTION_TYPE_LABELS

st.set_page_config(page_title="Crypto Dashboard", layout="wide")
initialize_state()
transactions = get_all_transactions()
st.title("Crypto Financial Dashboard")

# --- FIX: Handle empty transactions DataFrame ---
unique_symbols = []
if not transactions.empty:
    all_symbols = pd.concat([transactions['input_currency'], transactions['output_currency']]).dropna().unique()
    unique_symbols = [s for s in all_symbols if s != 'IRR']

update_prices_in_state(unique_symbols)
if st.button("Refresh Live Prices"): update_prices_in_state(unique_symbols, force_refresh=True)

# ... بقیه کد بدون تغییر باقی می‌ماند
last_update = st.session_state.get('last_price_fetch', 0)
if last_update > 0: st.caption(f"Prices last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_update))}")
st.caption("Price data provided by CoinGecko.")
st.markdown("---")

prices = st.session_state.get('prices', {})
portfolio_df, toman_stats_df, realized_pnl_df, fee_summary_df = generate_financial_analysis(transactions, prices)

tab1, tab2, tab3, tab4 = st.tabs(["Floating P/L", "Realized P/L", "Toman Exchange", "Fee Analysis"])

with tab1:
    st.subheader("Current Portfolio & Floating Profit/Loss")
    if portfolio_df.empty: st.info("No current holdings to analyze.")
    else:
        pnl_summary = portfolio_df.groupby('person_name').agg(total_value=('current_value_usd', 'sum'), total_cost=('total_cost_of_holdings', 'sum')).reset_index()
        pnl_summary['floating_pnl'] = pnl_summary['total_value'] - pnl_summary['total_cost']
        for _, row in pnl_summary.iterrows():
            with st.container(border=True):
                st.markdown(f"#### {row['person_name'].capitalize()}")
                delta_percent = (row['floating_pnl'] / row['total_cost']) * 100 if row['total_cost'] > 0 else 0
                c1,c2,c3 = st.columns(3); c1.metric("Market Value", f"${row['total_value']:,.2f}"); c2.metric("Total Cost", f"${row['total_cost']:,.2f}"); c3.metric("Floating P/L", f"${row['floating_pnl']:,.2f}", f"{delta_percent:.2f}%")

with tab2:
    st.subheader("Realized Profit/Loss from Sales & Swaps")
    if realized_pnl_df.empty: st.info("No sales or swaps have been recorded yet.")
    else: st.dataframe(realized_pnl_df, column_config={"person_name": "Person", "realized_pnl": st.column_config.NumberColumn("Net Realized P/L (USD)", format="$%.2f")}, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Toman-to-USDT Exchange Statistics")
    if toman_stats_df.empty: st.info("No Toman-to-USDT transactions recorded.")
    else: st.dataframe(toman_stats_df, column_config={"person_name": "Person", "total_toman_paid": st.column_config.NumberColumn("Total Toman Paid", format="%,.0f Toman"), "total_usdt_received": st.column_config.NumberColumn("Total USDT Received", format="%.2f USDT"), "avg_usdt_cost": st.column_config.NumberColumn("Avg. Cost per USDT", format="%,.0f Toman")}, hide_index=True, use_container_width=True)

with tab4:
    st.subheader("Comprehensive Fee Breakdown (in USD)")
    if fee_summary_df.empty:
        st.info("No fees have been recorded.")
    else:
        total_fees_per_person = fee_summary_df.groupby('person_name')['fee'].sum().reset_index().rename(columns={'fee': 'total_fee'})
        st.markdown("#### Total Fees Per Person")
        st.dataframe(total_fees_per_person, column_config={"person_name": "Person", "total_fee": st.column_config.NumberColumn("Total Fees Paid (USD)", format="$%.2f")}, hide_index=True, use_container_width=True)
        with st.expander("See detailed breakdown"):
            display_fees = fee_summary_df.copy()
            display_fees['transaction_type'] = display_fees['transaction_type'].map(TRANSACTION_TYPE_LABELS).fillna(display_fees['transaction_type'])
            st.dataframe(display_fees, column_config={"person_name": "Person", "transaction_type": "Transaction Type", "fee": st.column_config.NumberColumn("Fee (USD)", format="$%.2f")}, hide_index=True, use_container_width=True)```

---

#### ۲. فایل `utils.py`
(فقط ایموجی‌های `icon` از `st.toast` حذف شدند)

```python
import streamlit as st
import pandas as pd
import requests
import time
import sys
import os
import sqlite3

# --- DATABASE SETUP ---
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(base_path, "crypto_transactions.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY, transaction_type TEXT, person_name TEXT, transaction_date TEXT,
        input_currency TEXT, output_currency TEXT, input_amount REAL, output_amount REAL,
        rate REAL, fee REAL, notes TEXT
    )''')
    return conn

# --- DATA CONSISTENCY ---
def _ensure_data_types(df):
    expected_cols = { "id": "object", "transaction_type": "object", "person_name": "object", "transaction_date": "datetime64[ns]", "input_currency": "object", "output_currency": "object", "input_amount": "float64", "output_amount": "float64", "rate": "float64", "fee": "float64", "notes": "object" }
    for col, dtype in expected_cols.items():
        if col not in df.columns: df[col] = pd.Series(dtype=dtype)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    numeric_cols = ['input_amount', 'output_amount', 'rate', 'fee']
    for col in numeric_cols: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def initialize_state():
    if 'transactions' in st.session_state: return
    conn = get_db_connection()
    st.session_state.transactions = _ensure_data_types(pd.read_sql_query("SELECT * FROM transactions", conn))
    conn.close()
    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0
    if 'edit_transaction_id' not in st.session_state: st.session_state.edit_transaction_id = None

# --- CRUD OPERATIONS WITH SQLITE ---
def add_transaction(data):
    conn = get_db_connection()
    new_id = str(pd.Timestamp.now().timestamp())
    data_with_id = {**data, 'id': new_id}
    new_tx_df = pd.DataFrame([data_with_id])
    new_tx_df.to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_tx_df], ignore_index=True)

def update_transaction(id, data):
    conn = get_db_connection()
    set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
    values = list(data.values()) + [id]
    conn.execute(f"UPDATE transactions SET {set_clause} WHERE id = ?", tuple(values))
    conn.commit(); conn.close()
    idx = st.session_state.transactions[st.session_state.transactions['id'] == id].index
    if not idx.empty:
        for key, value in data.items(): st.session_state.transactions.loc[idx, key] = value
    st.session_state.transactions = _ensure_data_types(st.session_state.transactions)

def delete_transaction(transaction_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit(); conn.close()
    st.session_state.transactions = st.session_state.transactions[st.session_state.transactions['id'] != transaction_id]

# --- CONSTANTS AND HELPERS (UNCHANGED) ---
TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

def get_all_transactions():
    if 'transactions' in st.session_state:
        return _ensure_data_types(st.session_state.transactions.copy()).sort_values(by="transaction_date", ascending=False)
    return _ensure_data_types(pd.DataFrame())

def get_current_balance(person_name, currency_symbol, transactions_df=None):
    if transactions_df is None: transactions_df = get_all_transactions()
    if transactions_df.empty: return 0.0
    person_tx = transactions_df[transactions_df['person_name'] == person_name]
    gains = person_tx[person_tx['output_currency'] == currency_symbol]['output_amount'].sum()
    losses = person_tx[person_tx['input_currency'] == currency_symbol]['input_amount'].sum()
    return gains - losses

def update_prices_in_state(symbols, force_refresh=False):
    now = time.time()
    if not force_refresh and (now - st.session_state.get('last_price_fetch', 0)) < 300: return
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
        if force_refresh: st.toast("Prices updated!")
    except requests.exceptions.RequestException:
        if force_refresh: st.toast("Failed to update prices.")

# --- THE BRAIN OF THE APP - FULLY RESTORED ---
def generate_financial_analysis(transactions, prices):
    tx = _ensure_data_types(transactions.copy())
    if tx.empty:
        empty_df = pd.DataFrame()
        return empty_df, empty_df, empty_df, empty_df

    tx['calculated_fee'] = tx['fee']
    toman_mask = tx['transaction_type'] == 'buy_usdt_with_toman'
    if toman_mask.any():
        rate = tx.loc[toman_mask, 'rate']
        hidden_fee_usd = (tx.loc[toman_mask, 'input_amount'] / rate.replace(0, pd.NA)) - tx.loc[toman_mask, 'output_amount']
        tx.loc[toman_mask, 'calculated_fee'] = hidden_fee_usd.fillna(0)

    transfer_mask = tx['transaction_type'] == 'transfer'
    if transfer_mask.any():
        fee_amount = tx.loc[transfer_mask, 'input_amount'] - tx.loc[transfer_mask, 'output_amount']
        fee_currency_price = tx.loc[transfer_mask, 'input_currency'].map(prices).fillna(1.0)
        tx.loc[transfer_mask, 'calculated_fee'] = fee_amount * fee_currency_price

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
