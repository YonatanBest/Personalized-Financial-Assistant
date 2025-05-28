from typing import Dict, List, Optional
from api.currency_exchange import CurrencyExchangeAPI
from utils.file_manager import FileManager
import json
import os
import requests
from datetime import datetime
from calendar import monthrange

# Initialize our services
currency_api = CurrencyExchangeAPI()
file_manager = FileManager()

def get_exchange_rate(base_currency: str, target_currency: str) -> str:
    """Get the exchange rate between two currencies"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url)
        data = response.json()
        rate = data['rates'][target_currency]
        return f"1 {base_currency} = {rate} {target_currency}"
    except Exception as e:
        return f"Error fetching exchange rate: {str(e)}"

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url)
        data = response.json()
        rate = data['rates'][to_currency]
        converted_amount = amount * rate
        return f"{amount} {from_currency} = {converted_amount} {to_currency}"
    except Exception as e:
        return f"Error converting currency: {str(e)}"

def record_expense(amount: float, category: str, description: str, currency: str) -> str:
    """Record a new expense in the expenses.json file"""
    try:
        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load existing expenses or create new list
        expenses_file = 'data/expenses.json'
        if os.path.exists(expenses_file):
            with open(expenses_file, 'r') as f:
                expenses = json.load(f)
        else:
            expenses = []
        
        # Add new expense
        expense = {
            'timestamp': datetime.now().isoformat(),
            'amount': amount,
            'category': category,
            'description': description,
            'currency': currency
        }
        expenses.append(expense)
        
        # Save updated expenses
        with open(expenses_file, 'w') as f:
            json.dump(expenses, f, indent=2)
        
        return f"Successfully recorded expense: {amount} {currency} for {description} ({category})"
    except Exception as e:
        return f"Error recording expense: {str(e)}"

def get_expense_summary(start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Get a summary of all expenses"""
    try:
        # Load expenses
        expenses_file = 'data/expenses.json'
        if not os.path.exists(expenses_file):
            return "No expenses recorded yet."
            
        with open(expenses_file, 'r') as f:
            expenses = json.load(f)
        
        # Filter by date if provided
        if start_date:
            start = datetime.fromisoformat(start_date)
            expenses = [e for e in expenses if datetime.fromisoformat(e['timestamp']) >= start]
        if end_date:
            end = datetime.fromisoformat(end_date)
            expenses = [e for e in expenses if datetime.fromisoformat(e['timestamp']) <= end]
        
        # Calculate totals by currency
        totals = {}
        categories = {}
        for expense in expenses:
            # Skip income entries
            if expense['category'].lower() == 'income':
                continue
                
            amount = expense['amount']
            currency = expense['currency']
            category = expense['category']
            
            # Update currency totals
            if currency not in totals:
                totals[currency] = 0
            totals[currency] += amount
            
            # Update category totals
            if category not in categories:
                categories[category] = {'amount': 0, 'currency': currency}
            if categories[category]['currency'] == currency:
                categories[category]['amount'] += amount
        
        # Format the summary
        summary = "Expense Summary:\n\n"
        
        # Total by currency
        summary += "Total by Currency:\n"
        for currency, total in totals.items():
            summary += f"{currency}: {total:.2f}\n"
        
        # Total by category
        summary += "\nTotal by Category:\n"
        for category, data in categories.items():
            summary += f"{category}: {data['amount']:.2f} {data['currency']}\n"
        
        return summary
    except Exception as e:
        return f"Error generating expense summary: {str(e)}"

def get_expense_report(format: str = 'text') -> str:
    """Generate an expense report in the specified format"""
    try:
        # Load expenses
        expenses_file = 'data/expenses.json'
        if not os.path.exists(expenses_file):
            return "No expenses recorded yet."
            
        with open(expenses_file, 'r') as f:
            expenses = json.load(f)
        
        if format.lower() == 'text':
            # Generate text report
            report = "Expense Report\n\n"
            
            # Sort expenses by date
            expenses.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Group by month
            current_month = None
            monthly_total = {'amount': 0, 'currency': None}
            
            for expense in expenses:
                # Skip income entries
                if expense['category'].lower() == 'income':
                    continue
                    
                date = datetime.fromisoformat(expense['timestamp'])
                month = date.strftime("%B %Y")
                
                if month != current_month:
                    # Print previous month's total
                    if current_month and monthly_total['currency']:
                        report += f"\nTotal for {current_month}: {monthly_total['amount']:.2f} {monthly_total['currency']}\n"
                        report += "-" * 50 + "\n\n"
                    
                    # Start new month
                    current_month = month
                    monthly_total = {'amount': 0, 'currency': None}
                    report += f"{month}\n" + "=" * len(month) + "\n\n"
                
                # Add expense details
                report += f"Date: {date.strftime('%Y-%m-%d %H:%M')}\n"
                report += f"Category: {expense['category']}\n"
                report += f"Description: {expense['description']}\n"
                report += f"Amount: {expense['amount']} {expense['currency']}\n\n"
                
                # Update monthly total if same currency
                if not monthly_total['currency']:
                    monthly_total['currency'] = expense['currency']
                if monthly_total['currency'] == expense['currency']:
                    monthly_total['amount'] += expense['amount']
            
            # Add last month's total
            if current_month and monthly_total['currency']:
                report += f"\nTotal for {current_month}: {monthly_total['amount']:.2f} {monthly_total['currency']}\n"
            
            return report
            
        else:
            return "Unsupported report format. Currently only 'text' format is supported."
            
    except Exception as e:
        return f"Error generating expense report: {str(e)}"

