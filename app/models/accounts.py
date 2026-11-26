from app import db
from datetime import datetime


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    invoice_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    taxable_amount = db.Column(db.Numeric(10, 2), nullable=False)

    cgst = db.Column(db.Numeric(10, 2), default=0)

    sgst = db.Column(db.Numeric(10, 2), default=0)

    igst = db.Column(db.Numeric(10, 2), default=0)

    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    status = db.Column(db.String(20), default="Unpaid")

    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice.id"),
        nullable=False
    )

    amount = db.Column(db.Numeric(10, 2), nullable=False)

    payment_method = db.Column(db.String(30), default="Cash")

    reference_number = db.Column(db.String(100))

    payment_date = db.Column(db.DateTime, default=datetime.utcnow)