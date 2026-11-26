from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app.models.accounts import Invoice, Payment
from app.models.orders import Order

from app.services.payment_service import (
    record_payment,
    get_total_paid,
    get_outstanding_balance
)


payment_bp = Blueprint("payments", __name__)


# Payment dashboard
@payment_bp.route("/payments")
def payment_dashboard():

    invoices = Invoice.query.order_by(
        Invoice.invoice_date.desc()
    ).all()

    invoice_rows = []

    for invoice in invoices:

        total_paid = get_total_paid(invoice.id)

        balance = get_outstanding_balance(invoice.id)

        order = Order.query.get(invoice.order_id)

        invoice_rows.append({
            "invoice": invoice,
            "order": order,
            "total_paid": total_paid,
            "balance": balance
        })

    return render_template(
        "payment_dashboard.html",
        invoice_rows=invoice_rows
    )


# Record payment
@payment_bp.route(
    "/payments/record/<int:invoice_id>",
    methods=["GET", "POST"]
)
def record_invoice_payment(invoice_id):

    invoice = Invoice.query.get(invoice_id)

    if not invoice:
        flash("Invoice not found.", "error")
        return redirect(url_for("payments.payment_dashboard"))

    order = Order.query.get(invoice.order_id)

    total_paid = get_total_paid(invoice.id)

    balance = get_outstanding_balance(invoice.id)

    if request.method == "POST":

        amount = request.form.get("amount", "").strip()

        payment_method = request.form.get(
            "payment_method", ""
        ).strip()

        reference_number = request.form.get(
            "reference_number", ""
        ).strip()

        payment, message = record_payment(
            invoice_id=invoice.id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number or None
        )

        if payment:

            flash(message, "success")

            return redirect(
                url_for("payments.payment_dashboard")
            )

        flash(message, "error")

    return render_template(
        "payment_form.html",
        invoice=invoice,
        order=order,
        total_paid=total_paid,
        balance=balance
    )


# Payment history
@payment_bp.route("/payments/history")
def payment_history():

    payments = Payment.query.order_by(
        Payment.payment_date.desc()
    ).all()

    payment_rows = []

    for payment in payments:

        invoice = Invoice.query.get(payment.invoice_id)

        order = None

        if invoice:
            order = Order.query.get(invoice.order_id)

        payment_rows.append({
            "payment": payment,
            "invoice": invoice,
            "order": order
        })

    return render_template(
        "payment_history.html",
        payment_rows=payment_rows
    )


# Outstanding balance report
@payment_bp.route("/payments/outstanding")
def outstanding_payments():

    invoices = Invoice.query.all()

    outstanding_rows = []

    for invoice in invoices:

        balance = get_outstanding_balance(invoice.id)

        if balance is not None and balance > 0:

            total_paid = get_total_paid(invoice.id)

            order = Order.query.get(invoice.order_id)

            outstanding_rows.append({
                "invoice": invoice,
                "order": order,
                "total_paid": total_paid,
                "balance": balance
            })

    return render_template(
        "outstanding_payments.html",
        outstanding_rows=outstanding_rows
    )