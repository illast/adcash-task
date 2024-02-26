import pytest
from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()


def test_add_transaction(client):
    response = client.post('/transactions/add', json={'amount': 4.25})
    assert response.status_code == 201
    assert b'Transaction added successfully' in response.data


def test_list_transactions(client):
    client.post('/transactions/add', json={'amount': 17.5})
    client.post('/transactions/add', json={'amount': 20.75})

    response = client.get('/transactions')
    assert response.status_code == 200
    data = response.json
    assert len(data['transactions']) == 2


def test_get_balance(client, monkeypatch):
    def mock_get_exchange_rate():
        return 40000

    monkeypatch.setattr('app.routes.get_exchange_rate', mock_get_exchange_rate)

    client.post('/transactions/add', json={'amount': 5.5})
    client.post('/transactions/add', json={'amount': 10})

    response = client.get('/balance')
    assert response.status_code == 200
    data = response.json
    assert data['btc_balance'] == 5.5 + 10
    assert data['eur_balance'] == (5.5 + 10) * mock_get_exchange_rate()


def test_transfer_successful_created_new_transaction(client, monkeypatch):
    def mock_get_exchange_rate():
        return 40000

    monkeypatch.setattr('app.routes.get_exchange_rate', mock_get_exchange_rate)

    client.post('/transactions/add', json={'amount': 3})
    client.post('/transactions/add', json={'amount': 2})

    response = client.post('/transfer', json={'amount_eur': 4.5 * mock_get_exchange_rate()})
    assert response.status_code == 200
    assert b'Transfer successful' in response.data

    response = client.get('/transactions')
    data = response.json
    assert len(data['transactions']) == 3

    has_0_5_amount = any(item['amount'] == 0.5 for item in data['transactions'])
    assert has_0_5_amount

    for item in data['transactions']:
        if item['amount'] == 3 or item['amount'] == 2:
            assert item['spent']
        if item['amount'] == 0.5:
            assert not item['spent']


def test_transfer_successful_no_new_transaction_created(client, monkeypatch):
    def mock_get_exchange_rate():
        return 40000

    monkeypatch.setattr('app.routes.get_exchange_rate', mock_get_exchange_rate)

    client.post('/transactions/add', json={'amount': 3})
    client.post('/transactions/add', json={'amount': 2})

    response = client.post('/transfer', json={'amount_eur': 5 * mock_get_exchange_rate()})
    assert response.status_code == 200
    assert b'Transfer successful' in response.data

    response = client.get('/transactions')
    data = response.json
    assert len(data['transactions']) == 2

    for item in data['transactions']:
        assert item['spent']


def test_transfer_not_successful_no_necessary_parameters(client, monkeypatch):
    def mock_get_exchange_rate():
        return 40000

    monkeypatch.setattr('app.routes.get_exchange_rate', mock_get_exchange_rate)

    client.post('/transactions/add', json={'amount': 3})
    client.post('/transactions/add', json={'amount': 2})

    response = client.post('/transfer', json={'amount_btc': 5 * mock_get_exchange_rate()})
    assert response.status_code == 400
    assert b'Missing amount_eur parameter' in response.data

    response = client.get('/transactions')
    data = response.json
    assert len(data['transactions']) == 2

    for item in data['transactions']:
        assert not item['spent']


def test_transfer_invalid_amount(client, monkeypatch):
    def mock_get_exchange_rate():
        return 1

    monkeypatch.setattr('app.routes.get_exchange_rate', mock_get_exchange_rate)

    client.post('/transactions/add', json={'amount': 3})
    client.post('/transactions/add', json={'amount': 2})

    response = client.post('/transfer', json={'amount_eur': 0.000001})
    assert response.status_code == 400
    assert b'Invalid transfer amount or insufficient balance' in response.data

    response = client.get('/transactions')
    data = response.json
    assert len(data['transactions']) == 2

    for item in data['transactions']:
        assert not item['spent']


def test_transfer_insufficient_balance(client, monkeypatch):
    def mock_get_exchange_rate():
        return 40000

    monkeypatch.setattr('app.routes.get_exchange_rate', mock_get_exchange_rate)

    client.post('/transactions/add', json={'amount': 3})

    response = client.post('/transfer', json={'amount_eur': 4 * mock_get_exchange_rate()})
    assert response.status_code == 400
    assert b'Invalid transfer amount or insufficient balance' in response.data

    response = client.get('/transactions')
    data = response.json
    assert len(data['transactions']) == 1

    for item in data['transactions']:
        assert not item['spent']
