'''
CashHandler class for managing currency conversion and cash amounts.
This class provides methods to convert amounts between different currencies,
handle cash amounts in cents, and fetch exchange rates using an external API.
It is designed to work with a target currency specified in the configuration.
It includes error handling for invalid inputs and API failures.
It is part of a larger system that manages flight alerts and related services.
'''
import requests

try:
    from ..global_state import state
except ImportError:
    from global_state import state

class CashHandler:
    def __init__(self):
        self.cache = dict()
    
    def load(self, target_currency: str, api_key: str = None):
        """
        Load the target currency for conversion.
        
        Args:
            target_currency (str): The currency to convert amounts to.
            
        Raises:
            ValueError: If target_currency is not provided or is empty.
        """
        if api_key == "test":
            self.target_currency = "USD"
            self.cache = {
                "BRL": 5000,
                "GBP": 3000,
                "AUD": 4000,
                "EUR": 2000,
                "CAD": 2500,
            }
            return

        if not target_currency:
            state.logger.error("Target currency must be specified.")
            raise ValueError("Target currency must be specified.")
        
        self.target_currency = target_currency.upper()
        self.__api_key = api_key
        state.logger.info(f"CashHandler initialized with target currency: {self.target_currency}")

    def normal_to_cents(self, amount: float) -> int:
        """
        Convert a normal float amount to cents (integer representation).
        Args:
            amount (float): The amount to convert.
        Returns:
            int: The amount in cents.
        Raises:
            ValueError: If amount is negative.
        """
        if amount < 0:
            state.logger.error("Amount cannot be negative.")
            raise ValueError("Amount cannot be negative.")
        return int(amount * 100)
    
    def get_rate(self, base_currency):
        if base_currency in self.cache:
            return self.cache[base_currency]
        
        rate = self.fetch_rate(base_currency)
        if rate is not None:
            self.cache[base_currency] = self.normal_to_cents(rate)
        return self.normal_to_cents(rate)
    
    def fetch_rate(self, base_currency):
        """
        Fetch the exchange rate for the given base currency to the target currency.
        Args:
            base_currency (str): The currency to convert from.
        Returns:
            float: The exchange rate from base_currency to target_currency.
        Raises:
            Exception: If the API request fails or returns an error.
        """
        url = f"https://v6.exchangerate-api.com/v6/{self.__api_key}/pair/{base_currency}/{self.target_currency}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            conversion_rate = data.get("conversion_rate")
            if conversion_rate is not None:
                self.cache[base_currency] = conversion_rate
                return conversion_rate
            else:
                state.logger.error("Conversion rate not found in response.")
                raise ValueError("Conversion rate not found in response.")
        else:
            state.logger.error(f"Failed to fetch exchange rate: {response.status_code} - {response.text}")
            raise Exception(f"Failed to fetch exchange rate: {response.status_code} - {response.text}")
    
    def convert_to_system_base(self, amount_in_cents: int, base_currency: str) -> int:
        """
        Convert an amount in cents from a base currency to the target currency.
        Args:
            amount_in_cents (int): The amount in cents to convert.
            base_currency (str): The currency of the amount being converted.
        Returns:
            int: The converted amount in cents in the target currency.
        Raises:
            ValueError: If base_currency is not found in the exchange rates.
        """
        if self.target_currency == base_currency:
            return amount_in_cents
        rate = self.get_rate(base_currency)
        if rate is None:
            state.logger.error(f"Exchange rate for {base_currency} to {self.target_currency} not found.")
            raise ValueError(f"Exchange rate for {base_currency} to {self.target_currency} not found.")
        
        return amount_in_cents * rate // 100

handler = CashHandler()

def cents_to_str(cents: int, currency_symbol: str, currency_title: str) -> str:
    """
    Convert cents to a formatted currency string.
    
    This utility function converts integer cent values to properly formatted
    currency strings with symbol and currency code.
    
    Args:
        cents (int): Amount in cents
        currency_symbol (str): Currency symbol (e.g., '$', 'R$')
        currency_title (str): Currency code (e.g., 'USD', 'BRL')
        
    Returns:
        str: Formatted currency string (e.g., "$ 123.45 (USD)")
        
    Raises:
        ValueError: If currency_symbol or currency_title is not provided
    """
    if not currency_symbol or not currency_title:
        state.logger.error("CURRENCY_SYMBOL or CURRENCY_TITLE environment variable is not set.")
        raise ValueError("CURRENCY_SYMBOL or CURRENCY_TITLE environment variable is not set.")
    return f"{currency_symbol} {cents // 100}.{cents % 100:02d} ({currency_title})"