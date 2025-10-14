import streamlit as st
import pandas as pd

# This is a simple in-memory storage using session_state.
# In a real app, you might use a database.
def initialize_transactions():
    if 'transactions' not in st.session_state:
        # Create a sample DataFrame
        st.session_state.transactions = pd.DataFrame([
            {
                "id": "1", "transaction_type": "buy_usdt_with_toman", "person_name": "hassan",
                "transaction_date": pd.to_datetime("2025-10-01"), "input_currency": "IRR", "output_currency": "USDT",
                "input_amount": 5000000.0, "output_amount": 100.0, "rate": 50000.0, "fee": 10000.0, "notes": "First purchase"
            },
            {
                "id": "2", "transaction_type": "buy_crypto_with_usdt", "person_name": "abbas",
                "transaction_date": pd.to_datetime("2025-10-03"), "input_currency": "USDT", "output_currency": "BTC",
                "input_amount": 50.0, "output_amount": 0.002, "rate": 25000.0, "fee": 1.5, "notes": "Bought Bitcoin"
            },
            {
                "id": "3", "transaction_type": "sell", "person_name": "hassan",
                "transaction_date": pd.to_datetime("2025-10-05"), "input_currency": "BTC", "output_currency": "USDT",
                "input_amount": 0.001, "output_amount": 26.0, "rate": 26000.0, "fee": 0.5, "notes": "Sold some BTC"
            },
        ])
        st.session_state.transactions['transaction_date'] = pd.to_datetime(st.session_state.transactions['transaction_date'])


# --- Transaction Functions ---
def get_all_transactions():
    """Returns the full DataFrame of transactions, sorted by date."""
    if 'transactions' in st.session_state and not st.session_state.transactions.empty:
        return st.session_state.transactions.sort_values(by="transaction_date", ascending=False)
    return pd.DataFrame()

def add_transaction(data):
    """Adds a new transaction to the session state."""
    df = st.session_state.transactions
    new_id = str(pd.Timestamp.now().timestamp()) # Simple unique ID
    new_transaction = {"id": new_id, **data}
    st.session_state.transactions = pd.concat([df, pd.DataFrame([new_transaction])], ignore_index=True)

def delete_transaction(transaction_id):
    """Deletes a transaction by its ID."""
    df = st.session_state.transactions
    st.session_state.transactions = df[df['id'] != transaction_id]


# --- Formatting Functions ---
def format_currency(amount, currency):
  if pd.isna(amount):
      return '-'
  try:
      num_amount = float(amount)
      if currency == 'IRR':
          return f"{num_amount:,.0f} Toman"
      else:
          # Show more precision for cryptos
          return f"{num_amount:,.6f} {currency}".rstrip('0').rstrip('.')
  except (ValueError, TypeError):
      return '-'


TRANSACTION_TYPE_LABELS = {
  "buy_usdt_with_toman": "Buy USDT",
  "buy_crypto_with_usdt": "Buy Crypto",
  "sell": "Sell",
  "transfer": "Transfer",
  "swap": "Swap"
}

PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS
# --- Portfolio Calculation Functions ---
def calculate_portfolio(df):
    """
    Calculates the current holdings for each person and currency.
    """
    if df.empty:
        return pd.DataFrame(columns=['person_name', 'currency', 'amount'])

    # Create two separate dataframes for gains and losses
    gains = df[['person_name', 'output_currency', 'output_amount']].rename(
        columns={'output_currency': 'currency', 'output_amount': 'amount'}
    )
    
    losses = df[['person_name', 'input_currency', 'input_amount']].rename(
        columns={'input_currency': 'currency', 'input_amount': 'amount'}
    )
    
    # Mark losses as negative values
    losses['amount'] = -losses['amount']
    
    # Combine them into a single long-format dataframe
    all_movements = pd.concat([gains, losses], ignore_index=True)
    
    # Group by person and currency and sum up the amounts to get the final balance
    portfolio = all_movements.groupby(['person_name', 'currency'])['amount'].sum().reset_index()
    
    # Filter out any currencies with a zero or near-zero balance
    portfolio = portfolio[portfolio['amount'] > 1e-9] # Use a small threshold for floating point inaccuracies
    
    return portfolio.sort_values(by=['person_name', 'amount'], ascending=[True, False])
