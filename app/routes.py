from app import app, db
from app.models import Transaction
from flask import jsonify, request
import requests


@app.route('/transactions', methods=['GET'])
def list_transactions():
    transactions = Transaction.query.all()
    output = []
    for transaction in transactions:
        transaction_data = {'id': transaction.id,
                            'amount': transaction.amount,
                            'spent': transaction.spent,
                            'created_at': transaction.created_at}
        output.append(transaction_data)
    return jsonify({'transactions': output})


@app.route('/transactions/add', methods=['POST'])
def add_transaction():
    req_data = request.get_json()
    amount = req_data.get('amount')

    if not amount:
        return jsonify({'message': 'Missing amount parameter'}), 400

    new_transaction = Transaction(amount)
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({'message': 'Transaction added successfully'}), 201


@app.route('/balance', methods=['GET'])
def get_balance():
    unspent_transactions = Transaction.query.filter_by(spent=False).all()
    btc_balance = sum(transaction.amount for transaction in unspent_transactions)

    exchange_rate = get_exchange_rate()
    if not exchange_rate:
        return jsonify({'message': 'Failed to retrieve exchange rate'}), 500

    eur_balance = btc_balance * exchange_rate
    return jsonify({'btc_balance': btc_balance, 'eur_balance': eur_balance})


def get_exchange_rate():
    response = requests.get('http://api-cryptopia.adca.sh/v1/prices/ticker')
    if response.status_code == 200:
        data = response.json()
        for item in data['data']:
            if item['symbol'] == 'BTC/EUR':
                return float(item['value'])
