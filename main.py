
import requests
from bs4 import BeautifulSoup

def get_exchange_rate(currency_from, currency_to):
    url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={currency_from}&To={currency_to}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch data")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        rate_section = soup.find("p", class_="sc-63d8b7e3-1 bMdPIi")
        
        if rate_section:
            rate_text = rate_section.get_text(strip=True)
            import re
            match = re.search(r"(\d+\.\d+)", rate_text)
            
            if match:
                rate = match.group(1)
                return float(rate)
            else:
                print("Could not find a valid numeric rate in the text")
                return None
        else:
            print("Rate section not found")
            return None
    except Exception as e:
        print("Error while parsing the exchange rate:", e)
        return None

currency_from = "EUR"
currency_to = "GBP"
rate = get_exchange_rate(currency_from, currency_to)
if rate:
    print(f"Exchange rate from {currency_from} to {currency_to}: {rate}")
else:
    print("Could not retrieve the exchange rate.")
