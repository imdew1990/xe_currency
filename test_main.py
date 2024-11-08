import unittest
from unittest.mock import patch, Mock
import requests
from main import get_exchange_rate, fetch_multiple_exchange_rates

class TestGetExchangeRate(unittest.TestCase):

    @patch('main.requests.Session.get')
    def test_get_exchange_rate_success(self, mock_get):
        # Mock response content
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '''
        <html>
            <body>
                <p class="sc-63d8b7e3-1 bMdPIi">1.2345</p>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        session = requests.Session()
        currency_from = 'USD'
        currency_to = 'EUR'
        result = get_exchange_rate(session, currency_from, currency_to)

        self.assertEqual(result, (currency_from, currency_to, 1.2345))

    @patch('main.requests.Session.get')
    def test_get_exchange_rate_no_rate_section(self, mock_get):
        # Mock response content without rate section
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '''
        <html>
            <body>
                <p class="some-other-class">No rate here</p>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        session = requests.Session()
        currency_from = 'USD'
        currency_to = 'EUR'
        result = get_exchange_rate(session, currency_from, currency_to)

        self.assertEqual(result, (currency_from, currency_to, None))

    @patch('main.requests.Session.get')
    def test_get_exchange_rate_invalid_rate_format(self, mock_get):
        # Mock response content with invalid rate format
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '''
        <html>
            <body>
                <p class="sc-63d8b7e3-1 bMdPIi">Invalid rate</p>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        session = requests.Session()
        currency_from = 'USD'
        currency_to = 'EUR'
        result = get_exchange_rate(session, currency_from, currency_to)

        self.assertEqual(result, (currency_from, currency_to, None))

    @patch('main.requests.Session.get')
    def test_get_exchange_rate_http_error(self, mock_get):
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_get.return_value = mock_response

        session = requests.Session()
        currency_from = 'USD'
        currency_to = 'EUR'
        result = get_exchange_rate(session, currency_from, currency_to)

        self.assertEqual(result, (currency_from, currency_to, None))

    @patch('main.requests.Session.get')
    def test_get_exchange_rate_exception(self, mock_get):
        # Mock general exception
        mock_get.side_effect = Exception("Some error")

        session = requests.Session()
        currency_from = 'USD'
        currency_to = 'EUR'
        result = get_exchange_rate(session, currency_from, currency_to)

        self.assertEqual(result, (currency_from, currency_to, None))


class TestFetchMultipleExchangeRates(unittest.TestCase):

    @patch('main.get_exchange_rate')
    @patch('main.requests.Session')
    def test_fetch_multiple_exchange_rates_success(self, mock_session, mock_get_exchange_rate):
        # Mock get_exchange_rate to return a successful rate
        mock_get_exchange_rate.side_effect = [
            ('USD', 'EUR', 1.2345),
            ('GBP', 'USD', 1.5678)
        ]

        pairs = [('USD', 'EUR'), ('GBP', 'USD')]
        results = fetch_multiple_exchange_rates(mock_session, pairs)

        expected_results = [
            {"from": "USD", "to": "EUR", "rate": 1.2345},
            {"from": "GBP", "to": "USD", "rate": 1.5678}
        ]

        self.assertEqual(results, expected_results)

    @patch('main.get_exchange_rate')
    @patch('main.requests.Session')
    def test_fetch_multiple_exchange_rates_partial_failure(self, mock_session, mock_get_exchange_rate):
        # Mock get_exchange_rate to return a mix of successful and None rates
        mock_get_exchange_rate.side_effect = [
            ('USD', 'EUR', 1.2345),
            ('GBP', 'USD', None)
        ]

        pairs = [('USD', 'EUR'), ('GBP', 'USD')]
        results = fetch_multiple_exchange_rates(mock_session, pairs)

        expected_results = [
            {"from": "USD", "to": "EUR", "rate": 1.2345},
            {"from": "GBP", "to": "USD", "rate": None}
        ]

        self.assertEqual(results, expected_results)

    @patch('main.get_exchange_rate')
    @patch('main.requests.Session')
    def test_fetch_multiple_exchange_rates_all_failure(self, mock_session, mock_get_exchange_rate):
        # Mock get_exchange_rate to return None for all pairs
        mock_get_exchange_rate.side_effect = [
            ('USD', 'EUR', None),
            ('GBP', 'USD', None)
        ]

        pairs = [('USD', 'EUR'), ('GBP', 'USD')]
        results = fetch_multiple_exchange_rates(mock_session, pairs)

        expected_results = [
            {"from": "USD", "to": "EUR", "rate": None},
            {"from": "GBP", "to": "USD", "rate": None}
        ]

        self.assertEqual(results, expected_results)

if __name__ == '__main__':
    unittest.main()
