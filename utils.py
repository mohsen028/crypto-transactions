import streamlit as st
import pandas as pd
import requests

# --- Initial Data and Constants ---
def initialize_transactions():
    if 'transactions' not in st.session_state:
        st.session_state.transactions = pd.DataFrame([
            # Sample data remains the same...
            {
                "id": "1", "transaction_type": "buy_usdt_with_toman", "person_name": "hassan",
                "transaction_date": pd.to_datetime("2025-10-01"), "input_currency": "IRR", "output_currency": "USDT",
                "input_amount": 5000000.0, "output_amount": 100.0, "rate": 50000.0, "fee": 0.0, "notes": "First purchase"
            },
            {
                "id": "2", "transaction_type": "buy_crypto_with_usdt", "person_name": "hassan",
                "transaction_date": pd.to_datetime("2025-10-03"), "input_currency": "USDT", "output_currency": "BTC",
                "input_amount": 50.0, "output_amount": 0.002, "rate": 25000.0, "fee": 1.5, "notes": "Bought Bitcoin"
            },
             {
                "id": "3", "transaction_type": "buy_crypto_with_usdt", "person_name": "abbas",
                "transaction_date": pd.to_datetime("2025-10-04"), "input_currency": "USDT", "output_currency": "ETH",
                "input_amount": 500.0, "output_amount": 0.2, "rate": 2500.0, "fee": 2.0, "notes": "Bought Ethereum"
            },
            {
                "id": "4", "transaction_type": "sell", "person_name": "hassan",
                "transaction_date": pd.to_datetime("2025-10-05"), "input_currency": "BTC", "output_currency": "USDT",
                "input_amount": 0.001, "output_amount": 30.0, "rate": 30000.0, "fee": 0.5, "notes": "Sold some BTC"
            },
        ])
        st.session_state.transactions['transaction_date'] = pd.to_datetime(st.session_state.transactions['transaction_date'])

TRANSACTION_TYPE_LABELS = {
  "buy_usdt_with_toman": "Buy USDT", "buy_crypto_with_usdt": "Buy Crypto",
  "sell": "Sell", "transfer": "Transfer", "swap": "Swap"
}
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

# --- Data Fetching and Manipulation ---
def get_all_transactions():
    if 'transactions' in st.session_state and not st.session_state.transactions.empty:
        return st.session_state.transactions.sort_values(by="transaction_date", ascending=False)
    return pd.DataFrame()

def add_transaction(data):
    df = st.session_state.transactions
    new_id = str(pd.Timestamp.now().timestamp())
    new_transaction = {"id": new_id, **data}
    st.session_state.transactions = pd.concat([df, pd.DataFrame([new_transaction])], ignore_index=True)

def delete_transaction(transaction_id):
    df = st.session_state.transactions
    st.session_state.transactions = df[df['id'] != transaction_id]

# --- NEW: Real-time Price Fetching ---
@st.cache_data(ttl=300) # Cache data for 5 minutes
def get_crypto_prices(symbols):
    if not symbols:
        return {}
    # Map symbols to coingecko IDs
    symbol_to_id = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin', 'SOL': 'solana',
        'XRP': 'ripple', 'USDC': 'usd-coin', 'ADA': 'cardano', 'DOGE': 'dogecoin',
        'DOT': 'polkadot', 'PAXG': 'pax-gold', 'USDT': 'tether'
    }
    ids = [symbol_to_id[s] for s in symbols if s in symbol_to_id]
    if not ids:
        return {}
        
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Map back from ID to symbol
        prices = {symbol: data[id]['usd'] for symbol, id in symbol_to_id.items() if id in data}
        prices['USDT'] = 1.0 # USDT is always 1 USD
        return prices
    except requests.exceptions.RequestException as e:
        st.error(f"Could not fetch crypto prices: {e}")
        return {}

# --- NEW: Core Logic for Portfolio and P/L ---
def get_full_portfolio_analysis(transactions):
    if transactions.empty:
        return pd.DataFrame()

    # 1. Calculate current balances (same as before)
    gains = transactions[['person_name', 'output_currency', 'output_amount']].rename(columns={'output_currency': 'currency', 'output_amount': 'amount'})
    losses = transactions[['person_name', 'input_currency', 'input_amount']].rename(columns={'input_currency': 'currency', 'input_amount': 'amount'})
    losses['amount'] = -losses['amount']
    all_movements = pd.concat([gains, losses], ignore_index=True)
    portfolio = all_movements.groupby(['person_name', 'currency'])['amount'].sum().reset_index()
    portfolio = portfolio[portfolio['amount'] > 1e-9]

    # 2. Calculate cost basis for crypto assets bought with USDT
    buy_crypto_tx = transactions[transactions['transaction_type'] == 'buy_crypto_with_usdt'].copy()
    if not buy_crypto_tx.empty:
        cost_basis = buy_crypto_tx.groupby(['person_name', 'output_currency']).agg(
            total_cost_usd=('input_amount', 'sum'),
            total_amount_crypto=('output_amount', 'sum')
        ).reset_index()
        cost_basis = cost_basis.rename(columns={'output_currency': 'currency'})
        cost_basis['avg_buy_price'] = cost_basis['total_cost_usd'] / cost_basis['total_amount_crypto']
        
        # Merge cost basis into portfolio
        portfolio = pd.merge(portfolio, cost_basis[['person_name', 'currency', 'avg_buy_price']], on=['person_name', 'currency'], how='left')
    else:
        portfolio['avg_buy_price'] = pd.NA

    # 3. Get live prices
    crypto_symbols = portfolio['currency'].unique().tolist()
    prices = get_crypto_prices(crypto_symbols)
    
    if prices:
        portfolio['current_price'] = portfolio['currency'].map(prices)
        portfolio['current_value_usd'] = portfolio['amount'] * portfolio['current_price']
        
        # Calculate P/L
        portfolio['total_cost_of_current_holdings'] = portfolio['amount'] * portfolio['avg_buy_price']
        portfolio['pnl_usd'] = portfolio['current_value_usd'] - portfolio['total_cost_of_current_holdings']
    
    return portfolio.fillna(0)


# --- Formatting ---
def format_currency(amount, currency):
    if pd.isna(amount): return '-'
    try:
        num_amount = float(amount)
        if currency == 'IRR': return f"{num_amount:,.0f} Toman"
        else: return f"{num_amount:,.6f} {currency}".rstrip('0').rstrip('.')
    except (ValueError, TypeError): return '-'
