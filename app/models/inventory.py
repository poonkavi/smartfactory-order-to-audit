from datetime import datetime

from app import db


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    item_code = db.Column(db.String(50), unique=True, nullable=False)

    category = db.Column(db.String(30), nullable=False)

    unit = db.Column(db.String(20), nullable=False)

    current_stock = db.Column(db.Numeric(10, 3), default=0)

    average_rate = db.Column(db.Numeric(10, 2), default=0)


class StockLedger(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(

        db.Integer,
        db.ForeignKey("inventory_item.id"),
        nullable=False
    )


    movement_type = db.Column(db.String(30), nullable=False)

    quantity = db.Column(db.Numeric(10, 3), nullable=False)

    unit_rate = db.Column(db.Numeric(10, 2), default=0)

    reference = db.Column(db.String(100))

    notes = db.Column(db.String(200))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    