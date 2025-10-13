# app.py
import streamlit as st
import json
import os
import datetime
import uuid
import pandas as pd

DB_FILE = "transactions.json"
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

# --- توابع مدیریت داده (بدون تغییر) ---
def load_transactions():
    """تراکنش‌ها را از فایل JSON بارگذاری می‌کند"""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_transactions(transactions):
    """لیست تراکنش‌ها را در فایل JSON ذخیره می‌کند"""
    transactions.sort(key=lambda t: t['transaction_date'], reverse=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

# --- بارگذاری اولیه داده‌ها در Session State ---
# این کار باعث می‌شود با هر بار کلیک، فایل دوباره خوانده نشود
if 'transactions' not in st.session_state:
    st.session_state.transactions = load_transactions()


# --- تعریف صفحات مختلف برنامه ---

def show_dashboard():
    """صفحه داشبورد را با استفاده از کامپوننت‌های Streamlit نمایش می‌دهد"""
    st.title("📊 داشبورد")
    
    transactions = st.session_state.transactions
    
    # آمار کلی با st.metric
    st.header("آمار کلی")
    col1, col2, col3 = st.columns(3)
    buy_count = sum(1 for t in transactions if 'buy' in t['transaction_type'])
    sell_count = sum(1 for t in transactions if t['transaction_type'] == 'sell')
    
    col1.metric("تعداد کل تراکنش‌ها", len(transactions))
    col2.metric("تراکنش‌های خرید", buy_count)
    col3.metric("تراکنش‌های فروش", sell_count)

    # نمودار ۷ روز اخیر با Pandas و st.bar_chart
    st.header("فعالیت تراکنش‌ها (۷ روز اخیر)")
    if transactions:
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # داده‌ها را برای ۷ روز اخیر فیلتر کن
        last_7_days = df[df['transaction_date'] > (datetime.datetime.now() - datetime.timedelta(days=7))]
        
        # شمارش انواع تراکنش در هر روز
        if not last_7_days.empty:
            daily_counts = last_7_days.groupby([last_7_days['transaction_date'].dt.date, 'transaction_type']).size().unstack(fill_value=0)
            st.bar_chart(daily_counts)
        else:
            st.info("هیچ تراکنشی در ۷ روز اخیر ثبت نشده است.")
    else:
        st.info("هنوز هیچ تراکنشی ثبت نشده است.")


def view_transactions():
    """صفحه تاریخچه تراکنش‌ها را نمایش می‌دهد"""
    st.title("📜 تاریخچه تراکنش‌ها")
    
    transactions = st.session_state.transactions
    
    search_term = st.text_input("جستجو در یادداشت یا ارز")
    
    filtered = transactions
    if search_term:
        term = search_term.lower()
        filtered = [t for t in filtered if 
                    term in t.get('notes', '').lower() or
                    term in t.get('input_currency', '').lower() or
                    term in t.get('output_currency', '').lower()]

    if not filtered:
        st.warning("هیچ تراکنشی یافت نشد.")
    else:
        for trx in filtered:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"نوع: {trx['transaction_type'].replace('_', ' ').title()}")
                    st.caption(f"شخص: {trx['person_name'].capitalize()} | تاریخ: {trx['transaction_date']}")
                    if trx.get('input_currency'):
                        st.text(f"ورودی: {trx.get('input_amount', '-')} {trx['input_currency']}")
                    if trx.get('output_currency'):
                        st.text(f"خروجی: {trx.get('output_amount', '-')} {trx['output_currency']}")
                # ستون دوم برای دکمه‌های حذف و ویرایش (فعلاً غیرفعال)
                with col2:
                    st.button("ویرایش", key=f"edit_{trx['id']}", disabled=True)
                    st.button("حذف", key=f"delete_{trx['id']}", disabled=True, type="secondary")

def add_transaction():
    """صفحه ثبت تراکنش جدید را با یک فرم نمایش می‌دهد"""
    st.title("✍️ ثبت تراکنش جدید")

    with st.form(key="transaction_form"):
        transaction_type = st.selectbox("نوع تراکنش", ["buy_usdt_with_toman", "buy_crypto_with_usdt", "sell", "transfer", "swap"])
        person_name = st.selectbox("شخص", PEOPLE)
        transaction_date = st.date_input("تاریخ تراکنش", datetime.date.today())
        
        st.subheader("جزئیات تراکنش")
        if "buy" in transaction_type:
            input_currency = "IRR" if transaction_type == "buy_usdt_with_toman" else "USDT"
            output_currency = "USDT" if transaction_type == "buy_usdt_with_toman" else st.selectbox("ارز مقصد", CRYPTOS)
            input_amount = st.number_input(f"مقدار ورودی ({input_currency})", min_value=0.0, format="%.2f")
            output_amount = st.number_input(f"مقدار خروجی ({output_currency})", min_value=0.0, format="%.8f")
        # می‌توان منطق بقیه انواع تراکنش را هم به همین شکل اضافه کرد
        
        notes = st.text_area("یادداشت (اختیاری)")
        
        submitted = st.form_submit_button("ثبت تراکنش")

        if submitted:
            new_trx = {
                "id": str(uuid.uuid4()),
                "transaction_type": transaction_type,
                "person_name": person_name,
                "transaction_date": transaction_date.isoformat(),
                "input_currency": input_currency,
                "output_currency": output_currency,
                "input_amount": input_amount,
                "output_amount": output_amount,
                "notes": notes,
            }
            
            st.session_state.transactions.append(new_trx)
            save_transactions(st.session_state.transactions)
            st.success("تراکنش با موفقیت ثبت شد!")
            st.balloons()


# --- ساختار اصلی برنامه و منوی کناری ---
st.sidebar.title("منوی برنامه")
page_options = {
    "داشبورد": show_dashboard,
    "تاریخچه تراکنش‌ها": view_transactions,
    "ثبت تراکنش جدید": add_transaction,
}
selection = st.sidebar.radio("یک صفحه را انتخاب کنید:", list(page_options.keys()))

# اجرای تابع مربوط به صفحه انتخاب شده
page_to_show = page_options[selection]
page_to_show()
