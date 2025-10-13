import streamlit as st
import pandas as pd
from utils import get_all_transactions, delete_transaction, format_currency, TRANSACTION_TYPE_LABELS, PEOPLE

st.set_page_config(
    page_title="Transaction History",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Transaction History")
st.markdown("View, filter, and manage all your transactions.")

transactions = get_all_transactions()

if transactions.empty:
    st.warning("No transactions found. Go to the 'New Transaction' page to add one.")
    st.stop()

# --- Filtering UI ---
st.sidebar.header("Filters")
filter_person = st.sidebar.multiselect(
    "Filter by Person",
    options=PEOPLE,
    format_func=lambda x: x.capitalize()
)

filter_type = st.sidebar.multiselect(
    "Filter by Type",
    options=TRANSACTION_TYPE_LABELS.keys(),
    format_func=lambda x: TRANSACTION_TYPE_LABELS[x]
)

# Apply filters
filtered_transactions = transactions.copy()
if filter_person:
    filtered_transactions = filtered_transactions[filtered_transactions['person_name'].isin(filter_person)]
if filter_type:
    filtered_transactions = filtered_transactions[filtered_transactions['transaction_type'].isin(filter_type)]


# --- Display Transactions ---
st.write(f"Displaying **{len(filtered_transactions)}** of **{len(transactions)}** transactions.")

for index, row in filtered_transactions.iterrows():
    with st.container(border=True):
        col1, col2, col3 = st.columns([4, 4, 1])
        
        with col1:
            type_label = TRANSACTION_TYPE_LABELS.get(row['transaction_type'], 'N/A')
            st.markdown(f"**{type_label}** by **{row['person_name'].capitalize()}**")
            st.caption(f"Date: {row['transaction_date'].strftime('%Y-%m-%d')}")
        
        with col2:
            in_amount = format_currency(row['input_amount'], row['input_currency'])
            out_amount = format_currency(row['output_amount'], row['output_currency'])
            st.markdown(f"**Input:** {in_amount}")
            st.markdown(f"**Output:** {out_amount}")

        with col3:
            # Use a unique key for the button based on the transaction id
            if st.button("Delete", key=f"delete_{row['id']}", type="primary"):
                delete_transaction(row['id'])
                st.success(f"Transaction {row['id'][:6]}... deleted.")
                # Rerun the script to refresh the list
                st.rerun()
        
        if pd.notna(row['notes']) and row['notes'].strip():
            with st.expander("View Notes"):
                st.write(row['notes'])

```5.  روی **Commit new file** کلیک کنید.
