from app import db
from datetime import datetime
import uuid


class Transaction(db.Model):
    id = db.Column(db.String, primary_key=True)
    amount = db.Column(db.Float)
    spent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, amount):
        self.id = str(uuid.uuid4())
        self.amount = amount

    def __repr__(self):
        return f'Transaction(id={self.id}, amount={self.amount}, spent={self.spent}, created_at={self.created_at})'
