from flask import Blueprint, render_template, request, redirect, url_for, flash
from decimal import Decimal, InvalidOperation

from app import db
from app.models import (
    Product,
    InventoryItem,
    ProductionBatch,
    BillOfMaterial,
    BOMItem
)

from app.services.bom_service import calculate_material_requirements
from app.services.production_service import complete_production_batch


production_bp = Blueprint("production", __name__)


# =========================================================
# 1. PRODUCTION PLANNING
# URL: /production
# =========================================================

@production_bp.route("/production", methods=["GET", "POST"])
def production_page():

    products = Product.query.order_by(Product.name).all()

    requirements = None
    selected_product_id = None
    planned_output = None
    error = None

    if request.method == "POST":

        try:
            selected_product_id = int(
                request.form.get("product_id")
            )

            planned_output = int(
                request.form.get("planned_output")
            )

            if planned_output <= 0:
                raise ValueError(
                    "Planned output must be greater than zero."
                )

            requirements = calculate_material_requirements(
                selected_product_id,
                planned_output
            )

        except (ValueError, TypeError, InvalidOperation) as e:
            error = str(e)

    return render_template(
        "production.html",
        products=products,
        requirements=requirements,
        selected_product_id=selected_product_id,
        planned_output=planned_output,
        error=error
    )


# =========================================================
# 2. BOM / RECIPE SETUP
# URL: /production/bom
# =========================================================

@production_bp.route("/production/bom", methods=["GET", "POST"])
def bom_setup():

    products = Product.query.order_by(Product.name).all()

    inventory_items = InventoryItem.query.order_by(
        InventoryItem.name
    ).all()

    if request.method == "POST":

        try:
            product_id = int(
                request.form.get("product_id")
            )

            batch_size = int(
                request.form.get("batch_size")
            )

            if batch_size <= 0:
                raise ValueError(
                    "Batch size must be greater than zero."
                )

            product = db.session.get(
                Product, product_id
            )

            if not product:
                raise ValueError(
                    "Selected product does not exist."
                )

            inventory_ids = request.form.getlist(
                "inventory_item_id[]"
            )

            quantities = request.form.getlist(
                "quantity_required[]"
            )

            if len(inventory_ids) != len(quantities):
                raise ValueError(
                    "Invalid material details."
                )

            materials = []
            used_inventory_ids = set()

            for inventory_id, quantity in zip(
                inventory_ids, quantities
            ):

                if not inventory_id or not quantity:
                    continue

                inventory_id = int(inventory_id)
                quantity = Decimal(str(quantity))

                if quantity <= 0:
                    raise ValueError(
                        "Material quantity must be greater than zero."
                    )

                if inventory_id in used_inventory_ids:
                    raise ValueError(
                        "Do not select the same material more than once."
                    )

                inventory_item = db.session.get(
                    InventoryItem, inventory_id
                )

                if not inventory_item:
                    raise ValueError(
                        "Selected inventory item was not found."
                    )

                used_inventory_ids.add(inventory_id)

                materials.append({
                    "inventory_id": inventory_id,
                    "quantity": quantity
                })

            if not materials:
                raise ValueError(
                    "Add at least one material to the BOM."
                )

            # Deactivate previous active BOMs
            old_boms = BillOfMaterial.query.filter_by(
                product_id=product_id,
                is_active=True
            ).all()

            for old_bom in old_boms:
                old_bom.is_active = False

            # Create new BOM
            new_bom = BillOfMaterial(
                product_id=product_id,
                batch_size=batch_size,
                version="1.0",
                is_active=True
            )

            db.session.add(new_bom)
            db.session.flush()

            # Add BOM materials
            for material in materials:

                bom_item = BOMItem(
                    bom_id=new_bom.id,
                    inventory_item_id=material["inventory_id"],
                    quantity_required=material["quantity"]
                )

                db.session.add(bom_item)

            db.session.commit()

            flash(
                "BOM saved successfully!",
                "success"
            )

            return redirect(
                url_for("production.bom_setup")
            )

        except (ValueError, TypeError, InvalidOperation) as e:

            db.session.rollback()

            flash(str(e), "danger")

        except Exception:

            db.session.rollback()

            flash(
                "Unable to save BOM. Please check your entries.",
                "danger"
            )

    return render_template(
        "bom_setup.html",
        products=products,
        inventory_items=inventory_items
    )


