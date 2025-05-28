from sqlalchemy import create_engine, Column, Integer, Float, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Dict
import enum
import os

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
    amount = Column(Float)
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

def log_transaction(user_id: str, amount: float, category: str, type: str, date: datetime) -> bool:
    """Log a new financial transaction."""
    db = next(get_db())
    try:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
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
        'total_income': 0,
        'total_expenses': 0,
        'by_category': {}
    }
    
    for trans in transactions:
        if trans.type == 'income':
            summary['total_income'] += trans.amount
        else:
            summary['total_expenses'] += trans.amount
            
        if trans.category not in summary['by_category']:
            summary['by_category'][trans.category] = 0
        summary['by_category'][trans.category] += trans.amount
    
    return summary

def get_spending_by_category(user_id: str, category: str) -> float:
    """Get total spending for a specific category."""
    db = next(get_db())
    total = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.type == 'expense'
    ).with_entities(
        func.sum(Transaction.amount)
    ).scalar()
    
    return total or 0.0

def bulk_insert_transactions(transactions: List[Dict]) -> bool:
    """Insert multiple transactions at once."""
    db = next(get_db())
    try:
        db_transactions = [Transaction(**trans) for trans in transactions]
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