
from flask import Blueprint, render_template, redirect, url_for, flash

from app.models.orders import Order, OrderItem
from app.models.accounts import Invoice
from app.models.product import Product
from app.services.invoice_service import generate_invoice


invoice_bp = Blueprint("invoices", __name__)


@invoice_bp.route("/invoices")
def invoice_dashboard():

    # Orders that are not pending and do not have an invoice
    orders = Order.query.filter(
        Order.status != "Pending"
    ).order_by(
        Order.order_date.desc()
    ).all()

    eligible_orders = []

    for order in orders:

        existing_invoice = Invoice.query.filter_by(
            order_id=order.id
        ).first()

        if existing_invoice:
            continue

        items = OrderItem.query.filter_by(
            order_id=order.id
        ).all()

        order_products = []

        for item in items:

            product = Product.query.get(item.product_id)

            order_products.append({
                "item": item,
                "product": product
            })

        eligible_orders.append({
            "order": order,
            "items": order_products
        })

    return render_template(
        "invoice_dashboard.html",
        orders=eligible_orders
    )


@invoice_bp.route("/invoices/generate/<int:order_id>")
def generate_order_invoice(order_id):

    invoice, message = generate_invoice(order_id)

    if invoice:
        flash(message, "success")

        return redirect(
            url_for(
                "invoices.view_invoice",
                invoice_id=invoice.id
            )
        )

    flash(message, "danger")

    return redirect(url_for("invoices.invoice_dashboard"))


@invoice_bp.route("/invoices/history")
def invoice_history():

    invoices = Invoice.query.order_by(
        Invoice.invoice_date.desc()
    ).all()

    invoice_rows = []

    for invoice in invoices:

        order = Order.query.get(invoice.order_id)

        invoice_rows.append({
            "invoice": invoice,
            "order": order
        })

    return render_template(
        "invoice_history.html",
        invoice_rows=invoice_rows
    )


@invoice_bp.route("/invoices/<int:invoice_id>")
def view_invoice(invoice_id):

    invoice = Invoice.query.get_or_404(invoice_id)

    order = Order.query.get_or_404(invoice.order_id)

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

    return render_template(
        "invoice_view.html",
        invoice=invoice,
        order=order,
        item_rows=item_rows
    )
