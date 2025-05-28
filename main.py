import autogen
from dotenv import load_dotenv
import os
import json
from agents.functions import (
    get_exchange_rate,
    convert_currency,
    record_expense,
    get_expense_report,
    import_expense_data,
    get_expense_summary,
    set_budget,
    get_budget_status
)

# Load environment variables
load_dotenv()

# Configuration for the assistant
config_list = [
    {
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
]

# Function configurations
currency_functions = [
    {
        "name": "get_exchange_rate",
        "description": "Get the exchange rate between two currencies",
        "parameters": {
            "type": "object",
            "properties": {
                "base_currency": {"type": "string", "description": "The base currency code (e.g., USD)"},
                "target_currency": {"type": "string", "description": "The target currency code (e.g., EUR)"}
            },
            "required": ["base_currency", "target_currency"]
        }
    },
    {
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "The amount to convert"},
                "from_currency": {"type": "string", "description": "The source currency code"},
                "to_currency": {"type": "string", "description": "The target currency code"}
            },
            "required": ["amount", "from_currency", "to_currency"]
        }
    }
]

file_functions = [
    {
        "name": "record_expense",
        "description": "Record a new expense",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "The expense amount"},
                "category": {"type": "string", "description": "The expense category"},
                "description": {"type": "string", "description": "Description of the expense"},
                "currency": {"type": "string", "description": "The currency code"}
            },
            "required": ["amount", "category", "description", "currency"]
        }
    },
    {
        "name": "get_expense_summary",
        "description": "Get a summary of all expenses",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date in ISO format (optional)"},
                "end_date": {"type": "string", "description": "End date in ISO format (optional)"}
            }
        }
    },
    {
        "name": "set_budget",
        "description": "Set a budget for a specific category",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "The expense category to set budget for"},
                "amount": {"type": "number", "description": "The budget amount"},
                "currency": {"type": "string", "description": "The currency code"},
                "period": {"type": "string", "description": "Budget period (monthly/yearly)", "default": "monthly"}
            },
            "required": ["category", "amount", "currency"]
        }
    },
    {
        "name": "get_budget_status",
        "description": "Get the current status of all budgets",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_expense_report",
        "description": "Generate a detailed expense report",
        "parameters": {
            "type": "object",
            "properties": {
                "format": {"type": "string", "description": "Report format (text/csv)", "default": "text"}
            }
        }
    },
    {
        "name": "import_expense_data",
        "description": "Import expense data from a JSON file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the JSON file containing expense data"}
            },
            "required": ["file_path"]
        }
    }
]

# Create assistant agents
financial_advisor = autogen.AssistantAgent(
    name="financial_advisor",
    system_message="""You are a financial advisor assistant. You help users with:
    1. Currency exchange rate information
    2. Expense tracking and categorization
    3. Financial report generation
    4. Data import/export operations
    
    When the user asks for currency exchange rates, delegate to the api_specialist.
    When the user asks for file operations or expense summaries, delegate to the file_manager.""",
    llm_config={"config_list": config_list},
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=0,
    is_termination_msg=lambda x: x.get("content", "").lower().strip() in ["exit", "quit", "bye"],
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": False,
    },
)

# Create API agent for currency exchange
api_specialist = autogen.AssistantAgent(
    name="api_specialist",
    system_message="""You are an API specialist who handles currency exchange rate operations.
    You know how to:
    1. Fetch real-time exchange rates
    2. Convert between different currencies
    3. Handle API errors and rate limits""",
    llm_config={
        "config_list": config_list,
        "functions": currency_functions
    },
    function_map={
        "get_exchange_rate": get_exchange_rate,
        "convert_currency": convert_currency
    }
)

# Create file management agent
file_manager = autogen.AssistantAgent(
    name="file_manager",
    system_message="""You are a file management specialist who handles:
    1. Expense record storage and retrieval
    2. Report generation in various formats
    3. Budget management and tracking
    4. Data import/export operations
    
    When asked about expense summaries or totals, use the get_expense_summary function.
    When asked about budgets, use the set_budget and get_budget_status functions.
    When asked for detailed reports, use the get_expense_report function.""",
    llm_config={
        "config_list": config_list,
        "functions": file_functions
    },
    function_map={
        "record_expense": record_expense,
        "get_expense_report": get_expense_report,
        "import_expense_data": import_expense_data,
        "get_expense_summary": get_expense_summary,
        "set_budget": set_budget,
        "get_budget_status": get_budget_status
    }
)

def initialize_chat():
    """Initialize a group chat with all agents"""
    groupchat = autogen.GroupChat(
        agents=[user_proxy, financial_advisor, api_specialist, file_manager],
        messages=[],
        max_round=50
    )
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})
    
    return groupchat, manager

def main():
    # Initialize the group chat
    groupchat, manager = initialize_chat()
    
    # Start the conversation
    user_proxy.initiate_chat(
        manager,
        message="""Hello! I need help with managing my finances. 
        What services can you offer me?"""
    )

if __name__ == "__main__":
    main() 