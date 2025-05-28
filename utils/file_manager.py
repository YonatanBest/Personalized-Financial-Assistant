import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class FileManager:
    def __init__(self):
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.reports_dir = Path(os.getenv("REPORT_OUTPUT_DIR", "./reports"))
        
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def save_expense(self, expense: Dict[str, Any]) -> bool:
        """
        Save an expense record to JSON file.
        
        Args:
            expense (dict): Expense record containing amount, category, date, etc.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            expense_file = self.data_dir / "expenses.json"
            expenses = []
            
            if expense_file.exists():
                with open(expense_file, 'r') as f:
                    expenses = json.load(f)
                    
            # Add timestamp if not present
            if 'timestamp' not in expense:
                expense['timestamp'] = datetime.now().isoformat()
                
            expenses.append(expense)
            
            with open(expense_file, 'w') as f:
                json.dump(expenses, f, indent=4)
                
            return True
        except Exception as e:
            print(f"Error saving expense: {e}")
            return False
            
    def get_expenses(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve expense records within a date range.
        
        Args:
            start_date (str, optional): Start date in ISO format
            end_date (str, optional): End date in ISO format
            
        Returns:
            list: List of expense records
        """
        expense_file = self.data_dir / "expenses.json"
        if not expense_file.exists():
            return []
            
        try:
            with open(expense_file, 'r') as f:
                expenses = json.load(f)
                
            if start_date:
                expenses = [e for e in expenses if e['timestamp'] >= start_date]
            if end_date:
                expenses = [e for e in expenses if e['timestamp'] <= end_date]
                
            return expenses
        except Exception as e:
            print(f"Error reading expenses: {e}")
            return []
            
    def generate_expense_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                              format: str = "xlsx") -> Optional[str]:
        """
        Generate an expense report in the specified format.
        
        Args:
            start_date (str, optional): Start date in ISO format
            end_date (str, optional): End date in ISO format
            format (str): Output format ('xlsx' or 'csv')
            
        Returns:
            str: Path to the generated report file
        """
        expenses = self.get_expenses(start_date, end_date)
        if not expenses:
            return None
            
        try:
            df = pd.DataFrame(expenses)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == 'xlsx':
                output_file = self.reports_dir / f"expense_report_{timestamp}.xlsx"
                df.to_excel(output_file, index=False)
            else:
                output_file = self.reports_dir / f"expense_report_{timestamp}.csv"
                df.to_csv(output_file, index=False)
                
            return str(output_file)
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
            
    def import_expenses(self, file_path: str) -> bool:
        """
        Import expenses from a CSV or Excel file.
        
        Args:
            file_path (str): Path to the import file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path)
            elif file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                print("Unsupported file format")
                return False
                
            expenses = df.to_dict('records')
            for expense in expenses:
                self.save_expense(expense)
                
            return True
        except Exception as e:
            print(f"Error importing expenses: {e}")
            return False 