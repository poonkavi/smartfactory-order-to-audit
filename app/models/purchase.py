from datetime import datetime
from app import db


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    supplier_name = db.Column(
        db.String(100),
        nullable=False
    )

    invoice_number = db.Column(
        db.String(100),
        nullable=False
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory_item.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Numeric(10, 3),
        nullable=False
    )

    unit_rate = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    total_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    purchase_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    item = db.relationship(
        "InventoryItem",
        backref="purchases"
    )