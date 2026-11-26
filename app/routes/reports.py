
from flask import Blueprint, render_template

from app.models.orders import Order, OrderItem
from app.models.accounts import Invoice, Payment
from app.models.product import Product
from app.models.production import ProductionBatch

# Purchase model import
try:
    from app.models.inventory import Purchase
except ImportError:
    from app.models.purchase import Purchase


reports_bp = Blueprint("reports", __name__)


# --------------------------------------------------
# REPORTS DASHBOARD
# --------------------------------------------------

@reports_bp.route("/reports")
def reports_dashboard():

    orders = Order.query.all()
    invoices = Invoice.query.all()
    payments = Payment.query.all()
    purchases = Purchase.query.all()
    batches = ProductionBatch.query.all()

    total_orders = len(orders)
    total_sales = sum(
        (order.total_amount or 0 for order in orders), 0
    )

    total_invoices = len(invoices)

    total_payments = sum(
        (payment.amount or 0 for payment in payments), 0
    )

    total_purchases = sum(
        (purchase.total_amount or 0 for purchase in purchases), 0
    )

    total_production_batches = len(batches)

    total_outstanding = 0

    for invoice in invoices:

        invoice_payments = Payment.query.filter_by(
            invoice_id=invoice.id
        ).all()

        paid = sum(
            (payment.amount or 0 for payment in invoice_payments), 0
        )

        balance = invoice.total_amount - paid

        if balance > 0:
            total_outstanding += balance

    return render_template(
        "reports_dashboard.html",
        total_orders=total_orders,
        total_sales=total_sales,
        total_invoices=total_invoices,
        total_payments=total_payments,
        total_purchases=total_purchases,
        total_production_batches=total_production_batches,
        total_outstanding=total_outstanding
    )


# --------------------------------------------------
# SALES REPORT
# --------------------------------------------------

@reports_bp.route("/reports/sales")
def sales_report():

    orders = Order.query.order_by(
        Order.order_date.desc()
    ).all()

    total_sales = sum(
        (order.total_amount or 0 for order in orders), 0
    )

    return render_template(
        "sales_report.html",
        orders=orders,
        total_sales=total_sales,
        total_orders=len(orders)
    )


# --------------------------------------------------
# PURCHASE REPORT
# --------------------------------------------------

@reports_bp.route("/reports/purchases")
def purchase_report():

    purchases = Purchase.query.order_by(
        Purchase.purchase_date.desc()
    ).all()

    total_purchase_amount = sum(
        (purchase.total_amount or 0 for purchase in purchases), 0
    )

    total_purchase_records = len(purchases)

    total_quantity = sum(
        (purchase.quantity or 0 for purchase in purchases), 0
    )

    return render_template(
        "purchase_report.html",
        purchases=purchases,
        total_purchase_amount=total_purchase_amount,
        total_purchase_records=total_purchase_records,
        total_quantity=total_quantity
    )


# --------------------------------------------------
# PRODUCTION REPORT
# --------------------------------------------------

@reports_bp.route("/reports/production")
def production_report():

    batches = ProductionBatch.query.order_by(
        ProductionBatch.production_date.desc()
    ).all()

    production_rows = []

    total_planned = 0
    total_actual = 0
    total_rejected = 0
    total_damaged_packaging = 0

    for batch in batches:

        product = Product.query.get(batch.product_id)

        planned = batch.planned_output or 0
        actual = batch.actual_output or 0
        rejected = batch.rejected_quantity or 0
        damaged = batch.damaged_packaging_quantity or 0

        total_planned += planned
        total_actual += actual
        total_rejected += rejected
        total_damaged_packaging += damaged

        achievement = 0

        if planned > 0:
            achievement = round(
                (actual / planned) * 100, 2
            )

        production_rows.append({
            "batch": batch,
            "product": product,
            "achievement": achievement
        })

    overall_achievement = 0

    if total_planned > 0:
        overall_achievement = round(
            (total_actual / total_planned) * 100, 2
        )

    return render_template(
        "production_report.html",
        production_rows=production_rows,
        total_batches=len(batches),
        total_planned=total_planned,
        total_actual=total_actual,
        total_rejected=total_rejected,
        total_damaged_packaging=total_damaged_packaging,
        overall_achievement=overall_achievement
    )


# --------------------------------------------------
# DISPATCH REPORT
# --------------------------------------------------

@reports_bp.route("/reports/dispatch")
def dispatch_report():

    order_items = OrderItem.query.filter(
        OrderItem.dispatched_quantity > 0
    ).all()

    dispatch_rows = []

    total_dispatched_quantity = 0
    total_dispatch_records = 0

    for item in order_items:

        order = Order.query.get(item.order_id)
        product = Product.query.get(item.product_id)

        dispatched = item.dispatched_quantity or 0

        total_dispatched_quantity += dispatched
        total_dispatch_records += 1

        dispatch_rows.append({
            "item": item,
            "order": order,
            "product": product
        })

    return render_template(
        "dispatch_report.html",
        dispatch_rows=dispatch_rows,
        total_dispatch_records=total_dispatch_records,
        total_dispatched_quantity=total_dispatched_quantity
    )


# --------------------------------------------------
# PAYMENT REPORT
# --------------------------------------------------

@reports_bp.route("/reports/payments")
def payment_report():

    payments = Payment.query.order_by(
        Payment.payment_date.desc()
    ).all()

    total_received = sum(
        (payment.amount or 0 for payment in payments), 0
    )

    return render_template(
        "payment_report.html",
        payments=payments,
        total_received=total_received,
        total_payment_count=len(payments)
    )


# --------------------------------------------------
# OUTSTANDING REPORT
# --------------------------------------------------

@reports_bp.route("/reports/outstanding")
def outstanding_report():

    invoices = Invoice.query.all()

    outstanding_rows = []
    total_outstanding = 0
    total_outstanding_invoices = 0

    for invoice in invoices:

        payments = Payment.query.filter_by(
            invoice_id=invoice.id
        ).all()

        paid_amount = sum(
            (payment.amount or 0 for payment in payments), 0
        )

        balance = invoice.total_amount - paid_amount

        if balance > 0:

            order = Order.query.get(invoice.order_id)

            outstanding_rows.append({
                "invoice": invoice,
                "order": order,
                "paid_amount": paid_amount,
                "balance": balance
            })

            total_outstanding += balance
            total_outstanding_invoices += 1

    return render_template(
        "outstanding_report.html",
        outstanding_rows=outstanding_rows,
        total_outstanding=total_outstanding,
        total_outstanding_invoices=total_outstanding_invoices
    )
