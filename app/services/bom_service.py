from decimal import Decimal
from app.models import BillOfMaterial, BOMItem, InventoryItem


def calculate_material_requirements(product_id, planned_output):

    bom = BillOfMaterial.query.filter_by(
        product_id=product_id,
        is_active=True
    ).first()

    if not bom:
        raise ValueError("Active BOM not found for this product")

    planned_output = Decimal(str(planned_output))
    batch_size = Decimal(str(bom.batch_size))

    if planned_output <= 0:
        raise ValueError("Planned output must be greater than zero")

    factor = planned_output / batch_size

    requirements = []

    bom_items = BOMItem.query.filter_by(
        bom_id=bom.id
    ).all()

    for bom_item in bom_items:

        inventory_item = InventoryItem.query.get(
            bom_item.inventory_item_id
        )

        required_quantity = (
            Decimal(str(bom_item.quantity_required)) * factor
        )

        requirements.append({
            "item_name": inventory_item.name,
            "item_code": inventory_item.item_code,
            "unit": inventory_item.unit,
            "required_quantity": required_quantity,
            "available_stock": Decimal(
                str(inventory_item.current_stock)
            )
        })

    return requirements