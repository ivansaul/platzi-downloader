from pathlib import Path

import platformdirs

APP_NAME = "Platzi"
SESSION_DIR = Path(platformdirs.user_data_dir(APP_NAME))
SESSION_FILE = SESSION_DIR / "state.json"  # Cookies are stored here

LOGIN_URL = "https://platzi.com/login"
LOGIN_DETAILS_URL = "https://api.platzi.com/api/v1/components/headerv2/user/"


PLATZI_URL = "https://platzi.com"
REFERER = "https://platzi.com/"

# FIREFOX
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": REFERER,
}


# --- Session directory ---
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

# --- Cache directory ---
CACHE_DIR = SESSION_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
