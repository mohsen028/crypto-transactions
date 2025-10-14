import streamlit as st
import pandas as pd
from utils import get_all_transactions, calculate_portfolio

st.set_page_config(
    page_title="Global Portfolio",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Global Portfolio Overview")
st.markdown("View the current asset balance for everyone in one place.")

# Load and calculate the portfolio
transactions = get_all_transactions()
if transactions.empty:
    st.warning("No transactions recorded yet. Add a new transaction to begin.")
    st.stop()

full_portfolio = calculate_portfolio(transactions)
if full_portfolio.empty:
    st.info("No one has any assets with a positive balance right now.")
    st.stop()

# --- Display Full Portfolio Grouped by Person ---
st.subheader("All Asset Balances")

# Get a list of all people who have assets
people_with_assets = full_portfolio['person_name'].unique()

for person in people_with_assets:
    # Create a container for each person for better visual separation
    with st.container(border=True):
        st.markdown(f"#### {person.capitalize()}'s Holdings")
        
        # Filter the dataframe for the current person
        person_assets = full_portfolio[full_portfolio['person_name'] == person]
        
        # Prepare a clean dataframe for display
        display_df = person_assets[['currency', 'amount']].copy()
        
        # Display the assets in a table
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "currency": st.column_config.TextColumn("Asset", width="medium"),
                "amount": st.column_config.NumberColumn("Current Balance", format="%.8f")
            }
        )

# --- Optional: Show Raw Data in an Expander ---
with st.expander("View Raw Portfolio Data"):
    st.dataframe(full_portfolio, hide_index=True, use_container_width=True)
