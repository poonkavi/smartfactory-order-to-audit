
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.product import Product
from app.models.orders import Order, OrderItem

admin_bp = Blueprint("admin", __name__)


# ---------------- PRODUCT MANAGEMENT ----------------

@admin_bp.route("/admin/products", methods=["GET", "POST"])
def products():

    if request.method == "POST":

        name = request.form["name"].strip()
        sku = request.form["sku"].strip().upper()
        selling_price = float(request.form["selling_price"])
        gst_rate = float(request.form["gst_rate"])
        unit = request.form["unit"].strip()
        category = request.form["category"].strip()

        if not name or not sku or not unit or not category:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("admin.products"))

        existing_product = Product.query.filter_by(sku=sku).first()

        if existing_product:
            flash("This product SKU already exists.", "danger")
            return redirect(url_for("admin.products"))

        product = Product(
            name=name,
            sku=sku,
            selling_price=selling_price,
            gst_rate=gst_rate,
            unit=unit,
            category=category
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for("admin.products"))

    all_products = Product.query.order_by(Product.name).all()

    return render_template(
        "products.html",
        products=all_products
    )


# ---------------- ORDER MANAGEMENT ----------------

@admin_bp.route("/admin/orders")
def orders():

    all_orders = Order.query.order_by(
        Order.order_date.desc()
    ).all()

    order_rows = []

    for order in all_orders:

        items = OrderItem.query.filter_by(
            order_id=order.id
        ).all()

        item_rows = []

        for item in items:

            product = Product.query.get(item.product_id)

            item_rows.append({
                "item": item,
                "product": product
            })

        order_rows.append({
            "order": order,
            "items": item_rows
        })

    return render_template(
        "admin_orders.html",
        order_rows=order_rows
    )


# ---------------- APPROVE ORDER ----------------

@admin_bp.route("/admin/orders/<int:order_id>/approve", methods=["POST"])
def approve_order(order_id):

    order = Order.query.get_or_404(order_id)

    if order.status != "Pending":
        flash("Only pending orders can be approved.", "warning")
        return redirect(url_for("admin.orders"))

    order.status = "Approved"

    db.session.commit()

    flash(
        f"Order {order.order_number} approved successfully!",
        "success"
    )

    return redirect(url_for("admin.orders"))


# ---------------- REJECT ORDER ----------------

@admin_bp.route("/admin/orders/<int:order_id>/reject", methods=["POST"])
def reject_order(order_id):

    order = Order.query.get_or_404(order_id)

    if order.status != "Pending":
        flash("Only pending orders can be rejected.", "warning")
        return redirect(url_for("admin.orders"))

    order.status = "Rejected"

    db.session.commit()

    flash(
        f"Order {order.order_number} rejected.",
        "info"
    )

    return redirect(url_for("admin.orders"))
