from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.models.inventory import InventoryItem
from app.models.purchase import Purchase
from app.services.stock_service import record_stock_movement


purchase_bp = Blueprint("purchases", __name__)



@purchase_bp.route("/purchases", methods=["GET", "POST"])
def purchase_page():

    inventory_items = InventoryItem.query.order_by(
        InventoryItem.name
    ).all()

    if request.method == "POST":

        supplier_name = request.form.get(
            "supplier_name", ""
        ).strip()

        invoice_number = request.form.get(
            "invoice_number", ""
        ).strip()

        item_code = request.form.get(
            "item_code", ""
        ).strip()

        try:
            quantity = Decimal(
                request.form.get("quantity", "0")
            )

            unit_rate = Decimal(
                request.form.get("unit_rate", "0")
            )

        except (InvalidOperation, ValueError):
            flash("Enter valid quantity and rate.", "danger")
            return redirect(url_for("purchases.purchase_page"))

        if not supplier_name or not invoice_number or not item_code:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("purchases.purchase_page"))

        if quantity <= 0 or unit_rate < 0:
            flash("Quantity must be positive and rate cannot be negative.", "danger")
            return redirect(url_for("purchases.purchase_page"))

        item = InventoryItem.query.filter_by(
            item_code=item_code
        ).first()

        if not item:
            flash("Selected inventory item does not exist.", "danger")
            return redirect(url_for("purchases.purchase_page"))

        old_stock = Decimal(str(item.current_stock or 0))
        old_rate = Decimal(str(item.average_rate or 0))

        new_stock = old_stock + quantity

        total_amount = quantity * unit_rate

        if new_stock > 0:
            new_average_rate = (
                (old_stock * old_rate) +
                (quantity * unit_rate)
            ) / new_stock
        else:
            new_average_rate = unit_rate

        try:

            # Update stock and create stock ledger entry
            record_stock_movement(
                item_code=item_code,
                movement_type="Purchase",
                quantity=quantity,
                unit_rate=unit_rate,
                reference=invoice_number,
                notes=f"Purchase from {supplier_name}",
                commit=False
            )

            # Update average purchase rate
            item.average_rate = new_average_rate

            # Save purchase details
            purchase = Purchase(
                supplier_name=supplier_name,
                invoice_number=invoice_number,
                item_id=item.id,
                quantity=quantity,
                unit_rate=unit_rate,
                total_amount=total_amount
            )

            db.session.add(purchase)

            # Save everything together
            db.session.commit()

            flash(
                f"Purchase recorded successfully! "
                f"{quantity} {item.unit} added to stock.",
                "success"
            )

            return redirect(
                url_for("purchases.purchase_page")
            )

        except Exception as error:
            db.session.rollback()

            flash(
                f"Purchase failed: {error}",
                "danger"
            )

    purchases = Purchase.query.order_by(
        Purchase.purchase_date.desc()
    ).all()

    return render_template(
        "purchases.html",
        inventory_items=inventory_items,
        purchases=purchases
    )