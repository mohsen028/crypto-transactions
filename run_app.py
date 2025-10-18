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
    
    # This simulates the command: streamlit run 1_📈_Dashboard.py
    sys.argv = ["streamlit", "run", main_script_path, "--server.headless=true", "--server.port=8501"]
    stcli.main()
