from pathlib import Path

import platformdirs

APP_NAME = "Platzi"
SESSION_DIR = Path(platformdirs.user_data_dir(APP_NAME))
SESSION_FILE = SESSION_DIR / "state.json"

LOGIN_URL = "https://platzi.com/login"
LOGIN_DETAILS_URL = "https://api.platzi.com/api/v1/components/headerv2/user/"


PLATZI_URL = "https://platzi.com"
HOME_URL = PLATZI_URL + "/home"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Referer": HOME_URL,
}


# --- Session directory ---
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
