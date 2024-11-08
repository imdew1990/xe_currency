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
    """
    Fetches the exchange rate between two currencies using a given session.

    Args:
        session (requests.Session): The session object to perform the HTTP request.
        currency_from (str): The currency code to convert from.
        currency_to (str): The currency code to convert to.

    Returns:
        tuple: A tuple containing:
            - currency_from (str): The currency code to convert from.
            - currency_to (str): The currency code to convert to.
            - rate (float or None): The exchange rate if found, otherwise None.

    Raises:
        Exception: If there is an error fetching or parsing the data.
    """
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
    """
    Fetches exchange rates for multiple currency pairs concurrently.

    Args:
        pairs (list of tuple): A list of tuples where each tuple contains two strings representing the currency pair
                               (e.g., [('USD', 'EUR'), ('GBP', 'JPY')]).

    Returns:
        list of dict: A list of dictionaries where each dictionary contains the exchange rate information with keys
                      "from", "to", and "rate". If an exchange rate could not be fetched, the corresponding entry
                      will be None.

    Raises:
        Exception: If an error occurs during the fetching of exchange rates, it will be printed to the console.
    """
    results = []
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
    """
    Load configuration for service.

    This function attempts to open and read a JSON configuration file specified by
    `config.CONFIG_FILE`. If successful, it returns the parsed JSON data as a dictionary.
    If an error occurs during this process, it catches the exception and returns None.

    Returns:
        dict or None: The parsed JSON configuration data if successful, otherwise None.
    """
    try:
        with open(config.CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None


def write_results_to_file(results):
    """
    Writes the exchange rate results to a specified output file in JSON format.

    Args:
        results (dict): A dictionary containing the exchange rate results.

    Writes:
        A JSON file with the current timestamp and the exchange rates.
    """
    with open(config.OUTPUT_FILE, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "exchange_rates": [results]
        }, f, indent=4)
    print(f"Results written to {config.OUTPUT_FILE}")


def validate_config(config_data):
    """
    Validates the configuration data for the currency fetching application.

    Args:
        config_data (dict): The configuration data to validate. Expected to contain the following keys:
            - "interval_seconds" (int): The interval in seconds for fetching currency data.
            - "currency_pairs" (list): A list of currency pairs, where each pair is a list of two currency codes.

    Returns:
        bool: True if the configuration data is valid, False otherwise.

    Prints:
        Warning messages if the configuration data is invalid, specifying the nature of the issue.
    """
    if config_data is None:
        print(f"\t\tWARNING: Systax error in {config.CONFIG_FILE}. Using previous configuration.")
        return False

    required_keys = {
        "interval_seconds": int,
        "currency_pairs": list
    }

    for key, expected_type in required_keys.items():
        if key not in config_data:
            print(f"\t\tWarning: Missing required config key '{key}'. Using previous configuration.")
            return False
        if not isinstance(config_data[key], expected_type):
            print(f"\t\tWarning: Invalid type for '{key}'. Expected {expected_type.__name__}. Using previous configuration.")
            return False
        if key == "currency_pairs" and not all(isinstance(pair, list) and len(pair) == 2 for pair in config_data["currency_pairs"]):
            print("\t\tWarning: 'currency_pairs' should be a list of pairs. Using previous configuration.")
            return False

    return True


def main():
    last_modified_time = os.path.getmtime(config.CONFIG_FILE)
    config_data = load_config()

    if not validate_config(config_data):
        print("\t\tInvalid initial configuration file. Please check 'config.json'.")
        return

    while True:
        current_modified_time = os.path.getmtime(config.CONFIG_FILE)
        if current_modified_time != last_modified_time:
            print("Configuration file changed. Reloading...")
            new_config_data = load_config()
            if validate_config(new_config_data):
                config_data = new_config_data
                last_modified_time = current_modified_time
            else:
                print("\t\tWARNING:Invalid configuration. Continuing with the previous valid configuration.")

        interval_seconds = config_data.get("interval_seconds", 60)
        currency_pairs = config_data.get("currency_pairs", [])

        start_time = time.time()
        exchange_rates = fetch_multiple_exchange_rates(currency_pairs)
        write_results_to_file(exchange_rates)
        
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"Recieved data in {execution_time:.2f} sec. Waiting {interval_seconds} seconds until next run...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
