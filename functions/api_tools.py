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
    Get cryptocurrency price using Binance's public API
    """
    try:
        symbol = crypto_symbol.upper()
        
        # Get USD price (using USDT as proxy)
        url_usd = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        response_usd = requests.get(url_usd, headers=headers, timeout=10)
        
        if response_usd.status_code == 200:
            data_usd = response_usd.json()
            usd_price = float(data_usd['price'])
            
            # Get EUR price
            url_eur = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}EUR"
            response_eur = requests.get(url_eur, headers=headers, timeout=10)
            
            if response_eur.status_code == 200:
                data_eur = response_eur.json()
                eur_price = float(data_eur['price'])
            else:
                # If EUR pair not available, convert from USD using a fixed rate
                eur_price = usd_price * 0.92  # Approximate EUR/USD rate
            
            return {
                'symbol': symbol,
                'usd': usd_price,
                'eur': eur_price
            }
        
        print(f"Error getting crypto price: Status {response_usd.status_code}")
        return {
            'symbol': symbol,
            'usd': None,
            'eur': None,
            'error': f'API Error: Status {response_usd.status_code}'
        }
    except Exception as e:
        print(f"Error in get_crypto_price: {e}")
        return {
            'symbol': crypto_symbol.upper(),
            'usd': None,
            'eur': None,
            'error': str(e)
        } 