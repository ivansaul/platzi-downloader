from pathlib import Path

import platformdirs

APP_NAME = "Platzi"
SESSION_DIR = Path(platformdirs.user_data_dir(APP_NAME))
SESSION_FILE = SESSION_DIR / "state.json"  # Cookies are stored here

LOGIN_URL = "https://platzi.com/login"
LOGIN_DETAILS_URL = "https://api.platzi.com/api/v1/components/headerv2/user/"


PLATZI_URL = "https://platzi.com"
REFERER = "https://platzi.com/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": REFERER,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}


# --- Session directory ---
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

# --- Cache directory ---
CACHE_DIR = SESSION_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
