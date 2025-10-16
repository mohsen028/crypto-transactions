from PyInstaller.utils.hooks import collect_all, collect_entry_points

# This is the master hook for Streamlit.

# 1. Collect all standard files (data, binaries, hidden imports) for streamlit itself.
datas, binaries, hiddenimports = collect_all('streamlit')

# 2. CRITICAL STEP: Find and include all 'entry points'. This is what was failing.
# Streamlit uses this system to find its internal commands and components.
# Without this, the app crashes instantly on startup.
hiddenimports += collect_entry_points('streamlit.components.v1')
hiddenimports += collect_entry_points('streamlit')

# 3. Also include known dependencies that PyInstaller often misses.
hiddenimports.extend([
    'altair',
    'pandas',
    'pydeck',
    'requests',
    'tornado',
    'watchdog',
])
