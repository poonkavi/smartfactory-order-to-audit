from decimal import Decimal

from app import db
from app.models.inventory import InventoryItem, StockLedger


def record_stock_movement(
    item_code,
    movement_type,
    quantity,
    unit_rate=0,
    reference=None,
    notes=None,
    commit=True
):
    item = InventoryItem.query.filter_by(
        item_code=item_code
    ).first()

    if not item:
        raise ValueError(f"Inventory item {item_code} not found")

    quantity = Decimal(str(quantity))
    unit_rate = Decimal(str(unit_rate))

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    stock_in_types = [
        "Opening",
        "Purchase",
        "Production Receipt"
    ]

    stock_out_types = [
        "Production Issue",
        "Dispatch",
        "Damage"
    ]

    current_stock = Decimal(str(item.current_stock or 0))

    if movement_type in stock_in_types:
        item.current_stock = current_stock + quantity

    elif movement_type in stock_out_types:

        if current_stock < quantity:
            raise ValueError(
                f"Insufficient stock for {item.name}"
            )

        item.current_stock = current_stock - quantity

    else:
        raise ValueError("Invalid movement type")

    ledger = StockLedger(
        item_id=item.id,
        movement_type=movement_type,
        quantity=quantity,
        unit_rate=unit_rate,
        reference=reference,
        notes=notes
    )

    db.session.add(ledger)

    # Commit only if requested
    if commit:
        db.session.commit()

    return item