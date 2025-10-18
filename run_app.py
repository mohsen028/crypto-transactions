import streamlit.web.cli as stcli
import os
import sys

def get_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename

if __name__ == "__main__":
    main_script_path = get_path("1_📈_Dashboard.py")
    
    # دستور ساده شده که به استریملیت اجازه می‌دهد خودش پورت را انتخاب کند
    sys.argv = ["streamlit", "run", main_script_path]
    stcli.main()
