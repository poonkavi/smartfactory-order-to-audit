from decimal import Decimal, InvalidOperation
from datetime import datetime

from app import db
from app.models.product import Product
from app.models.inventory import InventoryItem
from app.models.production import ProductionBatch, BillOfMaterial, BOMItem
from app.services.stock_service import record_stock_movement


def complete_production_batch(
    product_id,
    planned_output,
    actual_materials,
    good_output,
    rejected_quantity=0,
    damaged_packaging_quantity=0
):
    try:
        product = db.session.get(Product, int(product_id))

        if not product:
            raise ValueError("Product not found.")

        planned_output = int(planned_output)
        good_output = int(good_output)
        rejected_quantity = int(rejected_quantity)
        damaged_packaging_quantity = int(damaged_packaging_quantity)

        if planned_output <= 0:
            raise ValueError("Planned output must be greater than zero.")

        if good_output < 0 or rejected_quantity < 0:
            raise ValueError("Output quantities cannot be negative.")

        if good_output + rejected_quantity <= 0:
            raise ValueError("Production output must be greater than zero.")

        if damaged_packaging_quantity < 0:
            raise ValueError("Damaged packaging cannot be negative.")

        # Get active BOM
        bom = BillOfMaterial.query.filter_by(
            product_id=product.id,
            is_active=True
        ).first()

        if not bom:
            raise ValueError("Active BOM not found for this product.")

        bom_items = BOMItem.query.filter_by(
            bom_id=bom.id
        ).all()

        if not bom_items:
            raise ValueError("The BOM has no materials configured.")

        # Convert actual material quantities to Decimal
        actual_materials = {
            int(item_id): Decimal(str(quantity))
            for item_id, quantity in actual_materials.items()
        }

        bom_inventory_ids = {
            item.inventory_item_id for item in bom_items
        }

        if set(actual_materials.keys()) != bom_inventory_ids:
            raise ValueError(
                "Actual material entries do not match the product BOM."
            )

        material_details = []
        total_material_cost = Decimal("0")

        # Validate material consumption and calculate costs
        for bom_item in bom_items:

            inventory_item = db.session.get(
                InventoryItem,
                bom_item.inventory_item_id
            )

            if not inventory_item:
                raise ValueError("BOM inventory item not found.")

            actual_quantity = actual_materials[
                bom_item.inventory_item_id
            ]

            if actual_quantity < 0:
                raise ValueError(
                    f"Consumption cannot be negative for "
                    f"{inventory_item.name}."
                )

            if actual_quantity == 0:
                continue

            available_stock = Decimal(
                str(inventory_item.current_stock or 0)
            )

            if actual_quantity > available_stock:
                raise ValueError(
                    f"Insufficient stock for {inventory_item.name}. "
                    f"Available: {available_stock}, "
                    f"Required: {actual_quantity}"
                )

            rate = Decimal(
                str(inventory_item.average_rate or 0)
            )

            material_cost = actual_quantity * rate

            total_material_cost += material_cost

            material_details.append({
                "item_code": inventory_item.item_code,
                "name": inventory_item.name,
                "quantity": actual_quantity,
                "rate": rate,
                "cost": material_cost
            })

        if not material_details:
            raise ValueError(
                "At least one material must be consumed."
            )

        # Find finished goods inventory
        finished_item = InventoryItem.query.filter_by(
            item_code=f"FG-{product.sku}"
        ).first()

        # Try matching an existing finished goods item by product name
        if not finished_item:

            finished_items = InventoryItem.query.filter_by(
                category="Finished Goods"
            ).all()

            for item in finished_items:
                if product.name.lower() in item.name.lower():
                    finished_item = item
                    break

        # Create finished goods item if it doesn't exist
        if not finished_item:

            finished_item = InventoryItem(
                name=f"{product.name} Finished Goods",
                item_code=f"FG-{product.sku}",
                category="Finished Goods",
                unit=product.unit,
                current_stock=0,
                average_rate=0
            )

            db.session.add(finished_item)
            db.session.flush()

        # Calculate material cost per good unit
        unit_cost = Decimal("0")

        if good_output > 0:
            unit_cost = (
                total_material_cost / Decimal(good_output)
            )

        # Generate unique production batch number
        batch_number = datetime.utcnow().strftime(
            "PB-%Y%m%d-%H%M%S-%f"
        )

        # Create production batch record
        batch = ProductionBatch(
            batch_number=batch_number,
            product_id=product.id,
            planned_output=planned_output,
            actual_output=good_output,
            rejected_quantity=rejected_quantity,
            damaged_packaging_quantity=damaged_packaging_quantity,
            status="Completed"
        )

        db.session.add(batch)
        db.session.flush()

        # Deduct raw materials
        for material in material_details:

            record_stock_movement(
                item_code=material["item_code"],
                movement_type="Production Issue",
                quantity=material["quantity"],
                unit_rate=material["rate"],
                reference=batch_number,
                notes=f"Materials consumed for {product.name}",
                commit=False
            )

        # Calculate finished goods weighted average cost
        if good_output > 0:

            old_stock = Decimal(
                str(finished_item.current_stock or 0)
            )

            old_rate = Decimal(
                str(finished_item.average_rate or 0)
            )

            new_stock = old_stock + Decimal(good_output)

            finished_item.average_rate = (
                (old_stock * old_rate)
                + (Decimal(good_output) * unit_cost)
            ) / new_stock

            # Receive finished goods
            record_stock_movement(
                item_code=finished_item.item_code,
                movement_type="Production Receipt",
                quantity=good_output,
                unit_rate=unit_cost,
                reference=batch_number,
                notes=f"Finished goods received: {product.name}",
                commit=False
            )

        # Commit the whole production transaction
        db.session.commit()

        return {
            "batch_number": batch_number,
            "product_name": product.name,
            "planned_output": planned_output,
            "good_output": good_output,
            "rejected_quantity": rejected_quantity,
            "damaged_packaging_quantity": damaged_packaging_quantity,
            "total_material_cost": total_material_cost,
            "unit_cost": unit_cost,
            "finished_goods_code": finished_item.item_code
        }

    except Exception:
        db.session.rollback()
        raise