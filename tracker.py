import json
import os
import datetime
import uuid

DB_FILE = "transactions.json"
PEOPLE = ["hassan", "abbas", "shahla", "mohsen"]
CRYPTOS = ["BTC", "ETH", "BNB", "SOL", "XRP", "USDC", "ADA", "DOGE", "DOT", "PAXG"]
CURRENCIES = ["USDT"] + CRYPTOS

# --- توابع مدیریت داده ---
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

# --- توابع کمکی رابط کاربری ---
def clear_screen():
    """صفحه ترمینال را پاک می‌کند"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt, required=True, input_type=str):
    """ورودی را از کاربر با اعتبارسنجی دریافت می‌کند"""
    while True:
        val = input(f"{prompt}: ").strip()
        if not val and required:
            print("این فیلد اجباری است.")
            continue
        if not val and not required:
            return None
        if input_type:
            try:
                return input_type(val)
            except ValueError:
                print(f"لطفاً یک مقدار معتبر از نوع {input_type.__name__} وارد کنید.")
                continue
        return val

def get_choice(prompt, options):
    """یک گزینه از لیست را از کاربر انتخاب می‌کند"""
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option.capitalize()}")
    while True:
        try:
            choice = int(input(f"{prompt} (عدد را وارد کنید): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("انتخاب نامعتبر است.")
        except ValueError:
            print("لطفاً فقط عدد وارد کنید.")

def print_transaction(trx, index=None):
    """یک تراکنش را با فرمت زیبا چاپ می‌کند"""
    prefix = f"[{index}] " if index is not None else ""
    print(f"{prefix}ID: {trx['id']}")
    print(f"  نوع: {trx['transaction_type'].replace('_', ' ').title()}")
    print(f"  شخص: {trx['person_name'].capitalize()} | تاریخ: {trx['transaction_date']}")
    if trx.get('input_currency'):
        print(f"  ورودی: {trx.get('input_amount', '-')} {trx['input_currency']}")
    if trx.get('output_currency'):
        print(f"  خروجی: {trx.get('output_amount', '-')} {trx['output_currency']}")
    if trx.get('notes'):
        print(f"  یادداشت: {trx['notes']}")
    print("-" * 30)

# --- توابع اصلی برنامه ---
def show_dashboard():
    """داشبورد اصلی شامل آمار و نمودار متنی را نمایش می‌دهد"""
    clear_screen()
    transactions = load_transactions()
    print("--- داشبورد ---")

    # آمار کلی
    buy_transactions = [t for t in transactions if 'buy' in t['transaction_type']]
    sell_transactions = [t for t in transactions if t['transaction_type'] == 'sell']
    total_fees = sum(t.get('fee', 0) for t in transactions if t.get('fee'))
    
    print(f"\nتعداد کل تراکنش‌ها: {len(transactions)}")
    print(f"تعداد تراکنش‌های خرید: {len(buy_transactions)}")
    print(f"تعداد تراکنش‌های فروش: {len(sell_transactions)}")
    print(f"مجموع کارمزدها: ${total_fees:.2f}")

    # نمودار متنی ۷ روز اخیر
    print("\n--- فعالیت تراکنش‌ها (۷ روز اخیر) ---")
    today = datetime.date.today()
    for i in range(7):
        day = today - datetime.timedelta(days=i)
        day_str = day.isoformat()
        day_transactions = [t for t in transactions if t['transaction_date'] == day_str]
        buy_count = sum(1 for t in day_transactions if 'buy' in t['transaction_type'])
        sell_count = sum(1 for t in day_transactions if t['transaction_type'] == 'sell')
        other_count = len(day_transactions) - buy_count - sell_count
        print(f"{day_str}: خرید: {buy_count}, فروش: {sell_count}, سایر: {other_count}")
    
    input("\nبرای بازگشت به منوی اصلی، Enter را بزنید...")

def view_transactions():
    """لیست تمام تراکنش‌ها را با قابلیت فیلتر نمایش می‌دهد"""
    clear_screen()
    transactions = load_transactions()
    print("--- تاریخچه تراکنش‌ها ---")

    # فیلترها
    search_term = get_input("جستجو در یادداشت یا ارز (خالی بگذارید برای همه)", required=False)
    
    filtered = transactions
    if search_term:
        term = search_term.lower()
        filtered = [
            t for t in filtered if 
            term in t.get('notes', '').lower() or
            term in t.get('input_currency', '').lower() or
            term in t.get('output_currency', '').lower()
        ]

    if not filtered:
        print("\nهیچ تراکنشی با این مشخصات یافت نشد.")
    else:
        for i, trx in enumerate(filtered, 1):
            print_transaction(trx, i)
    
    input("\nبرای بازگشت به منوی اصلی، Enter را بزنید...")

def add_transaction():
    """یک تراکنش جدید اضافه می‌کند"""
    clear_screen()
    print("--- ثبت تراکنش جدید ---")
    
    trx_type = get_choice("نوع تراکنش را انتخاب کنید", [
        "buy_usdt_with_toman", "buy_crypto_with_usdt", "sell", "transfer", "swap"
    ])

    person = get_choice("شخص را انتخاب کنید", PEOPLE)
    date = get_input("تاریخ (YYYY-MM-DD)", required=True, input_type=str) # Simple string for simplicity

    new_trx = {
        "id": str(uuid.uuid4()),
        "transaction_type": trx_type,
        "person_name": person,
        "transaction_date": date
    }

    if trx_type == 'buy_usdt_with_toman':
        new_trx['input_currency'] = "IRR"
        new_trx['output_currency'] = "USDT"
        new_trx['input_amount'] = get_input("مبلغ تومان پرداختی", input_type=float)
        new_trx['output_amount'] = get_input("مقدار USDT دریافتی", input_type=float)
        rate = get_input("نرخ USDT به تومان", input_type=float)
        new_trx['rate'] = rate
        effective_cost = new_trx['input_amount'] / new_trx['output_amount']
        new_trx['effective_cost'] = effective_cost
        new_trx['fee'] = new_trx['input_amount'] - (new_trx['output_amount'] * rate)
        print(f"هزینه تمام شده هر USDT: {effective_cost:,.2f} تومان")

    elif trx_type == 'buy_crypto_with_usdt':
        new_trx['input_currency'] = "USDT"
        new_trx['output_currency'] = get_choice("کدام ارز را خریدید؟", CRYPTOS)
        new_trx['input_amount'] = get_input("مبلغ USDT پرداختی", input_type=float)
        new_trx['output_amount'] = get_input(f"مقدار {new_trx['output_currency']} دریافتی", input_type=float)
        effective_cost = new_trx['input_amount'] / new_trx['output_amount']
        new_trx['effective_cost'] = effective_cost
        print(f"هزینه تمام شده هر واحد: {effective_cost:,.2f} USDT")

    # ... می‌توان بقیه انواع تراکنش‌ها را به همین شکل اضافه کرد ...

    new_trx['notes'] = get_input("یادداشت (اختیاری)", required=False)
    
    transactions = load_transactions()
    transactions.append(new_trx)
    save_transactions(transactions)
    print("\nتراکنش با موفقیت ثبت شد!")
    input("برای بازگشت به منوی اصلی، Enter را بزنید...")

def main():
    """حلقه اصلی برنامه و منوی اصلی"""
    while True:
        clear_screen()
        print("--- مدیریت تراکنش‌های ارز دیجیتال ---")
        print("1. نمایش داشبورد")
        print("2. مشاهده تاریخچه تراکنش‌ها")
        print("3. ثبت تراکنش جدید")
        print("4. ویرایش تراکنش (پیاده‌سازی نشده)")
        print("5. حذف تراکنش (پیاده‌سازی نشده)")
        print("6. خروج")
        
        choice = input("\nلطفاً انتخاب کنید: ")
        
        if choice == '1':
            show_dashboard()
        elif choice == '2':
            view_transactions()
        elif choice == '3':
            add_transaction()
        elif choice == '6':
            print("خدا نگهدار!")
            break
        else:
            input("انتخاب نامعتبر است. برای تلاش مجدد Enter را بزنید...")

if __name__ == "__main__":
    main()
