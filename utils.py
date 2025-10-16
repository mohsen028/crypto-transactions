import streamlit as st
import pandas as pd
import requests
import time

def initialize_state():
    # --- FIX: Start with an EMPTY but structured DataFrame ---
    if 'transactions' not in st.session_state:
        st.session_state.transactions = pd.DataFrame(columns=[
            "id", "transaction_type", "person_name", "transaction_date",
            "input_currency", "output_currency", "input_amount", "output_amount",
            "rate", "fee", "notes"
        ])
        # Ensure correct data types for empty df
        st.session_state.transactions['transaction_date'] = pd.to_datetime(st.session_state.transactions['transaction_date'])
        st.session_state.transactions['input_amount'] = st.session_state.transactions['input_amount'].astype(float)
        st.session_state.transactions['output_amount'] = st.session_state.transactions['output_amount'].astype(float)
        st.session_state.transactions['fee'] = st.session_state.transactions['fee'].astype(float)
        st.session_state.transactions['rate'] = st.session_state.transactions['rate'].astype(float)

    if 'prices' not in st.session_state: st.session_state.prices = {}
    if 'last_price_fetch' not in st.session_state: st.session_state.last_price_fetch = 0

# --- Constants and Basic Functions (No change) ---
TRANSACTION_TYPE_LABELS = {"buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto", "sell": "Sell", "transfer": "Transfer", "swap": "Swap"}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS
def get_all_transactions(): return st.session_state.transactions.sort_values(by="transaction_date", ascending=False) if 'transactions' in st.session_state else pd.DataFrame()
def add_transaction(data):
    df = st.session_state.transactions
    new_id = str(pd.Timestamp.now().timestamp())
    st.session_state.transactions = pd.concat([df, pd.DataFrame([{"id": new_id, **data}])], ignore_index=True)
def delete_transaction(transaction_id):
    df = st.session_state.transactions
    st.session_state.transactions = df[df['id'] != transaction_id]
def update_prices_in_state(symbols, force_refresh=False):
    now = time.time()
    if not force_refresh and (now - st.session_state.last_price_fetch) < 300: return
    if not symbols: return
    symbol_to_id = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin', 'SOL': 'solana', 'XRP': 'ripple', 'USDC': 'usd-coin', 'ADA': 'cardano', 'DOGE': 'dogecoin', 'DOT': 'polkadot', 'PAXG': 'pax-gold', 'USDT': 'tether'}
    ids = [symbol_to_id[s] for s in symbols if s in symbol_to_id]
    if not ids: return
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = {symbol: data[id]['usd'] for symbol, id in symbol_to_id.items() if id in data}
        prices['USDT'] = 1.0
        st.session_state.prices.update(prices)
        st.session_state.last_price_fetch = now
        if force_refresh: st.toast("Prices updated!", icon="✅")
    except requests.exceptions.RequestException:
        if force_refresh: st.toast("Failed to update prices.", icon="❌")