def import_expense_data(file_path: str) -> str:
    """Import expense data from a file"""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found."
            
        # Read the import file
        with open(file_path, 'r') as f:
            import_data = json.load(f)
            
        # Validate the import data
        required_fields = ['amount', 'category', 'description', 'currency', 'timestamp']
        for entry in import_data:
            missing_fields = [field for field in required_fields if field not in entry]
            if missing_fields:
                return f"Error: Missing required fields {missing_fields} in import data"
        
        # Load existing expenses
        expenses_file = 'data/expenses.json'
        if os.path.exists(expenses_file):
            with open(expenses_file, 'r') as f:
                expenses = json.load(f)
        else:
            expenses = []
            
        # Add new expenses
        expenses.extend(import_data)
        
        # Sort by timestamp
        expenses.sort(key=lambda x: x['timestamp'])
        
        # Save updated expenses
        with open(expenses_file, 'w') as f:
            json.dump(expenses, f, indent=2)
            
        return f"Successfully imported {len(import_data)} expense records"
        
    except json.JSONDecodeError:
        return "Error: Import file must be in valid JSON format"
    except Exception as e:
        return f"Error importing expense data: {str(e)}"

def set_budget(category: str, amount: float, currency: str, period: str = "monthly") -> str:
    """Set a budget for a specific category"""
    try:
        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load existing budgets or create new dict
        budget_file = 'data/budgets.json'
        if os.path.exists(budget_file):
            with open(budget_file, 'r') as f:
                budgets = json.load(f)
        else:
            budgets = {}
        
        # Add/update budget
        budget_key = f"{category}_{period}"
        budgets[budget_key] = {
            'category': category,
            'amount': amount,
            'currency': currency,
            'period': period,
            'last_updated': datetime.now().isoformat()
        }
        
        # Save updated budgets
        with open(budget_file, 'w') as f:
            json.dump(budgets, f, indent=2)
        
        return f"Successfully set {period} budget for {category}: {amount} {currency}"
    except Exception as e:
        return f"Error setting budget: {str(e)}"

def get_budget_status() -> str:
    """Get status of all budgets including spending"""
    try:
        # Load budgets
        budget_file = 'data/budgets.json'
        if not os.path.exists(budget_file):
            return "No budgets set yet."
            
        with open(budget_file, 'r') as f:
            budgets = json.load(f)
            
        # Load expenses
        expenses_file = 'data/expenses.json'
        if not os.path.exists(expenses_file):
            expenses = []
        else:
            with open(expenses_file, 'r') as f:
                expenses = json.load(f)
        
        # Get current month's expenses
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_expenses = [
            e for e in expenses 
            if datetime.fromisoformat(e['timestamp']) >= current_month
            and e['category'].lower() != 'income'
        ]
        
        # Calculate spending per category
        spending = {}
        for expense in month_expenses:
            category = expense['category']
            if category not in spending:
                spending[category] = {'amount': 0, 'currency': expense['currency']}
            if spending[category]['currency'] == expense['currency']:
                spending[category]['amount'] += expense['amount']
        
        # Format the status report
        status = "Budget Status Report:\n\n"
        
        for budget_key, budget in budgets.items():
            category = budget['category']
            period = budget['period']
            if period != 'monthly':  # Skip non-monthly budgets for now
                continue
                
            status += f"Category: {category}\n"
            status += f"Budget: {budget['amount']} {budget['currency']}\n"
            
            # Add spending if we have it
            if category in spending and spending[category]['currency'] == budget['currency']:
                spent = spending[category]['amount']
                percentage = (spent / budget['amount']) * 100
                status += f"Spent: {spent:.2f} {spending[category]['currency']} ({percentage:.1f}%)\n"
                
                # Add warning if over 80% of budget
                if percentage >= 100:
                    status += "⚠️ OVER BUDGET!\n"
                elif percentage >= 80:
                    status += "⚠️ Approaching budget limit!\n"
            else:
                status += "Spent: 0.00 (0%)\n"
            
            status += "\n"
        
        return status
    except Exception as e:
        return f"Error getting budget status: {str(e)}" 