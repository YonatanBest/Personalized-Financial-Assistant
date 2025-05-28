import pandas as pd
from fpdf import FPDF
from datetime import datetime
from typing import List, Dict
import os
from .db_tools import bulk_insert_transactions, get_monthly_summary, get_all_user_transactions

def import_transactions_from_csv(user_id: str, file_path: str) -> bool:
    """
    Import transactions from a CSV file.
    Expected CSV format: date,amount,category,type
    """
    try:
        df = pd.read_csv(file_path)
        required_columns = ['date', 'amount', 'category', 'type']
        
        # Validate CSV structure
        if not all(col in df.columns for col in required_columns):
            print("CSV file missing required columns")
            return False
        
        # Convert DataFrame to list of dictionaries
        transactions = []
        for _, row in df.iterrows():
            transaction = {
                'user_id': user_id,
                'date': datetime.strptime(row['date'], '%Y-%m-%d').date(),
                'amount': float(row['amount']),
                'category': row['category'],
                'type': row['type'].lower()
            }
            transactions.append(transaction)
        
        # Bulk insert into database
        return bulk_insert_transactions(transactions)
    
    except Exception as e:
        print(f"Error importing transactions: {e}")
        return False

def export_data_to_csv(user_id: str) -> str:
    """
    Export all user transactions to CSV
    """
    try:
        transactions = get_all_user_transactions(user_id)
        
        # Convert to DataFrame
        data = []
        for trans in transactions:
            data.append({
                'date': trans.date,
                'amount': trans.amount,
                'category': trans.category,
                'type': trans.type
            })
        
        df = pd.DataFrame(data)
        
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        # Save to CSV
        filename = f'exports/transactions_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(filename, index=False)
        return filename
    
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return None

def export_summary_to_pdf(user_id: str, month: int, year: int = None) -> str:
    """
    Generate a PDF report of monthly financial summary
    """
    try:
        if year is None:
            year = datetime.now().year
        
        # Get monthly summary
        summary = get_monthly_summary(user_id, month, year)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Financial Summary - {datetime(year, month, 1).strftime("%B %Y")}', ln=True, align='C')
        
        # Overview
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Overview', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Total Income: ${summary["total_income"]:.2f}', ln=True)
        pdf.cell(0, 10, f'Total Expenses: ${summary["total_expenses"]:.2f}', ln=True)
        pdf.cell(0, 10, f'Net: ${summary["total_income"] - summary["total_expenses"]:.2f}', ln=True)
        
        # Category Breakdown
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Category Breakdown', ln=True)
        pdf.set_font('Arial', '', 12)
        
        for category, amount in summary['by_category'].items():
            pdf.cell(0, 10, f'{category}: ${amount:.2f}', ln=True)
        
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        # Save PDF
        filename = f'exports/summary_{user_id}_{year}{month:02d}.pdf'
        pdf.output(filename)
        return filename
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None 