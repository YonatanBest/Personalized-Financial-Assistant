from openai import OpenAI
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
from functions.api_tools import get_exchange_rate, get_crypto_price
from functions.db_tools import (
    log_transaction,
    get_monthly_summary,
    get_spending_by_category
)
from functions.file_tools import (
    import_transactions_from_csv,
    export_summary_to_pdf,
    export_data_to_csv
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI()  # It will automatically use OPENAI_API_KEY from environment

# Define available functions
AVAILABLE_FUNCTIONS = {
    "get_exchange_rate": {
        "name": "get_exchange_rate",
        "description": "Get the exchange rate between two currencies",
        "parameters": {
            "type": "object",
            "properties": {
                "base_currency": {
                    "type": "string",
                    "description": "The base currency code (e.g., USD)"
                },
                "target_currency": {
                    "type": "string",
                    "description": "The target currency code (e.g., EUR)"
                }
            },
            "required": ["base_currency", "target_currency"]
        }
    },
    "get_crypto_price": {
        "name": "get_crypto_price",
        "description": "Get the current price of a cryptocurrency",
        "parameters": {
            "type": "object",
            "properties": {
                "crypto_symbol": {
                    "type": "string",
                    "description": "The cryptocurrency symbol (e.g., BTC, ETH)"
                }
            },
            "required": ["crypto_symbol"]
        }
    },
    "log_transaction": {
        "name": "log_transaction",
        "description": "Log a new financial transaction",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID"
                },
                "amount": {
                    "type": "number",
                    "description": "The transaction amount"
                },
                "category": {
                    "type": "string",
                    "description": "The transaction category"
                },
                "type": {
                    "type": "string",
                    "description": "The transaction type (income or expense)"
                },
                "date": {
                    "type": "string",
                    "description": "The transaction date (YYYY-MM-DD)"
                }
            },
            "required": ["user_id", "amount", "category", "type", "date"]
        }
    },
    "get_monthly_summary": {
        "name": "get_monthly_summary",
        "description": "Get financial summary for a specific month",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID"
                },
                "month": {
                    "type": "integer",
                    "description": "The month number (1-12)"
                },
                "year": {
                    "type": "integer",
                    "description": "The year (optional, defaults to current year)"
                }
            },
            "required": ["user_id", "month"]
        }
    }
}

def execute_function(function_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute the specified function with given arguments"""
    if function_name == "get_exchange_rate":
        return get_exchange_rate(**arguments)
    elif function_name == "get_crypto_price":
        return get_crypto_price(**arguments)
    elif function_name == "log_transaction":
        # Convert date string to datetime
        arguments['date'] = datetime.strptime(arguments['date'], '%Y-%m-%d').date()
        return log_transaction(**arguments)
    elif function_name == "get_monthly_summary":
        return get_monthly_summary(**arguments)
    elif function_name == "get_spending_by_category":
        return get_spending_by_category(**arguments)
    elif function_name == "import_transactions_from_csv":
        return import_transactions_from_csv(**arguments)
    elif function_name == "export_summary_to_pdf":
        return export_summary_to_pdf(**arguments)
    elif function_name == "export_data_to_csv":
        return export_data_to_csv(**arguments)
    else:
        raise ValueError(f"Unknown function: {function_name}")

def process_user_message(user_id: str, message: str) -> str:
    """
    Process user message and execute appropriate functions
    """
    try:
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant. Use the available functions to help users with their financial tasks."},
                {"role": "user", "content": message}
            ],
            functions=list(AVAILABLE_FUNCTIONS.values()),
            function_call="auto"
        )

        # Get the response
        response_message = response.choices[0].message

        # Check if the model wants to call a function
        if response_message.function_call:
            # Get function details
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            
            # Add user_id if the function requires it
            if "user_id" in AVAILABLE_FUNCTIONS[function_name]["parameters"]["properties"]:
                function_args["user_id"] = user_id
            
            # Execute the function
            function_response = execute_function(function_name, function_args)
            
            # Create a new response incorporating the function result
            second_response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "You are a helpful financial assistant. Use the available functions to help users with their financial tasks."},
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": None, "function_call": response_message.function_call},
                    {"role": "function", "name": function_name, "content": json.dumps(function_response)}
                ]
            )
            
            return second_response.choices[0].message.content
        
        return response_message.content

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}" 