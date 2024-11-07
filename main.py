import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_exchange_rate(session, currency_from, currency_to):
    url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={currency_from}&To={currency_to}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
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
    
    retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    with ThreadPoolExecutor(max_workers=5) as executor:  
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
