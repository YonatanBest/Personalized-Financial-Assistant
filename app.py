from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
import os
from agents.functions import (
    get_exchange_rate,
    convert_currency,
    record_expense,
    get_expense_report,
    get_expense_summary,
    set_budget,
    get_budget_status
)

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/expenses')
def expenses():
    summary = get_expense_summary()
    return render_template('expenses.html', summary=summary)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        currency = request.form['currency']
        
        record_expense(amount=amount, category=category, description=description, currency=currency)
        return redirect(url_for('expenses'))
    
    return render_template('add_expense.html')

@app.route('/budgets', methods=['GET', 'POST'])
def budgets():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        currency = request.form['currency']
        period = request.form.get('period', 'monthly')
        
        set_budget(category=category, amount=amount, currency=currency, period=period)
        return redirect(url_for('budgets'))
    
    budget_status = get_budget_status()
    return render_template('budgets.html', budget_status=budget_status)

@app.route('/api/convert_currency', methods=['POST'])
def api_convert_currency():
    data = request.get_json()
    result = convert_currency(
        amount=float(data['amount']),
        from_currency=data['from_currency'],
        to_currency=data['to_currency']
    )
    return jsonify(result)

@app.route('/api/exchange_rate', methods=['GET'])
def api_exchange_rate():
    base = request.args.get('base')
    target = request.args.get('target')
    rate = get_exchange_rate(base_currency=base, target_currency=target)
    return jsonify({'rate': rate})

if __name__ == '__main__':
    app.run(debug=True) 