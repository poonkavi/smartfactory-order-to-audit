from app import db
from datetime import datetime


class ProductionBatch(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    batch_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    planned_output = db.Column(
        db.Integer,
        nullable=False
    )

    actual_output = db.Column(
        db.Integer,
        default=0
    )

    rejected_quantity = db.Column(
        db.Integer,
        default=0
    )

    production_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default="Planned"
    )

    damaged_packaging_quantity = db.Column(
        db.Integer,
        default=0
    )


class BillOfMaterial(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    batch_size = db.Column(
        db.Integer,
        nullable=False
    )

    version = db.Column(
        db.String(20),
        default="1.0"
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )


class BOMItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    bom_id = db.Column(
        db.Integer,
        db.ForeignKey("bill_of_material.id"),
        nullable=False
    )

    inventory_item_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory_item.id"),
        nullable=False
    )

    quantity_required = db.Column(
        db.Numeric(10, 3),
        nullable=False
    )