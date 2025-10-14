import streamlit as st
from utils import get_all_transactions, calculate_portfolio, format_currency

st.set_page_config(
    page_title="My Portfolio",
    page_icon="📊",
    layout="centered"
)

st.title("📊 My Portfolio")
st.markdown("View the current balance of all your assets.")

# Load data
transactions = get_all_transactions()

if transactions.empty:
    st.warning("No transactions available. Please add a transaction first.")
    st.stop()

# Calculate the portfolio for everyone
full_portfolio = calculate_portfolio(transactions)

# --- Person Selector ---
people_with_assets = full_portfolio['person_name'].unique()
selected_person = st.selectbox(
    "Select a person to view their portfolio",
    options=people_with_assets,
    format_func=lambda x: x.capitalize()
)

st.markdown(f"### Assets for {selected_person.capitalize()}")

# Filter portfolio for the selected person
person_portfolio = full_portfolio[full_portfolio['person_name'] == selected_person]

if person_portfolio.empty:
    st.info(f"{selected_person.capitalize()} currently has no assets.")
else:
    # Display assets using st.metric for a nice card-like view
    for index, row in person_portfolio.iterrows():
        currency = row['currency']
        amount = row['amount']
        
        # Use the format_currency utility to display numbers nicely
        formatted_amount = format_currency(amount, currency).split(' ')[0] # Get only the number part
        
        st.metric(label=f"**{currency}** Balance", value=formatted_amount)
        
    # You can also display it as a table
    with st.expander("View as a table"):
        st.dataframe(
            person_portfolio[['currency', 'amount']], 
            hide_index=True, 
            use_container_width=True
        )
