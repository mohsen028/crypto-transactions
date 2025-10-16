import streamlit as st
import pandas as pd
from utils import get_all_transactions, get_full_portfolio_analysis

st.set_page_config(page_title="Detailed Portfolio", icon="📊", layout="wide")

st.title("📊 Detailed Portfolio View")
st.markdown("A detailed breakdown of assets, costs, and current market value for everyone.")

transactions = get_all_transactions()
if transactions.empty:
    st.warning("No transactions recorded yet.")
    st.stop()

analysis_df = get_full_portfolio_analysis(transactions)
if analysis_df.empty:
    st.info("No assets with a positive balance.")
    st.stop()

people = analysis_df['person_name'].unique()
for person in people:
    with st.container(border=True):
        st.markdown(f"### {person.capitalize()}'s Portfolio")
        person_df = analysis_df[analysis_df['person_name'] == person].copy()

        # Filter out non-crypto assets for P/L view
        person_crypto_df = person_df[person_df['currency'] != 'IRR']
        
        st.dataframe(
            person_crypto_df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "currency": "Asset",
                "amount": st.column_config.NumberColumn("Balance", format="%.6f"),
                "avg_buy_price": st.column_config.NumberColumn("Avg. Buy Price", format="$%.2f"),
                "current_price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                "current_value_usd": st.column_config.NumberColumn("Market Value", format="$%.2f"),
                "pnl_usd": st.column_config.NumberColumn("Floating P/L", format="$%.2f"),
            },
            # Hide columns we don't need for the view
            column_order=("currency", "amount", "current_value_usd", "pnl_usd", "avg_buy_price", "current_price")
        )
