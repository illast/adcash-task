# Backend Services & API Internship Assignment

- `__init__.py`: Initializes the Flask app and sets up the SQLAlchemy database.
- `models.py`: Defines database models for transactions.
- `routes.py`: Handles HTTP requests for transactions, balances, and transfers.
- `main.py`: Entry point for running the Flask server.

## How to Run:

1. Install Python 3.x.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run: `python main.py`.

## Endpoints:

- `/transactions` (GET): Retrieves transactions.
- `/transactions/add` (POST): Adds a new transaction.
- `/balance` (GET): Retrieves the balance.
- `/transfer` (POST): Transfers funds.

## External Dependencies:

- **Flask**: Web framework.
- **SQLAlchemy**: SQL toolkit and ORM.
- **Requests**: HTTP library.
- **pytest**: Testing framework.
