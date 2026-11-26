
from app import db
from datetime import datetime


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    customer_state = db.Column(
        db.String(50),
        nullable=False
    )

    salesman_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    order_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    total_amount = db.Column(
        db.Numeric(10, 2),
        default=0
    )


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    line_total = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    # Quantity already dispatched
    dispatched_quantity = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )


class Dispatch(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    dispatch_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    order_item_id = db.Column(
        db.Integer,
        db.ForeignKey("order_item.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    dispatch_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    notes = db.Column(
        db.String(200)
    )
