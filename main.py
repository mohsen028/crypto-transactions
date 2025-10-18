import subprocess
import sys
import os

# --- SAFETY SWITCH START ---
# This "if" statement is the crucial safety switch. It prevents the infinite loop.
# The code inside this block will only run when the user directly double-clicks the .exe file.
# It will NOT run in the child processes that Streamlit creates.
if __name__ == '__main__':
    # 1. Construct the path to the main dashboard script.
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    script_path = os.path.join(base_path, '1_📈_Dashboard.py')

    # 2. Construct the command to run Streamlit correctly.
    command = [
        sys.executable,
        "-m", "streamlit", "run",
        script_path,
        "--server.headless", "true",
        "--server.port", "8501"
    ]

    # 3. Launch the Streamlit server process.
    try:
        # We use Popen instead of run to launch it as a separate, non-blocking process.
        proc = subprocess.Popen(command)
        proc.wait() # Wait for the process to complete (i.e., user closes the app)
    except Exception as e:
        with open("error.log", "w") as f:
            f.write("Failed to launch Streamlit process.\n")
            f.write(str(e))
# --- SAFETY SWITCH END ---
