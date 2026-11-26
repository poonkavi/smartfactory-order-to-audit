from app import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    sku = db.Column(db.String(50), unique=True, nullable=False)

    selling_price = db.Column(db.Numeric(10, 2), nullable=False)

    gst_rate = db.Column(db.Numeric(5, 2), nullable=False)

    unit = db.Column(db.String(20), nullable=False)

    category = db.Column(db.String(50), nullable=False)