import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import config
import time
import os
import json
from datetime import datetime

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
        results = []
        future_to_pair = {executor.submit(get_exchange_rate, session, pair[0], pair[1]): pair for pair in pairs}
        
        for future in as_completed(future_to_pair):
            pair = future_to_pair[future]
            try:
                result = future.result()
                if result:
                    currency_from, currency_to, rate = result
                    result_json = {
                        "from": currency_from,
                        "to": currency_to,
                        "rate": rate
                    }
                    results.append(result_json)
                else:
                    results[pair] = None
            except Exception as e:
                print(f"Exception for {pair[0]} to {pair[1]}: {e}")
                results[pair] = None

    return results
def load_config():
    with open(config.CONFIG_FILE, 'r') as f:
        return json.load(f)

def write_results_to_file(results):
    with open(config.OUTPUT_FILE, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "exchange_rates": [results]
        }, f, indent=4)
    print(f"Results written to {config.OUTPUT_FILE}")


def main():
    last_modified_time = os.path.getmtime(config.CONFIG_FILE)
    config_data = load_config()
    
    while True:
        current_modified_time = os.path.getmtime(config.CONFIG_FILE)
        if current_modified_time != last_modified_time:
            print("Configuration file changed. Reloading...")
            config_data = load_config()
            last_modified_time = current_modified_time
        
        interval_seconds = config_data.get("interval_seconds", 60)
        currency_pairs = config_data.get("currency_pairs", [])
        
        exchange_rates = fetch_multiple_exchange_rates(currency_pairs)
        write_results_to_file(exchange_rates)
        
        print(f"Waiting {interval_seconds} seconds until next run...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