# =========================================================
# 3. PRODUCTION COMPLETION
# URL: /production/complete
# =========================================================

@production_bp.route(
    "/production/complete",
    methods=["GET", "POST"]
)
def production_completion():

    products = Product.query.order_by(Product.name).all()

    selected_product = None
    bom_items = []
    material_rows = []
    result = None
    error = None

    if request.method == "POST":
        product_id = request.form.get("product_id")
    else:
        product_id = request.args.get("product_id")

    if product_id:

        try:
            product_id = int(product_id)

            selected_product = db.session.get(
                Product, product_id
            )

            if not selected_product:
                raise ValueError(
                    "Selected product was not found."
                )

            # Find active BOM
            bom = BillOfMaterial.query.filter_by(
                product_id=selected_product.id,
                is_active=True
            ).first()

            if not bom:
                raise ValueError(
                    "Active BOM not found. Please create BOM first."
                )

            # Load BOM materials
            bom_items = BOMItem.query.filter_by(
                bom_id=bom.id
            ).all()

            if not bom_items:
                raise ValueError(
                    "The selected BOM has no materials."
                )

            # Pair BOM materials with inventory items
            material_rows = []

            for bom_item in bom_items:

                inventory_item = db.session.get(
                    InventoryItem,
                    bom_item.inventory_item_id
                )

                if not inventory_item:
                    raise ValueError(
                        "BOM inventory item was not found."
                    )

                material_rows.append(
                    (bom_item, inventory_item)
                )

            # Process submitted production
            if request.method == "POST":

                planned_output = request.form.get(
                    "planned_output"
                )

                good_output = request.form.get(
                    "good_output"
                )

                rejected_quantity = request.form.get(
                    "rejected_quantity", 0
                )

                damaged_packaging_quantity = request.form.get(
                    "damaged_packaging_quantity", 0
                )

                actual_materials = {}

                for bom_item, inventory_item in material_rows:

                    quantity = request.form.get(
                        f"material_{inventory_item.id}"
                    )

                    if quantity is None or quantity.strip() == "":
                        raise ValueError(
                            f"Enter consumption for "
                            f"{inventory_item.name}."
                        )

                    actual_materials[
                        inventory_item.id
                    ] = Decimal(str(quantity))

                # Call production service
                result = complete_production_batch(
                    product_id=selected_product.id,
                    planned_output=planned_output,
                    actual_materials=actual_materials,
                    good_output=good_output,
                    rejected_quantity=rejected_quantity,
                    damaged_packaging_quantity=(
                        damaged_packaging_quantity
                    )
                )

                flash(
                    "Production completed successfully!",
                    "success"
                )

        except (ValueError, TypeError, InvalidOperation) as e:

            error = str(e)

        except Exception as e:

            db.session.rollback()

            error = str(e)

    return render_template(
        "production_completion.html",
        products=products,
        selected_product=selected_product,
        bom_items=bom_items,
        material_rows=material_rows,
        result=result,
        error=error
    )


# =========================================================
# 4. PRODUCTION HISTORY
# URL: /production/history
# =========================================================

@production_bp.route("/production/history")
def production_history():

    batches = ProductionBatch.query.order_by(
        ProductionBatch.production_date.desc()
    ).all()

    batch_rows = []

    for batch in batches:

        product = db.session.get(
            Product,
            batch.product_id
        )

        batch_rows.append({
            "batch": batch,
            "product": product
        })

    return render_template(
        "production_history.html",
        batch_rows=batch_rows
    )