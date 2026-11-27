from app import db
from app.models import InventoryItem, Product
from app.models.user import User
from werkzeug.security import generate_password_hash


def load_benchmark_data():

    # -------------------------
    # RAW MATERIALS
    # -------------------------
    raw_materials = [
        {
            "name": "Flour",
            "item_code": "RM-FLOUR",
            "category": "Raw Material",
            "unit": "kg",
            "current_stock": 100,
            "average_rate": 42
        },
        {
            "name": "Oil",
            "item_code": "RM-OIL",
            "category": "Raw Material",
            "unit": "litre",
            "current_stock": 30,
            "average_rate": 140
        },
        {
            "name": "Spice",
            "item_code": "RM-SPICE",
            "category": "Raw Material",
            "unit": "kg",
            "current_stock": 5,
            "average_rate": 200
        },

        # -------------------------
        # PACKAGING MATERIALS
        # -------------------------
        {
            "name": "Pouches",
            "item_code": "PK-POUCH",
            "category": "Packaging",
            "unit": "pcs",
            "current_stock": 500,
            "average_rate": 2.50
        },
        {
            "name": "Cartons",
            "item_code": "PK-CARTON",
            "category": "Packaging",
            "unit": "pcs",
            "current_stock": 30,
            "average_rate": 15
        },

        # -------------------------
        # FINISHED GOODS
        # -------------------------
        {
            "name": "Murukku Packets",
            "item_code": "FG-MUR200",
            "category": "Finished Goods",
            "unit": "packet",
            "current_stock": 50,
            "average_rate": 0
        }
    ]

    for data in raw_materials:

        existing_item = InventoryItem.query.filter_by(
            item_code=data["item_code"]
        ).first()

        if not existing_item:
            item = InventoryItem(**data)
            db.session.add(item)

    db.session.commit()

    # -------------------------
    # PRODUCTS
    # -------------------------
    products = [
        {
            "name": "Murukku",
            "sku": "MUR-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        },
        {
            "name": "Mixture",
            "sku": "MIX-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        },
        {
            "name": "Thattai",
            "sku": "THA-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        },
        {
            "name": "Ribbon Pakoda",
            "sku": "RIB-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        },
        {
            "name": "Kara Sev",
            "sku": "KAR-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        },
        {
            "name": "Masala Peanuts",
            "sku": "PEA-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        },
        {
            "name": "Omapodi",
            "sku": "OMA-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        },
        {
            "name": "Sev",
            "sku": "SEV-200",
            "selling_price": 50,
            "gst_rate": 5,
            "unit": "packet",
            "category": "Snacks"
        }
    ]

    for data in products:

        existing_product = Product.query.filter_by(
            sku=data["sku"]
        ).first()

        if not existing_product:
            product = Product(**data)
            db.session.add(product)

    db.session.commit()

    # -------------------------
    # SALESMAN
    # -------------------------
    existing_salesman = User.query.filter_by(
        username="salesman_a"
    ).first()

    if not existing_salesman:
        salesman = User(
            username="salesman_a",
            name="Salesman A",
            password=generate_password_hash("salesman123"),
            role="Salesman"
        )

        db.session.add(salesman)
        db.session.commit()

    print("Benchmark data loaded successfully!")