from sqlalchemy import create_engine, Column, Integer, Float, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Dict
import enum
import os
from .api_tools import get_exchange_rate

# Create database directory if it doesn't exist
os.makedirs('database', exist_ok=True)

# Database setup
DATABASE_URL = "sqlite:///database/transactions.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    amount_usd = Column(Float)  # Amount in USD
    original_amount = Column(Float)  # Original amount in original currency
    original_currency = Column(String)  # Original currency code
    category = Column(String)
    type = Column(String)  # Using String instead of Enum for flexibility
    date = Column(Date)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def convert_to_usd(amount: float, currency: str) -> float:
    """Convert amount from given currency to USD."""
    if currency == 'USD':
        return amount
    
    rate = get_exchange_rate(currency, 'USD')
    if rate is None:
        raise ValueError(f"Could not get exchange rate for {currency} to USD")
    
    return amount * rate

def log_transaction(user_id: str, amount: float, category: str, type: str, date: datetime, currency: str = 'USD') -> bool:
    """
    Log a new financial transaction.
    All amounts are converted to USD before storing, but original amount and currency are preserved.
    """
    db = next(get_db())
    try:
        # Convert amount to USD if necessary
        amount_usd = convert_to_usd(amount, currency)
        
        transaction = Transaction(
            user_id=user_id,
            amount_usd=amount_usd,
            original_amount=amount,
            original_currency=currency,
            category=category,
            type=type,
            date=date
        )
        db.add(transaction)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error logging transaction: {e}")
        return False

def get_monthly_summary(user_id: str, month: int, year: int = None) -> Dict:
    """Get monthly financial summary."""
    if year is None:
        year = datetime.now().year
        
    db = next(get_db())
    
    # Get all transactions for the specified month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
        
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.date >= start_date,
        Transaction.date < end_date
    ).all()
    
    summary = {
        'period': {
            'month': month,
            'year': year,
            'month_name': start_date.strftime('%B')
        },
        'total_income': 0,
        'total_expenses': 0,
        'net': 0,
        'income_by_category': {},
        'expenses_by_category': {},
        'currencies_used': set(),
        'transaction_count': len(transactions)
    }
    
    for trans in transactions:
        amount = trans.amount_usd
        
        if trans.type == 'income':
            summary['total_income'] += amount
            if trans.category not in summary['income_by_category']:
                summary['income_by_category'][trans.category] = 0
            summary['income_by_category'][trans.category] += amount
        else:
            summary['total_expenses'] += amount
            if trans.category not in summary['expenses_by_category']:
                summary['expenses_by_category'][trans.category] = 0
            summary['expenses_by_category'][trans.category] += amount
            
        summary['currencies_used'].add(trans.original_currency)
    
    # Calculate net
    summary['net'] = summary['total_income'] - summary['total_expenses']
    
    # Convert currencies_used from set to list for JSON serialization
    summary['currencies_used'] = list(summary['currencies_used'])
    
    # Sort categories by amount
    summary['income_by_category'] = dict(sorted(
        summary['income_by_category'].items(),
        key=lambda x: x[1],
        reverse=True
    ))
    summary['expenses_by_category'] = dict(sorted(
        summary['expenses_by_category'].items(),
        key=lambda x: x[1],
        reverse=True
    ))
    
    return summary

def get_spending_by_category(user_id: str, category: str) -> float:
    """Get total spending for a specific category."""
    db = next(get_db())
    total = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.type == 'expense'
    ).with_entities(
        func.sum(Transaction.amount_usd)
    ).scalar()
    
    return total or 0.0

def bulk_insert_transactions(transactions: List[Dict]) -> bool:
    """Insert multiple transactions at once."""
    db = next(get_db())
    try:
        # Process each transaction to convert currency
        processed_transactions = []
        for trans in transactions:
            currency = trans.get('currency', 'USD')
            amount = trans['amount']
            amount_usd = convert_to_usd(amount, currency)
            
            processed_trans = {
                'user_id': trans['user_id'],
                'amount_usd': amount_usd,
                'original_amount': amount,
                'original_currency': currency,
                'category': trans['category'],
                'type': trans['type'],
                'date': trans['date']
            }
            processed_transactions.append(processed_trans)
            
        db_transactions = [Transaction(**trans) for trans in processed_transactions]
        db.bulk_save_objects(db_transactions)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error bulk inserting transactions: {e}")
        return False

def get_all_user_transactions(user_id: str) -> List[Transaction]:
    """Get all transactions for a user."""
    db = next(get_db())
    return db.query(Transaction).filter(Transaction.user_id == user_id).all() 