from flask import Flask, render_template, request, jsonify, send_file, session
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from functions.api_tools import get_exchange_rate, get_crypto_price
from functions.db_tools import log_transaction, get_monthly_summary, get_spending_by_category
from functions.file_tools import import_transactions_from_csv, export_summary_to_pdf, export_data_to_csv
from llm.agent import process_user_message
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set a consistent secret key from environment or generate one
if os.path.exists('.flask_secret_key'):
    with open('.flask_secret_key', 'rb') as f:
        app.secret_key = f.read()
else:
    app.secret_key = os.urandom(24)
    with open('.flask_secret_key', 'wb') as f:
        f.write(app.secret_key)

# Configure session
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)  # Sessions last for 31 days

# Ensure the uploads and exports directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('exports', exist_ok=True)

def get_or_create_user_id():
    if 'user_id' not in session:
        session.permanent = True  # Make the session permanent
        session['user_id'] = f"user_{str(uuid.uuid4())[:8]}"
    return session['user_id']

@app.route('/')
def index():
    user_id = get_or_create_user_id()
    return render_template('index.html', user_id=user_id)

@app.route('/dashboard')
def dashboard():
    user_id = get_or_create_user_id()
    # Get current month's summary
    current_month = datetime.now().month
    current_year = datetime.now().year
    summary = get_monthly_summary(user_id, current_month, current_year)
    return render_template('dashboard.html', summary=summary)

@app.route('/log_transaction', methods=['GET', 'POST'])
def transaction():
    user_id = get_or_create_user_id()
    if request.method == 'POST':
        data = request.form
        success = log_transaction(
            user_id=user_id,
            amount=float(data['amount']),
            category=data['category'],
            type=data['type'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            currency=data.get('currency', 'USD')  # Default to USD if not specified
        )
        return jsonify({'success': success})
    return render_template('log_transaction.html')

@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    user_id = get_or_create_user_id()
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join('uploads', file.filename)
            file.save(filepath)
            success = import_transactions_from_csv(user_id, filepath)
            os.remove(filepath)  # Clean up
            return jsonify({'success': success})
            
    return render_template('import_csv.html')

@app.route('/export')
def export():
    user_id = get_or_create_user_id()
    return render_template('export.html')

@app.route('/api/export_pdf')
def export_pdf():
    user_id = get_or_create_user_id()
    month = int(request.args.get('month', datetime.now().month))
    year = int(request.args.get('year', datetime.now().year))
    
    filename = export_summary_to_pdf(user_id, month, year)
    if filename:
        return send_file(filename, as_attachment=True)
    return jsonify({'success': False, 'error': 'Failed to generate PDF'})

@app.route('/api/export_csv')
def export_csv():
    user_id = get_or_create_user_id()
    filename = export_data_to_csv(user_id)
    if filename:
        return send_file(filename, as_attachment=True)
    return jsonify({'success': False, 'error': 'Failed to export CSV'})

@app.route('/exchange_rates')
def exchange_rates():
    return render_template('exchange_rates.html')

@app.route('/api/exchange_rate')
def get_rate():
    base = request.args.get('base', 'USD')
    target = request.args.get('target', 'EUR')
    rate = get_exchange_rate(base, target)
    return jsonify({'rate': rate})

@app.route('/crypto')
def crypto():
    return render_template('crypto.html')

@app.route('/api/crypto_price')
def get_crypto():
    symbol = request.args.get('symbol', 'BTC')
    price = get_crypto_price(symbol)
    return jsonify(price)

@app.route('/chat')
def chat():
    user_id = get_or_create_user_id()
    return render_template('chat.html', user_id=user_id)

@app.route('/api/chat', methods=['POST'])
def process_chat():
    user_id = get_or_create_user_id()
    message = request.json.get('message', '')
    response = process_user_message(user_id, message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True) 