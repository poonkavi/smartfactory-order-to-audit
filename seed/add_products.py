from app import create_app, db
from app.models.product import Product

app = create_app()

products = [
    {
        "name": "Murukku",
        "sku": "MUR-200",
        "selling_price": 50.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    },
    {
        "name": "Mixture",
        "sku": "MIX-200",
        "selling_price": 50.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    },
    {
        "name": "Thattai",
        "sku": "THA-200",
        "selling_price": 70.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    },
    {
        "name": "Ribbon Pakoda",
        "sku": "RIB-200",
        "selling_price": 70.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    },
    {
        "name": "Kara Sev",
        "sku": "KAR-200",
        "selling_price": 50.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    },
    {
        "name": "Masala Peanuts",
        "sku": "PEA-200",
        "selling_price": 30.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    },
    {
        "name": "Omapodi",
        "sku": "OMA-200",
        "selling_price": 40.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    },
    {
        "name": "Sev",
        "sku": "SEV-200",
        "selling_price": 60.00,
        "gst_rate": 5.00,
        "unit": "packet",
        "category": "Snacks"
    }
]

with app.app_context():
    added_count = 0

    for item in products:
        existing_product = Product.query.filter_by(
            sku=item["sku"]
        ).first()

        if existing_product:
            print(f"Already exists: {item['name']}")
            continue

        product = Product(**item)
        db.session.add(product)
        added_count += 1

    db.session.commit()

    print(f"\nSuccessfully added {added_count} new products!")