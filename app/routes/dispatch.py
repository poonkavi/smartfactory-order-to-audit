
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

from app import db
from app.models.orders import Order, OrderItem, Dispatch
from app.models.product import Product
from app.models.inventory import InventoryItem
from app.services.stock_service import record_stock_movement


dispatch_bp = Blueprint("dispatch", __name__)


def generate_dispatch_number():
    existing = Dispatch.query.all()

    highest = 0

    for dispatch in existing:
        number = dispatch.dispatch_number

        if number.startswith("DSP-"):
            part = number[4:]

            if part.isdigit():
                highest = max(highest, int(part))

    return f"DSP-{highest + 1:04d}"


def find_finished_goods(product):
    """
    Find finished-goods stock for a product.
    """

    expected_code = f"FG-{product.sku.replace('-', '')}"

    item = InventoryItem.query.filter_by(
        item_code=expected_code
    ).first()

    if item:
        return item

    # Fallback: match product name in finished-goods category
    item = InventoryItem.query.filter(
        InventoryItem.name.ilike(product.name),
        InventoryItem.category.ilike("%finished%")
    ).first()

    return item


# ==================================================
# DISPATCH DASHBOARD
# ==================================================
@dispatch_bp.route("/dispatch")
def dispatch_dashboard():

    orders = Order.query.order_by(
        Order.order_date.desc()
    ).all()

    order_rows = []

    for order in orders:

        items = OrderItem.query.filter_by(
            order_id=order.id
        ).all()

        remaining_items = []

        for item in items:

            remaining = (
                item.quantity -
                (item.dispatched_quantity or 0)
            )

            if remaining > 0:

                product = Product.query.get(item.product_id)

                finished_goods = find_finished_goods(product)

                available_stock = (
                    finished_goods.current_stock
                    if finished_goods
                    else 0
                )

                remaining_items.append({
                    "item": item,
                    "product": product,
                    "remaining": remaining,
                    "available_stock": available_stock
                })

        if remaining_items:

            order_rows.append({
                "order": order,
                "items": remaining_items
            })

    return render_template(
        "dispatch.html",
        order_rows=order_rows
    )


# ==================================================
# PROCESS DISPATCH
# ==================================================
@dispatch_bp.route(
    "/dispatch/<int:order_id>",
    methods=["GET", "POST"]
)
def process_dispatch(order_id):

    order = Order.query.get_or_404(order_id)

    items = OrderItem.query.filter_by(
        order_id=order.id
    ).all()

    item_rows = []

    for item in items:

        product = Product.query.get(item.product_id)

        remaining = (
            item.quantity -
            (item.dispatched_quantity or 0)
        )

        finished_goods = find_finished_goods(product)

        available_stock = (
            finished_goods.current_stock
            if finished_goods
            else 0
        )

        item_rows.append({
            "item": item,
            "product": product,
            "remaining": remaining,
            "finished_goods": finished_goods,
            "available_stock": available_stock
        })

    if request.method == "POST":

        try:

            # Pending orders must first be approved
            if order.status == "Pending":
                raise ValueError(
                    "This order is pending approval. "
                    "Approve it before dispatch."
                )

            dispatch_notes = request.form.get(
                "notes", ""
            ).strip()

            dispatch_number = generate_dispatch_number()

            dispatched_any = False

            for row in item_rows:

                item = row["item"]
                product = row["product"]
                remaining = row["remaining"]
                finished_goods = row["finished_goods"]

                quantity = int(
                    request.form.get(
                        f"dispatch_qty_{item.id}",
                        0
                    )
                )

                if quantity < 0:
                    raise ValueError(
                        "Dispatch quantity cannot be negative."
                    )

                if quantity == 0:
                    continue

                if quantity > remaining:
                    raise ValueError(
                        f"Dispatch quantity exceeds remaining "
                        f"quantity for {product.name}."
                    )

                if not finished_goods:
                    raise ValueError(
                        f"Finished goods stock not found "
                        f"for {product.name}."
                    )

                if quantity > finished_goods.current_stock:
                    raise ValueError(
                        f"Insufficient finished goods stock "
                        f"for {product.name}. Available: "
                        f"{finished_goods.current_stock}"
                    )

                # Deduct finished goods and create ledger entry
                record_stock_movement(
                    item_code=finished_goods.item_code,
                    movement_type="Dispatch",
                    quantity=quantity,
                    unit_rate=finished_goods.average_rate,
                    reference=order.order_number,
                    notes=f"Dispatch {dispatch_number}",
                    commit=False
                )

                # Update order item's dispatched quantity
                item.dispatched_quantity = (
                    (item.dispatched_quantity or 0)
                    + quantity
                )

                # Create dispatch record
                dispatch_record = Dispatch(
                    dispatch_number=dispatch_number,
                    order_id=order.id,
                    order_item_id=item.id,
                    product_id=product.id,
                    quantity=quantity,
                    notes=dispatch_notes
                )

                db.session.add(dispatch_record)

                dispatched_any = True

            if not dispatched_any:
                raise ValueError(
                    "Enter at least one dispatch quantity."
                )

            # Update order status
            total_order_quantity = sum(
                item.quantity for item in items
            )

            total_dispatched_quantity = sum(
                (item.dispatched_quantity or 0)
                for item in items
            )

            if total_dispatched_quantity >= total_order_quantity:
                order.status = "Dispatched"
            else:
                order.status = "Partially Dispatched"

            db.session.commit()

            flash(
                f"Dispatch {dispatch_number} recorded successfully!",
                "success"
            )

            return redirect(
                url_for("dispatch.dispatch_history")
            )

        except (ValueError, TypeError) as error:

            db.session.rollback()

            flash(str(error), "danger")

            return redirect(
                url_for(
                    "dispatch.process_dispatch",
                    order_id=order.id
                )
            )

        except Exception:

            db.session.rollback()

            flash(
                "Dispatch failed. No changes were saved.",
                "danger"
            )

            return redirect(
                url_for(
                    "dispatch.process_dispatch",
                    order_id=order.id
                )
            )

    return render_template(
        "process_dispatch.html",
        order=order,
        item_rows=item_rows
    )


# ==================================================
# DISPATCH HISTORY
# ==================================================
@dispatch_bp.route("/dispatch/history")
def dispatch_history():

    dispatches = Dispatch.query.order_by(
        Dispatch.dispatch_date.desc()
    ).all()

    dispatch_rows = []

    for dispatch in dispatches:

        order = Order.query.get(dispatch.order_id)

        product = Product.query.get(
            dispatch.product_id
        )

        dispatch_rows.append({
            "dispatch": dispatch,
            "order": order,
            "product": product
        })

    return render_template(
        "dispatch_history.html",
        dispatch_rows=dispatch_rows
    )
