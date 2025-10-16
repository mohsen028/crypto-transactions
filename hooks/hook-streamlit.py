from PyInstaller.utils.hooks import collect_all

# This hook ensures that all necessary data files, metadata, and hidden imports
# for Streamlit and its core dependencies are correctly bundled.

# Collect all data files, binaries, and hidden imports from streamlit
datas, binaries, hiddenimports = collect_all('streamlit')

# Also explicitly include altair and its dependencies, a common point of failure
_, _, altair_hiddenimports = collect_all('altair')
hiddenimports.extend(altair_hiddenimports)

# Add other known problematic imports
hiddenimports.extend([
    'pandas',
    'numpy',
    'pydeck',
    'watchdog',
    'tornado',
    'requests'
])
