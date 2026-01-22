from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Receipt(db.Model):
    """Model for storing receipt metadata"""
    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    source_type = db.Column(db.String(20), nullable=False)  # 'scan' or 'email'
    source_file = db.Column(db.String(255))
    raw_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('Item', backref='receipt', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'store_name': self.store_name,
            'purchase_date': self.purchase_date.isoformat(),
            'total_amount': self.total_amount,
            'tax_amount': self.tax_amount,
            'source_type': self.source_type,
            'source_file': self.source_file,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }


class Item(db.Model):
    """Model for storing individual items from receipts"""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'receipt_id': self.receipt_id,
            'name': self.name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'category': self.category
        }


class Category(db.Model):
    """Model for item categories with keyword matching"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    keywords = db.Column(db.Text)  # Comma-separated keywords
    color = db.Column(db.String(7))  # Hex color for charts

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'color': self.color
        }
