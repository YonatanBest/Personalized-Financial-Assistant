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
                },
                "currency": {
                    "type": "string",
                    "description": "The currency code (e.g., USD, EUR). Defaults to USD if not specified."
                }
            },
            "required": ["user_id", "amount", "category", "type"]
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
    },
    "get_spending_by_category": {
        "name": "get_spending_by_category",
        "description": "Get spending breakdown by category",
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
    },
    "import_transactions_from_csv": {
        "name": "import_transactions_from_csv",
        "description": "Import transactions from a CSV file",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the CSV file"
                }
            },
            "required": ["user_id", "file_path"]
        }
    },
    "export_summary_to_pdf": {
        "name": "export_summary_to_pdf",
        "description": "Export monthly summary to PDF",
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
                    "description": "The year"
                }
            },
            "required": ["user_id", "month", "year"]
        }
    },
    "export_data_to_csv": {
        "name": "export_data_to_csv",
        "description": "Export all transactions to CSV file",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The user ID"
                }
            },
            "required": ["user_id"]
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
        # Get current date information
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        current_month_name = current_date.strftime('%B')

        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"""You are a helpful financial assistant. Use the available functions to help users with their financial tasks.

IMPORTANT: You have direct access to the user's data through functions - NEVER ask for user_id or other information that's already provided to you.

When logging transactions:
1. ALWAYS use the log_transaction function to actually save the transaction
2. For foreign currencies, first calculate the USD amount but then use the original currency in the log_transaction call
3. Use today's date ({current_date.strftime('%Y-%m-%d')}) if no date is specified
4. Common categories: 'transport', 'food', 'utilities', 'entertainment', 'shopping', 'income', 'other'
5. For expenses, set type='expense'. For income, set type='income'
6. After logging, confirm the details and show the USD equivalent

Example transaction logging:
User: "Spent 50 euros on food"
Assistant: Let me log that transaction for you:
- Amount: 50 EUR
- Category: food
- Type: expense
- Date: {current_date.strftime('%Y-%m-%d')}
*calls log_transaction with these details*

When users ask to export their transactions to CSV:
1. Use the export_data_to_csv function immediately
2. Tell them the path where their CSV file has been saved

When users ask for their monthly summary:
1. Call get_monthly_summary immediately with the current month ({current_month}) and year ({current_year}) if not specified
2. Format the response like this:
📊 Monthly Summary for {current_month_name} {current_year}
💰 Income: $X
💸 Expenses: $X
💵 Net: $X
📈 Top Income Sources:
  - Category 1: $X
  - Category 2: $X
📉 Top Expenses:
  - Category 1: $X
  - Category 2: $X
🔄 Currencies Used: USD, EUR, etc.

After logging a transaction:
1. Automatically show the updated monthly summary for the current month
2. This helps users see their transaction was properly recorded

Always be proactive and context-aware:
1. Never ask for information you already have (like user_id)
2. After any transaction is logged, show the monthly summary
3. If a user asks about their spending, immediately show the summary
4. Use emojis and clear formatting to make information easy to read"""},
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
            
            # For get_monthly_summary, ensure current month/year if not specified
            if function_name == "get_monthly_summary":
                if "month" not in function_args:
                    function_args["month"] = current_month
                if "year" not in function_args:
                    function_args["year"] = current_year
                    
            # For log_transaction, ensure date and currency if not specified
            if function_name == "log_transaction":
                if "date" not in function_args:
                    function_args["date"] = current_date.strftime('%Y-%m-%d')
                if "currency" not in function_args:
                    function_args["currency"] = "USD"
            
            # Execute the function
            function_response = execute_function(function_name, function_args)
            
            # If this was a log_transaction, automatically get the monthly summary
            if function_name == "log_transaction" and function_response:
                summary_response = execute_function("get_monthly_summary", {
                    "user_id": user_id,
                    "month": current_month,
                    "year": current_year
                })
                function_response = {
                    "transaction_success": function_response,
                    "monthly_summary": summary_response
                }
            
            # Create a new response incorporating the function result
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"""You are a helpful financial assistant. Use the available functions to help users with their financial tasks.

IMPORTANT: You have direct access to the user's data through functions - NEVER ask for user_id or other information that's already provided to you.

When logging transactions:
1. ALWAYS use the log_transaction function to actually save the transaction
2. For foreign currencies, first calculate the USD amount but then use the original currency in the log_transaction call
3. Use today's date ({current_date.strftime('%Y-%m-%d')}) if no date is specified
4. Common categories: 'transport', 'food', 'utilities', 'entertainment', 'shopping', 'income', 'other'
5. For expenses, set type='expense'. For income, set type='income'
6. After logging, confirm the details and show the USD equivalent

Example transaction logging:
User: "Spent 50 euros on food"
Assistant: Let me log that transaction for you:
- Amount: 50 EUR
- Category: food
- Type: expense
- Date: {current_date.strftime('%Y-%m-%d')}
*calls log_transaction with these details*

When users ask to export their transactions to CSV:
1. Use the export_data_to_csv function immediately
2. Tell them the path where their CSV file has been saved

When users ask for their monthly summary:
1. Call get_monthly_summary immediately with the current month ({current_month}) and year ({current_year}) if not specified
2. Format the response like this:
📊 Monthly Summary for {current_month_name} {current_year}
💰 Income: $X
💸 Expenses: $X
💵 Net: $X
📈 Top Income Sources:
  - Category 1: $X
  - Category 2: $X
📉 Top Expenses:
  - Category 1: $X
  - Category 2: $X
🔄 Currencies Used: USD, EUR, etc.

After logging a transaction:
1. Automatically show the updated monthly summary for the current month
2. This helps users see their transaction was properly recorded

Always be proactive and context-aware:
1. Never ask for information you already have (like user_id)
2. After any transaction is logged, show the monthly summary
3. If a user asks about their spending, immediately show the summary
4. Use emojis and clear formatting to make information easy to read"""},
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": None, "function_call": response_message.function_call},
                    {"role": "function", "name": function_name, "content": json.dumps(function_response)}
                ]
            )
            
            return second_response.choices[0].message.content
        
        return response_message.content

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}" 