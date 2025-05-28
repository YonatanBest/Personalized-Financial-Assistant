import requests
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (should be in .env file)
EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', 'demo')

def get_exchange_rate(base_currency: str, target_currency: str) -> Optional[float]:
    """
    Get the exchange rate between two currencies using exchangerate-api.com
    """
    try:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{base_currency}/{target_currency}"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and 'conversion_rate' in data:
            return data['conversion_rate']
        else:
            print(f"Error getting exchange rate: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error in get_exchange_rate: {e}")
        return None

def get_crypto_price(crypto_symbol: str) -> Optional[Dict]:
    """
    Get cryptocurrency price using CoinDesk API
    Note: CoinDesk API only provides BTC price data
    """
    try:
        if crypto_symbol.upper() != 'BTC':
            return {
                'symbol': crypto_symbol.upper(),
                'usd': None,
                'eur': None,
                'error': 'Only BTC is supported through CoinDesk API'
            }

        url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and 'bpi' in data:
            return {
                'symbol': 'BTC',
                'usd': data['bpi']['USD']['rate_float'],
                'eur': data['bpi']['EUR']['rate_float']
            }
        else:
            print(f"Error getting crypto price: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error in get_crypto_price: {e}")
        return None 