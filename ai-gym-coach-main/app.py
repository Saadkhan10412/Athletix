"""
AI Real-Time GYM Coach - Root Application Entrypoint
Allows 1-click deployment on Streamlit Community Cloud and standard execution.
"""
import sys
from pathlib import Path

# Add the Main App directory to sys.path
APP_DIR = Path(__file__).resolve().parent / "Main App"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from main import main

if __name__ == "__main__":
    main()
