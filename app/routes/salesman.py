from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.models.user import User
from app.models.product import Product
from app.models.orders import Order
from app.services.order_service import create_order


salesman_bp = Blueprint("salesman", __name__)


# ==================================================
# AUTOMATIC ORDER NUMBER GENERATION
# ==================================================
def generate_order_number():

    existing_orders = Order.query.all()

    highest_number = 0

    for order in existing_orders:
        order_number = order.order_number

        if order_number.startswith("ORD-"):
            number_part = order_number[4:]

            if number_part.isdigit():
                highest_number = max(
                    highest_number,
                    int(number_part)
                )

    next_number = highest_number + 1

    return f"ORD-{next_number:04d}"


# ==================================================
# CREATE SALES ORDER
# ==================================================
@salesman_bp.route("/sales/orders/new", methods=["GET", "POST"])
def new_order():

    # Display only Salesman A
    salesmen = User.query.filter_by(
        username="salesman_a",
        role="Salesman"
    ).all()

    # Fetch all products dynamically from database
    products = Product.query.order_by(
        Product.name.asc()
    ).all()

    if request.method == "POST":

        try:
            salesman_id = int(request.form.get("salesman_id", 0))
            quantity = int(request.form.get("quantity", 0))

        except (ValueError, TypeError):
            flash("Please enter valid salesman and quantity.", "danger")

            return redirect(url_for("salesman.new_order"))

        customer_name = request.form.get(
            "customer_name", ""
        ).strip()

        customer_state = request.form.get(
            "customer_state", ""
        ).strip()

        product_sku = request.form.get(
            "product_sku", ""
        ).strip()

        # Basic form validation
        if not customer_name or not customer_state or not product_sku:
            flash("Please fill in all required fields.", "danger")

            return redirect(url_for("salesman.new_order"))

        if quantity <= 0:
            flash("Quantity must be greater than zero.", "danger")

            return redirect(url_for("salesman.new_order"))

        # Generate order number automatically
        order_number = generate_order_number()

        # Create order using the existing service
        order, message = create_order(
            salesman_id=salesman_id,
            customer_name=customer_name,
            customer_state=customer_state,
            product_sku=product_sku,
            quantity=quantity,
            order_number=order_number
        )

        if order:
            flash(
                f"{message} Order Number: {order_number}",
                "success"
            )

            return redirect(
                url_for("salesman.order_history")
            )

        flash(message, "danger")

    return render_template(
        "sales_order.html",
        salesmen=salesmen,
        products=products
    )


# ==================================================
# ORDER HISTORY
# ==================================================
@salesman_bp.route("/sales/orders")
def order_history():

    # Fetch orders with newest orders displayed first
    orders = Order.query.order_by(
        Order.order_date.desc()
    ).all()

    return render_template(
        "order_history.html",
        orders=orders
    )