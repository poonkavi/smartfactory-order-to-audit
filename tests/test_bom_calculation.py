from app import create_app
from app.models import Product
from app.services.bom_service import calculate_material_requirements

app = create_app()

with app.app_context():

    product = Product.query.filter_by(
        sku="MUR-200"
    ).first()

    requirements = calculate_material_requirements(
        product_id=product.id,
        planned_output=200
    )

    print("\nMaterial requirements for 200 packets:\n")

    for item in requirements:
        print(
            item["item_name"],
            ":",
            item["required_quantity"],
            item["unit"]
        )