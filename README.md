# Currency Exchange Rate Fetcher

This project fetches currency exchange rates for specified currency pairs at configurable intervals, saving the results in a JSON file. It uses `requests` to make HTTP requests and `BeautifulSoup` to parse exchange rate data from HTML.

## Table of Contents

- [How it works](#work-proccess)
- [Requirements](#requirements)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)

## Як працює цей скрипт {#work-proccess}

Скрипт `main.py` автоматизує процес отримання курсів обміну валют для зазначених валютних пар. Він працює циклічно, звертаючись до зовнішнього веб-сервісу для отримання курсів обміну валют, і зберігає результати у JSON-файлі. Основні етапи роботи скрипта такі:

1. **Ініціалізація**:

   - Скрипт спочатку завантажує параметри з файлів конфігурації (`config.py` та `config.json`).
   - У конфігураційному файлі `config.json` вказуються валютні пари (`currency_pairs`) та інтервал оновлення (`fetch_interval`).
   - У файлі config.py визначенні базові значення у тому числі в який файл зберігати отримані дані.

2. **Підготовка до запиту**:

   - Створюється сесія HTTP з використанням бібліотеки `requests`, до якої додається стратегія повторних спроб (retry strategy) для автоматичного повторного звернення у випадку невдалої відповіді від сервера.
   - Встановлюється заголовок запиту (User-Agent) для імітації запиту від браузера та уникнення блокувань.

3. **Отримання курсів валют**:

   - Для кожної валютної пари, зазначеної у `currency_pairs`, функція `get_exchange_rate` надсилає запит до веб-сервісу для отримання поточного курсу обміну.
   - Використовуючи `BeautifulSoup`, скрипт аналізує HTML-відповідь і знаходить курс обміну, якщо він присутній. Якщо курс знайдено, він повертається у вигляді кортежу.

4. **Обробка кількох валютних пар паралельно**:

   - Завдяки `ThreadPoolExecutor` обробка запитів для кількох валютних пар виконується паралельно, що зменшує час очікування і підвищує продуктивність.
   - Результати всіх запитів збираються у список словників із зазначенням валюти відправлення, валюти призначення та курсу.

5. **Запис результатів**:

   - Результати запитів зберігаються у JSON-файлі, зазначеному в `output_file` у `config.json`, разом із міткою часу.

6. **Циклічне виконання**:
   - Після запису результатів скрипт очікує вказаний у конфігурації інтервал часу (`fetch_interval`) перед наступним циклом. Скрипт також відстежує зміни у файлі `config.json` і, якщо зміни виявлено, автоматично перезавантажує нові параметри без перезапуску програми.

## Requirements {#requirements}

- Python 3.7+
- Install required libraries

## Setup {#setup}

- Clone the repository and navigate to the project directory:

```sh
git clone https://github.com/imdew1990/xe_currency_fetch.git
cd xe_currency_fetch
```

- Install the required libraries using pip:

```sh
pip3 install -r requirements.txt
```

## Configuration {#configuration}

- Create a configuration file `config.json` in the project directory with the following structure:

```json
{
  "interval_seconds": 15,
  "currency_pairs": [
    [
      "EUR",
      "GBP"
    ]
}
```

- `currency_pairs`: List of currency pairs to fetch.
- `fetch_interval`: Interval in seconds between fetches.
- `output_file`: File to save the fetched exchange rates.

## Usage {#usage}

- Run the script to start fetching exchange rates:

```sh
python3 main.py
```

## Testing {#testing}

- Run the tests using `pytest`:

```sh
python3 test_main.py
```
