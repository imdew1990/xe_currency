BASE_URL = "https://www.xe.com/currencyconverter/convert/"
DEFAULT_AMOUNT = 1
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}
MAX_WORKERS = 5
RETRY_COUNT = 3
BACKOFF_FACTOR = 0.1
RETRY_STATUS_CODES = [500, 502, 503, 504]