# --- NEW: Bulletproof Financial Analysis Function ---
def generate_financial_analysis(transactions, prices):
    # --- FIX: Define empty but structured dataframes to return on empty input ---
    empty_portfolio = pd.DataFrame(columns=['person_name', 'currency', 'amount', 'avg_buy_price', 'current_price', 'current_value_usd', 'total_cost_of_holdings', 'floating_pnl_usd'])
    empty_toman = pd.DataFrame(columns=['person_name', 'total_toman_paid', 'total_usdt_received', 'avg_usdt_cost'])
    empty_realized = pd.DataFrame(columns=['person_name', 'realized_pnl'])
    empty_fees = pd.DataFrame(columns=['person_name', 'transaction_type', 'fee'])

    if transactions.empty:
        return empty_portfolio, empty_toman, empty_realized, empty_fees

    # 1. Toman/USDT Analysis
    toman_tx = transactions[transactions['transaction_type'] == 'buy_usdt_with_toman'].copy()
    if not toman_tx.empty:
        toman_stats = toman_tx.groupby('person_name').agg(total_toman_paid=('input_amount', 'sum'), total_usdt_received=('output_amount', 'sum')).reset_index()
        toman_stats['avg_usdt_cost'] = toman_stats['total_toman_paid'] / toman_stats['total_usdt_received']
    else:
        toman_stats = empty_toman

    # 2. Comprehensive Cost Basis
    acquisitions = []
    buy_tx = transactions[transactions['transaction_type'] == 'buy_crypto_with_usdt'].copy()
    if not buy_tx.empty:
        buy_tx['total_cost'] = buy_tx['input_amount'] + buy_tx.get('fee', 0)
        acquisitions.append(buy_tx[['person_name', 'output_currency', 'output_amount', 'total_cost']])
    swap_tx = transactions[(transactions['transaction_type'] == 'swap') & (transactions['input_currency'] == 'USDT')].copy()
    if not swap_tx.empty:
        swap_tx['total_cost'] = swap_tx['input_amount'] + swap_tx.get('fee', 0)
        acquisitions.append(swap_tx[['person_name', 'output_currency', 'output_amount', 'total_cost']])
    
    cost_basis = pd.DataFrame(columns=['person_name', 'currency', 'avg_buy_price']) # FIX: ensure it has columns
    if acquisitions:
        all_acquisitions = pd.concat(acquisitions, ignore_index=True)
        cost_basis_agg = all_acquisitions.groupby(['person_name', 'output_currency']).agg(total_cost_usd=('total_cost', 'sum'), total_amount_crypto=('output_amount', 'sum')).reset_index()
        cost_basis_agg['avg_buy_price'] = cost_basis_agg['total_cost_usd'] / cost_basis_agg['total_amount_crypto']
        cost_basis = cost_basis_agg.rename(columns={'output_currency': 'currency'})[['person_name', 'currency', 'avg_buy_price']]

    # 3. Portfolio Balance
    gains = transactions[['person_name', 'output_currency', 'output_amount']].rename(columns={'output_currency': 'currency', 'output_amount': 'amount'})
    losses = transactions[['person_name', 'input_currency', 'input_amount']].rename(columns={'input_currency': 'currency', 'input_amount': 'amount'})
    losses['amount'] = -losses['amount']
    portfolio = pd.concat([gains, losses]).groupby(['person_name', 'currency'])['amount'].sum().reset_index()
    portfolio = portfolio[portfolio['amount'] > 1e-9]
    portfolio_analysis = pd.merge(portfolio, cost_basis, on=['person_name', 'currency'], how='left')

    # 4. Floating P/L
    if prices and not portfolio_analysis.empty:
        portfolio_analysis['current_price'] = portfolio_analysis['currency'].map(prices)
        portfolio_analysis['current_value_usd'] = portfolio_analysis['amount'] * portfolio_analysis['current_price']
        portfolio_analysis['total_cost_of_holdings'] = portfolio_analysis['amount'] * portfolio_analysis['avg_buy_price']
        portfolio_analysis['floating_pnl_usd'] = portfolio_analysis['current_value_usd'] - portfolio_analysis['total_cost_of_holdings']

    # 5. Realized P/L from Sales
    sell_tx = transactions[transactions['transaction_type'] == 'sell'].copy()
    if not sell_tx.empty and not cost_basis.empty:
        sell_tx = pd.merge(sell_tx, cost_basis, left_on=['person_name', 'input_currency'], right_on=['person_name', 'currency'], how='left')
        sell_tx['cost_of_goods_sold'] = sell_tx['input_amount'] * sell_tx['avg_buy_price']
        sell_tx['realized_pnl'] = sell_tx['output_amount'] - sell_tx['cost_of_goods_sold'] - sell_tx.get('fee', 0)
        realized_pnl_summary = sell_tx.groupby('person_name')['realized_pnl'].sum().reset_index()
    else:
        realized_pnl_summary = empty_realized

    # 6. Fee Analysis
    transactions['fee'] = transactions.get('fee', 0).fillna(0)
    transactions.loc[transactions['transaction_type'] == 'transfer', 'fee'] = transactions['input_amount'] - transactions['output_amount']
    if not transactions.empty and 'fee' in transactions.columns:
        fee_summary = transactions[transactions['fee'] > 0].groupby(['person_name', 'transaction_type'])['fee'].sum().reset_index()
    else:
        fee_summary = empty_fees

    return portfolio_analysis.fillna(0), toman_stats, realized_pnl_summary, fee_summary

# --- Formatting ---
def format_currency(amount, currency):
    # ... (بدون تغییر)
    if pd.isna(amount) or not isinstance(amount, (int, float)): return '-'
    if currency == 'IRR': return f"{amount:,.0f} Toman"
    return f"${amount:,.2f}"
