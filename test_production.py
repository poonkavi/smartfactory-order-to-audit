from app import create_app
from app.models import InventoryItem, ProductionBatch
from app.services.production_service import complete_benchmark_production

app = create_app()

with app.app_context():

    result = complete_benchmark_production()
    print(result)

    print("\nUpdated inventory after production:\n")

    codes = [
        "RM-FLOUR",
        "RM-OIL",
        "RM-SPICE",
        "PK-POUCH",
        "PK-CARTON",
        "FG-MUR200"
    ]

    for code in codes:

        item = InventoryItem.query.filter_by(
            item_code=code
        ).first()

        print(item.name, ":", item.current_stock, item.unit)

    batch = ProductionBatch.query.filter_by(
        batch_number="BATCH-001"
    ).first()

    print("\nBatch details:")
    print("Batch:", batch.batch_number)
    print("Planned output:", batch.planned_output)
    print("Good output:", batch.actual_output)
    print("Damaged pouches:", batch.damaged_packaging_quantity)
    print("Status:", batch.status)