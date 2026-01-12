import os


def load_dotenv(dotenv_path):
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r") as dotenv_file:
        for line in dotenv_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            os.environ.setdefault(key, value)


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

BASE_URL = "https://www.xe.com/currencyconverter/convert/"
DEFAULT_AMOUNT = 1
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}
MAX_WORKERS = 5
RETRY_COUNT = 3
BACKOFF_FACTOR = 0.1
RETRY_STATUS_CODES = [500, 502, 503, 504]
CONFIG_FILE = 'config.json'
OUTPUT_FILE = 'exchange_rates.json'
PROXIES = [proxy.strip() for proxy in os.getenv("PROXIES", "").split(",") if proxy.strip()]
PROXY_COOLDOWN_SECONDS = int(os.getenv("PROXY_COOLDOWN_SECONDS", "900"))
