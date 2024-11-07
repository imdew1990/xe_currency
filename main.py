import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import config

def get_exchange_rate(session, currency_from, currency_to):
    url = f"{config.BASE_URL}?Amount={config.DEFAULT_AMOUNT}&From={currency_from}&To={currency_to}"
    
    try:
        response = session.get(url, headers=config.HEADERS)
        response.raise_for_status()
        
        # Use lxml for faster parsing
        soup = BeautifulSoup(response.content, 'lxml')
        rate_section = soup.find("p", class_="sc-63d8b7e3-1 bMdPIi")
        
        if rate_section:
            rate_text = rate_section.get_text(strip=True)
            match = re.search(r"(\d+\.\d+)", rate_text)
            if match:
                return currency_from, currency_to, float(match.group(1))
        return currency_from, currency_to, None
    
    except Exception as e:
        print(f"Error fetching or parsing data for {currency_from} to {currency_to}: {e}")
        return currency_from, currency_to, None

def fetch_multiple_exchange_rates(pairs):
    results = {}
    session = requests.Session()
    
    # Configure retry strategy
    retries = Retry(
        total=config.RETRY_COUNT,
        backoff_factor=config.BACKOFF_FACTOR,
        status_forcelist=config.RETRY_STATUS_CODES
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
        future_to_pair = {executor.submit(get_exchange_rate, session, pair[0], pair[1]): pair for pair in pairs}
        
        for future in as_completed(future_to_pair):
            pair = future_to_pair[future]
            try:
                result = future.result()
                if result:
                    currency_from, currency_to, rate = result
                    results[(currency_from, currency_to)] = rate
                else:
                    results[pair] = None
            except Exception as e:
                print(f"Exception for {pair[0]} to {pair[1]}: {e}")
                results[pair] = None

    return results

currency_pairs = [
    ("EUR", "GBP"),
    ("USD", "EUR"),
    ("JPY", "USD"),
    ("AUD", "CAD"),
    ("CHF", "GBP"),
    ("ZAR", "USD"),
    ("USD", "ZAR")
]

exchange_rates = fetch_multiple_exchange_rates(currency_pairs)
for (currency_from, currency_to), rate in exchange_rates.items():
    if rate is not None:
        print(f"Exchange rate from {currency_from} to {currency_to}: {rate}")
    else:
        print(f"Could not retrieve exchange rate from {currency_from} to {currency_to}")
