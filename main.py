import subprocess
import sys
import os

# This is the "Ignition Switch" for our application.

# 1. Construct the path to the main dashboard script.
# This ensures it works correctly when frozen by PyInstaller.
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle/frozen exe
    base_path = sys._MEIPASS
else:
    # If run as a normal script
    base_path = os.path.dirname(os.path.abspath(__file__))

script_path = os.path.join(base_path, '1_📈_Dashboard.py')

# 2. Construct the command to run Streamlit correctly.
# We use sys.executable to ensure we're using the Python interpreter
# bundled within the .exe file.
command = [
    sys.executable,
    "-m", "streamlit", "run",
    script_path,
    "--server.headless", "true", # Important for packaged apps
    "--server.port", "8501" # Standard port
]

# 3. Launch the Streamlit server process.
try:
    subprocess.run(command)
except Exception as e:
    # If something goes wrong, write it to a file for debugging.
    with open("error.log", "w") as f:
        f.write(str(e))
