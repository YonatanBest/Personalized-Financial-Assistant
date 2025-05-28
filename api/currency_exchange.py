import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class CurrencyExchangeAPI:
    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        
    def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[float]:
        """
        Get the exchange rate between two currencies.
        
        Args:
            base_currency (str): The base currency code (e.g., 'USD')
            target_currency (str): The target currency code (e.g., 'EUR')
            
        Returns:
            float: The exchange rate or None if the request fails
        """
        try:
            response = requests.get(f"{self.base_url}{base_currency}")
            response.raise_for_status()
            data = response.json()
            return data['rates'].get(target_currency)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rate: {e}")
            return None
            
    def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Convert an amount from one currency to another.
        
        Args:
            amount (float): The amount to convert
            from_currency (str): The source currency code
            to_currency (str): The target currency code
            
        Returns:
            float: The converted amount or None if the conversion fails
        """
        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate is not None:
            return amount * rate
        return None
        
    def get_all_rates(self, base_currency: str) -> Optional[Dict[str, float]]:
        """
        Get all available exchange rates for a base currency.
        
        Args:
            base_currency (str): The base currency code
            
        Returns:
            dict: A dictionary of currency codes and their rates
        """
        try:
            response = requests.get(f"{self.base_url}{base_currency}")
            response.raise_for_status()
            data = response.json()
            return data['rates']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rates: {e}")
            return None 