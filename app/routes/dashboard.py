from flask import Blueprint, render_template

from app.models.orders import Order
from app.models.product import Product
from app.models.production import ProductionBatch
from app.models.accounts import Invoice, Payment
from app.models.inventory import InventoryItem


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def main_dashboard():

    # Product and inventory counts
    total_products = Product.query.count()
    total_inventory_items = InventoryItem.query.count()

    # Order statistics
    orders = Order.query.all()

    total_orders = len(orders)

    pending_orders = sum(
        1 for order in orders
        if (order.status or "").lower() == "pending"
    )

    approved_orders = sum(
        1 for order in orders
        if (order.status or "").lower() == "approved"
    )

    rejected_orders = sum(
        1 for order in orders
        if (order.status or "").lower() == "rejected"
    )

    total_sales = sum(
        (order.total_amount or 0 for order in orders),
        0
    )

    recent_orders = Order.query.order_by(
        Order.order_date.desc()
    ).limit(10).all()

    # Production statistics
    total_production_batches = ProductionBatch.query.count()

    # Invoice statistics
    invoices = Invoice.query.all()
    total_invoices = len(invoices)

    # Payment statistics
    payments = Payment.query.all()

    total_payments_received = sum(
        (payment.amount or 0 for payment in payments),
        0
    )

    # Outstanding amount calculation
    total_outstanding = 0

    for invoice in invoices:

        invoice_payments = Payment.query.filter_by(
            invoice_id=invoice.id
        ).all()

        paid_amount = sum(
            (payment.amount or 0 for payment in invoice_payments),
            0
        )

        balance = invoice.total_amount - paid_amount

        if balance > 0:
            total_outstanding += balance

    # Display dashboard
    return render_template(
        "main_dashboard.html",

        total_products=total_products,
        total_inventory_items=total_inventory_items,

        total_orders=total_orders,
        pending_orders=pending_orders,
        approved_orders=approved_orders,
        rejected_orders=rejected_orders,

        total_sales=total_sales,
        recent_orders=recent_orders,

        total_production_batches=total_production_batches,
        total_invoices=total_invoices,

        total_payments_received=total_payments_received,
        total_outstanding=total_outstanding
    )